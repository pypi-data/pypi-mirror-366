from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import time
import asyncio
from pathlib import Path

from ..chats.core import SegmentCacheManager, SegmentCacheManagerFactory
from ..core.kv_store import MultiLayerKVStore

# Initialize FastAPI app
app = FastAPI(
    title="Prarabdha Cache API",
    description="Async ingestion and inspection API for the Prarabdha caching system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache manager instance
cache_manager: Optional[SegmentCacheManager] = None

# Pydantic models
class ChatSegment(BaseModel):
    content: str = Field(..., description="Chat content")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    timestamp: Optional[int] = Field(default_factory=lambda: int(time.time()), description="Unix timestamp")
    model: Optional[str] = Field(None, description="Model used for generation")
    type: Optional[str] = Field("chat", description="Segment type")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class IngestRequest(BaseModel):
    segments: List[ChatSegment] = Field(..., description="List of chat segments to ingest")
    strategy: Optional[str] = Field("default", description="Caching strategy")
    enable_rag: Optional[bool] = Field(True, description="Enable RAG similarity search")
    similarity_threshold: Optional[float] = Field(0.8, description="Similarity threshold for RAG")

class IngestResponse(BaseModel):
    success: bool
    cached_count: int
    skipped_count: int
    cache_keys: List[str]
    stats: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    k: Optional[int] = Field(5, description="Number of similar segments to return")
    threshold: Optional[float] = Field(0.8, description="Similarity threshold")

class SearchResult(BaseModel):
    vector_id: str
    similarity: float
    segment: ChatSegment
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int

class StatsResponse(BaseModel):
    stats: Dict[str, Any]

class ConfigRequest(BaseModel):
    redis_url: Optional[str] = Field(None, description="Redis URL")
    strategy: Optional[str] = Field("default", description="Caching strategy")
    enable_rag: Optional[bool] = Field(True, description="Enable RAG")
    similarity_threshold: Optional[float] = Field(0.8, description="Similarity threshold")

def get_cache_manager() -> SegmentCacheManager:
    """Get or create cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = SegmentCacheManagerFactory.create_default_manager()
    return cache_manager

def create_cache_manager_from_config(config: ConfigRequest) -> SegmentCacheManager:
    """Create cache manager from configuration"""
    if config.redis_url:
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }
        
        # Parse Redis URL
        if config.redis_url.startswith('redis://'):
            parts = config.redis_url.replace('redis://', '').split('/')
            if len(parts) > 1:
                host_port = parts[0].split(':')
                if len(host_port) > 1:
                    redis_config['host'] = host_port[0]
                    redis_config['port'] = int(host_port[1])
                else:
                    redis_config['host'] = host_port[0]
                
                if len(parts) > 1 and parts[1].isdigit():
                    redis_config['db'] = int(parts[1])
        
        return SegmentCacheManagerFactory.create_redis_manager(redis_config)
    else:
        return SegmentCacheManagerFactory.create_default_manager()

@app.on_event("startup")
async def startup_event():
    """Initialize cache manager on startup"""
    global cache_manager
    cache_manager = get_cache_manager()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Prarabdha Cache API",
        "version": "1.0.0",
        "endpoints": [
            "/docs",
            "/ingest",
            "/search",
            "/stats",
            "/config",
            "/clear"
        ]
    }

@app.post("/config", response_model=Dict[str, Any])
async def configure_cache(request: ConfigRequest):
    """Configure cache manager"""
    global cache_manager
    
    try:
        cache_manager = create_cache_manager_from_config(request)
        
        # Apply RAG settings
        cache_manager.enable_rag = request.enable_rag
        cache_manager.rag_similarity_threshold = request.similarity_threshold
        
        return {
            "success": True,
            "message": "Cache configured successfully",
            "config": {
                "strategy": request.strategy,
                "enable_rag": request.enable_rag,
                "similarity_threshold": request.similarity_threshold,
                "redis_url": request.redis_url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_segments(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest chat segments into cache"""
    try:
        cache_manager = get_cache_manager()
        
        # Configure RAG settings
        cache_manager.enable_rag = request.enable_rag
        cache_manager.rag_similarity_threshold = request.similarity_threshold
        
        cached_count = 0
        skipped_count = 0
        cache_keys = []
        
        # Process segments
        for segment in request.segments:
            segment_dict = segment.dict()
            cache_key = cache_manager.cache_segment(segment_dict)
            
            if cache_key:
                cached_count += 1
                cache_keys.append(cache_key)
            else:
                skipped_count += 1
        
        # Get stats
        stats = cache_manager.get_stats()
        
        return IngestResponse(
            success=True,
            cached_count=cached_count,
            skipped_count=skipped_count,
            cache_keys=cache_keys,
            stats=stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/ingest/async")
async def ingest_segments_async(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest segments asynchronously in background"""
    try:
        cache_manager = get_cache_manager()
        
        # Configure RAG settings
        cache_manager.enable_rag = request.enable_rag
        cache_manager.rag_similarity_threshold = request.similarity_threshold
        
        # Add background task
        background_tasks.add_task(process_segments_async, request.segments, cache_manager)
        
        return {
            "success": True,
            "message": f"Started async ingestion of {len(request.segments)} segments",
            "task_id": f"ingest_{int(time.time())}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Async ingestion failed: {str(e)}")

async def process_segments_async(segments: List[ChatSegment], cache_manager: SegmentCacheManager):
    """Process segments asynchronously"""
    cached_count = 0
    skipped_count = 0
    
    for segment in segments:
        try:
            segment_dict = segment.dict()
            cache_key = cache_manager.cache_segment(segment_dict)
            
            if cache_key:
                cached_count += 1
            else:
                skipped_count += 1
            
            # Small delay to prevent blocking
            await asyncio.sleep(0.001)
            
        except Exception as e:
            print(f"Error processing segment: {e}")
            skipped_count += 1
    
    print(f"Async ingestion complete: {cached_count} cached, {skipped_count} skipped")

@app.post("/search", response_model=SearchResponse)
async def search_similar_segments(request: SearchRequest):
    """Search for similar segments using RAG"""
    try:
        cache_manager = get_cache_manager()
        
        # Create query segment
        query_segment = {
            'content': request.query,
            'user_id': 'search_user',
            'session_id': 'search_session',
            'timestamp': int(time.time())
        }
        
        # Find similar segments
        similar_segments = cache_manager.find_similar_segments(
            query_segment, 
            k=request.k,
            threshold=request.threshold
        )
        
        results = []
        for vector_id, similarity, metadata in similar_segments:
            cache_key = metadata.get('cache_key', '')
            segment_dict = cache_manager.get_segment(cache_key)
            
            if segment_dict:
                segment = ChatSegment(**segment_dict)
                result = SearchResult(
                    vector_id=vector_id,
                    similarity=similarity,
                    segment=segment,
                    metadata=metadata
                )
                results.append(result)
        
        return SearchResponse(
            results=results,
            total_found=len(results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_cache_stats():
    """Get cache statistics"""
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()
        
        return StatsResponse(stats=stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/clear")
async def clear_cache():
    """Clear all cache data"""
    try:
        cache_manager = get_cache_manager()
        cache_manager.flush()
        
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@app.get("/segment/{cache_key}")
async def get_segment(cache_key: str):
    """Get specific segment by cache key"""
    try:
        cache_manager = get_cache_manager()
        segment = cache_manager.get_segment(cache_key)
        
        if segment:
            return {
                "success": True,
                "segment": segment
            }
        else:
            raise HTTPException(status_code=404, detail=f"Segment with key '{cache_key}' not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segment: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()
        
        return {
            "status": "healthy",
            "cache_manager": "available",
            "stats": {
                "total_requests": stats.get('total_requests', 0),
                "hit_rate": stats.get('hit_rate', 0),
                "cache_size": stats.get('cache_size', 0)
            }
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
