"""
Pattern booster for enhanced algorithm detection.

This module provides additional pattern recognition for specific algorithm
families to boost cross-language similarity detection.
"""

import re
from typing import List, Dict, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)


class AlgorithmPatternBooster:
    """Boost pattern detection for specific algorithm families."""
    
    def __init__(self):
        """Initialize pattern booster with algorithm-specific patterns."""
        self.divide_conquer_patterns = {
            'quicksort': {
                'required': ['partition'],  # Only require partition
                'patterns': [
                    r'if.*<.*high',
                    r'if.*low.*<',
                    r'partition',
                    r'pivot',
                    r'low.*high',
                    r'quicksort',
                    r'sort.*low.*pivot',
                    r'sort.*pivot.*high'
                ],
                'boost_factor': 1.2
            },
            'mergesort': {
                'required': ['merge', 'recursive'],
                'patterns': [
                    r'if.*<.*right',
                    r'mid.*=.*\(.*\+.*\).*/',
                    r'merge\s*\(',
                    r'left.*mid',
                    r'mid.*right'
                ],
                'boost_factor': 1.15
            }
        }
        
    def detect_algorithm_family(self, code: str, ast_sequence: List[str]) -> Dict[str, float]:
        """Detect algorithm family from code and AST sequence."""
        code_lower = code.lower()
        detected = {}
        
        # Check divide and conquer patterns
        for algo, config in self.divide_conquer_patterns.items():
            score = 0.0
            
            # Check required elements
            required_found = all(req in code_lower for req in config['required'])
            if not required_found:
                continue
                
            # Check patterns
            pattern_matches = 0
            for pattern in config['patterns']:
                if re.search(pattern, code_lower):
                    pattern_matches += 1
                    
            if pattern_matches >= 2:  # At least 2 patterns
                score = config['boost_factor']
                detected[algo] = score
                
        # Additional AST-based detection
        if ast_sequence:
            ast_str = ' '.join(ast_sequence)
            
            # Quicksort specific
            if all(pattern in ast_str for pattern in ['CALL:PARTITION', 'RECURSIVE', 'VAR:PIVOT']):
                detected['quicksort'] = max(detected.get('quicksort', 0), 1.25)
                
            # Merge sort specific  
            if all(pattern in ast_str for pattern in ['CALL:MERGE', 'RECURSIVE', 'BINARY_OP:DIV']):
                detected['mergesort'] = max(detected.get('mergesort', 0), 1.2)
                
        return detected
    
    def boost_graph_patterns(self, graph_patterns: Dict[str, int], 
                           algorithm_family: str) -> Dict[str, int]:
        """Boost graph patterns based on detected algorithm family."""
        if algorithm_family == 'quicksort':
            # Boost quicksort-specific patterns
            boost_patterns = {
                'CALL_PARTITION': 3,
                'PIVOT_COMPARE': 3,
                'RECURSIVE_SORT': 2,
                'COND->BINOP': 2,
                'LOOP->BINOP': 2
            }
            
            for pattern, boost in boost_patterns.items():
                if pattern in graph_patterns:
                    graph_patterns[pattern] *= boost
                else:
                    # Add synthetic patterns if algorithm detected
                    graph_patterns[pattern] = boost
                    
        elif algorithm_family == 'mergesort':
            boost_patterns = {
                'CALL_MERGE': 3,
                'RECURSIVE_SORT': 2,
                'BINARY_OP:DIV': 2
            }
            
            for pattern, boost in boost_patterns.items():
                if pattern in graph_patterns:
                    graph_patterns[pattern] *= boost
                    
        return graph_patterns
    
    def boost_embedding_patterns(self, patterns: List[str], 
                               algorithm_family: str) -> List[str]:
        """Boost embedding patterns based on detected algorithm family."""
        boosted = patterns.copy()
        
        if algorithm_family == 'quicksort':
            # Add synthetic quicksort patterns
            quicksort_boost = [
                'PARTITION_CALL', 'PIVOT_COMPARE', 'RECURSIVE_SORT',
                'PARTITION_CALL', 'PIVOT_COMPARE'  # Duplicate for emphasis
            ]
            boosted.extend(quicksort_boost)
            
        elif algorithm_family == 'mergesort':
            merge_boost = [
                'MERGE_CALL', 'RECURSIVE_SORT', 'DIVIDE_CONQUER'
            ]
            boosted.extend(merge_boost)
            
        return boosted