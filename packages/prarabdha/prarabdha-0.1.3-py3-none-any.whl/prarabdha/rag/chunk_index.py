import hashlib
import json
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import threading

from ..core.kv_store import MultiLayerKVStore
from ..core.vector_index import SemanticVectorIndex

class DocumentChunk:
    """Represents a document chunk with metadata"""
    
    def __init__(self, 
                 content: str,
                 document_id: str,
                 chunk_id: str,
                 chunk_index: int,
                 metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.document_id = document_id
        self.chunk_id = chunk_id
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'content': self.content,
            'document_id': self.document_id,
            'chunk_id': self.chunk_id,
            'chunk_index': self.chunk_index,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentChunk':
        """Create from dictionary"""
        return cls(
            content=data['content'],
            document_id=data['document_id'],
            chunk_id=data['chunk_id'],
            chunk_index=data['chunk_index'],
            metadata=data.get('metadata', {})
        )

class ChunkIndex:
    """Document-aware RAG chunk cache"""
    
    def __init__(self,
                 kv_store: Optional[MultiLayerKVStore] = None,
                 vector_index: Optional[SemanticVectorIndex] = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 similarity_threshold: float = 0.8):
        
        # Initialize KV store
        self.kv_store = kv_store or MultiLayerKVStore()
        
        # Initialize vector index
        self.vector_index = vector_index or SemanticVectorIndex(
            similarity_threshold=similarity_threshold
        )
        
        # Chunking settings
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        
        # Document tracking
        self.document_chunks = {}  # document_id -> List[chunk_id]
        self.chunk_metadata = {}   # chunk_id -> metadata
        
        # Statistics
        self.stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0
        }
        self.stats_lock = threading.RLock()
    
    def _update_stats(self, hit: bool):
        """Update cache statistics"""
        with self.stats_lock:
            self.stats['total_requests'] += 1
            if hit:
                self.stats['cache_hits'] += 1
            else:
                self.stats['cache_misses'] += 1
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        return f"{document_id}:chunk:{chunk_index}"
    
    def _create_vector_embedding(self, content: str, metadata: Dict[str, Any]) -> np.ndarray:
        """Create vector embedding from chunk content and metadata"""
        # Simple feature vector based on content and metadata
        # In a real implementation, you'd use a proper embedding model
        embedding = []
        
        # Content length feature (normalized)
        content_length = len(content)
        embedding.append(min(content_length / 1000.0, 1.0))
        
        # Document ID hash feature
        doc_hash = hash(metadata.get('document_id', '')) % 1000 / 1000.0
        embedding.append(doc_hash)
        
        # Chunk index feature (normalized)
        chunk_index = metadata.get('chunk_index', 0)
        embedding.append(min(chunk_index / 100.0, 1.0))
        
        # Timestamp feature
        timestamp = metadata.get('created_at', time.time())
        normalized_time = (timestamp % 86400) / 86400.0
        embedding.append(normalized_time)
        
        # Pad to 768 dimensions
        while len(embedding) < 768:
            embedding.extend(embedding[:min(len(embedding), 768 - len(embedding))])
        
        return np.array(embedding[:768], dtype=np.float32)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def add_document(self, 
                     document_id: str,
                     content: str,
                     metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Add a document and split it into chunks"""
        
        # Split content into chunks
        text_chunks = self._chunk_text(content)
        chunk_ids = []
        
        for i, chunk_content in enumerate(text_chunks):
            chunk_id = self._generate_chunk_id(document_id, i)
            
            # Create chunk object
            chunk = DocumentChunk(
                content=chunk_content,
                document_id=document_id,
                chunk_id=chunk_id,
                chunk_index=i,
                metadata=metadata or {}
            )
            
            # Store chunk
            self._store_chunk(chunk)
            chunk_ids.append(chunk_id)
        
        # Track document chunks
        self.document_chunks[document_id] = chunk_ids
        self.stats['total_documents'] += 1
        self.stats['total_chunks'] += len(chunk_ids)
        
        return chunk_ids
    
    def _store_chunk(self, chunk: DocumentChunk):
        """Store a chunk in both KV store and vector index"""
        
        # Store in KV cache
        self.kv_store.set(chunk.chunk_id, chunk.to_dict())
        
        # Store in vector index
        embedding = self._create_vector_embedding(chunk.content, chunk.to_dict())
        
        vector_metadata = {
            'chunk_id': chunk.chunk_id,
            'document_id': chunk.document_id,
            'chunk_index': chunk.chunk_index,
            'content_length': len(chunk.content),
            'metadata': chunk.metadata
        }
        
        self.vector_index.add_vector(
            vector=embedding,
            metadata=vector_metadata,
            vector_id=chunk.chunk_id
        )
    
    def get_chunk(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a specific chunk by ID"""
        chunk_data = self.kv_store.get(chunk_id)
        hit = chunk_data is not None
        self._update_stats(hit)
        
        if chunk_data:
            return DocumentChunk.from_dict(chunk_data)
        return None
    
    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        chunk_ids = self.document_chunks.get(document_id, [])
        chunks = []
        
        for chunk_id in chunk_ids:
            chunk = self.get_chunk(chunk_id)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def search_similar_chunks(self, 
                             query: str, 
                             k: int = 5,
                             document_filter: Optional[str] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar chunks using vector search"""
        
        # Create query embedding
        query_metadata = {
            'document_id': 'query',
            'chunk_index': 0,
            'created_at': time.time()
        }
        query_embedding = self._create_vector_embedding(query, query_metadata)
        
        # Search in vector index
        similar_chunks = self.vector_index.search_similar(
            query_vector=query_embedding,
            k=k,
            threshold=self.similarity_threshold
        )
        
        # Filter by document if specified
        if document_filter:
            filtered_results = []
            for vector_id, similarity, metadata in similar_chunks:
                if metadata.get('document_id') == document_filter:
                    filtered_results.append((vector_id, similarity, metadata))
            return filtered_results
        
        return similar_chunks
    
    def get_chunk_with_rag_fallback(self, 
                                   query: str,
                                   k: int = 3) -> Optional[DocumentChunk]:
        """Get chunk with RAG fallback for similar content"""
        
        # Try to find similar chunks
        similar_chunks = self.search_similar_chunks(query, k)
        
        for vector_id, similarity, metadata in similar_chunks:
            chunk_id = metadata.get('chunk_id')
            if chunk_id:
                chunk = self.get_chunk(chunk_id)
                if chunk:
                    return chunk
        
        return None
    
    def remove_document(self, document_id: str) -> bool:
        """Remove all chunks for a document"""
        if document_id not in self.document_chunks:
            return False
        
        chunk_ids = self.document_chunks[document_id]
        
        # Remove chunks from KV store and vector index
        for chunk_id in chunk_ids:
            self.kv_store.delete(chunk_id)
            self.vector_index.remove_vector(chunk_id)
        
        # Remove from tracking
        del self.document_chunks[document_id]
        
        # Update stats
        self.stats['total_documents'] -= 1
        self.stats['total_chunks'] -= len(chunk_ids)
        
        return True
    
    def flush(self):
        """Clear all chunks and documents"""
        self.kv_store.flush()
        self.vector_index.flush()
        
        # Clear tracking
        self.document_chunks.clear()
        self.chunk_metadata.clear()
        
        # Reset stats
        with self.stats_lock:
            self.stats = {
                'total_documents': 0,
                'total_chunks': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_requests': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get chunk index statistics"""
        with self.stats_lock:
            stats = self.stats.copy()
            
            # Add hit rate
            if stats['total_requests'] > 0:
                stats['hit_rate'] = stats['cache_hits'] / stats['total_requests']
            else:
                stats['hit_rate'] = 0.0
            
            # Add KV store stats
            kv_stats = self.kv_store.get_stats()
            stats.update(kv_stats)
            
            # Add vector index stats
            vector_stats = self.vector_index.get_stats()
            stats['vector_index'] = vector_stats
            
            # Add chunking stats
            stats['chunk_size'] = self.chunk_size
            stats['chunk_overlap'] = self.chunk_overlap
            stats['similarity_threshold'] = self.similarity_threshold
            
            return stats
    
    def export_chunks(self, output_file: str):
        """Export all chunks and metadata"""
        export_data = {
            'stats': self.get_stats(),
            'documents': self.document_chunks,
            'chunks': {}
        }
        
        # Export chunk data
        for document_id, chunk_ids in self.document_chunks.items():
            for chunk_id in chunk_ids:
                chunk = self.get_chunk(chunk_id)
                if chunk:
                    export_data['chunks'][chunk_id] = chunk.to_dict()
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not export chunks: {e}")
    
    def import_chunks(self, input_file: str):
        """Import chunks and metadata"""
        try:
            with open(input_file, 'r') as f:
                import_data = json.load(f)
            
            # Clear existing data
            self.flush()
            
            # Import chunks
            for chunk_id, chunk_data in import_data.get('chunks', {}).items():
                chunk = DocumentChunk.from_dict(chunk_data)
                self._store_chunk(chunk)
            
            # Import document tracking
            self.document_chunks = import_data.get('documents', {})
            
            # Update stats
            self.stats['total_documents'] = len(self.document_chunks)
            self.stats['total_chunks'] = sum(len(chunks) for chunks in self.document_chunks.values())
            
        except Exception as e:
            print(f"Warning: Could not import chunks: {e}")

class ChunkIndexManager:
    """Manager for multiple chunk indices"""
    
    def __init__(self, base_cache_dir: str = ".chunk_cache"):
        self.base_cache_dir = Path(base_cache_dir)
        self.indices = {}
        self.lock = threading.RLock()
    
    def get_index(self, 
                  name: str,
                  chunk_size: int = 1000,
                  chunk_overlap: int = 200,
                  similarity_threshold: float = 0.8) -> ChunkIndex:
        """Get or create a chunk index by name"""
        with self.lock:
            if name not in self.indices:
                cache_dir = self.base_cache_dir / name
                kv_store = MultiLayerKVStore(disk_cache_dir=str(cache_dir))
                
                vector_index = SemanticVectorIndex(
                    cache_dir=str(cache_dir / "vectors"),
                    similarity_threshold=similarity_threshold
                )
                
                self.indices[name] = ChunkIndex(
                    kv_store=kv_store,
                    vector_index=vector_index,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    similarity_threshold=similarity_threshold
                )
            return self.indices[name]
    
    def list_indices(self) -> List[str]:
        """List all available indices"""
        with self.lock:
            return list(self.indices.keys())
    
    def remove_index(self, name: str):
        """Remove an index"""
        with self.lock:
            if name in self.indices:
                self.indices[name].flush()
                del self.indices[name]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all indices"""
        with self.lock:
            stats = {}
            for name, index in self.indices.items():
                stats[name] = index.get_stats()
            return stats
