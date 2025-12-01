"""Middleware de logging"""

import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formatter pour logs JSON"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)


def setup_logging():
    """Configurer le logging structuré"""
    logger = logging.getLogger("formbuilder")
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
