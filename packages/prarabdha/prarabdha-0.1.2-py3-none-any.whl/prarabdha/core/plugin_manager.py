import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable, Type
from abc import ABC, abstractmethod
import json
import os
from pathlib import Path


class VectorEncoder(ABC):
    """Abstract base class for vector encoders."""
    
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """Encode text into vector representation."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the encoded vectors."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the encoder."""
        pass


class DefaultVectorEncoder(VectorEncoder):
    """Default vector encoder using simple hash-based approach."""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
    
    def encode(self, text: str) -> List[float]:
        """Simple hash-based encoding for demonstration."""
        import hashlib
        import numpy as np
        
        # Create a hash of the text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to vector
        vector = []
        for i in range(self.dimension):
            byte_index = i % len(hash_bytes)
            vector.append(float(hash_bytes[byte_index]) / 255.0)
        
        return vector
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_name(self) -> str:
        return "default_hash_encoder"


class PluginManager:
    """Manages plugins for custom vector encoders and other extensible components."""
    
    def __init__(self, plugin_dir: Optional[str] = None):
        self.plugin_dir = plugin_dir or "plugins"
        self.plugins: Dict[str, Any] = {}
        self.encoders: Dict[str, VectorEncoder] = {}
        self.loaded_modules: Dict[str, Any] = {}
        
        # Register default encoder
        self.register_encoder("default", DefaultVectorEncoder())
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugin directory."""
        plugin_path = Path(self.plugin_dir)
        if not plugin_path.exists():
            return []
        
        plugins = []
        for item in plugin_path.iterdir():
            if item.is_file() and item.suffix == '.py':
                plugins.append(item.stem)
            elif item.is_dir() and (item / '__init__.py').exists():
                plugins.append(item.name)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name."""
        try:
            # Try to load from plugin directory first
            plugin_path = Path(self.plugin_dir) / f"{plugin_name}.py"
            if plugin_path.exists():
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Try to import as a regular module
                module = importlib.import_module(plugin_name)
            
            self.loaded_modules[plugin_name] = module
            
            # Look for vector encoders in the module
            self._discover_encoders(module, plugin_name)
            
            # Look for other plugin components
            self._discover_components(module, plugin_name)
            
            return True
            
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def _discover_encoders(self, module: Any, plugin_name: str) -> None:
        """Discover vector encoders in a module."""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, VectorEncoder) and 
                obj != VectorEncoder):
                
                try:
                    encoder = obj()
                    encoder_name = f"{plugin_name}.{encoder.get_name()}"
                    self.register_encoder(encoder_name, encoder)
                except Exception as e:
                    print(f"Failed to instantiate encoder {name}: {e}")
    
    def _discover_components(self, module: Any, plugin_name: str) -> None:
        """Discover other plugin components."""
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, '__plugin_type__'):
                component_type = getattr(obj, '__plugin_type__')
                component_name = f"{plugin_name}.{name}"
                self.plugins[component_name] = obj
    
    def register_encoder(self, name: str, encoder: VectorEncoder) -> None:
        """Register a vector encoder."""
        self.encoders[name] = encoder
    
    def get_encoder(self, name: str) -> Optional[VectorEncoder]:
        """Get a vector encoder by name."""
        return self.encoders.get(name)
    
    def list_encoders(self) -> List[str]:
        """List all available encoders."""
        return list(self.encoders.keys())
    
    def create_encoder(self, name: str, **kwargs) -> Optional[VectorEncoder]:
        """Create an encoder instance by name with parameters."""
        encoder_class = self.encoders.get(name)
        if encoder_class and inspect.isclass(encoder_class):
            return encoder_class(**kwargs)
        return encoder_class
    
    def encode_text(self, text: str, encoder_name: str = "default") -> List[float]:
        """Encode text using specified encoder."""
        encoder = self.get_encoder(encoder_name)
        if encoder is None:
            raise ValueError(f"Encoder '{encoder_name}' not found")
        
        return encoder.encode(text)
    
    def get_encoder_info(self, name: str) -> Dict[str, Any]:
        """Get information about an encoder."""
        encoder = self.get_encoder(name)
        if encoder is None:
            return {}
        
        return {
            'name': encoder.get_name(),
            'dimension': encoder.get_dimension(),
            'type': type(encoder).__name__
        }
    
    def list_plugins(self) -> List[str]:
        """List all loaded plugins."""
        return list(self.loaded_modules.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """Get information about a plugin."""
        module = self.loaded_modules.get(plugin_name)
        if module is None:
            return {}
        
        encoders = [name for name, encoder in self.encoders.items() 
                   if name.startswith(f"{plugin_name}.")]
        
        return {
            'name': plugin_name,
            'module': module.__name__,
            'encoders': encoders,
            'components': [name for name in self.plugins.keys() 
                         if name.startswith(f"{plugin_name}.")]
        }


class PluginDecorator:
    """Decorator for marking plugin components."""
    
    def __init__(self, plugin_type: str):
        self.plugin_type = plugin_type
    
    def __call__(self, cls):
        """Mark a class as a plugin component."""
        cls.__plugin_type__ = self.plugin_type
        return cls


# Example plugin components
@PluginDecorator("cache_strategy")
class CustomCacheStrategy:
    """Example custom cache strategy plugin."""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    def should_cache(self, key: str, value: Any) -> bool:
        """Determine if a value should be cached."""
        return True
    
    def get_ttl(self, key: str, value: Any) -> Optional[int]:
        """Get TTL for a cache entry."""
        return 3600  # 1 hour


@PluginDecorator("compression")
class CustomCompression:
    """Example custom compression plugin."""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    def compress(self, data: Any) -> bytes:
        """Compress data."""
        import pickle
        return pickle.dumps(data)
    
    def decompress(self, data: bytes) -> Any:
        """Decompress data."""
        import pickle
        return pickle.loads(data)


# Example vector encoder plugin
class ExampleVectorEncoder(VectorEncoder):
    """Example vector encoder plugin."""
    
    def __init__(self, dimension: int = 512):
        self.dimension = dimension
    
    def encode(self, text: str) -> List[float]:
        """Simple character-based encoding."""
        import numpy as np
        
        # Create a simple character frequency vector
        vector = [0.0] * self.dimension
        
        for i, char in enumerate(text):
            char_code = ord(char)
            vector[i % self.dimension] += char_code / 255.0
        
        # Normalize
        total = sum(vector)
        if total > 0:
            vector = [v / total for v in vector]
        
        return vector
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_name(self) -> str:
        return "example_encoder"


# Plugin configuration
class PluginConfig:
    """Configuration for plugin management."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "plugin_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load plugin configuration from file."""
        if not os.path.exists(self.config_file):
            return {
                'plugins': [],
                'encoders': {
                    'default': 'default'
                },
                'auto_load': True
            }
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self) -> None:
        """Save plugin configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_plugin(self, plugin_name: str) -> None:
        """Add a plugin to the configuration."""
        if plugin_name not in self.config['plugins']:
            self.config['plugins'].append(plugin_name)
            self.save_config()
    
    def remove_plugin(self, plugin_name: str) -> None:
        """Remove a plugin from the configuration."""
        if plugin_name in self.config['plugins']:
            self.config['plugins'].remove(plugin_name)
            self.save_config()
    
    def set_default_encoder(self, encoder_name: str) -> None:
        """Set the default encoder."""
        self.config['encoders']['default'] = encoder_name
        self.save_config()
    
    def get_default_encoder(self) -> str:
        """Get the default encoder name."""
        return self.config['encoders'].get('default', 'default') 