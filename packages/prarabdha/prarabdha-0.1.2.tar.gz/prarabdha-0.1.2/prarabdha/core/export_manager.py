import json
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import os
import pickle
import gzip
from pathlib import Path


class ExportManager:
    """Manages export and import of cache data in various formats."""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def export_to_json(self, export_path: str, include_vectors: bool = True) -> Dict[str, Any]:
        """Export cache data to JSON format."""
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'cache_type': 'prarabdha',
                'version': '1.0'
            },
            'cache_entries': [],
            'vector_data': [],
            'statistics': {}
        }
        
        # Export cache entries
        if hasattr(self.cache_manager, 'get_all_keys'):
            keys = self.cache_manager.get_all_keys()
            for key in keys:
                value = self.cache_manager.get(key)
                if value is not None:
                    entry = {
                        'key': key,
                        'value': value,
                        'exists': True
                    }
                    export_data['cache_entries'].append(entry)
        
        # Export vector data if requested
        if include_vectors and hasattr(self.cache_manager, 'vector_index'):
            vector_data = self._export_vector_data()
            export_data['vector_data'] = vector_data
        
        # Export statistics
        if hasattr(self.cache_manager, 'get_stats'):
            export_data['statistics'] = self.cache_manager.get_stats()
        
        # Write to file
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return export_data
    
    def export_to_parquet(self, export_path: str, include_vectors: bool = True) -> pd.DataFrame:
        """Export cache data to Parquet format."""
        data_rows = []
        
        # Collect cache entries
        if hasattr(self.cache_manager, 'get_all_keys'):
            keys = self.cache_manager.get_all_keys()
            for key in keys:
                value = self.cache_manager.get(key)
                if value is not None:
                    row = {
                        'key': key,
                        'value_type': type(value).__name__,
                        'value_size': len(str(value)),
                        'value': str(value)[:1000],  # Truncate for DataFrame
                        'exists': True
                    }
                    data_rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows)
        
        # Add metadata
        metadata = {
            'export_timestamp': datetime.now().isoformat(),
            'total_entries': len(data_rows),
            'include_vectors': include_vectors
        }
        
        # Write to Parquet with metadata
        df.to_parquet(export_path, index=False, compression='gzip')
        
        # Save metadata separately
        metadata_path = export_path.replace('.parquet', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return df
    
    def export_to_sqlite(self, export_path: str, include_vectors: bool = True) -> None:
        """Export cache data to SQLite database."""
        conn = sqlite3.connect(export_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value_type TEXT,
                value_size INTEGER,
                value_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vector_data (
                vector_id TEXT PRIMARY KEY,
                cache_key TEXT,
                vector_type TEXT,
                dimension INTEGER,
                vector_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cache_key) REFERENCES cache_entries (key)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_metadata (
                id INTEGER PRIMARY KEY,
                export_timestamp TEXT,
                total_entries INTEGER,
                include_vectors BOOLEAN
            )
        ''')
        
        # Export cache entries
        entry_count = 0
        if hasattr(self.cache_manager, 'get_all_keys'):
            keys = self.cache_manager.get_all_keys()
            for key in keys:
                value = self.cache_manager.get(key)
                if value is not None:
                    cursor.execute('''
                        INSERT OR REPLACE INTO cache_entries 
                        (key, value_type, value_size, value_data)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        key,
                        type(value).__name__,
                        len(str(value)),
                        str(value)
                    ))
                    entry_count += 1
        
        # Export vector data if requested
        if include_vectors and hasattr(self.cache_manager, 'vector_index'):
            self._export_vector_data_to_sqlite(cursor)
        
        # Save metadata
        cursor.execute('''
            INSERT INTO export_metadata 
            (export_timestamp, total_entries, include_vectors)
            VALUES (?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            entry_count,
            include_vectors
        ))
        
        conn.commit()
        conn.close()
    
    def export_to_compressed(self, export_path: str, compression_type: str = 'gzip') -> None:
        """Export cache data to compressed format."""
        # Get all data
        export_data = self.export_to_json('temp_export.json', include_vectors=True)
        
        # Compress the JSON data
        with open('temp_export.json', 'rb') as f_in:
            if compression_type == 'gzip':
                with gzip.open(export_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            else:
                # For other compression types, use pickle
                compressed_data = pickle.dumps(export_data)
                with open(export_path, 'wb') as f_out:
                    f_out.write(compressed_data)
        
        # Clean up temp file
        if os.path.exists('temp_export.json'):
            os.remove('temp_export.json')
    
    def import_from_json(self, import_path: str) -> int:
        """Import cache data from JSON format."""
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        imported_count = 0
        
        # Import cache entries
        for entry in import_data.get('cache_entries', []):
            key = entry['key']
            value = entry['value']
            
            if hasattr(self.cache_manager, 'set'):
                self.cache_manager.set(key, value)
                imported_count += 1
        
        # Import vector data if available
        if 'vector_data' in import_data and hasattr(self.cache_manager, 'vector_index'):
            self._import_vector_data(import_data['vector_data'])
        
        return imported_count
    
    def import_from_parquet(self, import_path: str) -> int:
        """Import cache data from Parquet format."""
        df = pd.read_parquet(import_path)
        
        imported_count = 0
        
        for _, row in df.iterrows():
            key = row['key']
            value = row['value']
            
            if hasattr(self.cache_manager, 'set'):
                self.cache_manager.set(key, value)
                imported_count += 1
        
        return imported_count
    
    def import_from_sqlite(self, import_path: str) -> int:
        """Import cache data from SQLite database."""
        conn = sqlite3.connect(import_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        # Import cache entries
        cursor.execute('SELECT key, value_data FROM cache_entries')
        for key, value_data in cursor.fetchall():
            if hasattr(self.cache_manager, 'set'):
                self.cache_manager.set(key, value_data)
                imported_count += 1
        
        # Import vector data if available
        cursor.execute('SELECT * FROM vector_data')
        vector_data = cursor.fetchall()
        if vector_data and hasattr(self.cache_manager, 'vector_index'):
            self._import_vector_data_from_sqlite(vector_data)
        
        conn.close()
        return imported_count
    
    def _export_vector_data(self) -> List[Dict[str, Any]]:
        """Export vector data from vector index."""
        vector_data = []
        
        if hasattr(self.cache_manager.vector_index, 'get_all_vectors'):
            vectors = self.cache_manager.vector_index.get_all_vectors()
            for vector_id, vector_info in vectors.items():
                vector_data.append({
                    'vector_id': vector_id,
                    'metadata': vector_info.get('metadata', {}),
                    'dimension': vector_info.get('dimension', 0),
                    'index_type': vector_info.get('index_type', 'unknown')
                })
        
        return vector_data
    
    def _export_vector_data_to_sqlite(self, cursor) -> None:
        """Export vector data to SQLite."""
        if hasattr(self.cache_manager.vector_index, 'get_all_vectors'):
            vectors = self.cache_manager.vector_index.get_all_vectors()
            for vector_id, vector_info in vectors.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO vector_data 
                    (vector_id, cache_key, vector_type, dimension, vector_data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    vector_id,
                    vector_info.get('cache_key', ''),
                    vector_info.get('vector_type', 'unknown'),
                    vector_info.get('dimension', 0),
                    pickle.dumps(vector_info.get('vector', []))
                ))
    
    def _import_vector_data(self, vector_data: List[Dict[str, Any]]) -> None:
        """Import vector data to vector index."""
        for vector_info in vector_data:
            vector_id = vector_info['vector_id']
            metadata = vector_info.get('metadata', {})
            
            if hasattr(self.cache_manager.vector_index, 'add_vector'):
                # Note: This is a simplified import - actual vector data would need to be reconstructed
                pass
    
    def _import_vector_data_from_sqlite(self, vector_data: List) -> None:
        """Import vector data from SQLite."""
        for vector_row in vector_data:
            vector_id, cache_key, vector_type, dimension, vector_data_blob, created_at = vector_row
            
            if hasattr(self.cache_manager.vector_index, 'add_vector'):
                # Note: This is a simplified import - actual vector data would need to be reconstructed
                pass
    
    def create_backup(self, backup_dir: str, backup_name: Optional[str] = None) -> str:
        """Create a comprehensive backup of cache data."""
        if backup_name is None:
            backup_name = f"prarabdha_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = Path(backup_dir) / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Export in multiple formats
        json_path = backup_path / "cache_data.json"
        parquet_path = backup_path / "cache_data.parquet"
        sqlite_path = backup_path / "cache_data.db"
        compressed_path = backup_path / "cache_data.json.gz"
        
        self.export_to_json(str(json_path))
        self.export_to_parquet(str(parquet_path))
        self.export_to_sqlite(str(sqlite_path))
        self.export_to_compressed(str(compressed_path))
        
        # Create backup manifest
        manifest = {
            'backup_name': backup_name,
            'backup_timestamp': datetime.now().isoformat(),
            'files': [
                str(json_path),
                str(parquet_path),
                str(sqlite_path),
                str(compressed_path)
            ],
            'total_entries': len(self.cache_manager.get_all_keys()) if hasattr(self.cache_manager, 'get_all_keys') else 0
        }
        
        manifest_path = backup_path / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return str(backup_path)
    
    def restore_from_backup(self, backup_path: str, format_type: str = 'json') -> int:
        """Restore cache data from backup."""
        backup_dir = Path(backup_path)
        
        if format_type == 'json':
            import_file = backup_dir / "cache_data.json"
            return self.import_from_json(str(import_file))
        elif format_type == 'parquet':
            import_file = backup_dir / "cache_data.parquet"
            return self.import_from_parquet(str(import_file))
        elif format_type == 'sqlite':
            import_file = backup_dir / "cache_data.db"
            return self.import_from_sqlite(str(import_file))
        else:
            raise ValueError(f"Unsupported format type: {format_type}") 