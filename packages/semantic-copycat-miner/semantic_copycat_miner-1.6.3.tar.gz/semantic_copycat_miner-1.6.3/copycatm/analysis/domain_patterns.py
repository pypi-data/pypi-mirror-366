"""
Domain-specific pattern configuration loader for algorithm detection.
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class DomainPatternManager:
    """Manages domain-specific patterns including function names, variables, and other identifiers."""
    
    def __init__(self):
        self._patterns: Dict[str, Any] = {}
        self._function_patterns: Dict[str, List[str]] = {}
        self._load_patterns()
    
    def _load_patterns(self):
        """Load all pattern configuration files."""
        patterns_dir = Path(__file__).parent.parent / "data" / "patterns"
        
        # Load function name patterns
        function_names_path = patterns_dir / "domain_function_names.json"
        if function_names_path.exists():
            with open(function_names_path, 'r') as f:
                self._patterns = json.load(f)
                self._build_function_patterns()
    
    def _build_function_patterns(self):
        """Build regex patterns from function names."""
        for domain, algorithms in self._patterns.items():
            for algo_name, patterns in algorithms.items():
                key = f"{domain}.{algo_name}"
                
                # Collect all function names
                all_names = []
                if "function_names" in patterns:
                    all_names.extend(patterns["function_names"])
                
                # Create regex pattern that matches any of the function names
                if all_names:
                    # Escape special regex characters and join with |
                    escaped_names = [re.escape(name) for name in all_names]
                    pattern = r'\b(' + '|'.join(escaped_names) + r')\b'
                    self._function_patterns[key] = pattern
    
    def get_function_pattern(self, domain: str, algorithm: str) -> Optional[str]:
        """Get regex pattern for function names of a specific algorithm."""
        key = f"{domain}.{algorithm}"
        return self._function_patterns.get(key)
    
    def get_all_patterns(self, domain: str, algorithm: str) -> Dict[str, Any]:
        """Get all patterns for a specific algorithm."""
        if domain in self._patterns and algorithm in self._patterns[domain]:
            return self._patterns[domain][algorithm]
        return {}
    
    def check_function_names(self, code: str, domain: str, algorithm: str) -> bool:
        """Check if code contains any of the known function names for an algorithm."""
        pattern = self.get_function_pattern(domain, algorithm)
        if pattern:
            return bool(re.search(pattern, code, re.IGNORECASE))
        return False
    
    def get_matching_functions(self, code: str, domain: str, algorithm: str) -> List[str]:
        """Get list of matching function names found in the code."""
        patterns = self.get_all_patterns(domain, algorithm)
        function_names = patterns.get("function_names", [])
        
        matches = []
        for name in function_names:
            if re.search(r'\b' + re.escape(name) + r'\b', code, re.IGNORECASE):
                matches.append(name)
        
        return matches
    
    def check_variables(self, code: str, domain: str, algorithm: str) -> int:
        """Check how many variable patterns match in the code."""
        patterns = self.get_all_patterns(domain, algorithm)
        matches = 0
        
        # Check variable names
        for var_name in patterns.get("variable_names", []):
            if re.search(r'\b' + re.escape(var_name) + r'\b', code, re.IGNORECASE):
                matches += 1
        
        # Check variable patterns (regex)
        for var_pattern in patterns.get("variable_patterns", []):
            if re.search(var_pattern, code):
                matches += 1
        
        return matches
    
    def check_all_identifiers(self, code: str, domain: str, algorithm: str) -> Dict[str, int]:
        """Check all types of identifiers and return match counts."""
        patterns = self.get_all_patterns(domain, algorithm)
        results = {
            "function_names": 0,
            "variable_names": 0,
            "buffer_names": 0,
            "table_names": 0,
            "constant_names": 0,
            "context_names": 0,
            "parameter_names": 0,
            "mode_names": 0,
            "kernel_names": 0
        }
        
        # Check each type of identifier
        for identifier_type in results.keys():
            if identifier_type in patterns:
                for name in patterns[identifier_type]:
                    if re.search(r'\b' + re.escape(name) + r'\b', code, re.IGNORECASE):
                        results[identifier_type] += 1
        
        # Check variable patterns separately
        variable_pattern_matches = 0
        for var_pattern in patterns.get("variable_patterns", []):
            if re.search(var_pattern, code):
                variable_pattern_matches += 1
        
        results["variable_patterns"] = variable_pattern_matches
        
        return results


# Singleton instance
_pattern_manager = None

def get_pattern_manager() -> DomainPatternManager:
    """Get the singleton pattern manager instance."""
    global _pattern_manager
    if _pattern_manager is None:
        _pattern_manager = DomainPatternManager()
    return _pattern_manager