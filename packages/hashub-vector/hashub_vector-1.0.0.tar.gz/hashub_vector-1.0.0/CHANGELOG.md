# Changelog

All notable changes to the Hashub Vector SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-04

### Added
- Initial release of Hashub Vector SDK
- Support for 6 embedding models (gte_base, nomic_base, e5_base, mpnet_base, e5_small, minilm_base)
- Synchronous and asynchronous client operations
- OpenAI-compatible embedding interface
- Comprehensive error handling with custom exceptions
- Automatic retry logic with exponential backoff
- Rate limiting support
- Turkish language optimization
- Support for 80+ languages
- Batch processing capabilities (up to 1000 texts)
- Text chunking for long documents
- Usage monitoring and model information endpoints
- Type hints and data validation
- Context manager support
- Similarity calculation utility
- Comprehensive documentation and examples

### Features
- **Multi-model support**: Choose from 6 different embedding models
- **Turkish excellence**: Optimized performance for Turkish language
- **Async/sync operations**: Both synchronous and asynchronous APIs
- **OpenAI compatibility**: Drop-in replacement for OpenAI embeddings
- **Smart retries**: Automatic retry with exponential backoff
- **Error handling**: Comprehensive exception handling
- **Type safety**: Full type hints and validation
- **Production ready**: Built for scale with proper error handling

### Supported Models
- `gte_base`: Premium model for long documents and RAG (768d, 8K tokens)
- `nomic_base`: Balanced performance with MoE architecture (768d, 2K tokens)
- `e5_base`: Excellent for search and retrieval (768d, 512 tokens)
- `mpnet_base`: Optimized for Q&A and similarity (768d, 512 tokens) 
- `e5_small`: Fast processing for high volume (384d, 512 tokens)
- `minilm_base`: Ultra-fast lightweight processing (384d, 512 tokens)

### Language Support
- **Tier 1**: Turkish, English, German, French, Spanish, Italian, Portuguese, and more
- **Tier 2**: Arabic, Persian, Chinese, Japanese, Korean, Hindi, Bengali, and more
- **Tier 3**: 50+ additional languages with good support

### API Endpoints
- `POST /vectorize` - Single text embedding
- `POST /vectorize/batch` - Batch text embedding
- `GET /models` - List available models
- `GET /usage` - Get usage statistics
