import hashlib
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import threading
import numpy as np

from ..core.kv_store import MultiLayerKVStore
from ..core.vector_index import SemanticVectorIndex

class AudioFeature:
    """Represents audio features with metadata"""
    
    def __init__(self,
                 audio_id: str,
                 feature_type: str,
                 features: np.ndarray,
                 metadata: Optional[Dict[str, Any]] = None):
        self.audio_id = audio_id
        self.feature_type = feature_type
        self.features = features
        self.metadata = metadata or {}
        self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'audio_id': self.audio_id,
            'feature_type': self.feature_type,
            'features': self.features.tolist(),
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFeature':
        """Create from dictionary"""
        return cls(
            audio_id=data['audio_id'],
            feature_type=data['feature_type'],
            features=np.array(data['features']),
            metadata=data.get('metadata', {})
        )

class AudioCache:
    """Audio feature-level cache for embeddings and processing"""
    
    def __init__(self,
                 kv_store: Optional[MultiLayerKVStore] = None,
                 vector_index: Optional[SemanticVectorIndex] = None,
                 feature_dimension: int = 768,
                 similarity_threshold: float = 0.8):
        
        # Initialize KV store
        self.kv_store = kv_store or MultiLayerKVStore()
        
        # Initialize vector index for audio embeddings
        self.vector_index = vector_index or SemanticVectorIndex(
            dimension=feature_dimension,
            similarity_threshold=similarity_threshold
        )
        
        # Audio processing settings
        self.feature_dimension = feature_dimension
        self.similarity_threshold = similarity_threshold
        
        # Audio tracking
        self.audio_features = {}  # audio_id -> List[feature_type]
        
        # Statistics
        self.stats = {
            'total_audio_files': 0,
            'total_features': 0,
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
    
    def _generate_feature_key(self, audio_id: str, feature_type: str) -> str:
        """Generate cache key for audio feature"""
        return f"{audio_id}:{feature_type}"
    
    def _create_vector_embedding(self, features: np.ndarray, metadata: Dict[str, Any]) -> np.ndarray:
        """Create vector embedding from audio features"""
        # Convert numpy array to list and normalize
        feature_list = features.flatten().tolist()
        
        # Normalize to unit length for cosine similarity
        norm = np.linalg.norm(features)
        if norm > 0:
            feature_list = (features / norm).flatten().tolist()
        
        # Pad or truncate to target dimension
        if len(feature_list) < self.feature_dimension:
            # Pad with zeros
            feature_list.extend([0.0] * (self.feature_dimension - len(feature_list)))
        elif len(feature_list) > self.feature_dimension:
            # Truncate
            feature_list = feature_list[:self.feature_dimension]
        
        return np.array(feature_list, dtype=np.float32)
    
    def cache_audio_features(self,
                           audio_id: str,
                           feature_type: str,
                           features: np.ndarray,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Cache audio features"""
        
        feature_key = self._generate_feature_key(audio_id, feature_type)
        
        # Create audio feature object
        audio_feature = AudioFeature(
            audio_id=audio_id,
            feature_type=feature_type,
            features=features,
            metadata=metadata or {}
        )
        
        # Store in KV cache
        self.kv_store.set(feature_key, audio_feature.to_dict())
        
        # Store in vector index for similarity search
        embedding = self._create_vector_embedding(features, audio_feature.to_dict())
        
        vector_metadata = {
            'feature_key': feature_key,
            'audio_id': audio_id,
            'feature_type': feature_type,
            'feature_shape': features.shape,
            'metadata': metadata or {}
        }
        
        self.vector_index.add_vector(
            vector=embedding,
            metadata=vector_metadata,
            vector_id=feature_key
        )
        
        # Track audio features
        if audio_id not in self.audio_features:
            self.audio_features[audio_id] = []
        if feature_type not in self.audio_features[audio_id]:
            self.audio_features[audio_id].append(feature_type)
        
        # Update stats
        self.stats['total_audio_files'] = len(self.audio_features)
        self.stats['total_features'] += 1
        
        return feature_key
    
    def get_audio_features(self, audio_id: str, feature_type: str) -> Optional[AudioFeature]:
        """Get cached audio features"""
        feature_key = self._generate_feature_key(audio_id, feature_type)
        feature_data = self.kv_store.get(feature_key)
        
        hit = feature_data is not None
        self._update_stats(hit)
        
        if feature_data:
            return AudioFeature.from_dict(feature_data)
        return None
    
    def get_all_audio_features(self, audio_id: str) -> List[AudioFeature]:
        """Get all features for an audio file"""
        feature_types = self.audio_features.get(audio_id, [])
        features = []
        
        for feature_type in feature_types:
            feature = self.get_audio_features(audio_id, feature_type)
            if feature:
                features.append(feature)
        
        return features
    
    def search_similar_audio(self,
                            query_features: np.ndarray,
                            feature_type: str,
                            k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar audio using feature embeddings"""
        
        # Create query embedding
        query_metadata = {
            'audio_id': 'query',
            'feature_type': feature_type,
            'created_at': time.time()
        }
        query_embedding = self._create_vector_embedding(query_features, query_metadata)
        
        # Search in vector index
        similar_features = self.vector_index.search_similar(
            query_vector=query_embedding,
            k=k,
            threshold=self.similarity_threshold
        )
        
        # Filter by feature type
        filtered_results = []
        for vector_id, similarity, metadata in similar_features:
            if metadata.get('feature_type') == feature_type:
                filtered_results.append((vector_id, similarity, metadata))
        
        return filtered_results
    
    def get_audio_with_rag_fallback(self,
                                   query_features: np.ndarray,
                                   feature_type: str,
                                   k: int = 3) -> Optional[AudioFeature]:
        """Get audio features with RAG fallback for similar content"""
        
        # Try to find similar audio features
        similar_features = self.search_similar_audio(query_features, feature_type, k)
        
        for vector_id, similarity, metadata in similar_features:
            feature_key = metadata.get('feature_key')
            if feature_key:
                feature = self.get_audio_features(
                    metadata.get('audio_id', ''),
                    metadata.get('feature_type', '')
                )
                if feature:
                    return feature
        
        return None
    
    def remove_audio_features(self, audio_id: str, feature_type: Optional[str] = None) -> bool:
        """Remove audio features"""
        if feature_type:
            # Remove specific feature type
            feature_key = self._generate_feature_key(audio_id, feature_type)
            self.kv_store.delete(feature_key)
            self.vector_index.remove_vector(feature_key)
            
            if audio_id in self.audio_features and feature_type in self.audio_features[audio_id]:
                self.audio_features[audio_id].remove(feature_type)
                if not self.audio_features[audio_id]:
                    del self.audio_features[audio_id]
        else:
            # Remove all features for audio file
            feature_types = self.audio_features.get(audio_id, [])
            for feature_type in feature_types:
                feature_key = self._generate_feature_key(audio_id, feature_type)
                self.kv_store.delete(feature_key)
                self.vector_index.remove_vector(feature_key)
            
            if audio_id in self.audio_features:
                del self.audio_features[audio_id]
        
        # Update stats
        self.stats['total_audio_files'] = len(self.audio_features)
        
        return True
    
    def flush(self):
        """Clear all audio features"""
        self.kv_store.flush()
        self.vector_index.flush()
        
        # Clear tracking
        self.audio_features.clear()
        
        # Reset stats
        with self.stats_lock:
            self.stats = {
                'total_audio_files': 0,
                'total_features': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_requests': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audio cache statistics"""
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
            
            # Add audio-specific stats
            stats['feature_dimension'] = self.feature_dimension
            stats['similarity_threshold'] = self.similarity_threshold
            
            return stats
    
    def export_features(self, output_file: str):
        """Export all audio features and metadata"""
        export_data = {
            'stats': self.get_stats(),
            'audio_features': self.audio_features,
            'features': {}
        }
        
        # Export feature data
        for audio_id, feature_types in self.audio_features.items():
            for feature_type in feature_types:
                feature = self.get_audio_features(audio_id, feature_type)
                if feature:
                    feature_key = self._generate_feature_key(audio_id, feature_type)
                    export_data['features'][feature_key] = feature.to_dict()
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not export audio features: {e}")
    
    def import_features(self, input_file: str):
        """Import audio features and metadata"""
        try:
            with open(input_file, 'r') as f:
                import_data = json.load(f)
            
            # Clear existing data
            self.flush()
            
            # Import features
            for feature_key, feature_data in import_data.get('features', {}).items():
                feature = AudioFeature.from_dict(feature_data)
                self.cache_audio_features(
                    feature.audio_id,
                    feature.feature_type,
                    feature.features,
                    feature.metadata
                )
            
            # Import audio tracking
            self.audio_features = import_data.get('audio_features', {})
            
            # Update stats
            self.stats['total_audio_files'] = len(self.audio_features)
            self.stats['total_features'] = sum(len(types) for types in self.audio_features.values())
            
        except Exception as e:
            print(f"Warning: Could not import audio features: {e}")

class AudioCacheManager:
    """Manager for multiple audio caches"""
    
    def __init__(self, base_cache_dir: str = ".audio_cache"):
        self.base_cache_dir = Path(base_cache_dir)
        self.caches = {}
        self.lock = threading.RLock()
    
    def get_cache(self,
                  name: str,
                  feature_dimension: int = 768,
                  similarity_threshold: float = 0.8) -> AudioCache:
        """Get or create an audio cache by name"""
        with self.lock:
            if name not in self.caches:
                cache_dir = self.base_cache_dir / name
                kv_store = MultiLayerKVStore(disk_cache_dir=str(cache_dir))
                
                vector_index = SemanticVectorIndex(
                    dimension=feature_dimension,
                    cache_dir=str(cache_dir / "vectors"),
                    similarity_threshold=similarity_threshold
                )
                
                self.caches[name] = AudioCache(
                    kv_store=kv_store,
                    vector_index=vector_index,
                    feature_dimension=feature_dimension,
                    similarity_threshold=similarity_threshold
                )
            return self.caches[name]
    
    def list_caches(self) -> List[str]:
        """List all available audio caches"""
        with self.lock:
            return list(self.caches.keys())
    
    def remove_cache(self, name: str):
        """Remove an audio cache"""
        with self.lock:
            if name in self.caches:
                self.caches[name].flush()
                del self.caches[name]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all audio caches"""
        with self.lock:
            stats = {}
            for name, cache in self.caches.items():
                stats[name] = cache.get_stats()
            return stats
