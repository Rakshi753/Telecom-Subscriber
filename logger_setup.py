import logging
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = request_id_var.get()
        return True

def setup_logger():
    logger = logging.getLogger("telemetry_logger")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler("telemetry.log")
        handler.addFilter(TraceIdFilter())
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - TraceID: %(trace_id)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()
