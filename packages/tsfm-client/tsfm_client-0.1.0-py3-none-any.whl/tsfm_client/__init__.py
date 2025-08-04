"""
TSFM Client - Python client library for TSFM Inference Platform
"""

from .client import TSFMClient, predict, clear_cache
from .models import (
    TimeSeriesData,
    PredictionRequest,
    PredictionResponse,
    TSFMException,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    APIError
)

__version__ = "0.1.0"
__all__ = [
    "TSFMClient",
    "predict",
    "clear_cache",
    "TimeSeriesData",
    "PredictionRequest", 
    "PredictionResponse",
    "TSFMException",
    "AuthenticationError",
    "RateLimitError",
    "ModelNotFoundError",
    "APIError",
]

# Alias for backward compatibility
SimpleTSFMClient = TSFMClient