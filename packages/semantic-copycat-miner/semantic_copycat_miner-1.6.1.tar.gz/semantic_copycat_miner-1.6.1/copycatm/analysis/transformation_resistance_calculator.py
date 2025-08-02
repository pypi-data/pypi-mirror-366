"""
Dynamic Transformation Resistance Calculator for CopycatM.

This module calculates transformation resistance scores based on actual extracted data,
helping to determine how resistant code is to AI-based transformations.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import math

logger = logging.getLogger(__name__)


@dataclass
class TransformationMetrics:
    """Metrics used to calculate transformation resistance."""
    # Structural metrics
    ast_depth: int = 0
    node_diversity: float = 0.0
    control_flow_complexity: int = 0
    nesting_depth: int = 0
    
    # Naming metrics
    identifier_length_avg: float = 0.0
    identifier_uniqueness: float = 0.0
    naming_pattern_consistency: float = 0.0
    
    # Pattern metrics
    algorithm_confidence: float = 0.0
    pattern_specificity: float = 0.0
    invariant_count: int = 0
    
    # Hash metrics
    hash_diversity: float = 0.0
    semantic_hash_strength: float = 0.0
    
    # Code characteristics
    comment_ratio: float = 0.0
    function_modularity: float = 0.0
    dependency_coupling: float = 0.0


class TransformationResistanceCalculator:
    """Calculate dynamic transformation resistance based on extracted code features."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.weights = {
            'variable_renaming': {
                'identifier_uniqueness': 0.3,
                'naming_pattern_consistency': 0.2,
                'identifier_length_avg': 0.1,
                'semantic_hash_strength': 0.2,
                'invariant_count': 0.2
            },
            'language_translation': {
                'algorithm_confidence': 0.3,
                'pattern_specificity': 0.3,
                'invariant_count': 0.2,
                'control_flow_complexity': 0.1,
                'ast_depth': 0.1
            },
            'style_changes': {
                'ast_depth': 0.3,
                'control_flow_complexity': 0.3,
                'nesting_depth': 0.15,
                'function_modularity': 0.15,
                'node_diversity': 0.1
            },
            'framework_adaptation': {
                'dependency_coupling': 0.3,
                'function_modularity': 0.3,
                'pattern_specificity': 0.2,
                'algorithm_confidence': 0.2
            }
        }
    
    def calculate_resistance(self, algorithm_data: Dict[str, Any], 
                           ast_data: Dict[str, Any],
                           hash_data: Dict[str, Any],
                           invariants: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate dynamic transformation resistance scores.
        
        Args:
            algorithm_data: Algorithm detection results
            ast_data: AST analysis results
            hash_data: Hash generation results
            invariants: Mathematical invariants
            
        Returns:
            Dictionary with transformation resistance scores
        """
        # Handle edge cases - return minimum viable scores
        if not algorithm_data or algorithm_data.get('confidence', 0) == 0:
            return {
                'variable_renaming': 0.1,
                'language_translation': 0.1,
                'style_changes': 0.1,
                'framework_adaptation': 0.1,
                'overall': 0.1,
                'metrics': {
                    'ast_complexity': 0.1,
                    'naming_strength': 0.1,
                    'pattern_confidence': 0.0,
                    'structural_uniqueness': 0.1
                }
            }
        
        # Extract metrics from data
        metrics = self._extract_metrics(algorithm_data, ast_data, hash_data, invariants)
        
        # Calculate individual resistance scores
        resistance_scores = {
            'variable_renaming': self._calculate_variable_renaming_resistance(metrics),
            'language_translation': self._calculate_language_translation_resistance(metrics),
            'style_changes': self._calculate_style_changes_resistance(metrics),
            'framework_adaptation': self._calculate_framework_adaptation_resistance(metrics)
        }
        
        # Ensure all scores are valid (not 0)
        for key in resistance_scores:
            if resistance_scores[key] == 0:
                resistance_scores[key] = 0.1  # Minimum score
        
        # Add overall score
        resistance_scores['overall'] = sum(resistance_scores.values()) / len(resistance_scores)
        
        # Add detailed metrics for transparency
        resistance_scores['metrics'] = {
            'ast_complexity': max(0.1, metrics.ast_depth * metrics.node_diversity),
            'naming_strength': max(0.1, metrics.identifier_uniqueness * metrics.naming_pattern_consistency),
            'pattern_confidence': metrics.algorithm_confidence * metrics.pattern_specificity,
            'structural_uniqueness': max(0.1, metrics.control_flow_complexity / max(1, metrics.nesting_depth))
        }
        
        return resistance_scores
    
    def _extract_metrics(self, algorithm_data: Dict[str, Any],
                        ast_data: Dict[str, Any],
                        hash_data: Dict[str, Any],
                        invariants: List[Dict[str, Any]]) -> TransformationMetrics:
        """Extract metrics from analysis data."""
        metrics = TransformationMetrics()
        
        # Extract from algorithm data
        if algorithm_data:
            metrics.algorithm_confidence = algorithm_data.get('confidence', 0.0)
            metrics.pattern_specificity = self._calculate_pattern_specificity(algorithm_data)
        
        # Extract from AST data
        if ast_data:
            metrics.ast_depth = ast_data.get('depth', 0)
            metrics.node_diversity = self._calculate_node_diversity(ast_data)
            metrics.control_flow_complexity = ast_data.get('complexity', {}).get('cyclomatic', 1)
            metrics.nesting_depth = ast_data.get('max_nesting_depth', 0)
            
            # Extract naming metrics
            identifiers = ast_data.get('identifiers', [])
            if identifiers:
                metrics.identifier_length_avg = sum(len(id) for id in identifiers) / len(identifiers)
                metrics.identifier_uniqueness = len(set(identifiers)) / len(identifiers)
                metrics.naming_pattern_consistency = self._calculate_naming_consistency(identifiers)
        
        # Extract from hash data
        if hash_data:
            metrics.hash_diversity = self._calculate_hash_diversity(hash_data)
            metrics.semantic_hash_strength = self._calculate_semantic_strength(hash_data)
        
        # Extract from invariants
        metrics.invariant_count = len(invariants)
        
        # Calculate derived metrics
        metrics.function_modularity = self._calculate_modularity(ast_data)
        metrics.dependency_coupling = self._calculate_coupling(ast_data)
        
        return metrics
    
    def _calculate_variable_renaming_resistance(self, metrics: TransformationMetrics) -> float:
        """Calculate resistance to variable renaming."""
        score = 0.0
        weights = self.weights['variable_renaming']
        
        # Strong identifiers resist renaming
        score += weights['identifier_uniqueness'] * metrics.identifier_uniqueness
        score += weights['naming_pattern_consistency'] * metrics.naming_pattern_consistency
        score += weights['identifier_length_avg'] * min(1.0, metrics.identifier_length_avg / 10)
        
        # Semantic hashes capture meaning beyond names
        score += weights['semantic_hash_strength'] * metrics.semantic_hash_strength
        
        # Mathematical invariants are name-independent
        score += weights['invariant_count'] * min(1.0, metrics.invariant_count / 5)
        
        return min(1.0, score)
    
    def _calculate_language_translation_resistance(self, metrics: TransformationMetrics) -> float:
        """Calculate resistance to language translation."""
        score = 0.0
        weights = self.weights['language_translation']
        
        # High confidence algorithms translate well
        score += weights['algorithm_confidence'] * metrics.algorithm_confidence
        score += weights['pattern_specificity'] * metrics.pattern_specificity
        
        # Mathematical invariants are language-agnostic
        score += weights['invariant_count'] * min(1.0, metrics.invariant_count / 5)
        
        # Complex control flow is harder to translate accurately
        score += weights['control_flow_complexity'] * min(1.0, metrics.control_flow_complexity / 10)
        score += weights['ast_depth'] * min(1.0, metrics.ast_depth / 20)
        
        return min(1.0, score)
    
    def _calculate_style_changes_resistance(self, metrics: TransformationMetrics) -> float:
        """Calculate resistance to style changes."""
        score = 0.0
        weights = self.weights['style_changes']
        
        # Structural complexity resists style changes
        score += weights['ast_depth'] * min(1.0, metrics.ast_depth / 20)
        score += weights['control_flow_complexity'] * min(1.0, metrics.control_flow_complexity / 10)
        score += weights['nesting_depth'] * min(1.0, metrics.nesting_depth / 5)
        
        # Well-modularized code maintains structure
        score += weights['function_modularity'] * metrics.function_modularity
        score += weights['node_diversity'] * metrics.node_diversity
        
        return min(1.0, score)
    
    def _calculate_framework_adaptation_resistance(self, metrics: TransformationMetrics) -> float:
        """Calculate resistance to framework adaptation."""
        score = 0.0
        weights = self.weights['framework_adaptation']
        
        # Low coupling resists framework changes
        score += weights['dependency_coupling'] * (1.0 - metrics.dependency_coupling)
        score += weights['function_modularity'] * metrics.function_modularity
        
        # Specific patterns are harder to adapt
        score += weights['pattern_specificity'] * metrics.pattern_specificity
        score += weights['algorithm_confidence'] * metrics.algorithm_confidence
        
        return min(1.0, score)
    
    def _calculate_pattern_specificity(self, algorithm_data: Dict[str, Any]) -> float:
        """Calculate how specific the detected pattern is."""
        subtype = algorithm_data.get('algorithm_subtype', '')
        evidence = algorithm_data.get('evidence', {})
        
        # More specific subtypes get higher scores
        specificity = 0.5  # Base score
        
        if subtype and subtype != 'generic':
            specificity += 0.2
        
        # More evidence means more specific pattern
        evidence_count = len(evidence.get('matched_keywords', [])) + \
                        len(evidence.get('ast_patterns', [])) + \
                        len(evidence.get('required_patterns', []))
        
        specificity += min(0.3, evidence_count * 0.05)
        
        return specificity
    
    def _calculate_node_diversity(self, ast_data: Dict[str, Any]) -> float:
        """Calculate diversity of AST node types."""
        node_types = ast_data.get('node_types', [])
        if not node_types:
            return 0.0
        
        # Shannon entropy for diversity
        type_counts = Counter(node_types)
        total = sum(type_counts.values())
        entropy = 0.0
        
        for count in type_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Normalize to 0-1 range
        max_entropy = math.log2(len(type_counts))
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_naming_consistency(self, identifiers: List[str]) -> float:
        """Calculate naming pattern consistency."""
        if not identifiers:
            return 0.0
        
        patterns = {
            'camelCase': 0,
            'snake_case': 0,
            'PascalCase': 0,
            'lowercase': 0,
            'UPPERCASE': 0
        }
        
        for identifier in identifiers:
            if '_' in identifier and identifier.islower():
                patterns['snake_case'] += 1
            elif identifier[0].isupper() and any(c.isupper() for c in identifier[1:]):
                patterns['PascalCase'] += 1
            elif identifier[0].islower() and any(c.isupper() for c in identifier[1:]):
                patterns['camelCase'] += 1
            elif identifier.isupper():
                patterns['UPPERCASE'] += 1
            elif identifier.islower():
                patterns['lowercase'] += 1
        
        # Consistency is how dominant the main pattern is
        total = len(identifiers)
        max_pattern_count = max(patterns.values())
        return max_pattern_count / total
    
    def _calculate_hash_diversity(self, hash_data: Dict[str, Any]) -> float:
        """Calculate diversity of hash values."""
        if not hash_data:
            return 0.0
            
        # Handle different hash data structures
        all_hashes = []
        
        # Direct hashes can be a string or dict
        direct = hash_data.get('direct', {})
        if isinstance(direct, str):
            all_hashes.append(direct)
        elif isinstance(direct, dict):
            all_hashes.extend(direct.values())
        
        # Fuzzy hashes
        fuzzy = hash_data.get('fuzzy', {})
        if isinstance(fuzzy, dict):
            if 'tlsh' in fuzzy:
                all_hashes.append(fuzzy['tlsh'])
            # Add other fuzzy hash types if present
            for k, v in fuzzy.items():
                if k not in ['tlsh_threshold'] and isinstance(v, str):
                    all_hashes.append(v)
        
        # Semantic hashes
        semantic = hash_data.get('semantic', {})
        if isinstance(semantic, dict):
            if 'minhash' in semantic:
                all_hashes.append(semantic['minhash'])
            if 'simhash' in semantic:
                all_hashes.append(semantic['simhash'])
            if 'lsh_hash' in semantic:
                all_hashes.append(semantic['lsh_hash'])
        
        unique_hashes = set(h for h in all_hashes if h and h != 'None')
        total_hashes = len([h for h in all_hashes if h and h != 'None'])
        
        return len(unique_hashes) / total_hashes if total_hashes > 0 else 0.0
    
    def _calculate_semantic_strength(self, hash_data: Dict[str, Any]) -> float:
        """Calculate strength of semantic hashes."""
        semantic_hashes = hash_data.get('semantic', {})
        
        strength = 0.0
        if semantic_hashes.get('minhash'):
            strength += 0.5
        if semantic_hashes.get('simhash'):
            strength += 0.3
        if semantic_hashes.get('lsh_hash'):
            strength += 0.2
        
        return strength
    
    def _calculate_modularity(self, ast_data: Dict[str, Any]) -> float:
        """Calculate function modularity score."""
        functions = ast_data.get('functions', [])
        if not functions:
            return 0.0
        
        # Average function size and count contribute to modularity
        avg_size = sum(f.get('line_count', 0) for f in functions) / len(functions)
        
        # Ideal function size is 10-50 lines
        if 10 <= avg_size <= 50:
            size_score = 1.0
        elif avg_size < 10:
            size_score = avg_size / 10
        else:
            size_score = max(0.3, 1.0 - (avg_size - 50) / 100)
        
        # More functions indicate better modularity
        count_score = min(1.0, len(functions) / 10)
        
        return (size_score + count_score) / 2
    
    def _calculate_coupling(self, ast_data: Dict[str, Any]) -> float:
        """Calculate dependency coupling score."""
        imports = ast_data.get('imports', [])
        functions = ast_data.get('functions', [])
        
        if not functions:
            return 0.0
        
        # Ratio of imports to functions indicates coupling
        coupling_ratio = len(imports) / len(functions)
        
        # Lower coupling is better, normalize inversely
        return min(1.0, coupling_ratio / 5)


def integrate_with_algorithm_detector(algorithm_detector_instance, 
                                    ast_tree: Any,
                                    code_str: str,
                                    language: str) -> Dict[str, float]:
    """
    Integration function to be called from AlgorithmDetector.
    
    This replaces the static _calculate_transformation_resistance method.
    """
    calculator = TransformationResistanceCalculator()
    
    # Gather data from the detector instance
    algorithm_data = {
        'confidence': getattr(algorithm_detector_instance, 'last_confidence', 0.0),
        'algorithm_type': getattr(algorithm_detector_instance, 'last_type', ''),
        'algorithm_subtype': getattr(algorithm_detector_instance, 'last_subtype', ''),
        'evidence': getattr(algorithm_detector_instance, 'last_evidence', {})
    }
    
    # Extract AST data
    ast_data = algorithm_detector_instance._extract_ast_features(ast_tree) if ast_tree else {}
    
    # Add more AST analysis
    if ast_tree and hasattr(algorithm_detector_instance, 'parser'):
        ast_data['identifiers'] = algorithm_detector_instance._extract_identifiers(ast_tree)
        ast_data['functions'] = algorithm_detector_instance._extract_functions(ast_tree)
        ast_data['imports'] = algorithm_detector_instance._extract_imports(ast_tree)
    
    # Get hash data (if available)
    hash_data = getattr(algorithm_detector_instance, 'last_hashes', {})
    
    # Get invariants (if available)
    invariants = getattr(algorithm_detector_instance, 'last_invariants', [])
    
    # Calculate dynamic resistance
    return calculator.calculate_resistance(algorithm_data, ast_data, hash_data, invariants)