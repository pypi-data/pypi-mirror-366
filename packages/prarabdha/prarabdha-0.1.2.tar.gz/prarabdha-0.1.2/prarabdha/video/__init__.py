# Video caching module for Prarabdha cache system

from .video_cache import VideoCache, VideoCacheManager, VideoSegment, VideoFrame

# Main classes for direct import
__all__ = [
    "VideoCache",
    "VideoCacheManager",
    "VideoSegment",
    "VideoFrame",
    "VideoCache"  # Alias for backward compatibility
]

# Create an alias for easier import
videoCache = VideoCache
