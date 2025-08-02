"""
Enhanced algorithm detector with transformation resistance.

This detector uses AST normalization and structural pattern matching
to detect algorithms even when variables and functions are renamed.
"""

import logging
from typing import Dict, List, Any, Optional

from .algorithm_detector import AlgorithmDetector
from .ast_normalizer import ASTNormalizer
from .pseudocode_normalizer import PseudocodeNormalizer
from .control_block_extractor import ControlBlockExtractor
from ..core.config import AnalysisConfig

logger = logging.getLogger(__name__)


class EnhancedAlgorithmDetector(AlgorithmDetector):
    """
    Enhanced algorithm detector with transformation resistance.
    
    Uses multiple techniques:
    1. AST structural pattern matching
    2. Control flow graph analysis
    3. Pseudocode normalization
    4. Mathematical invariant matching
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize enhanced detector with transformation-resistant components."""
        super().__init__(config)
        
        # Initialize transformation-resistant components
        self.ast_normalizer = ASTNormalizer()
        self.pseudocode_normalizer = PseudocodeNormalizer()
        self.control_extractor = ControlBlockExtractor()
        
        # Define structural patterns for algorithms (name-independent)
        self.structural_patterns = self._init_structural_patterns()
        
    def _init_structural_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize structural patterns for common algorithms."""
        return {
            'quicksort': {
                'control_flow': ['FUNCTION', 'CONDITION', 'RECURSIVE_CALL', 'RECURSIVE_CALL'],
                'recursion_pattern': True,
                'has_partition': True,
                'depth_pattern': 'divide_conquer',
                'invariants': ['comparison', 'swap', 'array_access'],
                'complexity_range': (10, 50)  # Typical complexity range
            },
            'binary_search': {
                'control_flow': ['FUNCTION', 'LOOP', 'CONDITION', 'ASSIGNMENT'],
                'loop_pattern': 'while',
                'has_midpoint': True,
                'invariants': ['comparison', 'division', 'bounds_check'],
                'complexity_range': (5, 20)
            },
            'bubble_sort': {
                'control_flow': ['FUNCTION', 'LOOP', 'LOOP', 'CONDITION', 'SWAP'],
                'nested_loops': 2,
                'swap_pattern': True,
                'invariants': ['comparison', 'swap', 'iteration'],
                'complexity_range': (8, 25)
            },
            'merge_sort': {
                'control_flow': ['FUNCTION', 'CONDITION', 'RECURSIVE_CALL', 'MERGE'],
                'recursion_pattern': True,
                'has_merge': True,
                'depth_pattern': 'divide_conquer',
                'invariants': ['comparison', 'array_split', 'merge'],
                'complexity_range': (15, 60)
            }
        }
    
    def detect_algorithms(self, ast_tree: Any, language: str, 
                         file_lines: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Detect algorithms using transformation-resistant techniques.
        
        Overrides parent method to add structural analysis.
        """
        detected_algorithms = []
        
        # First, try traditional detection for quick matches
        traditional_results = super().detect_algorithms(ast_tree, language, file_lines)
        detected_algorithms.extend(traditional_results)
        
        # If no algorithms detected, use enhanced structural analysis
        if not detected_algorithms and hasattr(self, 'content') and self.content:
            logger.debug("No algorithms detected with traditional method, trying structural analysis")
            structural_results = self._detect_with_structural_analysis(
                ast_tree, language, self.content
            )
            detected_algorithms.extend(structural_results)
        
        return detected_algorithms
    
    def _detect_with_structural_analysis(self, ast_tree: Any, language: str, 
                                       content: str) -> List[Dict[str, Any]]:
        """Detect algorithms using structural pattern matching."""
        detected = []
        
        try:
            # 1. Extract control flow patterns
            control_blocks = self.control_extractor.extract_control_blocks(ast_tree, language)
            control_flow_pattern = self._extract_control_flow_pattern(control_blocks)
            
            # 2. Generate pseudocode representation
            pseudocode = self.pseudocode_normalizer.to_pseudocode(ast_tree, language)
            
            # 3. Extract structural features
            structural_features = self._extract_structural_features(ast_tree, control_blocks)
            
            # 4. Match against structural patterns
            for algo_name, pattern in self.structural_patterns.items():
                confidence = self._match_structural_pattern(
                    pattern, control_flow_pattern, structural_features, pseudocode
                )
                
                if confidence > 0.5:  # Threshold for structural match
                    algo_type = self._get_algorithm_type(algo_name)
                    detected.append({
                        'algorithm_type': algo_type,
                        'algorithm_subtype': algo_name,
                        'confidence': confidence,
                        'detection_method': 'structural_analysis',
                        'evidence': {
                            'control_flow_match': control_flow_pattern,
                            'structural_features': structural_features,
                            'transformation_resistant': True
                        },
                        'location': {'start': 1, 'end': len(content.split('\n'))},
                        'function_name': 'unknown_transformed'
                    })
                    
        except Exception as e:
            logger.warning(f"Structural analysis failed: {e}")
            
        return detected
    
    def _extract_control_flow_pattern(self, control_blocks: List[Dict[str, Any]]) -> List[str]:
        """Extract control flow pattern from control blocks."""
        pattern = []
        
        # Sort blocks by location
        sorted_blocks = sorted(control_blocks, 
                             key=lambda b: b['location']['start_line'])
        
        for block in sorted_blocks:
            block_type = block['type'].upper()
            if block_type == 'IF_STATEMENT':
                pattern.append('CONDITION')
            elif block_type in ['FOR_LOOP', 'WHILE_LOOP']:
                pattern.append('LOOP')
            elif block_type == 'FUNCTION_CALL':
                # Check if it's recursive
                if self._is_recursive_call(block):
                    pattern.append('RECURSIVE_CALL')
                else:
                    pattern.append('CALL')
                    
        return pattern
    
    def _extract_structural_features(self, ast_tree: Any, 
                                   control_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract structural features from AST and control blocks."""
        features = {
            'has_recursion': False,
            'has_loops': False,
            'nested_loops': 0,
            'has_conditionals': False,
            'has_array_access': False,
            'has_swaps': False,
            'has_comparisons': False,
            'complexity_score': 0,
            'depth_pattern': None
        }
        
        # Analyze control blocks
        loop_count = 0
        max_nesting = 0
        
        for block in control_blocks:
            block_type = block['type']
            
            if 'loop' in block_type:
                features['has_loops'] = True
                loop_count += 1
                
            if block_type == 'if_statement':
                features['has_conditionals'] = True
                
            # Check nesting
            nesting = block.get('nested_structures', {}).get('max_depth', 0)
            max_nesting = max(max_nesting, nesting)
            
            # Check for recursive patterns
            if 'RECURSIVE' in str(block.get('normalized_code', '')):
                features['has_recursion'] = True
        
        features['nested_loops'] = min(loop_count, max_nesting)
        features['complexity_score'] = len(control_blocks) + max_nesting * 2
        
        # Check for common patterns in the AST
        ast_text = str(ast_tree) if hasattr(ast_tree, '__str__') else ''
        features['has_array_access'] = '[' in ast_text and ']' in ast_text
        features['has_swaps'] = ast_text.count('=') >= 2  # Simple swap detection
        features['has_comparisons'] = any(op in ast_text for op in ['<', '>', '<=', '>=', '=='])
        
        # Determine depth pattern
        if features['has_recursion'] and features['has_conditionals']:
            features['depth_pattern'] = 'divide_conquer'
        elif features['nested_loops'] >= 2:
            features['depth_pattern'] = 'nested_iteration'
            
        return features
    
    def _match_structural_pattern(self, pattern: Dict[str, Any], 
                                control_flow: List[str], 
                                features: Dict[str, Any],
                                pseudocode: str) -> float:
        """Match structural pattern and return confidence score."""
        score = 0.0
        matches = 0
        checks = 0
        
        # Check control flow pattern
        if 'control_flow' in pattern:
            checks += 1
            expected_flow = pattern['control_flow']
            if self._fuzzy_match_sequence(expected_flow, control_flow):
                matches += 1
                score += 0.3
        
        # Check recursion
        if 'recursion_pattern' in pattern:
            checks += 1
            if pattern['recursion_pattern'] == features['has_recursion']:
                matches += 1
                score += 0.2
        
        # Check loops
        if 'nested_loops' in pattern:
            checks += 1
            if features['nested_loops'] >= pattern['nested_loops']:
                matches += 1
                score += 0.15
        
        # Check complexity range
        if 'complexity_range' in pattern:
            checks += 1
            min_c, max_c = pattern['complexity_range']
            if min_c <= features['complexity_score'] <= max_c:
                matches += 1
                score += 0.1
        
        # Check specific patterns
        if 'has_partition' in pattern and pattern['has_partition']:
            checks += 1
            # Look for partition-like behavior in pseudocode
            if 'SWAP' in pseudocode and 'COMPARE' in pseudocode:
                matches += 1
                score += 0.15
        
        if 'has_midpoint' in pattern and pattern['has_midpoint']:
            checks += 1
            # Look for midpoint calculation
            if 'DIV' in pseudocode or '//' in pseudocode or '/ 2' in pseudocode:
                matches += 1
                score += 0.1
        
        # Adjust score based on match ratio
        if checks > 0:
            match_ratio = matches / checks
            score = score * (0.5 + 0.5 * match_ratio)
        
        return min(score, 1.0)
    
    def _fuzzy_match_sequence(self, expected: List[str], actual: List[str]) -> bool:
        """Fuzzy match for control flow sequences."""
        if not expected or not actual:
            return False
            
        # Allow some flexibility in matching
        expected_set = set(expected)
        actual_set = set(actual)
        
        # Check if most expected elements are present
        intersection = expected_set.intersection(actual_set)
        return len(intersection) >= len(expected_set) * 0.7
    
    def _is_recursive_call(self, block: Dict[str, Any]) -> bool:
        """Check if a function call is recursive."""
        # Simple heuristic - would need more context for accuracy
        return 'recursive' in str(block.get('normalized_code', '')).lower()
    
    def _get_algorithm_type(self, algo_name: str) -> str:
        """Map algorithm name to type."""
        type_mapping = {
            'quicksort': 'sorting_algorithm',
            'bubble_sort': 'sorting_algorithm',
            'merge_sort': 'sorting_algorithm',
            'binary_search': 'search_algorithm',
            'linear_search': 'search_algorithm'
        }
        return type_mapping.get(algo_name, 'unknown_algorithm')