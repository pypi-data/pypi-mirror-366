"""
Hashub Vector API Python SDK - Main Client

This module provides the main client class for interacting with the Hashub Vector API.
Supports both synchronous and asynchronous operations with comprehensive error handling.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, Union
import httpx
import json
from urllib.parse import urljoin

from .models import (
    VectorizeRequest,
    VectorizeResponse,
    BatchVectorizeRequest,
    BatchVectorizeResponse,
    ModelInfo,
    MODEL_CONFIGS,
    Usage,
    UsageResponse,
    UsageStats,
    DailyUsage,
    TopModel,
    APIResponse
)
from .exceptions import (
    HashubVectorError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    ValidationError,
    QuotaExceededError,
    ServerError,
    TimeoutError,
    NetworkError
)


class HashubVector:
    """
    HasHub Vector API Python SDK Client

    A comprehensive client for the HasHub Vector API that provides high-quality
    text embeddings with multilingual support.
    
    Features:
    - Support for 6 embedding models
    - Async/sync operations
    - Automatic retries with exponential backoff
    - Rate limiting
    - Comprehensive error handling
    - OpenAI-compatible interface
    
    Args:
        api_key: Your Hashub Vector API key
        base_url: API base URL (default: https://vector.Hashub.dev)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries (default: 3)
        retry_delay: Initial retry delay in seconds (default: 1)
        
    Example:
        >>> client = HasHubVector(api_key="your-api-key")
        >>> response = client.vectorize("Merhaba dünya!")
        >>> print(response.vector[:5])  # First 5 dimensions
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://vector.hashub.dev",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        user_agent: Optional[str] = None
    ):
        if not api_key:
            raise AuthenticationError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": user_agent or f"Hashub-vector-sdk/1.0.0",
                "Accept": "application/json"
            }
        )
        
        self._async_client: Optional[httpx.AsyncClient] = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
    
    def close(self):
        """Close the synchronous client."""
        if self._client:
            self._client.close()
    
    async def aclose(self):
        """Close the asynchronous client."""
        if self._async_client:
            await self._async_client.aclose()
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self._client.headers
            )
        return self._async_client
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise HashubVectorError(f"Invalid JSON response: {response.text}")
        
        if response.status_code == 200:
            return data
        elif response.status_code == 401:
            raise AuthenticationError(data.get("error", "Invalid API key"))
        elif response.status_code == 402:
            raise QuotaExceededError(data.get("error", "Quota exceeded"))
        elif response.status_code == 404:
            raise ModelNotFoundError(data.get("model", "unknown"))
        elif response.status_code == 400:
            raise ValidationError(data.get("error", "Invalid request"))
        elif response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise RateLimitError(
                data.get("error", "Rate limit exceeded"),
                retry_after=int(retry_after) if retry_after else None
            )
        elif response.status_code >= 500:
            raise ServerError(data.get("error", "Internal server error"))
        else:
            raise HashubVectorError(
                f"HTTP {response.status_code}: {data.get('error', 'Unknown error')}",
                status_code=response.status_code,
                response_data=data
            )
    
    def _retry_request(self, func, *args, **kwargs):
        """Execute request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (RateLimitError, ServerError, NetworkError, TimeoutError) as e:
                last_exception = e
                if attempt == self.max_retries:
                    break
                
                delay = self.retry_delay * (2 ** attempt)
                if isinstance(e, RateLimitError) and e.retry_after:
                    delay = max(delay, e.retry_after)
                
                time.sleep(delay)
            except Exception as e:
                # Don't retry on auth errors, validation errors, etc.
                raise e
        
        raise last_exception
    
    async def _async_retry_request(self, func, *args, **kwargs):
        """Execute async request with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except (RateLimitError, ServerError, NetworkError, TimeoutError) as e:
                last_exception = e
                if attempt == self.max_retries:
                    break
                
                delay = self.retry_delay * (2 ** attempt)
                if isinstance(e, RateLimitError) and e.retry_after:
                    delay = max(delay, e.retry_after)
                
                await asyncio.sleep(delay)
            except Exception as e:
                # Don't retry on auth errors, validation errors, etc.
                raise e
        
        raise last_exception
    
    def vectorize(
        self,
        text: str,
        model: str = "e5_base",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[float] = None,
        normalize: bool = True
    ) -> VectorizeResponse:
        """
        Vectorize a single text into embeddings.
        
        Args:
            text: Text to vectorize
            model: Model to use (default: "e5_base")
            chunk_size: Optional chunk size for long texts
            chunk_overlap: Optional overlap ratio between chunks (0-1)
            normalize: Whether to normalize vectors (default: True)
            
        Returns:
            VectorizeResponse with embedding vector and metadata
            
        Raises:
            ValidationError: Invalid parameters
            ModelNotFoundError: Model not available
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            QuotaExceededError: Account quota exceeded
            
        Example:
            >>> response = client.vectorize("Merhaba dünya!", model="gte_base")
            >>> print(f"Vector dimension: {response.dimension}")
            >>> print(f"Token count: {response.token_count}")
        """
        request = VectorizeRequest(
            text=text,
            model=model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            normalize=normalize
        )
        
        def _make_request():
            try:
                response = self._client.post(
                    f"{self.base_url}/vectorize",
                    json={
                        "text": request.text,
                        "model": request.model,
                        "chunk_size": request.chunk_size,
                        "chunk_overlap": request.chunk_overlap,
                        "normalize": request.normalize
                    }
                )
                return self._handle_response(response)
            except httpx.TimeoutException:
                raise TimeoutError()
            except httpx.NetworkError as e:
                raise NetworkError(f"Network error: {e}")
        
        data = self._retry_request(_make_request)
        
        return VectorizeResponse(
            vector=data["vector"],
            model=data["model_used"],
            dimension=data["dimension"],
            token_count=data.get("usage", {}).get("total_tokens", 0),
            chunk_count=data.get("chunks_processed", 1),
            processing_time_ms=data.get("processing_time_ms")
        )
    
    async def avectorize(
        self,
        text: str,
        model: str = "e5_base",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[float] = None,
        normalize: bool = True
    ) -> VectorizeResponse:
        """
        Asynchronously vectorize a single text into embeddings.
        
        Args:
            text: Text to vectorize
            model: Model to use (default: "e5_base")
            chunk_size: Optional chunk size for long texts
            chunk_overlap: Optional overlap ratio between chunks (0-1)
            normalize: Whether to normalize vectors (default: True)
            
        Returns:
            VectorizeResponse with embedding vector and metadata
            
        Example:
            >>> response = await client.avectorize("Merhaba dünya!")
            >>> print(f"Vector dimension: {response.dimension}")
        """
        request = VectorizeRequest(
            text=text,
            model=model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            normalize=normalize
        )
        
        async def _make_request():
            try:
                response = await self.async_client.post(
                    f"{self.base_url}/vectorize",
                    json={
                        "text": request.text,
                        "model": request.model,
                        "chunk_size": request.chunk_size,
                        "chunk_overlap": request.chunk_overlap,
                        "normalize": request.normalize
                    }
                )
                return self._handle_response(response)
            except httpx.TimeoutException:
                raise TimeoutError()
            except httpx.NetworkError as e:
                raise NetworkError(f"Network error: {e}")
        
        data = await self._async_retry_request(_make_request)
        
        return VectorizeResponse(
            vector=data["vector"],
            model=data["model_used"],
            dimension=data["dimension"],
            token_count=data.get("usage", {}).get("total_tokens", 0),
            chunk_count=data.get("chunks_processed", 1),
            processing_time_ms=data.get("processing_time_ms")
        )
    
    def vectorize_batch(
        self,
        texts: List[str],
        model: str = "e5_base",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[float] = None,
        normalize: bool = True
    ) -> BatchVectorizeResponse:
        """
        Vectorize multiple texts in a single batch request.
        
        Args:
            texts: List of texts to vectorize (max 1000)
            model: Model to use (default: "e5_base")
            chunk_size: Optional chunk size for long texts
            chunk_overlap: Optional overlap ratio between chunks (0-1)
            normalize: Whether to normalize vectors (default: True)
            
        Returns:
            BatchVectorizeResponse with multiple vectors and metadata
            
        Example:
            >>> texts = ["Hello world", "Merhaba dünya", "Bonjour monde"]
            >>> response = client.vectorize_batch(texts)
            >>> print(f"Processed {response.count} texts")
            >>> print(f"Total tokens: {response.total_tokens}")
        """
        request = BatchVectorizeRequest(
            texts=texts,
            model=model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            normalize=normalize
        )
        
        def _make_request():
            try:
                response = self._client.post(
                    f"{self.base_url}/vectorize/batch",
                    json={
                        "texts": request.texts,
                        "model": request.model,
                        "chunk_size": request.chunk_size,
                        "chunk_overlap": request.chunk_overlap,
                        "normalize": request.normalize
                    }
                )
                return self._handle_response(response)
            except httpx.TimeoutException:
                raise TimeoutError()
            except httpx.NetworkError as e:
                raise NetworkError(f"Network error: {e}")
        
        data = self._retry_request(_make_request)
        
        return BatchVectorizeResponse(
            vectors=data["vectors"],
            model=data["model_used"],
            dimension=data["dimension"],
            token_counts=data.get("token_counts", []),
            chunk_counts=data.get("chunk_counts", [1] * len(texts)),
            total_tokens=data.get("usage", {}).get("total_tokens", 0),
            processing_time_ms=data.get("processing_time_ms")
        )
    
    async def avectorize_batch(
        self,
        texts: List[str],
        model: str = "e5_base",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[float] = None,
        normalize: bool = True
    ) -> BatchVectorizeResponse:
        """
        Asynchronously vectorize multiple texts in a single batch request.
        
        Args:
            texts: List of texts to vectorize (max 1000)
            model: Model to use (default: "e5_base")
            chunk_size: Optional chunk size for long texts
            chunk_overlap: Optional overlap ratio between chunks (0-1)
            normalize: Whether to normalize vectors (default: True)
            
        Returns:
            BatchVectorizeResponse with multiple vectors and metadata
            
        Example:
            >>> texts = ["Hello world", "Merhaba dünya", "Bonjour monde"]
            >>> response = await client.avectorize_batch(texts)
            >>> print(f"Processed {response.count} texts")
        """
        request = BatchVectorizeRequest(
            texts=texts,
            model=model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            normalize=normalize
        )
        
        async def _make_request():
            try:
                response = await self.async_client.post(
                    f"{self.base_url}/vectorize/batch",
                    json={
                        "texts": request.texts,
                        "model": request.model,
                        "chunk_size": request.chunk_size,
                        "chunk_overlap": request.chunk_overlap,
                        "normalize": request.normalize
                    }
                )
                return self._handle_response(response)
            except httpx.TimeoutException:
                raise TimeoutError()
            except httpx.NetworkError as e:
                raise NetworkError(f"Network error: {e}")
        
        data = await self._async_retry_request(_make_request)
        
        return BatchVectorizeResponse(
            vectors=data["vectors"],
            model=data["model_used"],
            dimension=data["dimension"],
            token_counts=data.get("token_counts", []),
            chunk_counts=data.get("chunk_counts", [1] * len(texts)),
            total_tokens=data.get("usage", {}).get("total_tokens", 0),
            processing_time_ms=data.get("processing_time_ms")
        )
    
    def get_models(self) -> List[ModelInfo]:
        """
        Get list of available models with their specifications.
        
        Returns:
            List of ModelInfo objects with model details
            
        Example:
            >>> models = client.get_models()
            >>> for model in models:
            ...     print(f"{model.alias}: {model.description}")
        """
        try:
            response = self._client.get(f"{self.base_url}/models")
            data = self._handle_response(response)
            
            models = []
            for model_data in data.get("models", []):
                models.append(ModelInfo(
                    alias=model_data["alias"],
                    full_name=model_data["full_name"],
                    dimension=model_data["dimension"],
                    max_tokens=model_data["max_tokens"],
                    price_per_1m_tokens=model_data["price_per_1m_tokens"],
                    tier=model_data["tier"],
                    description=model_data.get("description", ""),
                    languages=model_data.get("languages", [])
                ))
            
            return models
        except httpx.TimeoutException:
            raise TimeoutError()
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")
    
    async def aget_models(self) -> List[ModelInfo]:
        """
        Asynchronously get list of available models.
        
        Returns:
            List of ModelInfo objects with model details
        """
        try:
            response = await self.async_client.get(f"{self.base_url}/models")
            data = self._handle_response(response)
            
            models = []
            for model_data in data.get("models", []):
                models.append(ModelInfo(
                    alias=model_data["alias"],
                    full_name=model_data["full_name"],
                    dimension=model_data["dimension"],
                    max_tokens=model_data["max_tokens"],
                    price_per_1m_tokens=model_data["price_per_1m_tokens"],
                    tier=model_data["tier"],
                    description=model_data.get("description", ""),
                    languages=model_data.get("languages", [])
                ))
            
            return models
        except httpx.TimeoutException:
            raise TimeoutError()
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")
    
    def get_usage(self, period: str = "last_30_days", include_daily_breakdown: bool = True) -> UsageResponse:
        """
        Get detailed API usage statistics with date range support.
        
        Args:
            period: Time period - 'today', 'yesterday', 'last_7_days', 'last_30_days', 'this_month', 'last_month'
            include_daily_breakdown: Include daily breakdown in response
            
        Returns:
            UsageResponse with detailed usage statistics
            
        Example:
            >>> usage = client.get_usage(period="last_7_days")
            >>> print(f"Total requests: {usage.summary.total_requests}")
            >>> print(f"Total cost: ${usage.summary.total_cost}")
            >>> for day in usage.daily_breakdown:
            ...     print(f"{day.date}: {day.requests} requests")
        """
        try:
            params = {
                "period": period,
                "include_daily_breakdown": include_daily_breakdown
            }
            response = self._client.get(f"{self.base_url}/usage", params=params)
            data = self._handle_response(response)
            
            # Parse response data
            summary_data = data["summary"]
            summary = UsageStats(
                user_id=summary_data["user_id"],
                user_email=summary_data["user_email"],
                total_requests=summary_data["total_requests"],
                total_tokens=summary_data["total_tokens"],
                total_cost=summary_data["total_cost"],
                current_balance=summary_data["current_balance"],
                period_start=summary_data["period_start"],
                period_end=summary_data["period_end"]
            )
            
            # Parse daily breakdown
            daily_breakdown = []
            for day_data in data.get("daily_breakdown", []):
                daily_breakdown.append(DailyUsage(
                    date=day_data["date"],
                    requests=day_data["requests"],
                    tokens=day_data["tokens"],
                    cost=day_data["cost"],
                    models_used=day_data["models_used"]
                ))
            
            # Parse top models
            top_models = []
            for model_data in data.get("top_models", []):
                top_models.append(TopModel(
                    model=model_data["model"],
                    requests=model_data["requests"],
                    tokens=model_data["tokens"],
                    cost=model_data["cost"],
                    percentage=model_data["percentage"]
                ))
            
            return UsageResponse(
                summary=summary,
                daily_breakdown=daily_breakdown,
                top_models=top_models
            )
            
        except httpx.TimeoutException:
            raise TimeoutError()
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")
    
    def get_usage_simple(self) -> Usage:
        """
        Get simple usage statistics (legacy method for backward compatibility).
        
        Returns:
            Usage object with basic token and request counts
        """
        try:
            detailed_usage = self.get_usage(period="last_30_days", include_daily_breakdown=False)
            summary = detailed_usage.summary
            
            return Usage(
                tokens_used=summary.total_tokens,
                tokens_remaining=None,  # Not provided by new API
                requests_used=summary.total_requests,
                requests_remaining=None  # Not provided by new API
            )
        except Exception as e:
            raise e
    
    async def aget_usage(self, period: str = "last_30_days", include_daily_breakdown: bool = True) -> UsageResponse:
        """
        Asynchronously get detailed API usage statistics.
        
        Args:
            period: Time period - 'today', 'yesterday', 'last_7_days', 'last_30_days', 'this_month', 'last_month'
            include_daily_breakdown: Include daily breakdown in response
            
        Returns:
            UsageResponse with detailed usage statistics
        """
        try:
            params = {
                "period": period,
                "include_daily_breakdown": include_daily_breakdown
            }
            response = await self.async_client.get(f"{self.base_url}/usage", params=params)
            data = self._handle_response(response)
            
            # Parse response data (same logic as sync version)
            summary_data = data["summary"]
            summary = UsageStats(
                user_id=summary_data["user_id"],
                user_email=summary_data["user_email"],
                total_requests=summary_data["total_requests"],
                total_tokens=summary_data["total_tokens"],
                total_cost=summary_data["total_cost"],
                current_balance=summary_data["current_balance"],
                period_start=summary_data["period_start"],
                period_end=summary_data["period_end"]
            )
            
            daily_breakdown = []
            for day_data in data.get("daily_breakdown", []):
                daily_breakdown.append(DailyUsage(
                    date=day_data["date"],
                    requests=day_data["requests"],
                    tokens=day_data["tokens"],
                    cost=day_data["cost"],
                    models_used=day_data["models_used"]
                ))
            
            top_models = []
            for model_data in data.get("top_models", []):
                top_models.append(TopModel(
                    model=model_data["model"],
                    requests=model_data["requests"],
                    tokens=model_data["tokens"],
                    cost=model_data["cost"],
                    percentage=model_data["percentage"]
                ))
            
            return UsageResponse(
                summary=summary,
                daily_breakdown=daily_breakdown,
                top_models=top_models
            )
        except httpx.TimeoutException:
            raise TimeoutError()
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")
    
    # OpenAI-compatible interface
    def create_embedding(
        self,
        input: Union[str, List[str]],
        model: str = "e5_base",
        encoding_format: str = "float",
        dimensions: Optional[int] = None,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        OpenAI-compatible embedding creation interface.
        
        Args:
            input: Text(s) to embed (string or list of strings)
            model: Model to use
            encoding_format: Format for embeddings (only "float" supported)
            dimensions: Not used (model dimension is fixed)
            user: Optional user identifier
            
        Returns:
            OpenAI-compatible response format
            
        Example:
            >>> response = client.create_embedding("Hello world")
            >>> embedding = response["data"][0]["embedding"]
        """
        if encoding_format != "float":
            raise ValidationError("Only 'float' encoding format is supported")
        
        # Handle single string vs list of strings
        if isinstance(input, str):
            response = self.vectorize(input, model=model)
            return {
                "object": "list",
                "data": [{
                    "object": "embedding",
                    "embedding": response.vector,
                    "index": 0
                }],
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.token_count,
                    "total_tokens": response.token_count
                }
            }
        else:
            response = self.vectorize_batch(input, model=model)
            return {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": vector,
                        "index": i
                    }
                    for i, vector in enumerate(response.vectors)
                ],
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.total_tokens,
                    "total_tokens": response.total_tokens
                }
            }
    
    # Convenience methods
    def similarity(self, text1: str, text2: str, model: str = "e5_base") -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            model: Model to use for embeddings
            
        Returns:
            Cosine similarity score (-1 to 1)
            
        Example:
            >>> similarity = client.similarity("Hello", "Hi")
            >>> print(f"Similarity: {similarity:.3f}")
        """
        batch_response = self.vectorize_batch([text1, text2], model=model)
        vec1, vec2 = batch_response.vectors[0], batch_response.vectors[1]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        return dot_product / (norm1 * norm2) if norm1 * norm2 > 0 else 0.0
