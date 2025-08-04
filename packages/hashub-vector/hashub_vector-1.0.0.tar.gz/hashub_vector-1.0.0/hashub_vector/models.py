"""
HashHub Vector API Python SDK - Data Models

This module defines the data models and schemas used by the HashHub Vector SDK
for request/response handling and type safety.
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class ModelAlias(str, Enum):
    """Available embedding model aliases."""
    GTE_BASE = "gte_base"
    NOMIC_BASE = "nomic_base" 
    E5_BASE = "e5_base"
    MPNET_BASE = "mpnet_base"
    E5_SMALL = "e5_small"
    MINILM_BASE = "minilm_base"


class ModelTier(str, Enum):
    """Model pricing tiers."""
    PREMIUM = "premium"
    STANDARD = "standard"
    BUDGET = "budget"


@dataclass
class ModelInfo:
    """Information about an embedding model."""
    alias: str
    full_name: str
    dimension: int
    max_tokens: int
    price_per_1m_tokens: float
    tier: ModelTier
    description: str
    languages: List[str] = field(default_factory=list)
    
    @property
    def is_premium(self) -> bool:
        """Check if model is premium tier."""
        return self.tier == ModelTier.PREMIUM
        
    @property
    def is_budget(self) -> bool:
        """Check if model is budget tier."""
        return self.tier == ModelTier.BUDGET


@dataclass
class VectorizeRequest:
    """Request for single text vectorization."""
    text: str
    model: str = "e5_base"
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[float] = None
    normalize: bool = True
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.text.strip():
            raise ValueError("Text cannot be empty")
        if self.chunk_size is not None and self.chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap is not None and not 0 <= self.chunk_overlap <= 1:
            raise ValueError("chunk_overlap must be between 0 and 1")


@dataclass
class VectorizeResponse:
    """Response from single text vectorization."""
    vector: List[float]
    model: str
    dimension: int
    token_count: int
    chunk_count: int = 1
    processing_time_ms: Optional[float] = None
    
    @property
    def magnitude(self) -> float:
        """Calculate vector magnitude (L2 norm)."""
        return sum(x * x for x in self.vector) ** 0.5


@dataclass
class BatchVectorizeRequest:
    """Request for batch text vectorization."""
    texts: List[str]
    model: str = "e5_base"
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[float] = None
    normalize: bool = True
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.texts:
            raise ValueError("texts cannot be empty")
        if any(not text.strip() for text in self.texts):
            raise ValueError("All texts must be non-empty")
        if len(self.texts) > 1000:
            raise ValueError("Maximum 1000 texts per batch")
        if self.chunk_size is not None and self.chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap is not None and not 0 <= self.chunk_overlap <= 1:
            raise ValueError("chunk_overlap must be between 0 and 1")


@dataclass
class BatchVectorizeResponse:
    """Response from batch text vectorization."""
    vectors: List[List[float]]
    model: str
    dimension: int
    token_counts: List[int]
    chunk_counts: List[int]
    total_tokens: int
    processing_time_ms: Optional[float] = None
    
    @property
    def count(self) -> int:
        """Number of vectors returned."""
        return len(self.vectors)
    
    def get_vector(self, index: int) -> List[float]:
        """Get vector by index with bounds checking."""
        if not 0 <= index < len(self.vectors):
            raise IndexError(f"Vector index {index} out of range")
        return self.vectors[index]


@dataclass
class Usage:
    """API usage information."""
    tokens_used: int
    tokens_remaining: Optional[int] = None
    requests_used: int = 0
    requests_remaining: Optional[int] = None
    
    @property
    def tokens_percentage_used(self) -> Optional[float]:
        """Calculate percentage of tokens used."""
        if self.tokens_remaining is None:
            return None
        total = self.tokens_used + self.tokens_remaining
        return (self.tokens_used / total) * 100 if total > 0 else 0


@dataclass
class APIResponse:
    """Generic API response wrapper."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    usage: Optional[Usage] = None
    
    @classmethod
    def success_response(cls, data: Dict[str, Any], usage: Optional[Usage] = None) -> "APIResponse":
        """Create successful response."""
        return cls(success=True, data=data, usage=usage)
    
    @classmethod
    def error_response(cls, error: str) -> "APIResponse":
        """Create error response."""
        return cls(success=False, error=error)


# Model configuration constants
MODEL_CONFIGS = {
    ModelAlias.GTE_BASE: ModelInfo(
        alias="gte_base",
        full_name="Alibaba-NLP/gte-multilingual-base",
        dimension=768,
        max_tokens=8192,
        price_per_1m_tokens=0.01,
        tier=ModelTier.PREMIUM,
        description="Premium model optimized for long documents and RAG systems"
    ),
    ModelAlias.NOMIC_BASE: ModelInfo(
        alias="nomic_base", 
        full_name="nomic-ai/nomic-embed-text-v2-moe",
        dimension=768,
        max_tokens=2048,
        price_per_1m_tokens=0.005,
        tier=ModelTier.PREMIUM,
        description="Balanced performance model with Mixture of Experts architecture"
    ),
    ModelAlias.E5_BASE: ModelInfo(
        alias="e5_base",
        full_name="intfloat/multilingual-e5-base", 
        dimension=768,
        max_tokens=512,
        price_per_1m_tokens=0.003,
        tier=ModelTier.STANDARD,
        description="Excellent for search and retrieval applications"
    ),
    ModelAlias.MPNET_BASE: ModelInfo(
        alias="mpnet_base",
        full_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        dimension=768,
        max_tokens=512, 
        price_per_1m_tokens=0.0035,
        tier=ModelTier.STANDARD,
        description="Optimized for Q&A and semantic similarity tasks"
    ),
    ModelAlias.E5_SMALL: ModelInfo(
        alias="e5_small",
        full_name="intfloat/multilingual-e5-small",
        dimension=384,
        max_tokens=512,
        price_per_1m_tokens=0.002,
        tier=ModelTier.BUDGET,
        description="Fast processing for high-volume applications"
    ),
    ModelAlias.MINILM_BASE: ModelInfo(
        alias="minilm_base",
        full_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        dimension=384,
        max_tokens=512,
        price_per_1m_tokens=0.0025,
        tier=ModelTier.BUDGET,
        description="Ultra-fast processing for lightweight applications"
    )
}


@dataclass
class DailyUsage:
    """Daily usage statistics."""
    date: str
    requests: int
    tokens: int
    cost: float
    models_used: Dict[str, int] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Usage summary statistics."""
    user_id: str
    user_email: str
    total_requests: int
    total_tokens: int
    total_cost: float
    current_balance: float
    period_start: str
    period_end: str


@dataclass
class TopModel:
    """Top model usage statistics."""
    model: str
    requests: int
    tokens: int
    cost: float
    percentage: float


@dataclass
class UsageResponse:
    """Complete usage response."""
    summary: UsageStats
    daily_breakdown: List[DailyUsage] = field(default_factory=list)
    top_models: List[TopModel] = field(default_factory=list)


@dataclass
class UsageRequest:
    """Usage request parameters."""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: str = "last_30_days"
    include_daily_breakdown: bool = True
    
    def __post_init__(self):
        """Validate period parameter."""
        valid_periods = ["today", "yesterday", "last_7_days", "last_30_days", "this_month", "last_month"]
        if self.period not in valid_periods:
            raise ValueError(f"Invalid period. Must be one of: {valid_periods}")


# Legacy Usage class for backward compatibility
@dataclass
class Usage:
    """Legacy usage information for backward compatibility."""
    tokens_used: int
    tokens_remaining: Optional[int] = None
    requests_used: int = 0
    requests_remaining: Optional[int] = None
    
    @property
    def tokens_percentage_used(self) -> float:
        """Calculate percentage of tokens used."""
        if self.tokens_remaining is None:
            return 0.0
        total = self.tokens_used + self.tokens_remaining
        return (self.tokens_used / total * 100) if total > 0 else 0.0
