"""
Pattern loader for algorithm detection patterns.
Loads patterns from JSON files to keep them separate from code.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class PatternLoader:
    """Loads and caches algorithm detection patterns from data files."""
    
    _instance: Optional['PatternLoader'] = None
    _patterns: Optional[Dict[str, Any]] = None
    
    def __new__(cls):
        """Singleton pattern to ensure patterns are loaded only once."""
        if cls._instance is None:
            cls._instance = super(PatternLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the pattern loader."""
        if self._patterns is None:
            self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from JSON file."""
        # Find the data directory relative to this file
        current_dir = Path(__file__).parent
        data_file = current_dir.parent / 'data' / 'algorithm_patterns.json'
        
        # Fallback locations
        if not data_file.exists():
            # Try from package root
            package_root = current_dir.parent
            data_file = package_root / 'data' / 'algorithm_patterns.json'
        
        if not data_file.exists():
            # Try from working directory
            data_file = Path('copycatm/data/algorithm_patterns.json')
        
        if not data_file.exists():
            raise FileNotFoundError(f"Algorithm patterns file not found. Tried: {data_file}")
        
        with open(data_file, 'r') as f:
            self._patterns = json.load(f)
    
    def get_algorithm_patterns(self) -> Dict[str, Any]:
        """Get algorithm detection patterns."""
        if self._patterns is None:
            self._load_patterns()
        return self._patterns.get('algorithm_patterns', {})
    
    def get_type_mapping(self) -> Dict[str, str]:
        """Get algorithm type mappings for normalization."""
        if self._patterns is None:
            self._load_patterns()
        return self._patterns.get('algorithm_type_mapping', {})
    
    def get_function_patterns(self, language: str) -> list:
        """Get function extraction patterns for a specific language."""
        if self._patterns is None:
            self._load_patterns()
        
        function_patterns = self._patterns.get('function_patterns', {})
        lang_patterns = function_patterns.get(language.lower(), {})
        return lang_patterns.get('patterns', [])
    
    def get_pattern_for_algorithm(self, algorithm_type: str, algorithm_name: str) -> Dict[str, Any]:
        """Get specific pattern for an algorithm."""
        patterns = self.get_algorithm_patterns()
        type_patterns = patterns.get(algorithm_type, {})
        return type_patterns.get(algorithm_name, {})
    
    def reload_patterns(self):
        """Force reload of patterns (useful for development)."""
        self._patterns = None
        self._load_patterns()


# Global instance
pattern_loader = PatternLoader()