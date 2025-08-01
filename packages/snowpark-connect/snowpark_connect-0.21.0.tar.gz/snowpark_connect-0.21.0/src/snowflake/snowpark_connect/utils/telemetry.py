#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import json
import os
import queue
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from contextvars import ContextVar
from enum import Enum, unique
from typing import Dict

import google.protobuf.message

from snowflake.connector.telemetry import (
    TelemetryClient as PCTelemetryClient,
    TelemetryData as PCTelemetryData,
    TelemetryField as PCTelemetryField,
)
from snowflake.connector.time_util import get_time_millis
from snowflake.snowpark import Session
from snowflake.snowpark._internal.telemetry import safe_telemetry
from snowflake.snowpark._internal.utils import get_os_name, get_python_version
from snowflake.snowpark.version import VERSION as snowpark_version
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger
from snowflake.snowpark_connect.version import VERSION as sas_version


@unique
class TelemetryField(Enum):
    # inherited from snowflake.connector.telemetry.TelemetryField
    KEY_TYPE = PCTelemetryField.KEY_TYPE.value
    KEY_SOURCE = PCTelemetryField.KEY_SOURCE.value

    # constants
    KEY_ERROR_MSG = "error_msg"
    # Message keys for telemetry
    KEY_VERSION = "version"
    KEY_PYTHON_VERSION = "python_version"
    KEY_SNOWPARK_VERSION = "snowpark_version"
    KEY_OS = "operating_system"
    KEY_DATA = "data"
    KEY_START_TIME = "start_time"


class TelemetryType(Enum):
    TYPE_REQUEST_SUMMARY = "scos_request_summary"
    TYPE_EVENT = "scos_event"
    EVENT_TYPE = "scos_event_type"


class EventType(Enum):
    SERVER_STARTED = "scos_server_started"


# global labels
SOURCE = "SparkConnectForSnowpark"
SCOS_VERSION = ".".join([str(d) for d in sas_version if d is not None])
SNOWPARK_VERSION = ".".join([str(d) for d in snowpark_version if d is not None])
PYTHON_VERSION = get_python_version()
OS = get_os_name()

STATIC_TELEMETRY_DATA = {
    TelemetryField.KEY_SOURCE.value: SOURCE,
    TelemetryField.KEY_VERSION.value: SCOS_VERSION,
    TelemetryField.KEY_SNOWPARK_VERSION.value: SNOWPARK_VERSION,
    TelemetryField.KEY_PYTHON_VERSION.value: PYTHON_VERSION,
    TelemetryField.KEY_OS.value: OS,
}

# list of config keys for which we record values, other config values are not recorded
RECORDED_CONFIG_KEYS = {
    "spark.sql.pyspark.inferNestedDictAsStruct.enabled",
    "spark.sql.pyspark.legacy.inferArrayTypeFromFirstElement.enabled",
    "spark.sql.repl.eagerEval.enabled",
    "spark.sql.crossJoin.enabled",
    "spark.sql.caseSensitive",
    "spark.sql.ansi.enabled",
    "spark.Catalog.databaseFilterInformationSchema",
    "spark.sql.tvf.allowMultipleTableArguments.enabled",
    "spark.sql.repl.eagerEval.maxNumRows",
    "spark.sql.repl.eagerEval.truncate",
    "spark.sql.session.localRelationCacheThreshold",
    "spark.sql.mapKeyDedupPolicy",
    "snowpark.connect.sql.passthrough",
    "snowpark.connect.iceberg.external_volume",
    "snowpark.connect.sql.identifiers.auto-uppercase",
    "snowpark.connect.udtf.compatibility_mode",
    "snowpark.connect.views.duplicate_column_names_handling_mode",
}

# io types for which we don't track options
REDACTED_IO_TYPES = {
    "jdbc",
    "net.snowflake.spark.snowflake",
}

# these fields will be redacted when reporting the spark query plan
REDACTED_PLAN_SUFFIXES = [
    # config values can be set using SQL, so we have to redact it
    "sql",
    "pairs.value",
    "local_relation",
    "options",
]


class TelemetrySink(ABC):
    @abstractmethod
    def add_telemetry_data(self, message: dict, timestamp: int) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass


class NoOpTelemetrySink(TelemetrySink):
    def add_telemetry_data(self, message: dict, timestamp: int) -> None:
        pass

    def flush(self) -> None:
        pass


class ClientTelemetrySink(TelemetrySink):
    def __init__(self, telemetry_client: PCTelemetryClient) -> None:
        self._telemetry_client = telemetry_client

    def add_telemetry_data(self, message: dict, timestamp: int) -> None:
        telemetry_data = PCTelemetryData(message=message, timestamp=timestamp)
        self._telemetry_client.try_add_log_to_batch(telemetry_data)

    def flush(self) -> None:
        self._telemetry_client.send_batch()


class QueryTelemetrySink(TelemetrySink):

    MAX_BUFFER_SIZE = 100 * 1024  # 100KB
    MAX_WAIT_MS = 10000  # 10 seconds
    TELEMETRY_JOB_ID = "43e72d9b-56d0-4cdb-a615-6b5b5059d6df"

    def __init__(self, session: Session) -> None:
        self._session = session
        self._reset()

    def add_telemetry_data(self, message: dict, timestamp: int) -> None:
        telemetry_entry = {"message": message, "timestamp": timestamp}

        # stringify entry, and escape single quotes
        entry_str = json.dumps(telemetry_entry).replace("'", "''")
        self._buffer.append(entry_str)
        self._buffer_size += len(entry_str)

        current_time = get_time_millis()
        if (
            self._buffer_size > QueryTelemetrySink.MAX_BUFFER_SIZE
            or (current_time - self._last_export_time) > QueryTelemetrySink.MAX_WAIT_MS
        ):
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return

        # prefix query with a unique identifier for easier tracking
        query = f"select '{self.TELEMETRY_JOB_ID}' as scos_telemetry_export, '[{','.join(self._buffer)}]'"
        self._session.sql(query).collect_nowait()

        self._reset()

    def _reset(self) -> None:
        self._buffer = []
        self._buffer_size = 0
        self._last_export_time = get_time_millis()


class Telemetry:
    def __init__(self, is_enabled=True) -> None:
        self._sink = NoOpTelemetrySink()  # use no-op sink until initialized
        self._request_summary: ContextVar[dict] = ContextVar(
            "request_summary", default={}
        )
        self._is_enabled = is_enabled

        # Async processing setup
        self._message_queue = queue.Queue(maxsize=10000)
        self._worker_thread = None

    def __del__(self):
        self.shutdown()

    def initialize(self, session: Session):
        """
        Must be called after the session is created to initialize telemetry.
        Gets the telemetry client from the session's connection and uses it
        to report telemetry data.
        """
        if not self._is_enabled:
            return

        telemetry = getattr(session._conn._conn, "_telemetry", None)
        if telemetry is None:
            # no telemetry client available, so we export with queries
            self._sink = QueryTelemetrySink(session)
        else:
            self._sink = ClientTelemetrySink(telemetry)

        self._start_worker_thread()

    @safe_telemetry
    def initialize_request_summary(
        self, request: google.protobuf.message.Message
    ) -> None:
        summary = {
            "client_type": request.client_type,
            "spark_session_id": request.session_id,
            "request_type": request.__class__.__name__,
            "was_successful": True,
            "internal_queries": 0,
            "created_on": get_time_millis(),
        }

        if hasattr(request, "operation_id"):
            summary["spark_operation_id"] = request.operation_id

        self._request_summary.set(summary)

        if hasattr(request, "plan"):
            summary["query_plan"] = _protobuf_to_json_with_redaction(
                request.plan, REDACTED_PLAN_SUFFIXES
            )

    @safe_telemetry
    def report_function_usage(self, function_name: str) -> None:
        summary = self._request_summary.get()

        if "used_functions" not in summary:
            summary["used_functions"] = defaultdict(int)

        summary["used_functions"][function_name] += 1

    @safe_telemetry
    def report_request_failure(self, e: Exception) -> None:
        summary = self._request_summary.get()

        summary["was_successful"] = False
        summary["error_message"] = str(e)
        summary["error_type"] = type(e).__name__

        error_location = _error_location(e)
        if error_location:
            summary["error_location"] = error_location

    @safe_telemetry
    def report_config_set(self, key, value):
        summary = self._request_summary.get()

        if "config_set" not in summary:
            summary["config_set"] = []

        summary["config_set"].append(
            {
                "key": key,
                "value": value if key in RECORDED_CONFIG_KEYS else "<redacted>",
            }
        )

    @safe_telemetry
    def report_config_unset(self, key):
        summary = self._request_summary.get()

        if "config_unset" not in summary:
            summary["config_unset"] = []

        summary["config_unset"].append(key)

    @safe_telemetry
    def report_config_op_type(self, op_type: str):
        summary = self._request_summary.get()

        summary["config_op_type"] = op_type

    @safe_telemetry
    def report_query_id(self, query_id: str):
        summary = self._request_summary.get()

        if "queries" not in summary:
            summary["queries"] = []

        summary["queries"].append(query_id)

    @safe_telemetry
    def report_internal_query(self):
        summary = self._request_summary.get()
        summary["internal_queries"] += 1

    @safe_telemetry
    def report_udf_usage(self, udf_name: str):
        summary = self._request_summary.get()

        if "udf_usage" not in summary:
            summary["udf_usage"] = defaultdict(int)

        summary["udf_usage"][udf_name] += 1

    @safe_telemetry
    def report_io(self, op: str, type: str, options: dict | None):
        summary = self._request_summary.get()

        if "io" not in summary:
            summary["io"] = []

        if options is None or type.lower() in REDACTED_IO_TYPES:
            io = {"op": op, "type": type}
        else:
            io = {"op": op, "type": type, "options": options}

        summary["io"].append(io)

    def report_io_read(self, type: str, options: dict | None):
        self.report_io("read", type, options)

    def report_io_write(self, type: str, options: dict | None):
        self.report_io("write", type, options)

    @safe_telemetry
    def send_server_started_telemetry(self):
        message = {
            **STATIC_TELEMETRY_DATA,
            TelemetryField.KEY_TYPE.value: TelemetryType.TYPE_EVENT.value,
            TelemetryType.EVENT_TYPE.value: EventType.SERVER_STARTED.value,
            TelemetryField.KEY_DATA.value: {
                TelemetryField.KEY_START_TIME.value: get_time_millis(),
            },
        }
        self._send(message)

    @safe_telemetry
    def send_request_summary_telemetry(self):
        summary = self._request_summary.get()
        message = {
            **STATIC_TELEMETRY_DATA,
            TelemetryField.KEY_TYPE.value: TelemetryType.TYPE_REQUEST_SUMMARY.value,
            TelemetryField.KEY_DATA.value: summary,
        }
        self._send(message)

    @safe_telemetry
    def _send(self, msg: Dict) -> None:
        """Queue a telemetry message for asynchronous processing."""
        if not self._is_enabled:
            return

        timestamp = get_time_millis()
        try:
            self._message_queue.put_nowait((msg, timestamp))
        except queue.Full:
            # If queue is full, drop the message to avoid blocking
            logger.warning("Telemetry queue is full, dropping message")

    def _start_worker_thread(self) -> None:
        """Start the background worker thread for processing telemetry messages."""
        if self._worker_thread is None:
            self._worker_thread = threading.Thread(
                target=self._worker_loop, daemon=True, name="TelemetryWorker"
            )
            self._worker_thread.start()

    def _worker_loop(self) -> None:
        """Worker thread loop that processes messages from the queue."""
        while True:
            try:
                # block to allow the GIL to switch threads
                message, timestamp = self._message_queue.get()
                if timestamp is None and message is None:
                    # shutdown
                    break
                self._sink.add_telemetry_data(message, timestamp)
            except Exception:
                logger.warning("Failed to add telemetry message to sink", exc_info=True)
            finally:
                self._message_queue.task_done()

        # Process any remaining messages
        while not self._message_queue.empty():
            try:
                message, timestamp = self._message_queue.get_nowait()
                self._sink.add_telemetry_data(message, timestamp)
                self._message_queue.task_done()
            except Exception:
                logger.warning(
                    "Failed to add remaining telemetry messages to sink during shutdown",
                    exc_info=True,
                )
                break

        # Flush the sink
        self._sink.flush()

    def shutdown(self) -> None:
        """Shutdown the telemetry worker thread and flush any remaining messages."""
        if not self._worker_thread or self._worker_thread.is_alive():
            return

        try:
            self._message_queue.put_nowait((None, None))
            # Wait for worker thread to finish
            self._worker_thread.join(timeout=3.0)
        except Exception:
            logger.warning(
                "Could not put shutdown message on telemetry queue", exc_info=True
            )


def _error_location(e: Exception) -> Dict | None:
    """
    Inspect the exception traceback and extract the file name, line number, and function name
    from the last frame (the one that raised the exception).
    """
    tb = e.__traceback__
    if tb is None:
        return None

    while tb.tb_next is not None:
        tb = tb.tb_next

    # Get just the file name without the path
    full_path = tb.tb_frame.f_code.co_filename
    file_name = full_path.split("/")[-1]

    return {
        "file": file_name,
        "line": tb.tb_lineno,
        "fn": tb.tb_frame.f_code.co_name,
    }


def _protobuf_to_json_with_redaction(
    message: google.protobuf.message.Message, redacted_suffixes: list[str]
) -> dict:
    """
    Convert a protobuf Message to JSON dict with selective field redaction.

    Args:
        message: The protobuf Message to convert
        redacted_suffixes: List of field path suffixes to redact (e.g. ["jdbc.options"])

    Returns:
        Dictionary representation with specified fields redacted
    """

    MAX_MESSAGE_SIZE = 200 * 1024  # 200KB

    def _convert_field_value(value, field_descriptor, field_path: str):
        """Convert a protobuf field value to its JSON representation"""
        # Check if this field should be redacted
        should_redact = any(field_path.endswith(suffix) for suffix in redacted_suffixes)
        if should_redact:
            return "<redacted>"

        # Handle different field types
        if field_descriptor.type == field_descriptor.TYPE_MESSAGE:
            if field_descriptor.label == field_descriptor.LABEL_REPEATED:
                # Repeated message field
                return [_protobuf_to_json_recursive(item, field_path) for item in value]
            else:
                # Singular message field
                return _protobuf_to_json_recursive(value, field_path)
        elif field_descriptor.label == field_descriptor.LABEL_REPEATED:
            # Repeated scalar field
            return list(value)
        else:
            # Singular scalar field
            return value

    def _protobuf_to_json_recursive(
        msg: google.protobuf.message.Message, current_path: str = ""
    ) -> dict:
        """Recursively convert protobuf message to dict"""
        result = {}

        # Use ListFields() to get all set fields
        for field_descriptor, field_value in msg.ListFields():
            field_name = field_descriptor.name
            field_path = f"{current_path}.{field_name}" if current_path else field_name

            # Convert the field value
            result[field_name] = _convert_field_value(
                field_value, field_descriptor, field_path
            )

        return result

    return (
        _protobuf_to_json_recursive(message)
        if message.ByteSize() <= MAX_MESSAGE_SIZE
        # do not report huge query plans to avoid failures when sending telemetry
        else "<too_big>"
    )


# global telemetry client
telemetry = Telemetry(is_enabled="SNOWPARK_CONNECT_DISABLE_TELEMETRY" not in os.environ)


class SnowparkConnectNotImplementedError(NotImplementedError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
