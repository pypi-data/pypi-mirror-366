# Hashub Vector SDK Examples

This directory contains comprehensive examples demonstrating how to use the Hashub Vector SDK in various scenarios.

## 📁 Examples Overview

### 1. **basic_usage.py** - Getting Started
Complete introduction to the SDK with essential operations:
- ✅ Single text embedding
- ✅ Batch processing
- ✅ Turkish language optimization
- ✅ Model comparison
- ✅ Similarity calculation
- ✅ Async operations
- ✅ Error handling
- ✅ Usage monitoring

**Run:**
```bash
python examples/basic_usage.py
```

### 2. **langchain_integration.py** - LangChain RAG
Integration with LangChain for RAG applications:
- ✅ Custom Hashub embeddings class
- ✅ Turkish knowledge base creation
- ✅ Semantic search examples
- ✅ Cross-lingual search capabilities
- ✅ Complete RAG pipeline

**Dependencies:**
```bash
pip install langchain faiss-cpu
```

**Run:**
```bash
python examples/langchain_integration.py
```

### 3. **production_rag.py** - Production-Ready RAG
Enterprise-grade RAG system implementation:
- ✅ Production vector store
- ✅ Performance monitoring
- ✅ Batch processing optimization
- ✅ Async operations
- ✅ Caching mechanisms
- ✅ Error recovery
- ✅ Save/load functionality

**Dependencies:**
```bash
pip install numpy scikit-learn
```

**Run:**
```bash
python examples/production_rag.py
```

## 🚀 Quick Start

1. **Set your API key:**
```bash
export HASHUB_API_KEY="your-api-key-here"
```

2. **Install dependencies:**
```bash
# Basic dependencies (included with SDK)
pip install hashub-vector

# For LangChain examples
pip install langchain faiss-cpu

# For production examples
pip install numpy scikit-learn
```

3. **Run an example:**
```bash
python examples/basic_usage.py
```

## 📊 Performance Comparison

| Example | Use Case | Performance | Complexity | Best For |
|---------|----------|-------------|------------|----------|
| **basic_usage** | Learning & Testing | Fast | Simple | Getting started |
| **langchain_integration** | RAG Applications | Medium | Medium | LangChain users |
| **production_rag** | Enterprise Systems | Optimized | Advanced | Production use |

## 🇹🇷 Turkish Language Examples

All examples include Turkish language optimization and demonstrate:
- Best model selection for Turkish text
- Turkish-English cross-lingual search
- Turkish knowledge base creation
- Multilingual similarity comparison

## 📝 Example Code Snippets

### Quick Embedding
```python
from hashhub_vector import HashubVector

client = HashubVector(api_key="your-key")
response = client.vectorize("Merhaba dünya!", model="gte_base")
print(response.vector[:5])  # First 5 dimensions
```

### Batch Processing
```python
texts = ["Hello world", "Merhaba dünya", "Bonjour monde"]
response = client.vectorize_batch(texts, model="e5_base")
print(f"Processed {response.count} texts")
```

### Async Operations
```python
import asyncio

async def main():
    async with HashubVector(api_key="your-key") as client:
        response = await client.avectorize("Async example")
        print(f"Embedding: {len(response.vector)} dimensions")

asyncio.run(main())
```

### Similarity Search
```python
similarity = client.similarity(
    "Machine learning", 
    "Makine öğrenmesi"  # Turkish translation
)
print(f"Similarity: {similarity:.3f}")
```

## 🔧 Customization

Each example can be customized by modifying:
- **Model selection**: Choose from 6 available models
- **Batch sizes**: Optimize for your use case
- **Similarity thresholds**: Adjust search relevance
- **Chunking parameters**: Handle long documents
- **Error handling**: Add custom retry logic

## 📚 Additional Resources

- **[API Documentation](https://github.com/hasanbahadir/hashub-vector-sdk#api-documentation)** - Complete API reference
- **[Model Comparison](https://github.com/hasanbahadir/hashub-vector-sdk#models)** - Model specifications
- **[Turkish Optimization Guide](https://github.com/hasanbahadir/hashub-vector-sdk#turkish-optimization)** - Turkish-specific tips
- **[Production Deployment](https://github.com/hasanbahadir/hashub-vector-sdk#production-deployment)** - Scaling guidelines

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/hasanbahadir/hashub-vector-sdk/issues)
- **Email**: [support@hashub.dev](mailto:support@hashub.dev)
- **Documentation**: [GitHub Repository](https://github.com/hasanbahadir/hashub-vector-sdk)

Happy coding! 🚀
