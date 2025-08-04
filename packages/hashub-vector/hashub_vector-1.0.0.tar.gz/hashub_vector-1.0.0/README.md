# Hashub Vector SDK

[![PyPI version](https://badge.fury.io/py/hashub-vector.svg)](https://badge.fury.io/py/hashub-vector)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/hashub-vector)](https://pepy.tech/project/hashub-vector)

**High-quality multilingual text embeddings with Turkish excellence** 🇹🇷

The official Python SDK for Hashub Vector API - providing state-of-the-art text embeddings with exceptional Turkish language support and 80+ other languages.

## 🚀 Features

- **6 Premium Models** - From ultra-fast to premium quality
- **Turkish Excellence** - Optimized for Turkish market with exceptional Turkish language performance
- **80+ Languages** - Comprehensive multilingual support
- **Async/Sync Support** - Both synchronous and asynchronous operations
- **OpenAI Compatible** - Drop-in replacement for OpenAI embeddings
- **Smart Retry Logic** - Automatic retries with exponential backoff
- **Type Safety** - Full type hints and validation
- **Production Ready** - Built for scale with rate limiting and error handling

## 📦 Installation

```bash
pip install hashub-vector
```

For development with all extras:
```bash
pip install hashub-vector[dev,examples]
```

## 🏃‍♂️ Quick Start

```python
from hashub_vector import HashubVector

# Initialize client
client = HashubVector(api_key="your-api-key")

# Single text embedding
response = client.vectorize("Merhaba dünya! Hashub ile güçlü vektör embedding'ler.")
print(f"Vector dimension: {response.dimension}")
print(f"First 5 dimensions: {response.vector[:5]}")

# Batch processing
texts = [
    "Artificial intelligence is transforming the world",
    "Yapay zeka dünyayı dönüştürüyor",
    "L'intelligence artificielle transforme le monde"
]

batch_response = client.vectorize_batch(texts, model="gte_base")
print(f"Processed {batch_response.count} texts")
print(f"Total tokens: {batch_response.total_tokens}")

# Calculate similarity
similarity = client.similarity(
    "Machine learning", 
    "Makine öğrenmesi"
)
print(f"Similarity: {similarity:.3f}")
```

## 🤖 Async Support

```python
import asyncio
from hashub_vector import HashubVector

async def main():
    async with HashubVector(api_key="your-api-key") as client:
        # Async single embedding
        response = await client.avectorize("Async ile hızlı embedding!")
        
        # Async batch processing
        texts = ["Hello", "Merhaba", "Bonjour"]
        batch_response = await client.avectorize_batch(texts)
        
        print(f"Processed {batch_response.count} texts asynchronously")

asyncio.run(main())
```

## 🎯 Model Selection Guide

| Model | Best For | Dimension | Max Tokens | Price/1M | Turkish Support |
|-------|----------|-----------|------------|----------|-----------------|
| `gte_base` | Long documents, RAG | 768 | 8,192 | $0.01 | ⭐⭐⭐⭐⭐ |
| `nomic_base` | General purpose | 768 | 2,048 | $0.005 | ⭐⭐⭐⭐ |
| `e5_base` | Search, retrieval | 768 | 512 | $0.003 | ⭐⭐⭐⭐⭐ |
| `mpnet_base` | Q&A, similarity | 768 | 512 | $0.0035 | ⭐⭐⭐⭐⭐ |
| `e5_small` | High volume, speed | 384 | 512 | $0.002 | ⭐⭐⭐⭐ |
| `minilm_base` | Ultra-fast | 384 | 512 | $0.0025 | ⭐⭐⭐⭐ |

### Turkish Market Optimization

All models provide excellent Turkish language support, with `gte_base`, `e5_base`, and `mpnet_base` offering the highest quality for Turkish text processing.

```python
# Optimized for Turkish content
response = client.vectorize(
    "Hashub Vector API ile Türkçe metinlerinizi güçlü vektörlere dönüştürün!",
    model="gte_base"  # Best for Turkish
)
```

## 🔄 OpenAI Compatibility

Drop-in replacement for OpenAI's embedding API:

```python
# OpenAI style (compatible)
response = client.create_embedding(
    input="Your text here",
    model="e5_base"
)
embedding = response["data"][0]["embedding"]

# Multiple texts
response = client.create_embedding(
    input=["Text 1", "Text 2", "Text 3"],
    model="gte_base"
)
```

## 🧠 Advanced Features

### Chunking for Long Documents

```python
# Automatic chunking for long texts
response = client.vectorize(
    long_document,
    model="gte_base",
    chunk_size=1024,
    chunk_overlap=0.1  # 10% overlap
)
print(f"Document split into {response.chunk_count} chunks")
```

### Model Information

```python
# Get available models
models = client.get_models()
for model in models:
    print(f"{model.alias}: {model.description}")
    print(f"  Dimension: {model.dimension}")
    print(f"  Max tokens: {model.max_tokens}")
    print(f"  Price: ${model.price_per_1m_tokens}/1M tokens")
```

### Usage Monitoring

```python
# Check your usage
usage = client.get_usage()
print(f"Tokens used: {usage.tokens_used:,}")
print(f"Usage percentage: {usage.tokens_percentage_used:.1f}%")
```

## 🛠️ Integration Examples

### With LangChain

```python
from hashub_vector import HashubVector
from langchain.embeddings.base import Embeddings

class HashubEmbeddings(Embeddings):
    def __init__(self, api_key: str, model: str = "e5_base"):
        self.client = HashubVector(api_key=api_key)
        self.model = model
    
    def embed_documents(self, texts):
        response = self.client.vectorize_batch(texts, model=self.model)
        return response.vectors
    
    def embed_query(self, text):
        response = self.client.vectorize(text, model=self.model)
        return response.vector

# Usage
embeddings = HashubEmbeddings(api_key="your-key", model="gte_base")
```

### With Pinecone

```python
import pinecone
from hashub_vector import HashubVector

# Initialize clients
client = HashubVector(api_key="your-Hashub-key")
pinecone.init(api_key="your-pinecone-key", environment="your-env")

# Create embeddings and store
texts = ["Your documents here..."]
response = client.vectorize_batch(texts, model="gte_base")

# Upsert to Pinecone
index = pinecone.Index("your-index")
vectors = [
    (f"doc_{i}", embedding, {"text": text})
    for i, (embedding, text) in enumerate(zip(response.vectors, texts))
]
index.upsert(vectors)
```

## 🔧 Error Handling

```python
from hashub_vector import (
    HashubVector,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError
)

client = HashubVector(api_key="your-key")

try:
    response = client.vectorize("Your text")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except QuotaExceededError:
    print("Quota exceeded. Please upgrade your plan")
```

## 🌍 Language Support

Hashub Vector SDK supports 80+ languages with excellent Turkish performance:

### Tier 1 (Excellent Performance)
🇹🇷 **Turkish**, English, German, French, Spanish, Italian, Portuguese, Dutch, Russian, Polish, Czech, Swedish, Danish, Norwegian, Finnish, Ukrainian

### Tier 2 (Very Good Performance)  
Arabic, Persian, Chinese, Japanese, Korean, Hindi, Bengali, Indonesian, Malay, Thai, Vietnamese, Bulgarian, Romanian, Hungarian, Croatian

### Tier 3 (Good Performance)
And 50+ additional languages including African, South Asian, and other European languages.

## 📊 Performance & Pricing

### Speed Benchmarks (texts/second)
- `minilm_base`: ~950 texts/second (Ultra-fast)
- `e5_small`: ~780 texts/second (Fast)
- `e5_base`: ~520 texts/second (Balanced)
- `mpnet_base`: ~465 texts/second (Quality)
- `nomic_base`: ~350 texts/second (Premium)
- `gte_base`: ~280 texts/second (Maximum quality)

### Cost Examples
- **1M tokens with `e5_small`**: $2.00 (Most economical)
- **1M tokens with `e5_base`**: $3.00 (Best value)
- **1M tokens with `gte_base`**: $10.00 (Premium quality)

## 🔐 Authentication

Get your API key from [Hashub Console](https://console.Hashub.dev):

1. Sign up at Hashub Console
2. Create a new API key
3. Choose your pricing tier
4. Start building!

```python
# Environment variable (recommended)
import os
client = HashubVector(api_key=os.getenv("Hashub_API_KEY"))

# Direct initialization
client = HashubVector(api_key="hv-1234567890abcdef...")
```

## 🚦 Rate Limits

| Tier | Requests/Minute | Tokens/Month | Batch Size |
|------|----------------|--------------|------------|
| **Free** | 60 | 100K | 100 texts |
| **Starter** | 300 | 1M | 500 texts |
| **Pro** | 1,000 | 10M | 1,000 texts |
| **Enterprise** | Custom | Custom | Custom |

The SDK automatically handles rate limiting with intelligent retry logic.

## 🧪 Testing

```bash
# Install dev dependencies
pip install hashub-vector[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=hashub_vector

# Run specific test
pytest tests/test_client.py::test_vectorize
```

## 📚 Documentation

- **[Official Documentation](https://docs.vector.Hashub.dev)** - Complete API reference
- **[Model Comparison](https://vector.Hashub.dev/models)** - Detailed model specifications
- **[Pricing](https://vector.Hashub.dev/pricing)** - Transparent pricing information
- **[Examples](./examples/)** - Integration examples and tutorials

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Development setup
git clone https://github.com/hasanbahadir/hashub-vector-sdk.git
cd hashub-vector-sdk
pip install -e ".[dev]"
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.vector.hashub.dev](https://docs.vector.hashub.dev)
- **Email**: [support@hashub.dev](mailto:support@hashub.dev)
- **Issues**: [GitHub Issues](https://github.com/hasanbahadir/hashub-vector-sdk/issues)
- **Discord**: [Hashub Community](https://discord.gg/hashub)

## 🚀 What's Next?

Check out our roadmap for upcoming features:
- [ ] Vector database integrations (Weaviate, Qdrant, Chroma)
- [ ] Embedding visualization tools
- [ ] Fine-tuning capabilities
- [ ] On-premise deployment options
- [ ] More language-specific optimizations

---

**Made with ❤️ in Turkey** 🇹🇷

**Hashub Vector SDK** - Powering the next generation of AI applications with Turkish excellence.
