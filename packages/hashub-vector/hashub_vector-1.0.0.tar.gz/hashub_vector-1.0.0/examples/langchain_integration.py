"""
LangChain Integration Example for Hashub Vector SDK

This example shows how to integrate Hashub Vector embeddings with LangChain
for building RAG (Retrieval Augmented Generation) applications.
"""

import os
from typing import List
from hashub_vector import HashubVector

# LangChain imports (install with: pip install langchain)
try:
    from langchain.embeddings.base import Embeddings
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("LangChain not installed. Install with: pip install langchain")
    LANGCHAIN_AVAILABLE = False


class HashubEmbeddings(Embeddings):
    """
    LangChain-compatible embeddings class using Hashub Vector API.
    
    This class implements the LangChain Embeddings interface, making it
    a drop-in replacement for other embedding providers.
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "e5_base",
        chunk_size: int = None,
        chunk_overlap: float = None
    ):
        """
        Initialize Hashub embeddings.
        
        Args:
            api_key: Hashub API key
            model: Model to use for embeddings
            chunk_size: Optional chunk size for long texts
            chunk_overlap: Optional overlap ratio (0-1)
        """
        self.client = HashubVector(api_key=api_key)
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Use batch processing for efficiency
        response = self.client.vectorize_batch(
            texts=texts,
            model=self.model,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        return response.vectors
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        response = self.client.vectorize(
            text=text,
            model=self.model,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        return response.vector


def create_turkish_knowledge_base():
    """Create a Turkish knowledge base using Hashub embeddings."""
    print("🇹🇷 Creating Turkish Knowledge Base with LangChain")
    print("-" * 60)
    
    # Sample Turkish documents about AI and technology
    turkish_documents = [
        """
        Yapay Zeka (AI) Nedir?
        Yapay zeka, makinelerin insan benzeri düşünme ve öğrenme yeteneklerini 
        simüle etmesini sağlayan teknoloji dalıdır. AI sistemleri, büyük veri 
        setlerinden öğrenerek karmaşık problemleri çözebilir ve karar verebilir.
        """,
        
        """
        Makine Öğrenmesi Türleri
        Makine öğrenmesi üç ana kategoriye ayrılır: Denetimli öğrenme, 
        denetimsiz öğrenme ve pekiştirmeli öğrenme. Her biri farklı problem 
        türleri için optimize edilmiştir ve farklı veri gereksinimleri vardır.
        """,
        
        """
        Doğal Dil İşleme (NLP)
        NLP, bilgisayarların insan dilini anlayıp işlemesini sağlayan AI dalıdır. 
        Metin analizi, çeviri, duygu analizi ve chatbot'lar NLP'nin 
        uygulama alanlarından bazılarıdır.
        """,
        
        """
        Deep Learning ve Neural Networks
        Derin öğrenme, çok katmanlı yapay sinir ağları kullanarak karmaşık 
        pattern'leri öğrenen makine öğrenmesi alt dalıdır. Görüntü tanıma, 
        ses işleme ve dil modelleri için yaygın olarak kullanılır.
        """,
        
        """
        AI'nin İş Dünyasındaki Etkileri
        Yapay zeka, iş süreçlerini otomatikleştirme, müşteri deneyimini 
        iyileştirme ve veri odaklı karar verme konularında devrim yaratmaktadır. 
        Finans, sağlık, perakende ve üretim sektörlerinde yaygın olarak 
        benimsenmiştir.
        """
    ]
    
    # Initialize Hashub embeddings optimized for Turkish
    embeddings = HashubEmbeddings(
        api_key=os.getenv("HASHUB_API_KEY"),
        model="gte_base",  # Best model for Turkish
        chunk_size=512
    )
    
    # Create text splitter for long documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    
    # Process documents
    documents = []
    for i, doc_text in enumerate(turkish_documents):
        # Split into chunks
        chunks = text_splitter.split_text(doc_text.strip())
        
        # Create Document objects
        for j, chunk in enumerate(chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={"source": f"document_{i}", "chunk": j}
            ))
    
    print(f"Created {len(documents)} document chunks")
    
    # Create vector store
    print("Creating FAISS vector store...")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    print("✅ Turkish knowledge base created successfully!")
    return vectorstore, embeddings


def query_knowledge_base(vectorstore, embeddings):
    """Query the knowledge base with Turkish questions."""
    print("\n🔍 Querying Turkish Knowledge Base")
    print("-" * 40)
    
    # Turkish questions about AI
    questions = [
        "Yapay zeka nedir?",
        "Makine öğrenmesi türleri neler?",
        "NLP ne için kullanılır?",
        "Deep learning'in avantajları neler?",
        "AI iş dünyasını nasıl etkiliyor?"
    ]
    
    for question in questions:
        print(f"\n❓ Soru: {question}")
        
        # Search for relevant documents
        docs = vectorstore.similarity_search(question, k=2)
        
        print("📄 İlgili belgeler:")
        for i, doc in enumerate(docs, 1):
            print(f"{i}. {doc.page_content[:150]}...")
            print(f"   Kaynak: {doc.metadata['source']}")


def semantic_search_example():
    """Advanced semantic search with Turkish queries."""
    print("\n🎯 Advanced Semantic Search Example")
    print("-" * 45)
    
    # Create embeddings client
    embeddings = HashubEmbeddings(
        api_key=os.getenv("HASHUB_API_KEY"),
        model="e5_base"  # Good for search tasks
    )
    
    # Knowledge base about Turkish cities
    city_descriptions = [
        "İstanbul Türkiye'nin en büyük şehri ve ekonomik merkezidir.",
        "Ankara Türkiye'nin başkenti ve ikinci büyük şehridir.",
        "İzmir Ege Denizi kıyısında önemli bir liman şehridir.",
        "Antalya Akdeniz sahilinde turistik bir şehirdir.",
        "Bursa eski Osmanlı başkenti ve sanayi şehridir.",
        "Konya Anadolu'nun ortasında tarihi bir şehirdir."
    ]
    
    # Create vector store
    documents = [Document(page_content=desc) for desc in city_descriptions]
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Test queries
    queries = [
        "ekonomik merkez",
        "başkent", 
        "turizm",
        "sanayi",
        "tarih"
    ]
    
    for query in queries:
        print(f"\n🔍 Arama: '{query}'")
        docs = vectorstore.similarity_search(query, k=2)
        
        for i, doc in enumerate(docs, 1):
            print(f"  {i}. {doc.page_content}")


def cross_lingual_search():
    """Demonstrate cross-lingual search capabilities."""
    print("\n🌍 Cross-Lingual Search Example")
    print("-" * 35)
    
    embeddings = HashubEmbeddings(
        api_key=os.getenv("HASHUB_API_KEY"),
        model="gte_base"  # Best for multilingual
    )
    
    # Mixed language documents
    mixed_documents = [
        "Machine learning enables computers to learn without programming.",
        "Makine öğrenmesi bilgisayarların programlanmadan öğrenmesini sağlar.",
        "L'apprentissage automatique permet aux ordinateurs d'apprendre.",
        "El aprendizaje automático permite a las computadoras aprender.",
        "机器学习使计算机能够学习而无需编程。"
    ]
    
    documents = [Document(page_content=doc) for doc in mixed_documents]
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Search with different languages
    test_queries = [
        ("English", "computer learning"),
        ("Turkish", "bilgisayar öğrenmesi"),
        ("French", "apprentissage machine"),
        ("Spanish", "aprendizaje computadora")
    ]
    
    for lang, query in test_queries:
        print(f"\n🔍 {lang} query: '{query}'")
        docs = vectorstore.similarity_search(query, k=3)
        
        for i, doc in enumerate(docs, 1):
            print(f"  {i}. {doc.page_content}")


def rag_pipeline_example():
    """Complete RAG pipeline with Hashub embeddings."""
    print("\n🤖 RAG Pipeline Example")
    print("-" * 25)
    
    # This would integrate with a language model for complete RAG
    # For this example, we'll show the retrieval part
    
    embeddings = HashubEmbeddings(
        api_key=os.getenv("HASHUB_API_KEY"),
        model="gte_base"
    )
    
    # Technical documentation
    tech_docs = [
        """
        API Authentication: Hashub Vector API uses Bearer token authentication. 
        Include your API key in the Authorization header: 
        'Authorization: Bearer your-api-key'
        """,
        
        """
        Rate Limits: Free tier allows 60 requests per minute. 
        Starter tier allows 300 requests per minute. 
        Pro tier allows 1000 requests per minute.
        """,
        
        """
        Error Handling: The API returns standard HTTP status codes. 
        401 for authentication errors, 429 for rate limits, 
        400 for validation errors.
        """,
        
        """
        Model Selection: Choose gte_base for long documents, 
        e5_base for search tasks, e5_small for high volume processing.
        """,
        
        """
        Batch Processing: Send up to 1000 texts in a single batch request 
        for better performance and cost efficiency.
        """
    ]
    
    documents = [Document(page_content=doc.strip()) for doc in tech_docs]
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # User questions
    user_questions = [
        "How do I authenticate with the API?",
        "What are the rate limits?",
        "How should I handle errors?",
        "Which model should I use for search?",
        "Can I process multiple texts at once?"
    ]
    
    for question in user_questions:
        print(f"\n❓ Question: {question}")
        
        # Retrieve relevant context
        relevant_docs = vectorstore.similarity_search(question, k=1)
        context = relevant_docs[0].page_content if relevant_docs else "No relevant information found."
        
        print(f"📄 Context: {context[:200]}...")
        # In a real RAG system, this context would be sent to an LLM
        # to generate a comprehensive answer


def main():
    """Run LangChain integration examples."""
    if not LANGCHAIN_AVAILABLE:
        return
    
    print("🔗 Hashub Vector SDK - LangChain Integration Examples")
    print("=" * 65)
    
    # Check API key
    api_key = os.getenv("HASHUB_API_KEY")
    if not api_key:
        print("⚠️ Please set your HASHUB_API_KEY environment variable")
        return
    
    try:
        # Create knowledge base and run queries
        vectorstore, embeddings = create_turkish_knowledge_base()
        query_knowledge_base(vectorstore, embeddings)
        
        # Run other examples
        semantic_search_example()
        cross_lingual_search()
        rag_pipeline_example()
        
        print("\n✅ LangChain integration examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
