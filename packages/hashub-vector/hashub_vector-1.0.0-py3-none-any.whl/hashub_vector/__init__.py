"""
Hashub Vector SDK - Python client for Hashub Vector API

A powerful, easy-to-use Python SDK for the Hashub Vector API that provides 
high-quality text embeddings with multilingual support.

Features:
- 6 embedding models with different performance/cost trade-offs
- Support for 80+ languages including Turkish
- Async/sync support with automatic retries
- Built-in rate limiting and error handling
- OpenAI-compatible interface
- Comprehensive documentation

Example:
    >>> from hashub_vector import HashubVector
    >>> client = HashubVector(api_key="your-api-key")
    >>> embeddings = client.vectorize("Merhaba dünya!")
    >>> print(embeddings.vector[:5])  # First 5 dimensions
"""

from .client import HashubVector
from .models import (
    VectorizeRequest,
    VectorizeResponse,
    BatchVectorizeRequest,
    BatchVectorizeResponse,
    ModelInfo,
    ModelAlias,
    ModelTier,
    MODEL_CONFIGS,
    UsageResponse,
    UsageStats,
    DailyUsage,
    TopModel,
    Usage
)
from .exceptions import (
    HashubVectorError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    ValidationError
)

__version__ = "1.0.0"
__author__ = "Hashub Team"
__email__ = "support@Hashub.dev"
__description__ = "Python SDK for Hashub Vector API - High-quality multilingual text embeddings"

__all__ = [
    "HashubVector",
    "VectorizeRequest",
    "VectorizeResponse", 
    "BatchVectorizeRequest",
    "BatchVectorizeResponse",
    "ModelInfo",
    "ModelAlias",
    "ModelTier",
    "MODEL_CONFIGS",
    "UsageResponse",
    "UsageStats", 
    "DailyUsage",
    "TopModel",
    "Usage",
    "HashubVectorError",
    "AuthenticationError",
    "RateLimitError",
    "ModelNotFoundError",
    "ValidationError"
]
