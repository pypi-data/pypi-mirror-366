import numpy as np
import faiss
import pickle
import hashlib
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import threading
import time

class SemanticVectorIndex:
    """FAISS-based semantic vector index for similarity matching"""
    
    def __init__(self, 
                 dimension: int = 768,
                 index_type: str = "flat",
                 cache_dir: str = ".vector_cache",
                 similarity_threshold: float = 0.8):
        self.dimension = dimension
        self.index_type = index_type
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.similarity_threshold = similarity_threshold
        self.lock = threading.RLock()
        
        # Initialize FAISS index
        self._init_index()
        
        # Metadata storage
        self.id_to_metadata = {}
        self.metadata_file = self.cache_dir / "metadata.pkl"
        self._load_metadata()
    
    def _init_index(self):
        """Initialize FAISS index based on type"""
        if self.index_type == "flat":
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        elif self.index_type == "ivf":
            # IVF index with 100 clusters
            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif self.index_type == "hnsw":
            # HNSW index for approximate nearest neighbor search
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 neighbors
        else:
            raise ValueError("index_type must be 'flat', 'ivf', or 'hnsw'")
        
        # Load existing index if available
        index_file = self.cache_dir / "faiss_index.bin"
        if index_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
            except Exception as e:
                print(f"Warning: Could not load existing index: {e}")
    
    def _load_metadata(self):
        """Load metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'rb') as f:
                    self.id_to_metadata = pickle.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
                self.id_to_metadata = {}
    
    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.id_to_metadata, f)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            index_file = self.cache_dir / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
        except Exception as e:
            print(f"Warning: Could not save index: {e}")
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector
    
    def add_vector(self, 
                   vector: np.ndarray, 
                   metadata: Dict[str, Any],
                   vector_id: Optional[str] = None) -> str:
        """Add a vector to the index with metadata"""
        with self.lock:
            # Normalize vector
            normalized_vector = self._normalize_vector(vector.astype(np.float32))
            
            # Generate ID if not provided
            if vector_id is None:
                vector_id = hashlib.md5(normalized_vector.tobytes()).hexdigest()
            
            # Add to FAISS index
            if self.index_type == "ivf" and not self.index.is_trained:
                # Train IVF index if needed
                self.index.train(normalized_vector.reshape(1, -1))
            
            self.index.add(normalized_vector.reshape(1, -1))
            
            # Store metadata
            self.id_to_metadata[vector_id] = {
                **metadata,
                'added_at': time.time(),
                'vector_id': vector_id
            }
            
            # Save to disk
            self._save_metadata()
            self._save_index()
            
            return vector_id
    
    def search_similar(self, 
                      query_vector: np.ndarray, 
                      k: int = 5,
                      threshold: Optional[float] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar vectors"""
        with self.lock:
            # Normalize query vector
            normalized_query = self._normalize_vector(query_vector.astype(np.float32))
            
            # Search in FAISS index
            if self.index_type == "ivf":
                # For IVF, we need to set the number of probes
                self.index.nprobe = min(10, self.index.nlist)
            
            similarities, indices = self.index.search(normalized_query.reshape(1, -1), k)
            
            # Filter by threshold
            threshold = threshold or self.similarity_threshold
            results = []
            
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity >= threshold and idx != -1:
                    # Get metadata for this index
                    vector_id = list(self.id_to_metadata.keys())[idx] if idx < len(self.id_to_metadata) else f"idx_{idx}"
                    metadata = self.id_to_metadata.get(vector_id, {})
                    
                    results.append((vector_id, float(similarity), metadata))
            
            return results
    
    def get_vector_by_id(self, vector_id: str) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """Get vector and metadata by ID"""
        with self.lock:
            if vector_id not in self.id_to_metadata:
                return None
            
            # Note: FAISS doesn't support direct retrieval by ID
            # This is a limitation - we'd need to maintain a separate mapping
            metadata = self.id_to_metadata[vector_id]
            return None, metadata  # Vector retrieval not implemented
    
    def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector from the index"""
        with self.lock:
            if vector_id not in self.id_to_metadata:
                return False
            
            # Note: FAISS doesn't support direct removal
            # This would require rebuilding the index
            # For now, we'll just remove from metadata
            del self.id_to_metadata[vector_id]
            self._save_metadata()
            return True
    
    def flush(self):
        """Clear the entire index"""
        with self.lock:
            self._init_index()  # Reinitialize empty index
            self.id_to_metadata.clear()
            self._save_metadata()
            self._save_index()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        with self.lock:
            return {
                "total_vectors": len(self.id_to_metadata),
                "index_type": self.index_type,
                "dimension": self.dimension,
                "similarity_threshold": self.similarity_threshold,
                "cache_dir": str(self.cache_dir),
                "index_size": self.index.ntotal if hasattr(self.index, 'ntotal') else 0
            }
    
    def export_vectors(self, output_file: str):
        """Export all vectors and metadata"""
        with self.lock:
            export_data = {
                "vectors": {},
                "metadata": self.id_to_metadata,
                "config": {
                    "dimension": self.dimension,
                    "index_type": self.index_type,
                    "similarity_threshold": self.similarity_threshold
                }
            }
            
            # Note: FAISS doesn't support direct vector export
            # This would require maintaining a separate vector storage
            
            try:
                with open(output_file, 'wb') as f:
                    pickle.dump(export_data, f)
            except Exception as e:
                print(f"Warning: Could not export vectors: {e}")
    
    def import_vectors(self, input_file: str):
        """Import vectors and metadata"""
        with self.lock:
            try:
                with open(input_file, 'rb') as f:
                    import_data = pickle.load(f)
                
                # Clear existing data
                self.flush()
                
                # Import metadata
                self.id_to_metadata = import_data.get("metadata", {})
                self._save_metadata()
                
                # Note: Vector reimport would require rebuilding the index
                print("Note: Vector reimport requires manual index rebuilding")
                
            except Exception as e:
                print(f"Warning: Could not import vectors: {e}")

class VectorIndexManager:
    """Manager for multiple vector indices"""
    
    def __init__(self, base_cache_dir: str = ".vector_cache"):
        self.base_cache_dir = Path(base_cache_dir)
        self.indices = {}
        self.lock = threading.RLock()
    
    def get_index(self, 
                  name: str,
                  dimension: int = 768,
                  index_type: str = "flat",
                  similarity_threshold: float = 0.8) -> SemanticVectorIndex:
        """Get or create a vector index by name"""
        with self.lock:
            if name not in self.indices:
                cache_dir = self.base_cache_dir / name
                self.indices[name] = SemanticVectorIndex(
                    dimension=dimension,
                    index_type=index_type,
                    cache_dir=str(cache_dir),
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
