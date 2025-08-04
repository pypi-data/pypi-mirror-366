# Prarabdha - Modular AI Cache System

A futuristic modular caching system for AI applications supporting multi-layer caching, vector similarity search, RAG-aware chunk indexing, and async ingestion APIs.

## Performance Benefits

![Prarabdha Performance](prarabdha_performance.png)

**Key Performance Improvements:**
- **8.0x speedup** for long context processing (25K tokens)
- **3.9x speedup** for RAG processing (4 x 2K chunks)
- **3-10x delay savings** and GPU cycle reduction
- **Multi-layer caching** across GPU, RAM, Disk, and Redis

## Features

### Core Components
- **Multi-layer KV Store**: RAM, disk, and Redis support with TTL and eviction policies
- **Vector Index**: FAISS-based semantic similarity search
- **RAG Chunk Index**: Document-aware chunking and retrieval
- **Audio Cache**: Feature-level audio processing cache
- **Video Cache**: Segment/frame-level video processing cache

### Advanced Features
- **LRU/LFU Eviction**: Configurable memory eviction policies
- **TTL Support**: Automatic expiration for all cache layers
- **Redis Integration**: Distributed caching with auto-sharding
- **RAG Integration**: Similarity-based retrieval with fallback
- **Async APIs**: FastAPI-based ingestion and inspection
- **CLI Tools**: Command-line interface for management

## Installation

```bash
# Install dependencies
pip install redis faiss-cpu fastapi uvicorn numpy aiohttp pydantic typer

# Clone the repository
git clone <repository-url>
cd prarabdha_cache_package

# Run examples
python3 simple_example.py
```

## Quick Start

### Clean Import Interface

The easiest way to use Prarabdha is with the clean import interface:

```python
# Import specific cache types
from prarabdha.chats import ChatCache
from prarabdha.audio import audioCache
from prarabdha.video import videoCache
from prarabdha.rag import RAGCache

# Create cache instances
chat_cache = ChatCache()
audio_cache = audioCache()
video_cache = videoCache()
rag_cache = RAGCache()
```

### Chat Caching

```python
from prarabdha.chats import ChatCache

# Create chat cache
chat_cache = ChatCache()

# Cache a chat segment
segment = {
    "content": "Hello, how can I help you?",
    "user_id": "user123",
    "session_id": "session456",
    "timestamp": 1234567890,
    "model": "gpt-4"
}

cache_key = chat_cache.cache_segment(segment)
print(f"Cached with key: {cache_key}")

# Retrieve segment with RAG fallback
retrieved = chat_cache.get_segment_with_rag_fallback(segment)
if retrieved:
    print(f"Retrieved: {retrieved['content']}")

# Get statistics
stats = chat_cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### Audio Caching

```python
from prarabdha.audio import audioCache
import numpy as np

# Create audio cache
audio_cache = audioCache()

# Cache audio features
features = np.random.rand(13, 100)  # MFCC features
feature_key = audio_cache.cache_audio_features(
    audio_id="audio1",
    feature_type="mfcc",
    features=features,
    metadata={"duration": 5.0, "sample_rate": 16000}
)

# Retrieve features
retrieved = audio_cache.get_audio_features("audio1", "mfcc")
if retrieved:
    print(f"Retrieved features shape: {retrieved.features.shape}")
```

### Video Caching

```python
from prarabdha.video import videoCache
import numpy as np

# Create video cache
video_cache = videoCache()

# Cache video segment
segment_key = video_cache.cache_video_segment(
    video_id="video1",
    segment_id="seg1",
    start_frame=0,
    end_frame=150,
    start_time=0.0,
    end_time=5.0,
    features=np.random.rand(768),
    metadata={"resolution": "1920x1080", "fps": 30}
)

# Retrieve segment
retrieved = video_cache.get_video_segment("video1", "seg1")
if retrieved:
    print(f"Retrieved segment: {retrieved.video_id}:{retrieved.segment_id}")
```

### RAG Chunk Indexing

```python
from prarabdha.rag import RAGCache

# Create RAG cache
rag_cache = RAGCache()

# Add document
chunk_ids = rag_cache.add_document(
    document_id="doc1",
    content="Python is a high-level programming language...",
    metadata={"author": "John Doe", "topic": "programming"}
)

# Search similar chunks
similar_chunks = rag_cache.search_similar_chunks("What is Python?", k=3)
for vector_id, similarity, metadata in similar_chunks:
    chunk = rag_cache.get_chunk(metadata.get('chunk_id', ''))
    print(f"Similarity: {similarity:.3f}, Content: {chunk.content[:100]}...")
```

### Advanced Usage

For more advanced usage, you can import the full classes:

```python
from prarabdha import (
    SegmentCacheManager,
    SegmentCacheManagerFactory,
    AudioCache,
    VideoCache,
    ChunkIndex
)

# Create with custom configuration
cache_manager = SegmentCacheManagerFactory.create_high_performance_manager()
audio_cache = AudioCache(feature_dimension=1024, similarity_threshold=0.9)
video_cache = VideoCache(segment_duration=10.0)
chunk_index = ChunkIndex(chunk_size=2000, chunk_overlap=400)
```

## CLI Usage

### Basic Commands

```bash
# Show help
python3 -m prarabdha.cli.cli --help

# View cache statistics
python3 -m prarabdha.cli.cli stats

# Clear all cache data
python3 -m prarabdha.cli.cli clear --yes

# Search for similar segments
python3 -m prarabdha.cli.cli search "Python programming help" --limit 5
```

### Ingest Data

```bash
# Ingest from JSON file
python3 -m prarabdha.cli.cli ingest segments.json --verbose

# Ingest with Redis backend
python3 -m prarabdha.cli.cli ingest segments.json --redis redis://localhost:6379/0

# Ingest with high-performance strategy
python3 -m prarabdha.cli.cli ingest segments.json --strategy high-performance
```

## API Usage

### Start the API Server

```bash
# Start the FastAPI server
python3 -m prarabdha.api.app
```

### API Endpoints

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Ingest segments
segments = [
    {
        "content": "Hello, how can I help you?",
        "user_id": "user123",
        "session_id": "session456",
        "timestamp": 1234567890,
        "model": "gpt-4"
    }
]

response = requests.post("http://localhost:8000/ingest", json={
    "segments": segments,
    "enable_rag": True,
    "similarity_threshold": 0.8
})
print(response.json())

# Search similar segments
response = requests.post("http://localhost:8000/search", json={
    "query": "Python programming help",
    "k": 3,
    "threshold": 0.7
})
print(response.json())

# Get statistics
response = requests.get("http://localhost:8000/stats")
print(response.json())
```

## Configuration

### Redis Configuration

```python
from prarabdha import SegmentCacheManagerFactory

# Create cache manager with Redis
redis_config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

cache_manager = SegmentCacheManagerFactory.create_redis_manager(redis_config)
```

### Custom Strategies

```python
from prarabdha import CacheStrategy, SegmentCacheManager

class CustomStrategy(CacheStrategy):
    def should_cache(self, segment):
        # Custom caching logic
        return len(segment.get('content', '')) > 50
    
    def generate_key(self, segment):
        # Custom key generation
        return f"{segment['user_id']}:{hash(segment['content'])}"
    
    def extract_features(self, segment):
        # Custom feature extraction
        return {
            'content_length': len(segment.get('content', '')),
            'user_id': segment.get('user_id', ''),
            'timestamp': segment.get('timestamp', 0)
        }

# Use custom strategy
cache_manager = SegmentCacheManager(strategy=CustomStrategy())
```

## Architecture

### Multi-layer Cache Architecture

```
┌─────────────────┐
│   Memory Cache  │  ← LRU/LFU with TTL
│   (RAM)         │
├─────────────────┤
│   Disk Cache    │  ← Persistent storage
│   (Local)       │
├─────────────────┤
│   Redis Cache   │  ← Distributed cache
│   (Optional)    │
└─────────────────┘
```

### Vector Index Architecture

```
┌─────────────────┐
│   Input Data    │
│   (Text/Audio/  │
│    Video)       │
├─────────────────┤
│   Feature       │  ← Embedding generation
│   Extraction    │
├─────────────────┤
│   FAISS Index   │  ← Vector similarity
│   (Flat/IVF/    │     search
│    HNSW)        │
└─────────────────┘
```

## Performance Features

### Eviction Policies
- **LRU (Least Recently Used)**: Removes least recently accessed items
- **LFU (Least Frequently Used)**: Removes least frequently accessed items
- **TTL (Time To Live)**: Automatic expiration based on time

### Scaling Features
- **Auto-sharding**: Automatic Redis sharding for horizontal scaling
- **Multi-layer promotion**: Hot data moves to faster layers
- **Background processing**: Async ingestion for high throughput

### Monitoring
- **Hit rate tracking**: Real-time cache performance metrics
- **Memory usage**: Per-layer memory consumption
- **Request statistics**: Detailed request/response tracking

## Testing

### Run Tests

```bash
# Run unit tests
python3 -m unittest prarabdha.tests.test_kv_backends

# Run simple example
python3 simple_example.py

# Run comprehensive example
python3 example_usage.py

# Test API
python3 test_api.py
```

### Example Output

```
Prarabdha Clean Import Interface Demo
==================================================
=== Chat Caching Demo ===
Cached chat segment with key: 68d3ccc8fd1c11dadd2d559e214dd360:28d5d305a0cc8e573a65c8aaa9bd4412
Retrieved: Hello, how can I help you with Python programming?
Chat cache hit rate: 100.00%

=== Audio Caching Demo ===
Cached audio features with key: audio1:mfcc
Retrieved audio features shape: (13, 100)
Audio cache: 1 files, 1 features

=== Video Caching Demo ===
Cached video segment with key: video1:segment:seg1
Retrieved video segment: video1:seg1
Video cache: 1 videos, 1 segments

=== RAG Caching Demo ===
Added document with 1 chunks
Found 2 similar chunks
RAG cache: 1 documents, 1 chunks
```

## Roadmap

### Completed Features
- [x] Multi-layer KV store (RAM, disk, Redis)
- [x] LRU/LFU eviction policies
- [x] TTL support for all layers
- [x] FAISS vector similarity search
- [x] RAG chunk indexing
- [x] Audio and video caching
- [x] FastAPI async ingestion
- [x] CLI management tools
- [x] Redis auto-sharding
- [x] Background processing
- [x] Clean import interface

### Planned Features
- [x] GPU-native tier for vLLM prefill (Basic implementation)
- [x] Persistent metadata store (SQLite-based)
- [x] Exportable cache storage (JSON, Parquet, SQLite)
- [x] Compression and encryption (AES-256 + GZIP/LZMA/ZLIB)
- [x] Plugin support for custom encoders
- [x] Advanced monitoring dashboard (Real-time WebSocket)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions and support, please open an issue on GitHub or contact the maintainers.

---

**Prarabdha** - Empowering AI applications with intelligent caching. 