"""
Basic Usage Examples for Hashub Vector SDK

This example demonstrates the fundamental operations of the Hashub Vector SDK
including single text embedding, batch processing, model selection, and
Turkish language optimization.
"""

import os
import asyncio
from hashub_vector import HashubVector

# Initialize client with API key
API_KEY = os.getenv("HASHUB_API_KEY", "your-api-key-here")
client = HashubVector(api_key=API_KEY)

"""
This example demonstrates the fundamental operations of the Hashub Vector SDK
including single text embedding, batch processing, model selection, and
Turkish language optimization.
"""

import os
import asyncio
from hashub_vector import HashubVector

# Initialize client with API key
API_KEY = os.getenv("HASHUB_API_KEY", "your-api-key-here")
client = HashubVector(api_key=API_KEY)


def basic_embedding():
    """Basic single text embedding example."""
    print("🔹 Basic Embedding Example")
    print("-" * 50)
    
    # Simple text embedding
    text = "HashHub Vector API provides high-quality multilingual embeddings!"
    response = client.vectorize(text, model="e5_base")
    
    print(f"Text: {text}")
    print(f"Model: {response.model}")
    print(f"Dimension: {response.dimension}")
    print(f"Token count: {response.token_count}")
    print(f"First 5 dimensions: {response.vector[:5]}")
    print(f"Vector magnitude: {response.magnitude:.4f}")
    print()


def turkish_optimization():
    """Example optimized for Turkish language."""
    print("🇹🇷 Turkish Language Optimization")
    print("-" * 50)
    
    # Turkish text with the best model for Turkish
    turkish_text = "HashHub Vector API ile Türkçe metinlerinizi güçlü vektörlere dönüştürün!"
    response = client.vectorize(turkish_text, model="gte_base")  # Best for Turkish
    
    print(f"Türkçe metin: {turkish_text}")
    print(f"Model: {response.model} (Turkish için optimize)")
    print(f"Boyut: {response.dimension}")
    print(f"Token sayısı: {response.token_count}")
    print(f"İlk 5 boyut: {response.vector[:5]}")
    print()


def batch_processing():
    """Batch processing example with multiple languages."""
    print("📦 Batch Processing Example")
    print("-" * 50)
    
    # Multiple texts in different languages
    texts = [
        "Artificial intelligence is transforming the world",
        "Yapay zeka dünyayı dönüştürüyor",
        "L'intelligence artificielle transforme le monde",
        "人工智能正在改变世界",
        "الذكاء الاصطناعي يغير العالم"
    ]
    
    # Process all texts in a single batch
    response = client.vectorize_batch(texts, model="gte_base")
    
    print(f"Processed {response.count} texts in one batch")
    print(f"Total tokens: {response.total_tokens}")
    print(f"Average tokens per text: {response.total_tokens / response.count:.1f}")
    print(f"Processing time: {response.processing_time_ms:.1f}ms")
    
    # Show embeddings for each text
    for i, (text, vector) in enumerate(zip(texts, response.vectors)):
        print(f"\nText {i+1}: {text[:50]}...")
        print(f"Vector preview: {vector[:3]}...")
        print(f"Tokens: {response.token_counts[i]}")
    print()


def model_comparison():
    """Compare different models on the same text."""
    print("⚖️ Model Comparison Example")
    print("-" * 50)
    
    text = "Machine learning enables computers to learn and improve from experience."
    models = ["e5_small", "e5_base", "mpnet_base", "gte_base"]
    
    print(f"Text: {text}")
    print(f"{'Model':<15} {'Dimension':<10} {'Tokens':<8} {'Time (ms)':<10}")
    print("-" * 50)
    
    for model in models:
        response = client.vectorize(text, model=model)
        print(f"{model:<15} {response.dimension:<10} {response.token_count:<8} {response.processing_time_ms or 0:<10.1f}")
    print()


def similarity_calculation():
    """Calculate semantic similarity between texts."""
    print("🔍 Similarity Calculation Example")
    print("-" * 50)
    
    # Compare similar concepts
    text_pairs = [
        ("Machine learning", "Artificial intelligence"),
        ("Machine learning", "Makine öğrenmesi"),  # Turkish translation
        ("Cat", "Dog"),
        ("Car", "Bicycle"),
        ("Happy", "Sad")
    ]
    
    print(f"{'Text 1':<20} {'Text 2':<20} {'Similarity':<12}")
    print("-" * 55)
    
    for text1, text2 in text_pairs:
        similarity = client.similarity(text1, text2, model="e5_base")
        print(f"{text1:<20} {text2:<20} {similarity:<12.3f}")
    print()


def chunking_example():
    """Example with automatic text chunking for long documents."""
    print("📄 Document Chunking Example")
    print("-" * 50)
    
    # Simulate a long document
    long_document = """
    HashHub Vector API is a powerful service that provides high-quality text embeddings 
    with exceptional multilingual support. The API supports 6 different embedding models, 
    each optimized for different use cases and performance requirements. 
    
    The service excels in Turkish language processing, making it perfect for Turkish 
    market applications. With support for over 80 languages, it enables global 
    applications while maintaining excellent performance for local markets.
    
    The API is designed for production use with features like automatic retry logic, 
    rate limiting, comprehensive error handling, and both synchronous and asynchronous 
    operations. It provides a drop-in replacement for OpenAI's embedding API while 
    offering better multilingual performance and competitive pricing.
    """ * 3  # Make it longer
    
    print(f"Document length: {len(long_document)} characters")
    
    # Process with chunking
    response = client.vectorize(
        long_document,
        model="gte_base",  # Best for long documents
        chunk_size=512,    # Split into 512-token chunks
        chunk_overlap=0.1  # 10% overlap between chunks
    )
    
    print(f"Chunks created: {response.chunk_count}")
    print(f"Total tokens: {response.token_count}")
    print(f"Average tokens per chunk: {response.token_count / response.chunk_count:.1f}")
    print(f"Final vector dimension: {response.dimension}")
    print()


def error_handling_example():
    """Demonstrate error handling."""
    print("⚠️ Error Handling Example")
    print("-" * 50)
    
    from hashub_vector import (
        AuthenticationError, 
        ModelNotFoundError, 
        ValidationError,
        RateLimitError
    )
    
    # Example 1: Invalid model
    try:
        client.vectorize("Test", model="invalid_model")
    except ModelNotFoundError as e:
        print(f"Model error: {e}")
    
    # Example 2: Empty text validation
    try:
        client.vectorize("")
    except ValueError as e:
        print(f"Validation error: {e}")
    
    # Example 3: Batch size validation
    try:
        large_batch = ["text"] * 1001
        client.vectorize_batch(large_batch)
    except ValueError as e:
        print(f"Batch size error: {e}")
    
    print("Error handling examples completed successfully!")
    print()


async def async_example():
    """Asynchronous operations example."""
    print("⚡ Async Operations Example")
    print("-" * 50)
    
    async with HashubVector(api_key=API_KEY) as async_client:
        # Async single embedding
        response = await async_client.avectorize("Async embedding example")
        print(f"Async single embedding completed: {response.dimension}d vector")
        
        # Async batch processing
        texts = ["Fast async", "Hızlı async", "Async rapide"]
        batch_response = await async_client.avectorize_batch(texts)
        print(f"Async batch completed: {batch_response.count} vectors")
        
        # Get models asynchronously
        models = await async_client.aget_models()
        print(f"Retrieved {len(models)} models asynchronously")
    
    print()


def usage_monitoring():
    """Monitor API usage."""
    print("📊 Usage Monitoring Example")
    print("-" * 50)
    
    try:
        usage = client.get_usage()
        print(f"Tokens used: {usage.tokens_used:,}")
        
        if usage.tokens_remaining:
            print(f"Tokens remaining: {usage.tokens_remaining:,}")
            print(f"Usage percentage: {usage.tokens_percentage_used:.1f}%")
        
        if usage.requests_used:
            print(f"Requests made: {usage.requests_used}")
        
    except Exception as e:
        print(f"Could not retrieve usage info: {e}")
    
    print()


def model_information():
    """Get detailed model information."""
    print("ℹ️ Model Information Example")
    print("-" * 50)
    
    try:
        models = client.get_models()
        
        print(f"{'Model':<15} {'Tier':<10} {'Dimension':<10} {'Max Tokens':<12} {'Price/1M':<10}")
        print("-" * 70)
        
        for model in models:
            price = f"${model.price_per_1m_tokens:.3f}"
            print(f"{model.alias:<15} {model.tier:<10} {model.dimension:<10} {model.max_tokens:<12} {price:<10}")
        
    except Exception as e:
        print(f"Could not retrieve model info: {e}")
    
    print()


def main():
    """Run all examples."""
    print("🚀 HashHub Vector SDK - Basic Usage Examples")
    print("=" * 60)
    print()
    
    # Check API key
    if API_KEY == "your-api-key-here":
        print("⚠️ Please set your HASHHUB_API_KEY environment variable or update the API_KEY in this script")
        print("   export HASHHUB_API_KEY=your-actual-api-key")
        return
    
    try:
        # Run synchronous examples
        basic_embedding()
        turkish_optimization()
        batch_processing()
        model_comparison()
        similarity_calculation()
        chunking_example()
        error_handling_example()
        usage_monitoring()
        model_information()
        
        # Run async example
        print("Running async examples...")
        asyncio.run(async_example())
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Please check your API key and internet connection.")
    
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
