import hashlib
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import threading
import numpy as np

from ..core.kv_store import MultiLayerKVStore
from ..core.vector_index import SemanticVectorIndex

class VideoFrame:
    """Represents a video frame with metadata"""
    
    def __init__(self,
                 video_id: str,
                 frame_index: int,
                 timestamp: float,
                 frame_data: Optional[np.ndarray] = None,
                 features: Optional[np.ndarray] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.video_id = video_id
        self.frame_index = frame_index
        self.timestamp = timestamp
        self.frame_data = frame_data
        self.features = features
        self.metadata = metadata or {}
        self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'video_id': self.video_id,
            'frame_index': self.frame_index,
            'timestamp': self.timestamp,
            'frame_data': self.frame_data.tolist() if self.frame_data is not None else None,
            'features': self.features.tolist() if self.features is not None else None,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoFrame':
        """Create from dictionary"""
        return cls(
            video_id=data['video_id'],
            frame_index=data['frame_index'],
            timestamp=data['timestamp'],
            frame_data=np.array(data['frame_data']) if data.get('frame_data') else None,
            features=np.array(data['features']) if data.get('features') else None,
            metadata=data.get('metadata', {})
        )

class VideoSegment:
    """Represents a video segment with multiple frames"""
    
    def __init__(self,
                 video_id: str,
                 segment_id: str,
                 start_frame: int,
                 end_frame: int,
                 start_time: float,
                 end_time: float,
                 frames: Optional[List[VideoFrame]] = None,
                 features: Optional[np.ndarray] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.video_id = video_id
        self.segment_id = segment_id
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.start_time = start_time
        self.end_time = end_time
        self.frames = frames or []
        self.features = features
        self.metadata = metadata or {}
        self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'video_id': self.video_id,
            'segment_id': self.segment_id,
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'frames': [frame.to_dict() for frame in self.frames],
            'features': self.features.tolist() if self.features is not None else None,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoSegment':
        """Create from dictionary"""
        return cls(
            video_id=data['video_id'],
            segment_id=data['segment_id'],
            start_frame=data['start_frame'],
            end_frame=data['end_frame'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            frames=[VideoFrame.from_dict(f) for f in data.get('frames', [])],
            features=np.array(data['features']) if data.get('features') else None,
            metadata=data.get('metadata', {})
        )

class VideoCache:
    """Video segment/frame cache for video processing"""
    
    def __init__(self,
                 kv_store: Optional[MultiLayerKVStore] = None,
                 vector_index: Optional[SemanticVectorIndex] = None,
                 feature_dimension: int = 768,
                 similarity_threshold: float = 0.8,
                 segment_duration: float = 5.0):  # 5 seconds per segment
        
        # Initialize KV store
        self.kv_store = kv_store or MultiLayerKVStore()
        
        # Initialize vector index for video embeddings
        self.vector_index = vector_index or SemanticVectorIndex(
            dimension=feature_dimension,
            similarity_threshold=similarity_threshold
        )
        
        # Video processing settings
        self.feature_dimension = feature_dimension
        self.similarity_threshold = similarity_threshold
        self.segment_duration = segment_duration
        
        # Video tracking
        self.video_segments = {}  # video_id -> List[segment_id]
        self.video_frames = {}    # video_id -> List[frame_index]
        
        # Statistics
        self.stats = {
            'total_videos': 0,
            'total_segments': 0,
            'total_frames': 0,
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
    
    def _generate_segment_key(self, video_id: str, segment_id: str) -> str:
        """Generate cache key for video segment"""
        return f"{video_id}:segment:{segment_id}"
    
    def _generate_frame_key(self, video_id: str, frame_index: int) -> str:
        """Generate cache key for video frame"""
        return f"{video_id}:frame:{frame_index}"
    
    def _create_vector_embedding(self, features: np.ndarray, metadata: Dict[str, Any]) -> np.ndarray:
        """Create vector embedding from video features"""
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
    
    def cache_video_segment(self,
                           video_id: str,
                           segment_id: str,
                           start_frame: int,
                           end_frame: int,
                           start_time: float,
                           end_time: float,
                           frames: Optional[List[VideoFrame]] = None,
                           features: Optional[np.ndarray] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Cache a video segment"""
        
        segment_key = self._generate_segment_key(video_id, segment_id)
        
        # Create video segment object
        video_segment = VideoSegment(
            video_id=video_id,
            segment_id=segment_id,
            start_frame=start_frame,
            end_frame=end_frame,
            start_time=start_time,
            end_time=end_time,
            frames=frames or [],
            features=features,
            metadata=metadata or {}
        )
        
        # Store in KV cache
        self.kv_store.set(segment_key, video_segment.to_dict())
        
        # Store in vector index if features are available
        if features is not None:
            embedding = self._create_vector_embedding(features, video_segment.to_dict())
            
            vector_metadata = {
                'segment_key': segment_key,
                'video_id': video_id,
                'segment_id': segment_id,
                'start_time': start_time,
                'end_time': end_time,
                'feature_shape': features.shape,
                'metadata': metadata or {}
            }
            
            self.vector_index.add_vector(
                vector=embedding,
                metadata=vector_metadata,
                vector_id=segment_key
            )
        
        # Track video segments
        if video_id not in self.video_segments:
            self.video_segments[video_id] = []
        if segment_id not in self.video_segments[video_id]:
            self.video_segments[video_id].append(segment_id)
        
        # Update stats
        self.stats['total_videos'] = len(self.video_segments)
        self.stats['total_segments'] += 1
        self.stats['total_frames'] += len(frames) if frames else 0
        
        return segment_key
    
    def cache_video_frame(self,
                         video_id: str,
                         frame_index: int,
                         timestamp: float,
                         frame_data: Optional[np.ndarray] = None,
                         features: Optional[np.ndarray] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Cache a single video frame"""
        
        frame_key = self._generate_frame_key(video_id, frame_index)
        
        # Create video frame object
        video_frame = VideoFrame(
            video_id=video_id,
            frame_index=frame_index,
            timestamp=timestamp,
            frame_data=frame_data,
            features=features,
            metadata=metadata or {}
        )
        
        # Store in KV cache
        self.kv_store.set(frame_key, video_frame.to_dict())
        
        # Track video frames
        if video_id not in self.video_frames:
            self.video_frames[video_id] = []
        if frame_index not in self.video_frames[video_id]:
            self.video_frames[video_id].append(frame_index)
        
        # Update stats
        self.stats['total_frames'] += 1
        
        return frame_key
    
    def get_video_segment(self, video_id: str, segment_id: str) -> Optional[VideoSegment]:
        """Get cached video segment"""
        segment_key = self._generate_segment_key(video_id, segment_id)
        segment_data = self.kv_store.get(segment_key)
        
        hit = segment_data is not None
        self._update_stats(hit)
        
        if segment_data:
            return VideoSegment.from_dict(segment_data)
        return None
    
    def get_video_frame(self, video_id: str, frame_index: int) -> Optional[VideoFrame]:
        """Get cached video frame"""
        frame_key = self._generate_frame_key(video_id, frame_index)
        frame_data = self.kv_store.get(frame_key)
        
        hit = frame_data is not None
        self._update_stats(hit)
        
        if frame_data:
            return VideoFrame.from_dict(frame_data)
        return None
    
    def get_video_segments(self, video_id: str) -> List[VideoSegment]:
        """Get all segments for a video"""
        segment_ids = self.video_segments.get(video_id, [])
        segments = []
        
        for segment_id in segment_ids:
            segment = self.get_video_segment(video_id, segment_id)
            if segment:
                segments.append(segment)
        
        return segments
    
    def get_video_frames(self, video_id: str, start_frame: Optional[int] = None, end_frame: Optional[int] = None) -> List[VideoFrame]:
        """Get frames for a video with optional range"""
        frame_indices = self.video_frames.get(video_id, [])
        frames = []
        
        for frame_index in frame_indices:
            if start_frame is not None and frame_index < start_frame:
                continue
            if end_frame is not None and frame_index > end_frame:
                continue
            
            frame = self.get_video_frame(video_id, frame_index)
            if frame:
                frames.append(frame)
        
        return frames
    
    def search_similar_segments(self,
                               query_features: np.ndarray,
                               k: int = 5,
                               video_filter: Optional[str] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar video segments using feature embeddings"""
        
        # Create query embedding
        query_metadata = {
            'video_id': 'query',
            'segment_id': 'query',
            'start_time': 0.0,
            'end_time': 0.0,
            'created_at': time.time()
        }
        query_embedding = self._create_vector_embedding(query_features, query_metadata)
        
        # Search in vector index
        similar_segments = self.vector_index.search_similar(
            query_vector=query_embedding,
            k=k,
            threshold=self.similarity_threshold
        )
        
        # Filter by video if specified
        if video_filter:
            filtered_results = []
            for vector_id, similarity, metadata in similar_segments:
                if metadata.get('video_id') == video_filter:
                    filtered_results.append((vector_id, similarity, metadata))
            return filtered_results
        
        return similar_segments
    
    def get_segment_with_rag_fallback(self,
                                     query_features: np.ndarray,
                                     k: int = 3) -> Optional[VideoSegment]:
        """Get video segment with RAG fallback for similar content"""
        
        # Try to find similar segments
        similar_segments = self.search_similar_segments(query_features, k)
        
        for vector_id, similarity, metadata in similar_segments:
            segment_key = metadata.get('segment_key')
            if segment_key:
                # Extract video_id and segment_id from key
                parts = segment_key.split(':')
                if len(parts) >= 3:
                    video_id = parts[0]
                    segment_id = parts[2]
                    segment = self.get_video_segment(video_id, segment_id)
                    if segment:
                        return segment
        
        return None
    
    def remove_video(self, video_id: str) -> bool:
        """Remove all segments and frames for a video"""
        if video_id not in self.video_segments and video_id not in self.video_frames:
            return False
        
        # Remove segments
        segment_ids = self.video_segments.get(video_id, [])
        for segment_id in segment_ids:
            segment_key = self._generate_segment_key(video_id, segment_id)
            self.kv_store.delete(segment_key)
            self.vector_index.remove_vector(segment_key)
        
        # Remove frames
        frame_indices = self.video_frames.get(video_id, [])
        for frame_index in frame_indices:
            frame_key = self._generate_frame_key(video_id, frame_index)
            self.kv_store.delete(frame_key)
        
        # Remove from tracking
        if video_id in self.video_segments:
            del self.video_segments[video_id]
        if video_id in self.video_frames:
            del self.video_frames[video_id]
        
        # Update stats
        self.stats['total_videos'] = len(self.video_segments)
        
        return True
    
    def flush(self):
        """Clear all video data"""
        self.kv_store.flush()
        self.vector_index.flush()
        
        # Clear tracking
        self.video_segments.clear()
        self.video_frames.clear()
        
        # Reset stats
        with self.stats_lock:
            self.stats = {
                'total_videos': 0,
                'total_segments': 0,
                'total_frames': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'total_requests': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get video cache statistics"""
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
            
            # Add video-specific stats
            stats['feature_dimension'] = self.feature_dimension
            stats['similarity_threshold'] = self.similarity_threshold
            stats['segment_duration'] = self.segment_duration
            
            return stats
    
    def export_video_data(self, output_file: str):
        """Export all video data and metadata"""
        export_data = {
            'stats': self.get_stats(),
            'video_segments': self.video_segments,
            'video_frames': self.video_frames,
            'segments': {},
            'frames': {}
        }
        
        # Export segment data
        for video_id, segment_ids in self.video_segments.items():
            for segment_id in segment_ids:
                segment = self.get_video_segment(video_id, segment_id)
                if segment:
                    segment_key = self._generate_segment_key(video_id, segment_id)
                    export_data['segments'][segment_key] = segment.to_dict()
        
        # Export frame data
        for video_id, frame_indices in self.video_frames.items():
            for frame_index in frame_indices:
                frame = self.get_video_frame(video_id, frame_index)
                if frame:
                    frame_key = self._generate_frame_key(video_id, frame_index)
                    export_data['frames'][frame_key] = frame.to_dict()
        
        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not export video data: {e}")
    
    def import_video_data(self, input_file: str):
        """Import video data and metadata"""
        try:
            with open(input_file, 'r') as f:
                import_data = json.load(f)
            
            # Clear existing data
            self.flush()
            
            # Import segments
            for segment_key, segment_data in import_data.get('segments', {}).items():
                segment = VideoSegment.from_dict(segment_data)
                self.cache_video_segment(
                    segment.video_id,
                    segment.segment_id,
                    segment.start_frame,
                    segment.end_frame,
                    segment.start_time,
                    segment.end_time,
                    segment.frames,
                    segment.features,
                    segment.metadata
                )
            
            # Import frames
            for frame_key, frame_data in import_data.get('frames', {}).items():
                frame = VideoFrame.from_dict(frame_data)
                self.cache_video_frame(
                    frame.video_id,
                    frame.frame_index,
                    frame.timestamp,
                    frame.frame_data,
                    frame.features,
                    frame.metadata
                )
            
            # Import tracking
            self.video_segments = import_data.get('video_segments', {})
            self.video_frames = import_data.get('video_frames', {})
            
            # Update stats
            self.stats['total_videos'] = len(self.video_segments)
            self.stats['total_segments'] = sum(len(segments) for segments in self.video_segments.values())
            self.stats['total_frames'] = sum(len(frames) for frames in self.video_frames.values())
            
        except Exception as e:
            print(f"Warning: Could not import video data: {e}")

class VideoCacheManager:
    """Manager for multiple video caches"""
    
    def __init__(self, base_cache_dir: str = ".video_cache"):
        self.base_cache_dir = Path(base_cache_dir)
        self.caches = {}
        self.lock = threading.RLock()
    
    def get_cache(self,
                  name: str,
                  feature_dimension: int = 768,
                  similarity_threshold: float = 0.8,
                  segment_duration: float = 5.0) -> VideoCache:
        """Get or create a video cache by name"""
        with self.lock:
            if name not in self.caches:
                cache_dir = self.base_cache_dir / name
                kv_store = MultiLayerKVStore(disk_cache_dir=str(cache_dir))
                
                vector_index = SemanticVectorIndex(
                    dimension=feature_dimension,
                    cache_dir=str(cache_dir / "vectors"),
                    similarity_threshold=similarity_threshold
                )
                
                self.caches[name] = VideoCache(
                    kv_store=kv_store,
                    vector_index=vector_index,
                    feature_dimension=feature_dimension,
                    similarity_threshold=similarity_threshold,
                    segment_duration=segment_duration
                )
            return self.caches[name]
    
    def list_caches(self) -> List[str]:
        """List all available video caches"""
        with self.lock:
            return list(self.caches.keys())
    
    def remove_cache(self, name: str):
        """Remove a video cache"""
        with self.lock:
            if name in self.caches:
                self.caches[name].flush()
                del self.caches[name]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all video caches"""
        with self.lock:
            stats = {}
            for name, cache in self.caches.items():
                stats[name] = cache.get_stats()
            return stats
