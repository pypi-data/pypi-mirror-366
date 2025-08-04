"""
Test suite for HashHub Vector SDK

Run with: pytest
"""

import pytest
import httpx
from unittest.mock import Mock, patch, AsyncMock
from hashub_vector import (
    HasHubVector,
    VectorizeResponse,
    BatchVectorizeResponse,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    ValidationError
)


class TestHasHubVector:
    """Test cases for HashHub Vector client."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return HasHubVector(api_key="test-key")
    
    @pytest.fixture
    def mock_response(self):
        """Mock successful API response."""
        return {
            "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
            "model": "e5_base",
            "dimension": 768,
            "token_count": 10,
            "chunk_count": 1,
            "processing_time_ms": 50.0
        }
    
    @pytest.fixture
    def mock_batch_response(self):
        """Mock successful batch API response."""
        return {
            "vectors": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "model": "e5_base",
            "dimension": 768,
            "token_counts": [5, 7],
            "chunk_counts": [1, 1],
            "total_tokens": 12,
            "processing_time_ms": 80.0
        }
    
    def test_init_valid_api_key(self):
        """Test client initialization with valid API key."""
        client = HasHubVector(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://vector.hashhub.dev"
    
    def test_init_empty_api_key(self):
        """Test client initialization with empty API key."""
        with pytest.raises(AuthenticationError):
            HasHubVector(api_key="")
    
    def test_init_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = HasHubVector(
            api_key="test-key",
            base_url="https://custom.api.com/"
        )
        assert client.base_url == "https://custom.api.com"
    
    @patch('httpx.Client.post')
    def test_vectorize_success(self, mock_post, client, mock_response):
        """Test successful single text vectorization."""
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        response = client.vectorize("Test text")
        
        assert isinstance(response, VectorizeResponse)
        assert response.vector == [0.1, 0.2, 0.3, 0.4, 0.5]
        assert response.model == "e5_base"
        assert response.dimension == 768
        assert response.token_count == 10
        
        mock_post.assert_called_once()
    
    @patch('httpx.Client.post')
    def test_vectorize_batch_success(self, mock_post, client, mock_batch_response):
        """Test successful batch vectorization."""
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_batch_response)
        )
        
        texts = ["Text 1", "Text 2"]
        response = client.vectorize_batch(texts)
        
        assert isinstance(response, BatchVectorizeResponse)
        assert len(response.vectors) == 2
        assert response.total_tokens == 12
        assert response.count == 2
        
        mock_post.assert_called_once()
    
    @patch('httpx.Client.post')
    def test_authentication_error(self, mock_post, client):
        """Test authentication error handling."""
        mock_post.return_value = Mock(
            status_code=401,
            json=Mock(return_value={"error": "Invalid API key"})
        )
        
        with pytest.raises(AuthenticationError):
            client.vectorize("Test text")
    
    @patch('httpx.Client.post')
    def test_rate_limit_error(self, mock_post, client):
        """Test rate limit error handling."""
        mock_post.return_value = Mock(
            status_code=429,
            json=Mock(return_value={"error": "Rate limit exceeded"}),
            headers={"retry-after": "60"}
        )
        
        with pytest.raises(RateLimitError) as exc_info:
            client.vectorize("Test text")
        
        assert exc_info.value.retry_after == 60
    
    @patch('httpx.Client.post')
    def test_model_not_found_error(self, mock_post, client):
        """Test model not found error handling."""
        mock_post.return_value = Mock(
            status_code=404,
            json=Mock(return_value={"error": "Model not found", "model": "invalid_model"})
        )
        
        with pytest.raises(ModelNotFoundError):
            client.vectorize("Test text", model="invalid_model")
    
    def test_validation_error_empty_text(self, client):
        """Test validation error for empty text."""
        with pytest.raises(ValueError):
            client.vectorize("")
    
    def test_validation_error_empty_batch(self, client):
        """Test validation error for empty batch."""
        with pytest.raises(ValueError):
            client.vectorize_batch([])
    
    def test_validation_error_large_batch(self, client):
        """Test validation error for batch too large."""
        large_batch = ["text"] * 1001
        with pytest.raises(ValueError):
            client.vectorize_batch(large_batch)
    
    @patch('httpx.Client.post')
    def test_similarity(self, mock_post, client):
        """Test similarity calculation."""
        # Mock batch response with two vectors
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "vectors": [[1.0, 0.0], [0.0, 1.0]],  # Orthogonal vectors
                "model": "e5_base",
                "dimension": 2,
                "token_counts": [5, 5],
                "chunk_counts": [1, 1],
                "total_tokens": 10
            })
        )
        
        similarity = client.similarity("Hello", "World")
        assert similarity == 0.0  # Orthogonal vectors have 0 similarity
    
    def test_create_embedding_single_text(self, client):
        """Test OpenAI-compatible embedding creation for single text."""
        with patch.object(client, 'vectorize') as mock_vectorize:
            mock_vectorize.return_value = VectorizeResponse(
                vector=[0.1, 0.2, 0.3],
                model="e5_base",
                dimension=768,
                token_count=5
            )
            
            response = client.create_embedding("Hello world")
            
            assert response["object"] == "list"
            assert len(response["data"]) == 1
            assert response["data"][0]["embedding"] == [0.1, 0.2, 0.3]
            assert response["model"] == "e5_base"
            assert response["usage"]["prompt_tokens"] == 5
    
    def test_create_embedding_multiple_texts(self, client):
        """Test OpenAI-compatible embedding creation for multiple texts."""
        with patch.object(client, 'vectorize_batch') as mock_vectorize_batch:
            mock_vectorize_batch.return_value = BatchVectorizeResponse(
                vectors=[[0.1, 0.2], [0.3, 0.4]],
                model="e5_base",
                dimension=768,
                token_counts=[3, 4],
                chunk_counts=[1, 1],
                total_tokens=7
            )
            
            response = client.create_embedding(["Hello", "World"])
            
            assert response["object"] == "list"
            assert len(response["data"]) == 2
            assert response["data"][0]["embedding"] == [0.1, 0.2]
            assert response["data"][1]["embedding"] == [0.3, 0.4]
            assert response["usage"]["total_tokens"] == 7
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with HasHubVector(api_key="test-key") as client:
            assert isinstance(client, HasHubVector)
        # Should not raise any errors on exit


class TestAsyncHasHubVector:
    """Test cases for async HashHub Vector client operations."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return HasHubVector(api_key="test-key")
    
    @pytest.fixture
    def mock_response(self):
        """Mock successful API response."""
        return {
            "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
            "model": "e5_base",
            "dimension": 768,
            "token_count": 10,
            "chunk_count": 1,
            "processing_time_ms": 50.0
        }
    
    @pytest.mark.asyncio
    async def test_avectorize_success(self, client, mock_response):
        """Test successful async single text vectorization."""
        with patch.object(client, 'async_client') as mock_async_client:
            mock_async_client.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            ))
            
            response = await client.avectorize("Test text")
            
            assert isinstance(response, VectorizeResponse)
            assert response.vector == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert response.model == "e5_base"
    
    @pytest.mark.asyncio
    async def test_avectorize_batch_success(self, client):
        """Test successful async batch vectorization."""
        mock_batch_response = {
            "vectors": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "model": "e5_base",
            "dimension": 768,
            "token_counts": [5, 7],
            "chunk_counts": [1, 1],
            "total_tokens": 12,
            "processing_time_ms": 80.0
        }
        
        with patch.object(client, 'async_client') as mock_async_client:
            mock_async_client.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_batch_response)
            ))
            
            texts = ["Text 1", "Text 2"]
            response = await client.avectorize_batch(texts)
            
            assert isinstance(response, BatchVectorizeResponse)
            assert len(response.vectors) == 2
            assert response.total_tokens == 12
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager functionality."""
        async with HasHubVector(api_key="test-key") as client:
            assert isinstance(client, HasHubVector)
        # Should not raise any errors on exit


class TestModels:
    """Test cases for data models."""
    
    def test_vectorize_response_magnitude(self):
        """Test vector magnitude calculation."""
        response = VectorizeResponse(
            vector=[3.0, 4.0],  # 3-4-5 triangle
            model="e5_base",
            dimension=2,
            token_count=5
        )
        assert response.magnitude == 5.0
    
    def test_batch_vectorize_response_get_vector(self):
        """Test getting vector by index."""
        response = BatchVectorizeResponse(
            vectors=[[1, 2], [3, 4], [5, 6]],
            model="e5_base",
            dimension=2,
            token_counts=[1, 1, 1],
            chunk_counts=[1, 1, 1],
            total_tokens=3
        )
        
        assert response.get_vector(0) == [1, 2]
        assert response.get_vector(1) == [3, 4]
        assert response.get_vector(2) == [5, 6]
        
        with pytest.raises(IndexError):
            response.get_vector(3)
    
    def test_usage_percentage_calculation(self):
        """Test usage percentage calculation."""
        from hashub_vector.models import Usage
        
        usage = Usage(tokens_used=750, tokens_remaining=250)
        assert usage.tokens_percentage_used == 75.0
        
        usage_no_remaining = Usage(tokens_used=1000)
        assert usage_no_remaining.tokens_percentage_used is None


if __name__ == "__main__":
    pytest.main([__file__])
