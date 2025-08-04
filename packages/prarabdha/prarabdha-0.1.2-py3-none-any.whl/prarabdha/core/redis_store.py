import redis
import json
import hashlib
from typing import Any, Dict, Optional, List
import threading

class RedisKVStore:
    """Redis-backed KV store with TTL support and auto-sharding"""
    
    def __init__(self, 
                 namespace: str = "default", 
                 ttl_seconds: Optional[int] = None, 
                 redis_config: Optional[Dict] = None,
                 shard_count: int = 1):
        self.namespace = namespace
        self.ttl = ttl_seconds
        self.redis_config = redis_config or {}
        self.shard_count = shard_count
        self.lock = threading.RLock()
        
        # Initialize Redis connections
        if shard_count == 1:
            self.clients = [redis.Redis(**self.redis_config)]
        else:
            # For multiple shards, we'll use different databases or different Redis instances
            self.clients = []
            for i in range(shard_count):
                config = self.redis_config.copy()
                if 'db' in config:
                    config['db'] = (config['db'] + i) % 16  # Redis supports 0-15 databases
                self.clients.append(redis.Redis(**config))
    
    def _get_shard(self, key: str) -> redis.Redis:
        """Get the appropriate Redis client for a given key"""
        if self.shard_count == 1:
            return self.clients[0]
        
        # Use consistent hashing for sharding
        key_hash = hashlib.md5(key.encode()).hexdigest()
        shard_index = int(key_hash, 16) % self.shard_count
        return self.clients[shard_index]
    
    def _full_key(self, key: str) -> str:
        """Generate full key with namespace"""
        return f"{self.namespace}:{key}"
    
    def set(self, key: str, value: Any):
        """Set a key-value pair with optional TTL"""
        full_key = self._full_key(key)
        client = self._get_shard(key)
        
        try:
            serialized_value = json.dumps(value, default=str)
            if self.ttl:
                client.setex(full_key, self.ttl, serialized_value)
            else:
                client.set(full_key, serialized_value)
        except (redis.RedisError, TypeError) as e:
            # Fallback to string representation if JSON serialization fails
            serialized_value = str(value)
            if self.ttl:
                client.setex(full_key, self.ttl, serialized_value)
            else:
                client.set(full_key, serialized_value)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        full_key = self._full_key(key)
        client = self._get_shard(key)
        
        try:
            val = client.get(full_key)
            if val is None:
                return None
            
            # Try to deserialize as JSON first
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                # Return as string if JSON deserialization fails
                return val.decode('utf-8') if isinstance(val, bytes) else val
        except redis.RedisError:
            return None
    
    def exists(self, key: str) -> bool:
        """Check if a key exists"""
        full_key = self._full_key(key)
        client = self._get_shard(key)
        
        try:
            return client.exists(full_key) > 0
        except redis.RedisError:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        full_key = self._full_key(key)
        client = self._get_shard(key)
        
        try:
            return client.delete(full_key) > 0
        except redis.RedisError:
            return False
    
    def flush(self):
        """Flush all keys in the namespace"""
        with self.lock:
            for client in self.clients:
                try:
                    # Get all keys in the namespace
                    pattern = f"{self.namespace}:*"
                    keys = client.keys(pattern)
                    if keys:
                        client.delete(*keys)
                except redis.RedisError:
                    continue
    
    def get_all_keys(self) -> List[str]:
        """Get all keys in the namespace"""
        all_keys = []
        for client in self.clients:
            try:
                pattern = f"{self.namespace}:*"
                keys = client.keys(pattern)
                # Remove namespace prefix
                keys = [k.decode('utf-8').replace(f"{self.namespace}:", "") 
                       for k in keys if isinstance(k, bytes)]
                all_keys.extend(keys)
            except redis.RedisError:
                continue
        return all_keys
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "namespace": self.namespace,
            "shard_count": self.shard_count,
            "ttl_seconds": self.ttl,
        }
        
        total_keys = 0
        total_memory = 0
        
        for i, client in enumerate(self.clients):
            try:
                pattern = f"{self.namespace}:*"
                keys = client.keys(pattern)
                shard_keys = len(keys)
                total_keys += shard_keys
                
                # Try to get memory usage (Redis 4.0+)
                try:
                    info = client.info('memory')
                    memory_usage = info.get('used_memory', 0)
                    total_memory += memory_usage
                except:
                    pass
                
                stats[f"shard_{i}_keys"] = shard_keys
            except redis.RedisError:
                stats[f"shard_{i}_keys"] = 0
        
        stats["total_keys"] = total_keys
        stats["total_memory_bytes"] = total_memory
        
        return stats
    
    def ping(self) -> bool:
        """Test Redis connectivity"""
        try:
            for client in self.clients:
                client.ping()
            return True
        except redis.RedisError:
            return False
    
    def set_eviction_policy(self, policy: str):
        """Set Redis eviction policy (requires Redis 2.8+)"""
        valid_policies = [
            'volatile-lru', 'allkeys-lru', 'volatile-lfu', 
            'allkeys-lfu', 'volatile-random', 'allkeys-random', 
            'volatile-ttl', 'noeviction'
        ]
        
        if policy not in valid_policies:
            raise ValueError(f"Invalid eviction policy. Must be one of: {valid_policies}")
        
        for client in self.clients:
            try:
                client.config_set('maxmemory-policy', policy)
            except redis.RedisError as e:
                print(f"Warning: Could not set eviction policy: {e}")
    
    def set_memory_limit(self, max_memory: str):
        """Set Redis memory limit (e.g., '256mb', '1gb')"""
        for client in self.clients:
            try:
                client.config_set('maxmemory', max_memory)
            except redis.RedisError as e:
                print(f"Warning: Could not set memory limit: {e}")
