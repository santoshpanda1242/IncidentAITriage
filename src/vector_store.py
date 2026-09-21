import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import hashlib
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class ChromaVectorStore:
    """ChromaDB vector store for semantic search with Ollama embeddings"""
    
    def __init__(self, collection_name: str = "incident_kb", persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist vector database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        print(f"✓ ChromaDB initialized with collection: {collection_name}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
            print(f"✓ Using existing collection: {self.collection_name}")
            return collection
        except:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Incident knowledge base documents"}
            )
            print(f"✓ Created new collection: {self.collection_name}")
            return collection
    
    def ingest_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Ingest a single document into the vector store
        
        Args:
            file_path: Path to the document file
            metadata: Additional metadata to attach to document chunks
        
        Returns:
            Number of chunks added
        """
        if not os.path.exists(file_path):
            print(f"✗ File not found: {file_path}")
            return 0
        
        # Read document content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create document object
        doc = Document(page_content=content, metadata=metadata or {})
        
        # Split document into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        # Prepare data for ChromaDB
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Generate unique IDs for chunks
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
        
        # Add file metadata to each chunk
        for i, chunk_metadata in enumerate(metadatas):
            chunk_metadata.update({
                'source_file': os.path.basename(file_path),
                'chunk_index': i,
                'total_chunks': len(chunks)
            })
        
        # Generate embeddings and add to collection
        embeddings = self.embeddings.embed_documents(texts)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✓ Ingested {len(chunks)} chunks from {os.path.basename(file_path)}")
        return len(chunks)
    
    def ingest_directory(self, directory_path: str, file_pattern: str = "*.md") -> int:
        """
        Ingest all documents from a directory
        
        Args:
            directory_path: Path to directory containing documents
            file_pattern: File pattern to match (e.g., "*.md", "*.txt")
        
        Returns:
            Total number of chunks added
        """
        directory = Path(directory_path)
        if not directory.exists():
            print(f"✗ Directory not found: {directory_path}")
            return 0
        
        total_chunks = 0
        files = list(directory.glob(file_pattern))
        
        print(f"Found {len(files)} files matching '{file_pattern}'")
        
        for file_path in files:
            chunks_added = self.ingest_document(str(file_path))
            total_chunks += chunks_added
        
        print(f"✓ Total chunks ingested: {total_chunks}")
        return total_chunks
    
    def similarity_search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search
        
        Args:
            query: Search query text
            n_results: Number of results to return
        
        Returns:
            List of search results with content and metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return formatted_results
    
    def hybrid_search(self, query: str, filters: Dict[str, Any] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with metadata filters
        
        Args:
            query: Search query text
            filters: Metadata filters (e.g., {'source_file': 'payment.md'})
            n_results: Number of results to return
        
        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search with filters
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filters if filters else None
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'total_documents': count,
            'persist_directory': self.persist_directory
        }
    
    def delete_collection(self):
        """Delete the current collection"""
        self.client.delete_collection(name=self.collection_name)
        print(f"✓ Collection deleted: {self.collection_name}")


class KnowledgeBaseManager:
    """Manager for knowledge base operations"""
    
    def __init__(self, kb_directory: str = "./kb"):
        """
        Initialize knowledge base manager
        
        Args:
            kb_directory: Directory containing knowledge base documents
        """
        self.kb_directory = kb_directory
        self.vector_store = ChromaVectorStore()
        self.is_ingested = False
    
    def initialize_knowledge_base(self, force_reingest: bool = False) -> bool:
        """
        Initialize knowledge base by ingesting documents
        
        Args:
            force_reingest: Force re-ingestion even if already done
        
        Returns:
            True if successful, False otherwise
        """
        # Check if collection already has data
        collection_stats = self.vector_store.get_collection_stats()
        existing_docs = collection_stats.get('total_documents', 0)
        
        if existing_docs > 0 and not force_reingest:
            print(f"✓ Knowledge base already has {existing_docs} documents - skipping ingestion")
            self.is_ingested = True
            return True
        
        if not os.path.exists(self.kb_directory):
            print(f"✗ KB directory not found: {self.kb_directory}")
            return False
        
        # Ingest all markdown and text files
        total_chunks = 0
        total_chunks += self.vector_store.ingest_directory(self.kb_directory, "*.md")
        total_chunks += self.vector_store.ingest_directory(self.kb_directory, "*.txt")
        
        if total_chunks > 0:
            self.is_ingested = True
            print(f"✓ Knowledge base initialized with {total_chunks} chunks")
            return True
        else:
            print("✗ No documents ingested")
            return False
    
    def search_knowledge_base(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of relevant document chunks
        """
        if not self.is_ingested:
            print("Warning: Knowledge base not initialized")
        
        results = self.vector_store.similarity_search(query, n_results)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return self.vector_store.get_collection_stats()


# Convenience function for quick search
def search_kb(query: str, kb_directory: str = "./kb", n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to search knowledge base
    
    Args:
        query: Search query
        kb_directory: Directory containing KB documents
        n_results: Number of results to return
    
    Returns:
        Search results
    """
    kb_manager = KnowledgeBaseManager(kb_directory)
    kb_manager.initialize_knowledge_base()
    return kb_manager.search_knowledge_base(query, n_results)