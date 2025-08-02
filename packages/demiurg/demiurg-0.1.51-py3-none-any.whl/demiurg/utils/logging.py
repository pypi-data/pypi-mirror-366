"""
Logging utilities for the Demiurg SDK.
"""

import logging
import os
from typing import Optional


def configure_third_party_logging(level: Optional[str] = None):
    """
    Configure logging levels for third-party libraries to reduce verbosity.
    
    Args:
        level: Logging level for third-party libraries. Defaults to WARNING.
    """
    if level is None:
        level = os.getenv('DEMIURG_THIRD_PARTY_LOG_LEVEL', 'WARNING')
    
    # Set logging levels for verbose third-party libraries
    third_party_loggers = [
        'apscheduler',
        'apscheduler.scheduler',
        'apscheduler.executors',
        'apscheduler.executors.default', 
        'httpcore',
        'httpcore.connection',
        'httpcore.http11',
        'openai._base_client',
        'urllib3',
        'requests'
    ]
    
    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(getattr(logging, level.upper()))


def setup_demiurg_logging(level: str = "INFO"):
    """
    Setup logging configuration for Demiurg SDK.
    
    Args:
        level: Log level for Demiurg loggers (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure root demiurg logger
    demiurg_logger = logging.getLogger('demiurg')
    demiurg_logger.setLevel(getattr(logging, level.upper()))
    
    # Configure third-party logging
    configure_third_party_logging()