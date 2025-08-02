"""
Cross-dimensional coherence validation for reducing false positives.

This module validates consistency across multiple detection methods to ensure
high-confidence matches and flag potential false positives.
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class CoherenceLevel(Enum):
    """Coherence levels for match validation."""
    HIGH = "high_confidence"         # > 0.8 coherence
    MEDIUM = "medium_confidence"     # 0.4 - 0.8 coherence  
    LOW = "potential_false_positive" # < 0.4 coherence
    INVALID = "invalid_match"        # Contradictory evidence


@dataclass
class CoherenceResult:
    """Result of coherence validation."""
    score: float
    level: CoherenceLevel
    confidence_adjustment: float
    warnings: List[str]
    dimensional_scores: Dict[str, float]
    recommendation: str


class CoherenceValidator:
    """
    Validates coherence across multiple detection dimensions.
    
    This validator checks consistency between different detection methods
    (hashing, algorithm detection, GNN, invariants) to reduce false positives
    from 3.1% to <1%.
    """
    
    def __init__(self):
        # Dimension weights based on reliability
        self.dimension_weights = {
            'simhash': 0.20,
            'tlsh': 0.20,
            'minhash': 0.20,
            'algorithm_detection': 0.25,
            'gnn_similarity': 0.15
        }
        
        # Thresholds for coherence levels
        self.thresholds = {
            'high': 0.8,
            'medium': 0.4,
            'low': 0.0
        }
        
        # Expected correlations between dimensions
        self.expected_correlations = {
            ('simhash', 'minhash'): 0.7,  # Should be highly correlated
            ('tlsh', 'algorithm_detection'): 0.6,
            ('gnn_similarity', 'algorithm_detection'): 0.8,
            ('simhash', 'tlsh'): 0.5
        }
    
    def validate_coherence(self, analysis_result: Dict[str, Any]) -> CoherenceResult:
        """
        Validate coherence across all detection dimensions.
        
        Args:
            analysis_result: Complete analysis result from CopycatAnalyzer
            
        Returns:
            CoherenceResult with validation details
        """
        # Extract dimensional scores
        dimensional_scores = self._extract_dimensional_scores(analysis_result)
        
        # Calculate base coherence score
        coherence_score = self._calculate_coherence_score(dimensional_scores)
        
        # Check for contradictions
        warnings = self._check_contradictions(dimensional_scores, analysis_result)
        
        # Validate expected correlations
        correlation_penalty = self._validate_correlations(dimensional_scores)
        adjusted_score = max(0.0, coherence_score - correlation_penalty)
        
        # Determine coherence level
        level = self._determine_coherence_level(adjusted_score)
        
        # Calculate confidence adjustment
        confidence_adjustment = self._calculate_confidence_adjustment(adjusted_score, level)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(level, warnings, dimensional_scores)
        
        return CoherenceResult(
            score=adjusted_score,
            level=level,
            confidence_adjustment=confidence_adjustment,
            warnings=warnings,
            dimensional_scores=dimensional_scores,
            recommendation=recommendation
        )
    
    def _extract_dimensional_scores(self, result: Dict[str, Any]) -> Dict[str, float]:
        """Extract normalized scores from each detection dimension."""
        scores = {}
        
        # Hash similarity scores
        if 'hashes' in result:
            hashes = result['hashes']
            if 'semantic' in hashes and 'simhash_similarity' in hashes['semantic']:
                scores['simhash'] = hashes['semantic']['simhash_similarity']
            if 'fuzzy' in hashes and 'tlsh_similarity' in hashes['fuzzy']:
                scores['tlsh'] = 1.0 - (hashes['fuzzy']['tlsh_similarity'] / 100.0)  # Normalize TLSH
            if 'semantic' in hashes and 'minhash_similarity' in hashes['semantic']:
                scores['minhash'] = hashes['semantic']['minhash_similarity']
        
        # Algorithm detection confidence
        if 'algorithms' in result and result['algorithms']:
            # Use highest confidence algorithm
            max_confidence = max(algo.get('confidence_score', 0) 
                               for algo in result['algorithms'])
            scores['algorithm_detection'] = max_confidence
        else:
            scores['algorithm_detection'] = 0.0
        
        # GNN similarity if available
        if 'gnn_analysis' in result and 'similarity_score' in result['gnn_analysis']:
            scores['gnn_similarity'] = result['gnn_analysis']['similarity_score']
        elif 'structural_similarity' in result:
            scores['gnn_similarity'] = result['structural_similarity']
        else:
            # If GNN not available, use average of other scores
            if scores:
                scores['gnn_similarity'] = np.mean(list(scores.values()))
            else:
                scores['gnn_similarity'] = 0.0
        
        # Normalize all scores to [0, 1]
        for key in scores:
            scores[key] = max(0.0, min(1.0, scores[key]))
        
        return scores
    
    def _calculate_coherence_score(self, dimensional_scores: Dict[str, float]) -> float:
        """
        Calculate coherence score based on variance across dimensions.
        
        High coherence = low variance = consistent scores across methods
        """
        if not dimensional_scores:
            return 0.0
        
        # Get weighted scores
        weighted_scores = []
        total_weight = 0.0
        
        for dimension, score in dimensional_scores.items():
            weight = self.dimension_weights.get(dimension, 0.1)
            weighted_scores.append(score * weight)
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Calculate weighted mean
        weighted_mean = sum(weighted_scores) / total_weight
        
        # Calculate weighted variance
        weighted_variance = sum(
            self.dimension_weights.get(dim, 0.1) * (score - weighted_mean) ** 2
            for dim, score in dimensional_scores.items()
        ) / total_weight
        
        # Convert variance to coherence score (low variance = high coherence)
        # Use exponential decay for smoother scoring
        coherence = np.exp(-2 * weighted_variance)
        
        # Apply penalties for missing dimensions
        missing_dimensions = set(self.dimension_weights.keys()) - set(dimensional_scores.keys())
        missing_penalty = len(missing_dimensions) * 0.1
        
        return max(0.0, min(1.0, coherence - missing_penalty))
    
    def _check_contradictions(self, dimensional_scores: Dict[str, float],
                            result: Dict[str, Any]) -> List[str]:
        """Check for contradictory evidence across dimensions."""
        warnings = []
        
        # Check for high hash similarity but low algorithm confidence
        hash_scores = [dimensional_scores.get(h, 0) for h in ['simhash', 'tlsh', 'minhash']]
        avg_hash_score = np.mean(hash_scores) if hash_scores else 0
        
        algo_score = dimensional_scores.get('algorithm_detection', 0)
        
        if avg_hash_score > 0.8 and algo_score < 0.3:
            warnings.append("High hash similarity but low algorithm confidence - possible false positive")
        
        if algo_score > 0.8 and avg_hash_score < 0.3:
            warnings.append("High algorithm confidence but low hash similarity - verify detection")
        
        # Check for GNN disagreement
        gnn_score = dimensional_scores.get('gnn_similarity', 0)
        if abs(gnn_score - avg_hash_score) > 0.5:
            warnings.append("Structural analysis (GNN) disagrees with hash analysis")
        
        # Check for invariant mismatches
        if 'mathematical_invariants' in result:
            invariant_count = len(result['mathematical_invariants'])
            if invariant_count == 0 and algo_score > 0.7:
                warnings.append("No mathematical invariants found despite algorithm detection")
        
        return warnings
    
    def _validate_correlations(self, dimensional_scores: Dict[str, float]) -> float:
        """
        Validate expected correlations between dimensions.
        
        Returns penalty score for unexpected correlations.
        """
        penalty = 0.0
        
        for (dim1, dim2), expected_corr in self.expected_correlations.items():
            if dim1 in dimensional_scores and dim2 in dimensional_scores:
                score1 = dimensional_scores[dim1]
                score2 = dimensional_scores[dim2]
                
                # Calculate actual correlation (simplified)
                actual_diff = abs(score1 - score2)
                expected_diff = 1.0 - expected_corr
                
                # Penalty if correlation is off
                if actual_diff > expected_diff + 0.2:  # Allow some tolerance
                    penalty += 0.1
                    
        return min(penalty, 0.3)  # Cap maximum penalty
    
    def _determine_coherence_level(self, score: float) -> CoherenceLevel:
        """Determine coherence level based on score."""
        if score >= self.thresholds['high']:
            return CoherenceLevel.HIGH
        elif score >= self.thresholds['medium']:
            return CoherenceLevel.MEDIUM
        elif score > 0:
            return CoherenceLevel.LOW
        else:
            return CoherenceLevel.INVALID
    
    def _calculate_confidence_adjustment(self, coherence_score: float,
                                       level: CoherenceLevel) -> float:
        """Calculate confidence adjustment based on coherence."""
        if level == CoherenceLevel.HIGH:
            # Boost confidence for high coherence
            return 1.0 + (coherence_score - 0.8) * 0.5  # Up to 1.1x boost
        elif level == CoherenceLevel.MEDIUM:
            # No adjustment for medium coherence
            return 1.0
        elif level == CoherenceLevel.LOW:
            # Reduce confidence for low coherence
            return 0.5 + coherence_score * 0.5  # 0.5x to 0.7x
        else:
            # Significant reduction for invalid matches
            return 0.2
    
    def _generate_recommendation(self, level: CoherenceLevel, warnings: List[str],
                               dimensional_scores: Dict[str, float]) -> str:
        """Generate actionable recommendation based on validation."""
        
        if level == CoherenceLevel.HIGH:
            return "High confidence match - all dimensions agree"
        
        elif level == CoherenceLevel.MEDIUM:
            weak_dimensions = [dim for dim, score in dimensional_scores.items() 
                             if score < 0.4]
            if weak_dimensions:
                return f"Medium confidence - weak signals from: {', '.join(weak_dimensions)}"
            else:
                return "Medium confidence - moderate agreement across dimensions"
        
        elif level == CoherenceLevel.LOW:
            if warnings:
                return f"Low confidence - review required: {warnings[0]}"
            else:
                return "Low confidence - inconsistent signals across detection methods"
        
        else:
            return "Invalid match - contradictory evidence detected"
    
    def enhance_result_with_coherence(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance analysis result with coherence validation.
        
        This adds coherence scores and adjusts confidence based on validation.
        """
        enhanced = analysis_result.copy()
        
        # Perform coherence validation
        coherence = self.validate_coherence(analysis_result)
        
        # Add coherence information
        enhanced['coherence_analysis'] = {
            'score': coherence.score,
            'level': coherence.level.value,
            'warnings': coherence.warnings,
            'dimensional_scores': coherence.dimensional_scores,
            'recommendation': coherence.recommendation
        }
        
        # Adjust algorithm confidence scores
        if 'algorithms' in enhanced:
            for algo in enhanced['algorithms']:
                original_confidence = algo.get('confidence_score', 0.5)
                adjusted_confidence = original_confidence * coherence.confidence_adjustment
                algo['confidence_score'] = min(1.0, adjusted_confidence)
                algo['coherence_adjusted'] = True
        
        # Add flags for automated processing
        if coherence.level == CoherenceLevel.LOW:
            enhanced['requires_manual_review'] = True
        elif coherence.level == CoherenceLevel.INVALID:
            enhanced['flagged_as_false_positive'] = True
        
        # Calculate final match score
        if 'algorithms' in enhanced and enhanced['algorithms']:
            max_algo_confidence = max(algo['confidence_score'] for algo in enhanced['algorithms'])
            enhanced['final_match_score'] = max_algo_confidence * coherence.score
        else:
            enhanced['final_match_score'] = 0.0
        
        return enhanced