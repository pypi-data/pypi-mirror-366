"""
sagikoza: A Python library for crawling Japan's Furikome Sagi Relief Act notices.

This library provides functions to automatically retrieve public notices under 
Japan's Furikome Sagi Relief Act, supporting both full and incremental data extraction.
"""

from .core import (
    fetch,
    FetchError,
    ValidationError,
    SagiKozaError,
    ErrorType,
    ProcessingStats,
    DEFAULT_MAX_WORKERS,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY
)

__version__ = "2.1.0"
__author__ = "new-village"
__email__ = ""
__description__ = "A Python library for crawling and retrieving all notices published under Japan's Furikome Sagi Relief Act"

# 主要な公開API
__all__ = [
    'fetch',
    'get_data',
    'FetchError',
    'ValidationError', 
    'SagiKozaError',
    'ErrorType',
    'ProcessingStats',
    'DEFAULT_MAX_WORKERS',
    'DEFAULT_TIMEOUT',
    'DEFAULT_MAX_RETRIES',
    'DEFAULT_RETRY_DELAY'
]
