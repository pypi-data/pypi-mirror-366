"""
Production RAG System Example with Hashub Vector SDK

This example demonstrates building a production-ready RAG (Retrieval Augmented Generation)
system using Hashub Vector embeddings with proper error handling, monitoring, and optimization.
"""

import os
import asyncio
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

from hashub_vector import HashubVector

# Additional dependencies for production RAG
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a document chunk with metadata."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    source: str = "unknown"
    chunk_index: int = 0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProductionVectorStore:
    """
    Production-ready vector store with Hashub Vector embeddings.
    
    Features:
    - Efficient similarity search
    - Batch processing
    - Error handling and retries
    - Performance monitoring
    - Async operations
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gte_base",
        similarity_threshold: float = 0.7,
        max_retries: int = 3
    ):
        self.client = HashubVector(api_key=api_key, max_retries=max_retries)
        self.model = model
        self.similarity_threshold = similarity_threshold
        self.documents: List[DocumentChunk] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        
        # Performance metrics
        self.metrics = {
            "total_documents": 0,
            "total_embeddings": 0,
            "average_embedding_time": 0,
            "search_times": [],
            "cache_hits": 0
        }
        
        # Simple cache for embeddings
        self._embedding_cache: Dict[str, List[float]] = {}
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        sources: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> None:
        """Add documents to the vector store with batch processing."""
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        if metadatas is None:
            metadatas = [{}] * len(documents)
        if sources is None:
            sources = ["unknown"] * len(documents)
        
        start_time = time.time()
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_sources = sources[i:i + batch_size]
            
            try:
                # Get embeddings for batch
                response = self.client.vectorize_batch(
                    texts=batch_docs,
                    model=self.model
                )
                
                # Create document chunks
                for j, (doc, embedding, meta, source) in enumerate(
                    zip(batch_docs, response.vectors, batch_meta, batch_sources)
                ):
                    chunk = DocumentChunk(
                        id=f"doc_{len(self.documents) + j}",
                        content=doc,
                        embedding=embedding,
                        metadata=meta,
                        source=source,
                        chunk_index=j
                    )
                    self.documents.append(chunk)
                
                self.metrics["total_embeddings"] += len(batch_docs)
                logger.info(f"Processed batch {i//batch_size + 1}, total documents: {len(self.documents)}")
                
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                continue
        
        # Update embeddings matrix
        self._update_embeddings_matrix()
        
        embedding_time = time.time() - start_time
        self.metrics["average_embedding_time"] = embedding_time / len(documents)
        self.metrics["total_documents"] = len(self.documents)
        
        logger.info(f"Added {len(documents)} documents in {embedding_time:.2f}s")
    
    def _update_embeddings_matrix(self) -> None:
        """Update the embeddings matrix for efficient similarity search."""
        if not self.documents or not NUMPY_AVAILABLE:
            return
        
        embeddings = [doc.embedding for doc in self.documents if doc.embedding]
        if embeddings:
            self.embeddings_matrix = np.array(embeddings)
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar documents."""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{query}_{self.model}"
        if cache_key in self._embedding_cache:
            query_embedding = self._embedding_cache[cache_key]
            self.metrics["cache_hits"] += 1
        else:
            # Get query embedding
            response = self.client.vectorize(query, model=self.model)
            query_embedding = response.vector
            self._embedding_cache[cache_key] = query_embedding
        
        # Filter documents by metadata if specified
        candidates = self.documents
        if filter_metadata:
            candidates = [
                doc for doc in self.documents
                if all(doc.metadata.get(k) == v for k, v in filter_metadata.items())
            ]
        
        # Calculate similarities
        similarities = []
        if NUMPY_AVAILABLE and self.embeddings_matrix is not None:
            # Efficient numpy-based similarity calculation
            query_vec = np.array(query_embedding).reshape(1, -1)
            candidate_embeddings = np.array([doc.embedding for doc in candidates])
            sims = cosine_similarity(query_vec, candidate_embeddings)[0]
            
            for doc, sim in zip(candidates, sims):
                if sim >= self.similarity_threshold:
                    similarities.append((doc, float(sim)))
        else:
            # Fallback to manual calculation
            for doc in candidates:
                if doc.embedding:
                    sim = self._cosine_similarity(query_embedding, doc.embedding)
                    if sim >= self.similarity_threshold:
                        similarities.append((doc, sim))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = similarities[:k]
        
        search_time = time.time() - start_time
        self.metrics["search_times"].append(search_time)
        
        logger.info(f"Search completed in {search_time:.3f}s, found {len(results)} results")
        return results
    
    async def asearch(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Async version of search."""
        start_time = time.time()
        
        # Get query embedding asynchronously
        response = await self.client.avectorize(query, model=self.model)
        query_embedding = response.vector
        
        # Use thread pool for similarity calculations
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Filter documents
            candidates = self.documents
            if filter_metadata:
                candidates = [
                    doc for doc in self.documents
                    if all(doc.metadata.get(k) == v for k, v in filter_metadata.items())
                ]
            
            # Calculate similarities in parallel
            similarity_futures = [
                executor.submit(self._cosine_similarity, query_embedding, doc.embedding)
                for doc in candidates if doc.embedding
            ]
            
            similarities = []
            for doc, future in zip(candidates, similarity_futures):
                try:
                    sim = future.result()
                    if sim >= self.similarity_threshold:
                        similarities.append((doc, sim))
                except Exception as e:
                    logger.error(f"Error calculating similarity: {e}")
        
        # Sort and return results
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = similarities[:k]
        
        search_time = time.time() - start_time
        logger.info(f"Async search completed in {search_time:.3f}s")
        return results
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 * norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        metrics = self.metrics.copy()
        if metrics["search_times"]:
            metrics["average_search_time"] = sum(metrics["search_times"]) / len(metrics["search_times"])
            metrics["max_search_time"] = max(metrics["search_times"])
            metrics["min_search_time"] = min(metrics["search_times"])
        
        return metrics
    
    def save_to_file(self, filepath: str) -> None:
        """Save vector store to file."""
        data = {
            "documents": [
                {
                    "id": doc.id,
                    "content": doc.content,
                    "embedding": doc.embedding,
                    "metadata": doc.metadata,
                    "source": doc.source,
                    "chunk_index": doc.chunk_index
                }
                for doc in self.documents
            ],
            "model": self.model,
            "metrics": self.metrics
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Vector store saved to {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str, api_key: str) -> "ProductionVectorStore":
        """Load vector store from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        instance = cls(api_key=api_key, model=data.get("model", "gte_base"))
        
        # Restore documents
        for doc_data in data["documents"]:
            chunk = DocumentChunk(
                id=doc_data["id"],
                content=doc_data["content"],
                embedding=doc_data["embedding"],
                metadata=doc_data["metadata"],
                source=doc_data["source"],
                chunk_index=doc_data["chunk_index"]
            )
            instance.documents.append(chunk)
        
        # Restore metrics
        instance.metrics = data.get("metrics", instance.metrics)
        
        # Update embeddings matrix
        instance._update_embeddings_matrix()
        
        logger.info(f"Vector store loaded from {filepath}")
        return instance


class RAGSystem:
    """Complete RAG system with Hashub Vector embeddings."""
    
    def __init__(self, api_key: str, model: str = "gte_base"):
        self.vector_store = ProductionVectorStore(api_key=api_key, model=model)
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_knowledge_base(
        self,
        documents: List[str],
        sources: Optional[List[str]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> None:
        """Add documents to the knowledge base with chunking."""
        logger.info("Building knowledge base...")
        
        # Simple text chunking
        chunked_docs = []
        chunked_sources = []
        chunked_metadata = []
        
        for i, doc in enumerate(documents):
            source = sources[i] if sources else f"document_{i}"
            chunks = self._chunk_text(doc, chunk_size, chunk_overlap)
            
            for j, chunk in enumerate(chunks):
                chunked_docs.append(chunk)
                chunked_sources.append(source)
                chunked_metadata.append({
                    "document_index": i,
                    "chunk_index": j,
                    "total_chunks": len(chunks)
                })
        
        self.vector_store.add_documents(
            documents=chunked_docs,
            sources=chunked_sources,
            metadatas=chunked_metadata
        )
    
    def query(
        self,
        question: str,
        k: int = 3,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """Query the RAG system."""
        logger.info(f"Processing query: {question}")
        
        # Search for relevant documents
        search_results = self.vector_store.search(question, k=k)
        
        # Extract relevant context
        context_chunks = []
        sources = set()
        
        for doc, similarity in search_results:
            context_chunks.append(doc.content)
            sources.add(doc.source)
        
        context = "\n\n".join(context_chunks)
        
        # In a real system, this context would be sent to an LLM
        # For this example, we'll return the context and metadata
        response = {
            "question": question,
            "context": context,
            "relevant_chunks": len(context_chunks),
            "sources": list(sources) if include_sources else [],
            "similarities": [sim for _, sim in search_results],
            "avg_similarity": sum(sim for _, sim in search_results) / len(search_results) if search_results else 0
        }
        
        # Add to conversation history
        self.conversation_history.append({
            "question": question,
            "response": context[:200] + "..." if len(context) > 200 else context
        })
        
        return response
    
    async def aquery(self, question: str, k: int = 3) -> Dict[str, Any]:
        """Async version of query."""
        search_results = await self.vector_store.asearch(question, k=k)
        
        context_chunks = [doc.content for doc, _ in search_results]
        context = "\n\n".join(context_chunks)
        
        return {
            "question": question,
            "context": context,
            "relevant_chunks": len(context_chunks),
            "similarities": [sim for _, sim in search_results]
        }
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
        """Simple text chunking."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
        
        return chunks if chunks else [text]
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        return {
            "vector_store_metrics": self.vector_store.get_metrics(),
            "total_queries": len(self.conversation_history),
            "knowledge_base_size": len(self.vector_store.documents)
        }


def create_turkish_tech_knowledge_base():
    """Create a comprehensive Turkish technology knowledge base."""
    
    turkish_tech_documents = [
        """
        Türkiye'de Yapay Zeka Gelişimi
        
        Türkiye, yapay zeka alanında hızla ilerleyen ülkeler arasında yer almaktadır. 
        Üniversiteler, araştırma merkezleri ve teknoloji şirketleri AI konusunda 
        yoğun çalışmalar yürütmektedir. TÜBITAK ve KOSGEB gibi kurumlar yapay zeka 
        projelerine destek sağlamaktadır.
        
        Özellikle doğal dil işleme, görüntü işleme ve makine öğrenmesi alanlarında 
        önemli projeler geliştirilmektedir. Türkçe dil modelleri ve çok dilli 
        AI sistemleri üzerinde çalışan ekipler bulunmaktadır.
        """,
        
        """
        Blockchain Teknolojisi ve Kripto Para
        
        Blockchain teknolojisi, merkezi olmayan dijital kayıt tutma sistemidir. 
        Bu teknoloji, finansal işlemlerden tedarik zinciri yönetimine kadar 
        birçok alanda kullanılmaktadır. Bitcoin ve Ethereum gibi kripto paralar 
        blockchain teknolojisinin en bilinen uygulamalarıdır.
        
        Türkiye'de blockchain teknolojisine olan ilgi artmaktadır. Merkez Bankası 
        dijital para birimi (CBDC) üzerinde çalışmalar yapmaktadır. Ayrıca 
        birçok Türk teknoloji şirketi blockchain tabanlı çözümler geliştirmektedir.
        """,
        
        """
        Bulut Bilişim ve Veri Merkezi Hizmetleri
        
        Bulut bilişim, IT kaynaklarının internet üzerinden hizmet olarak 
        sunulmasıdır. Amazon Web Services (AWS), Microsoft Azure ve Google Cloud 
        Platform (GCP) en büyük bulut sağlayıcılarıdır.
        
        Türkiye'de bulut bilişim hızla yaygınlaşmaktadır. Yerel veri merkezleri 
        kurulmakta ve veri lokalizasyonu konusunda çalışmalar yapılmaktadır. 
        KVKK (Kişisel Verilerin Korunması Kanunu) uyumluluğu önemli bir 
        gereksinim haline gelmiştir.
        """,
        
        """
        Siber Güvenlik ve Veri Koruma
        
        Siber güvenlik, dijital sistemleri, ağları ve verileri kötü niyetli 
        saldırılardan koruma sürecidir. Günümüzde siber saldırılar artmakta 
        ve daha sofistike hale gelmektedir.
        
        Türkiye'de siber güvenlik alanında önemli gelişmeler yaşanmaktadır. 
        Siber Güvenlik Kurulu (SGK) kurulmuş ve Ulusal Siber Güvenlik Stratejisi 
        belirlenmiştir. Birçok üniversitede siber güvenlik eğitimi verilmektedir.
        """,
        
        """
        Nesnelerin İnterneti (IoT) ve Akıllı Şehirler
        
        IoT, fiziksel nesnelerin internet bağlantısı sayesinde veri toplaması 
        ve paylaşması teknolojisidir. Akıllı şehir uygulamalarında yaygın 
        olarak kullanılmaktadır.
        
        Türkiye'de akıllı şehir projeleri hızla gelişmektedir. İstanbul, 
        Ankara ve İzmir gibi büyük şehirlerde IoT tabanlı çözümler uygulanmaktadır. 
        Akıllı ulaşım, enerji yönetimi ve çevre izleme sistemleri kurulmaktadır.
        """
    ]
    
    return turkish_tech_documents


async def main():
    """Run production RAG system examples."""
    print("🏭 Hashub Vector SDK - Production RAG System")
    print("=" * 50)
    
    api_key = os.getenv("HASHUB_API_KEY")
    if not api_key:
        print("⚠️ Please set your HASHUB_API_KEY environment variable")
        return
    
    try:
        # Create RAG system
        rag = RAGSystem(api_key=api_key, model="gte_base")
        
        # Build knowledge base
        print("📚 Building Turkish technology knowledge base...")
        documents = create_turkish_tech_knowledge_base()
        rag.add_knowledge_base(documents, chunk_size=400)
        
        # Test queries
        test_queries = [
            "Türkiye'de yapay zeka nasıl gelişiyor?",
            "Blockchain teknolojisi nedir?",
            "Bulut bilişimin avantajları neler?",
            "Siber güvenlik neden önemli?",
            "IoT ve akıllı şehirler hakkında bilgi ver"
        ]
        
        print("\n🔍 Testing RAG system...")
        for query in test_queries:
            print(f"\n❓ Soru: {query}")
            
            response = rag.query(query, k=2)
            print(f"📊 Benzerlik ortalaması: {response['avg_similarity']:.3f}")
            print(f"📄 İlgili parça sayısı: {response['relevant_chunks']}")
            print(f"🎯 Cevap preview: {response['context'][:200]}...")
        
        # Test async query
        print("\n⚡ Testing async query...")
        async_response = await rag.aquery("Yapay zeka projeleri")
        print(f"📊 Async query completed, {len(async_response['similarities'])} results")
        
        # Show system metrics
        print("\n📈 System Performance Metrics:")
        metrics = rag.get_system_metrics()
        vector_metrics = metrics["vector_store_metrics"]
        
        print(f"• Total documents: {vector_metrics['total_documents']}")
        print(f"• Total embeddings: {vector_metrics['total_embeddings']}")
        print(f"• Average embedding time: {vector_metrics['average_embedding_time']:.3f}s")
        print(f"• Cache hits: {vector_metrics['cache_hits']}")
        print(f"• Total queries: {metrics['total_queries']}")
        
        if vector_metrics.get("average_search_time"):
            print(f"• Average search time: {vector_metrics['average_search_time']:.3f}s")
        
        # Save vector store
        print("\n💾 Saving vector store...")
        rag.vector_store.save_to_file("turkish_tech_knowledge_base.json")
        
        print("\n✅ Production RAG system example completed successfully!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if not NUMPY_AVAILABLE:
        print("⚠️ Install numpy for better performance: pip install numpy scikit-learn")
    
    asyncio.run(main())
