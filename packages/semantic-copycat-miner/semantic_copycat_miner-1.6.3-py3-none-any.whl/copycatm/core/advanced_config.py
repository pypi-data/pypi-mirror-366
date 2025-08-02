"""
Advanced configuration system with conflict resolution and validation.

This module provides a sophisticated configuration management system that supports
multiple sources, conflict resolution, validation, and dynamic reloading.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import threading
import time

# Try to import watchdog for file monitoring (optional)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes if watchdog not available
    class FileSystemEventHandler:
        pass
    class Observer:
        def __init__(self):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self):
            pass
        def is_alive(self):
            return False
        def schedule(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration sources in priority order."""
    CLI = 1  # Highest priority
    ENV = 2
    USER_FILE = 3
    PROJECT_FILE = 4
    DEFAULT = 5  # Lowest priority


class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    PRIORITY = "priority"  # Use highest priority source
    MERGE = "merge"  # Merge values (for dicts/lists)
    OVERRIDE = "override"  # Complete override
    VALIDATE = "validate"  # Validate compatibility before merge
    CUSTOM = "custom"  # Use custom resolver function


@dataclass
class ConfigValue:
    """Wrapper for configuration values with metadata."""
    value: Any
    source: ConfigSource
    timestamp: float = field(default_factory=time.time)
    validator: Optional[Callable] = None
    resolver: Optional[ConflictResolution] = ConflictResolution.PRIORITY


class ConfigFileWatcher(FileSystemEventHandler):
    """Watch configuration files for changes."""
    
    def __init__(self, config_manager: 'AdvancedConfigManager'):
        self.config_manager = config_manager
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            logger.info(f"Configuration file modified: {event.src_path}")
            self.config_manager.reload_from_file(event.src_path)


class AdvancedConfigManager:
    """
    Advanced configuration manager with multi-source support and conflict resolution.
    
    Features:
    - Multiple configuration sources (CLI, env, files)
    - Conflict resolution strategies
    - Configuration validation
    - Dynamic reloading
    - Per-tier weight configuration
    - Type checking and schema validation
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self._config: Dict[str, ConfigValue] = {}
        self._lock = threading.RLock()
        self._observers: List[Observer] = []
        self._change_callbacks: List[Callable] = []
        self._schema = self._load_schema()
        self._tier_weights = self._default_tier_weights()
        
    def _load_schema(self) -> Dict[str, Any]:
        """Load configuration schema for validation."""
        return {
            'analysis': {
                'complexity_threshold': {'type': int, 'min': 1, 'max': 100, 'default': 3},
                'min_lines': {'type': int, 'min': 1, 'max': 1000, 'default': 20},
                'confidence_threshold': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.0},
                'semantic_threshold': {'type': int, 'min': 10, 'max': 10000, 'default': 50}
            },
            'hashing': {
                'algorithms': {
                    'type': list, 
                    'allowed': ['sha256', 'md5', 'sha1', 'tlsh', 'minhash', 'simhash', 'gnn'],
                    'default': ['sha256', 'tlsh', 'minhash', 'simhash']
                },
                'tlsh_threshold': {'type': int, 'min': 1, 'max': 1000, 'default': 100},
                'lsh_bands': {'type': int, 'min': 1, 'max': 100, 'default': 20}
            },
            'performance': {
                'parallel_workers': {'type': int, 'min': 1, 'max': 64, 'default': None},
                'chunk_size': {'type': int, 'min': 1, 'max': 10000, 'default': 100},
                'memory_limit_mb': {'type': int, 'min': 100, 'max': 100000, 'default': None}
            },
            'tiers': {
                'weights': {
                    'baseline': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.2},
                    'traditional': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.4},
                    'semantic': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.4}
                },
                'thresholds': {
                    'traditional_max_lines': {'type': int, 'min': 1, 'max': 10000, 'default': 50},
                    'semantic_min_lines': {'type': int, 'min': 1, 'max': 10000, 'default': 50}
                }
            },
            'detection': {
                'mutation_similarity_range': {
                    'min': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.7},
                    'max': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.85}
                },
                'unknown_algorithm_threshold': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.6}
            },
            'output': {
                'include_intermediates': {'type': bool, 'default': False},
                'format': {'type': str, 'allowed': ['json', 'csv', 'html'], 'default': 'json'},
                'pretty_print': {'type': bool, 'default': True}
            }
        }
    
    def _default_tier_weights(self) -> Dict[str, float]:
        """Default weights for three-tier analysis."""
        return {
            'baseline': 0.2,
            'traditional': 0.4,
            'semantic': 0.4
        }
    
    def load_from_cli(self, cli_args: Dict[str, Any]) -> None:
        """Load configuration from CLI arguments."""
        with self._lock:
            for key, value in cli_args.items():
                if value is not None:
                    self._set_value(key, value, ConfigSource.CLI)
    
    def load_from_env(self, prefix: str = "COPYCATM_") -> None:
        """Load configuration from environment variables."""
        with self._lock:
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    config_key = key[len(prefix):].lower().replace('_', '.')
                    self._set_value(config_key, self._parse_env_value(value), ConfigSource.ENV)
    
    def load_from_file(self, file_path: Union[str, Path], 
                      source: ConfigSource = ConfigSource.PROJECT_FILE) -> None:
        """Load configuration from JSON file."""
        file_path = Path(file_path)
        if not file_path.exists():
            logger.debug(f"Configuration file not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            with self._lock:
                self._load_nested_config(config_data, source)
            
            # Set up file watching if not already watching
            self._setup_file_watcher(file_path)
            
            logger.info(f"Loaded configuration from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
    
    def _load_nested_config(self, data: Dict[str, Any], source: ConfigSource, 
                           prefix: str = "") -> None:
        """Recursively load nested configuration."""
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict) and not self._is_leaf_value(value):
                self._load_nested_config(value, source, full_key)
            else:
                self._set_value(full_key, value, source)
    
    def _is_leaf_value(self, value: Any) -> bool:
        """Check if a value is a leaf configuration value."""
        # If it has metadata keys, it's a leaf value
        if isinstance(value, dict):
            metadata_keys = {'value', 'validator', 'resolver'}
            return bool(metadata_keys.intersection(value.keys()))
        return True
    
    def _set_value(self, key: str, value: Any, source: ConfigSource) -> None:
        """Set a configuration value with conflict resolution."""
        # Validate the value
        if not self._validate_value(key, value):
            logger.warning(f"Invalid value for {key}: {value}")
            return
        
        # Create config value wrapper
        config_value = ConfigValue(
            value=value,
            source=source,
            validator=self._get_validator(key),
            resolver=self._get_resolver(key)
        )
        
        # Check for conflicts
        if key in self._config:
            resolved_value = self._resolve_conflict(
                key, self._config[key], config_value
            )
            if resolved_value:
                self._config[key] = resolved_value
                self._notify_change(key, resolved_value.value)
        else:
            self._config[key] = config_value
            self._notify_change(key, value)
    
    def _resolve_conflict(self, key: str, existing: ConfigValue, 
                         new: ConfigValue) -> Optional[ConfigValue]:
        """Resolve configuration conflicts."""
        resolver = new.resolver or ConflictResolution.PRIORITY
        
        if resolver == ConflictResolution.PRIORITY:
            # Higher priority wins (lower enum value = higher priority)
            if new.source.value <= existing.source.value:
                return new
            return None
            
        elif resolver == ConflictResolution.OVERRIDE:
            return new
            
        elif resolver == ConflictResolution.MERGE:
            # Merge dictionaries and lists
            if isinstance(existing.value, dict) and isinstance(new.value, dict):
                merged = {**existing.value, **new.value}
                return ConfigValue(merged, new.source)
            elif isinstance(existing.value, list) and isinstance(new.value, list):
                merged = existing.value + new.value
                return ConfigValue(list(set(merged)), new.source)  # Unique values
            else:
                # Can't merge, use priority
                return new if new.source.value <= existing.source.value else None
                
        elif resolver == ConflictResolution.VALIDATE:
            # Validate compatibility
            if self._are_compatible(existing.value, new.value):
                return new if new.source.value <= existing.source.value else None
            else:
                logger.warning(f"Incompatible values for {key}: {existing.value} vs {new.value}")
                return None
                
        return None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        with self._lock:
            parts = key.split('.')
            
            # Direct lookup
            if key in self._config:
                return self._config[key].value
            
            # Nested lookup
            self._config
            for part in parts:
                # Build partial key
                partial_key = '.'.join(parts[:parts.index(part) + 1])
                if partial_key in self._config:
                    value = self._config[partial_key].value
                    # Navigate nested structure
                    remaining_parts = parts[parts.index(part) + 1:]
                    for remaining in remaining_parts:
                        if isinstance(value, dict) and remaining in value:
                            value = value[remaining]
                        else:
                            return default
                    return value
            
            # Check schema for default
            schema_default = self._get_schema_default(key)
            if schema_default is not None:
                return schema_default
            
            return default
    
    def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.CLI) -> None:
        """Set configuration value programmatically."""
        with self._lock:
            self._set_value(key, value, source)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as nested dictionary."""
        with self._lock:
            result = {}
            for key, config_value in self._config.items():
                parts = key.split('.')
                current = result
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = config_value.value
            return result
    
    def get_tier_weights(self) -> Dict[str, float]:
        """Get tier weights for analysis."""
        with self._lock:
            return {
                'baseline': self.get('tiers.weights.baseline', self._tier_weights['baseline']),
                'traditional': self.get('tiers.weights.traditional', self._tier_weights['traditional']),
                'semantic': self.get('tiers.weights.semantic', self._tier_weights['semantic'])
            }
    
    def validate_all(self) -> List[str]:
        """Validate all configuration values."""
        errors = []
        with self._lock:
            for key, config_value in self._config.items():
                if not self._validate_value(key, config_value.value):
                    errors.append(f"Invalid value for {key}: {config_value.value}")
        return errors
    
    def _validate_value(self, key: str, value: Any) -> bool:
        """Validate a configuration value against schema."""
        schema_path = key.split('.')
        schema_node = self._schema
        
        # Navigate to schema definition
        try:
            for part in schema_path:
                if part in schema_node:
                    schema_node = schema_node[part]
                else:
                    # No schema validation for this key
                    return True
        except:
            return True
        
        # Validate type
        if 'type' in schema_node:
            expected_type = schema_node['type']
            if not isinstance(value, expected_type):
                return False
        
        # Validate range
        if 'min' in schema_node and value < schema_node['min']:
            return False
        if 'max' in schema_node and value > schema_node['max']:
            return False
        
        # Validate allowed values
        if 'allowed' in schema_node:
            if isinstance(value, list):
                return all(v in schema_node['allowed'] for v in value)
            else:
                return value in schema_node['allowed']
        
        return True
    
    def _get_validator(self, key: str) -> Optional[Callable]:
        """Get validator function for a key."""
        # Can be extended with custom validators
        return None
    
    def _get_resolver(self, key: str) -> ConflictResolution:
        """Get conflict resolver for a key."""
        # Special resolvers for specific keys
        if key.endswith('.algorithms') or key.endswith('_list'):
            return ConflictResolution.MERGE
        return ConflictResolution.PRIORITY
    
    def _get_schema_default(self, key: str) -> Any:
        """Get default value from schema."""
        schema_path = key.split('.')
        schema_node = self._schema
        
        try:
            for part in schema_path:
                if part in schema_node:
                    schema_node = schema_node[part]
                else:
                    return None
            
            return schema_node.get('default')
        except:
            return None
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value."""
        # Try to parse as JSON
        try:
            return json.loads(value)
        except:
            pass
        
        # Try to parse as boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except:
            pass
        
        # Return as string
        return value
    
    def _are_compatible(self, value1: Any, value2: Any) -> bool:
        """Check if two values are compatible."""
        # Same type
        if type(value1) != type(value2):
            return False
        
        # Numeric compatibility
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            # Check if they're within reasonable range
            return abs(value1 - value2) / max(abs(value1), abs(value2), 1) < 0.5
        
        return True
    
    def _setup_file_watcher(self, file_path: Path) -> None:
        """Set up file watching for configuration changes."""
        if not WATCHDOG_AVAILABLE:
            logger.debug("Watchdog not available, file watching disabled")
            return
            
        # Check if already watching this file
        for observer in self._observers:
            if observer.is_alive() and str(file_path.parent) in str(observer):
                return
        
        observer = Observer()
        handler = ConfigFileWatcher(self)
        observer.schedule(handler, str(file_path.parent), recursive=False)
        observer.start()
        self._observers.append(observer)
    
    def reload_from_file(self, file_path: str) -> None:
        """Reload configuration from a specific file."""
        # Determine source based on file name
        if 'user' in file_path.lower():
            source = ConfigSource.USER_FILE
        else:
            source = ConfigSource.PROJECT_FILE
        
        self.load_from_file(file_path, source)
    
    def register_change_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Register callback for configuration changes."""
        self._change_callbacks.append(callback)
    
    def _notify_change(self, key: str, value: Any) -> None:
        """Notify callbacks of configuration change."""
        for callback in self._change_callbacks:
            try:
                callback(key, value)
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")
    
    def export_config(self, file_path: Union[str, Path], 
                     source_filter: Optional[List[ConfigSource]] = None) -> None:
        """Export current configuration to file."""
        with self._lock:
            config_dict = {}
            
            for key, config_value in self._config.items():
                # Filter by source if specified
                if source_filter and config_value.source not in source_filter:
                    continue
                
                # Build nested structure
                parts = key.split('.')
                current = config_dict
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Include metadata
                current[parts[-1]] = {
                    'value': config_value.value,
                    'source': config_value.source.name,
                    'timestamp': config_value.timestamp
                }
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        # Stop file watchers
        for observer in self._observers:
            if observer.is_alive():
                observer.stop()
                observer.join()
        
        self._observers.clear()
        self._change_callbacks.clear()