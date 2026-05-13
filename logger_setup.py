import logging
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = request_id_var.get()
        return True

class StackTraceFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return f"\n--- STACK TRACE ---\n{result}\n-------------------"

def setup_logger():
    logger = logging.getLogger("telemetry_logger")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler("telemetry.log")
        handler.addFilter(TraceIdFilter())
        formatter = StackTraceFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - TraceID: %(trace_id)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()
