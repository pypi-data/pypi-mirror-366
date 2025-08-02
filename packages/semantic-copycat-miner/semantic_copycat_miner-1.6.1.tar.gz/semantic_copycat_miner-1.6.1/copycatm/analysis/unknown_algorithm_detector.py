"""
Unknown algorithm detector using structural complexity analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import uuid4

from .structural_complexity import StructuralComplexityAnalyzer
from .algorithm_types import AlgorithmType

logger = logging.getLogger(__name__)


class UnknownAlgorithmDetector:
    """Detects unknown complex algorithms through structural analysis."""
    
    # New algorithm type for unknown complex algorithms
    UNKNOWN_COMPLEX_ALGORITHM = "unknown_complex_algorithm"
    
    def __init__(self, min_complexity_score: float = 0.6):
        """
        Initialize unknown algorithm detector.
        
        Args:
            min_complexity_score: Minimum complexity score to classify as unknown algorithm
        """
        self.structural_analyzer = StructuralComplexityAnalyzer()
        self.min_complexity_score = min_complexity_score
    
    def detect_unknown_algorithms(self, ast_tree: Any, language: str, 
                                file_lines: int) -> List[Dict[str, Any]]:
        """
        Detect unknown complex algorithms in code.
        
        Args:
            ast_tree: Parsed AST
            language: Programming language
            file_lines: Total lines in file (for performance optimization)
            
        Returns:
            List of detected unknown algorithms
        """
        # Skip structural analysis for small files (performance optimization)
        if file_lines and file_lines < 50:
            return []
        
        try:
            # Perform structural complexity analysis
            analysis = self.structural_analyzer.analyze_complexity(ast_tree, language)
            
            if not analysis['complex_functions']:
                return []
            
            # Convert complex functions to algorithm entries
            algorithms = []
            for func in analysis['functions']:
                if func['is_complex'] and func['complexity_score'] >= self.min_complexity_score:
                    algorithm = self._create_algorithm_entry(func, analysis, language)
                    algorithms.append(algorithm)
            
            return algorithms
            
        except Exception as e:
            logger.debug(f"Unknown algorithm detection failed: {e}")
            return []
    
    def _create_algorithm_entry(self, func: Dict[str, Any], 
                              analysis: Dict[str, Any], 
                              language: str) -> Dict[str, Any]:
        """Create algorithm entry for unknown complex algorithm."""
        # Generate unique ID
        algo_id = f"unknown_{uuid4().hex[:8]}"
        
        # Create evidence based on structural analysis
        evidence = {
            'complexity_score': func['complexity_score'],
            'cyclomatic_complexity': func['metrics']['cyclomatic_complexity'],
            'nesting_depth': func['metrics']['nesting_depth'],
            'operation_density': func['metrics']['operation_density'],
            'unique_operations': len(func['metrics']['unique_operations']),
            'structural_hash': func['structural_hash'],
            'detected_patterns': [
                f"pattern: {' '.join(pattern)}" 
                for pattern, _ in func['operation_ngrams'][:5]
            ],
            'algorithmic_fingerprint': analysis['algorithmic_fingerprint']
        }
        
        # Calculate confidence based on complexity metrics
        confidence = self._calculate_confidence(func)
        
        # Determine subtype based on dominant patterns
        subtype = self._determine_subtype(func['metrics'])
        
        return {
            'id': algo_id,
            'algorithm_type': self.UNKNOWN_COMPLEX_ALGORITHM,
            'subtype_classification': subtype,
            'function_name': func['name'],
            'confidence_score': confidence,
            'lines': {
                'start': func.get('start_line', 0),
                'end': func.get('end_line', 0),
                'total': func['lines']
            },
            'evidence': evidence,
            'transformation_resistance': {
                'structural_hash': 0.9,  # High resistance due to structural analysis
                'operation_patterns': 0.85,
                'complexity_metrics': 0.95
            },
            'metrics': {
                'complexity': func['complexity_score'],
                'operations': len(func['metrics']['unique_operations']),
                'patterns': len(func['operation_ngrams'])
            }
        }
    
    def _calculate_confidence(self, func: Dict[str, Any]) -> float:
        """Calculate confidence score for unknown algorithm detection."""
        score = func['complexity_score']
        
        # Boost confidence for very complex functions
        if func['metrics']['cyclomatic_complexity'] > 15:
            score = min(1.0, score + 0.1)
        
        # Boost for deep nesting
        if func['metrics']['nesting_depth'] > 5:
            score = min(1.0, score + 0.05)
        
        # Boost for many unique operations
        if len(func['metrics']['unique_operations']) > 20:
            score = min(1.0, score + 0.1)
        
        return round(score, 2)
    
    def _determine_subtype(self, metrics: Dict[str, Any]) -> str:
        """Determine subtype based on structural patterns."""
        # Analyze dominant characteristics
        loop_score = sum(metrics['loop_complexity'].values())
        conditional_score = sum(metrics['conditional_complexity'].values())
        data_flow_score = sum([
            metrics['data_flow_complexity']['assignments'],
            metrics['data_flow_complexity']['array_accesses']
        ])
        
        # Computational primitive analysis
        primitives = metrics['computational_primitives']
        
        # Determine subtype based on dominant patterns
        if loop_score > 5 and metrics['loop_complexity']['nested_loops'] > 0:
            return "complex_iteration_pattern"
        elif primitives.get('bitwise', 0) > 10:
            return "bitwise_manipulation_algorithm"
        elif primitives.get('arithmetic', 0) > 20:
            return "mathematical_computation"
        elif conditional_score > 10:
            return "complex_decision_logic"
        elif data_flow_score > 15:
            return "data_transformation_algorithm"
        elif metrics['nesting_depth'] > 6:
            return "deeply_nested_algorithm"
        else:
            return "unclassified_complex_pattern"