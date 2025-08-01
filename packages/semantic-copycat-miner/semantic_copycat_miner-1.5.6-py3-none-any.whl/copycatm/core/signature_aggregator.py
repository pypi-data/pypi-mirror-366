"""
Signature Aggregation and Ranking System for CopycatM.

This module implements sophisticated signature aggregation to combine results from
the three-tier analysis system with proper ranking, deduplication, and confidence scoring.
"""

import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


class SignatureImportance(Enum):
    """Signature importance levels based on uniqueness and reliability."""
    CRITICAL = "critical"    # Unique, high-confidence signatures
    HIGH = "high"           # Algorithm-specific signatures
    MEDIUM = "medium"       # Common patterns with context
    LOW = "low"            # Generic patterns
    NOISE = "noise"        # Very common, low-value patterns


class AggregationStrategy(Enum):
    """Different strategies for combining signatures."""
    WEIGHTED_CONFIDENCE = "weighted_confidence"    # Weight by confidence scores
    TIER_PRIORITY = "tier_priority"               # Prefer higher tiers
    IMPORTANCE_BASED = "importance_based"         # Based on signature importance
    ENSEMBLE = "ensemble"                         # Combine multiple strategies
    CONSENSUS = "consensus"                       # Require agreement across tiers


@dataclass
class SignatureMetrics:
    """Metrics for evaluating signature quality."""
    uniqueness_score: float      # How unique this signature is (0-1)
    confidence: float           # Confidence in the signature (0-1)
    transformation_resistance: float  # Resistance to code transformations (0-1)
    cross_language_consistency: float  # Consistency across languages (0-1)
    evidence_strength: float    # Strength of supporting evidence (0-1)
    frequency: int             # How often this signature appears
    tier_support: Set[int]     # Which tiers support this signature (1, 2, 3)


class SignatureAggregator:
    """
    Advanced signature aggregation and ranking system.
    
    Combines signatures from three-tier analysis with sophisticated ranking,
    deduplication, and confidence-based aggregation strategies.
    """
    
    def __init__(self, strategy: AggregationStrategy = AggregationStrategy.ENSEMBLE):
        """Initialize aggregator with specified strategy."""
        self.strategy = strategy
        self.signature_database = {}  # For uniqueness calculation
        self.importance_weights = {
            SignatureImportance.CRITICAL: 1.0,
            SignatureImportance.HIGH: 0.8,
            SignatureImportance.MEDIUM: 0.6,
            SignatureImportance.LOW: 0.3,
            SignatureImportance.NOISE: 0.1
        }
        self.tier_weights = {
            1: 0.6,  # Baseline tier - reliable but basic
            2: 0.8,  # Traditional tier - good balance
            3: 1.0   # Semantic tier - most sophisticated
        }
    
    def aggregate_signatures(self, tier_results: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Aggregate signatures from all three tiers.
        
        Args:
            tier_results: Dictionary mapping tier number to list of signatures
            
        Returns:
            Aggregated signature analysis with rankings and confidence scores
        """
        logger.info(f"Aggregating signatures from {len(tier_results)} tiers")
        
        # Step 1: Collect and enhance all signatures
        all_signatures = []
        for tier, signatures in tier_results.items():
            for sig in signatures:
                enhanced_sig = self._enhance_signature(sig, tier)
                all_signatures.append(enhanced_sig)
        
        logger.debug(f"Collected {len(all_signatures)} total signatures")
        
        # Step 2: Calculate metrics for each signature
        signature_metrics = self._calculate_signature_metrics(all_signatures)
        
        # Step 3: Deduplicate similar signatures
        deduplicated_signatures = self._deduplicate_signatures(all_signatures, signature_metrics)
        
        logger.debug(f"After deduplication: {len(deduplicated_signatures)} signatures")
        
        # Step 4: Rank signatures by importance and quality
        ranked_signatures = self._rank_signatures(deduplicated_signatures, signature_metrics)
        
        # Step 5: Apply aggregation strategy
        aggregated_result = self._apply_aggregation_strategy(ranked_signatures, signature_metrics)
        
        # Step 6: Generate final summary
        summary = self._generate_aggregation_summary(aggregated_result, tier_results)
        
        return {
            'aggregated_signatures': aggregated_result,
            'signature_metrics': signature_metrics,
            'aggregation_summary': summary,
            'tier_coverage': self._calculate_tier_coverage(tier_results),
            'confidence_distribution': self._calculate_confidence_distribution(ranked_signatures)
        }
    
    def _enhance_signature(self, signature: Dict[str, Any], tier: int) -> Dict[str, Any]:
        """Enhance signature with additional metadata and tier information."""
        enhanced = signature.copy()
        enhanced['tier'] = tier
        enhanced['tier_weight'] = self.tier_weights.get(tier, 0.5)
        
        # Calculate importance based on signature characteristics
        importance = self._calculate_signature_importance(signature)
        enhanced['importance'] = importance
        enhanced['importance_weight'] = self.importance_weights[importance]
        
        # Add normalized confidence (tier-weighted)
        original_confidence = signature.get('confidence_score', 0.0)
        enhanced['normalized_confidence'] = original_confidence * self.tier_weights.get(tier, 0.5)
        
        # Extract key features for deduplication
        enhanced['signature_key'] = self._generate_signature_key(signature)
        enhanced['algorithm_key'] = self._generate_algorithm_key(signature)
        
        return enhanced
    
    def _calculate_signature_importance(self, signature: Dict[str, Any]) -> SignatureImportance:
        """Calculate the importance level of a signature."""
        confidence = signature.get('confidence_score', 0.0)
        algo_type = signature.get('algorithm_classification', {}).get('type', 'unknown')
        evidence_strength = len(signature.get('evidence', {}))
        
        # Critical: High confidence, specific algorithm, strong evidence
        if confidence >= 0.9 and algo_type != 'unknown' and evidence_strength > 5:
            return SignatureImportance.CRITICAL
        
        # High: Good confidence, known algorithm
        if confidence >= 0.7 and algo_type != 'unknown':
            return SignatureImportance.HIGH
        
        # Medium: Moderate confidence or context
        if confidence >= 0.5 or evidence_strength > 3:
            return SignatureImportance.MEDIUM
        
        # Low: Low confidence but some evidence
        if confidence >= 0.3 or evidence_strength > 1:
            return SignatureImportance.LOW
        
        # Noise: Very low confidence, minimal evidence
        return SignatureImportance.NOISE
    
    def _calculate_signature_metrics(self, signatures: List[Dict[str, Any]]) -> Dict[str, SignatureMetrics]:
        """Calculate comprehensive metrics for each signature."""
        metrics = {}
        
        # Count signature frequencies for uniqueness calculation
        signature_counts = {}
        algorithm_counts = {}
        
        for sig in signatures:
            sig_key = sig['signature_key']
            algo_key = sig['algorithm_key']
            
            signature_counts[sig_key] = signature_counts.get(sig_key, 0) + 1
            algorithm_counts[algo_key] = algorithm_counts.get(algo_key, 0) + 1
        
        # Calculate metrics for each signature
        for sig in signatures:
            sig_key = sig['signature_key']
            algo_key = sig['algorithm_key']
            
            # Uniqueness: inverse of frequency
            uniqueness = 1.0 / (signature_counts[sig_key] + 1)
            
            # Confidence from signature
            confidence = sig.get('normalized_confidence', 0.0)
            
            # Transformation resistance from signature
            trans_resistance = sig.get('transformation_resistance', 0.0)
            
            # Cross-language consistency (placeholder - would need cross-language analysis)
            cross_lang_consistency = 0.8 if sig.get('algorithm_classification', {}).get('type') != 'unknown' else 0.3
            
            # Evidence strength
            evidence = sig.get('evidence', {})
            evidence_strength = min(1.0, len(evidence) / 10.0)  # Normalize to 0-1
            
            # Tier support
            tier_support = {sig['tier']}
            
            metrics[sig_key] = SignatureMetrics(
                uniqueness_score=uniqueness,
                confidence=confidence,
                transformation_resistance=trans_resistance,
                cross_language_consistency=cross_lang_consistency,
                evidence_strength=evidence_strength,
                frequency=signature_counts[sig_key],
                tier_support=tier_support
            )
        
        return metrics
    
    def _deduplicate_signatures(self, signatures: List[Dict[str, Any]], 
                              metrics: Dict[str, SignatureMetrics]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar signatures."""
        seen_signatures = {}
        deduplicated = []
        
        # Group signatures by algorithm key
        algorithm_groups = {}
        for sig in signatures:
            algo_key = sig['algorithm_key']
            if algo_key not in algorithm_groups:
                algorithm_groups[algo_key] = []
            algorithm_groups[algo_key].append(sig)
        
        # For each algorithm group, keep the best signature(s)
        for algo_key, group in algorithm_groups.items():
            if len(group) == 1:
                deduplicated.extend(group)
            else:
                # Multiple signatures for same algorithm - keep the best ones
                scored_group = []
                for sig in group:
                    sig_key = sig['signature_key']
                    metric = metrics[sig_key]
                    
                    # Calculate overall quality score
                    quality_score = (
                        metric.confidence * 0.3 +
                        metric.uniqueness_score * 0.2 +
                        metric.transformation_resistance * 0.2 +
                        metric.evidence_strength * 0.2 +
                        sig['importance_weight'] * 0.1
                    )
                    
                    scored_group.append((quality_score, sig))
                
                # Sort by quality and keep top signatures
                scored_group.sort(key=lambda x: x[0], reverse=True)
                
                # Keep top 2 signatures for each algorithm (diversity)
                for score, sig in scored_group[:2]:
                    deduplicated.append(sig)
        
        return deduplicated
    
    def _rank_signatures(self, signatures: List[Dict[str, Any]], 
                        metrics: Dict[str, SignatureMetrics]) -> List[Dict[str, Any]]:
        """Rank signatures by overall quality and importance."""
        ranked_signatures = []
        
        for sig in signatures:
            sig_key = sig['signature_key']
            metric = metrics[sig_key]
            
            # Calculate comprehensive ranking score
            ranking_score = self._calculate_ranking_score(sig, metric)
            
            sig_with_score = sig.copy()
            sig_with_score['ranking_score'] = ranking_score
            sig_with_score['metrics'] = metric
            
            ranked_signatures.append(sig_with_score)
        
        # Sort by ranking score (highest first)
        ranked_signatures.sort(key=lambda x: x['ranking_score'], reverse=True)
        
        return ranked_signatures
    
    def _calculate_ranking_score(self, signature: Dict[str, Any], 
                                metric: SignatureMetrics) -> float:
        """Calculate comprehensive ranking score for a signature."""
        if self.strategy == AggregationStrategy.WEIGHTED_CONFIDENCE:
            return metric.confidence
        
        elif self.strategy == AggregationStrategy.TIER_PRIORITY:
            return signature['tier_weight']
        
        elif self.strategy == AggregationStrategy.IMPORTANCE_BASED:
            return signature['importance_weight']
        
        elif self.strategy == AggregationStrategy.ENSEMBLE:
            # Weighted combination of multiple factors
            return (
                metric.confidence * 0.25 +
                metric.uniqueness_score * 0.20 +
                metric.transformation_resistance * 0.15 +
                metric.evidence_strength * 0.15 +
                signature['importance_weight'] * 0.15 +
                signature['tier_weight'] * 0.10
            )
        
        elif self.strategy == AggregationStrategy.CONSENSUS:
            # Bonus for cross-tier agreement
            tier_bonus = len(metric.tier_support) * 0.1
            base_score = metric.confidence * signature['importance_weight']
            return base_score + tier_bonus
        
        else:
            return metric.confidence
    
    def _apply_aggregation_strategy(self, ranked_signatures: List[Dict[str, Any]], 
                                  metrics: Dict[str, SignatureMetrics]) -> List[Dict[str, Any]]:
        """Apply the configured aggregation strategy to get final results."""
        if not ranked_signatures:
            return []
        
        # For most strategies, return top-ranked signatures with quality threshold
        quality_threshold = 0.3
        high_quality_signatures = [
            sig for sig in ranked_signatures 
            if sig['ranking_score'] >= quality_threshold
        ]
        
        # Limit to top 10 signatures to avoid noise
        final_signatures = high_quality_signatures[:10]
        
        # Add aggregation metadata
        for i, sig in enumerate(final_signatures):
            sig['aggregation_rank'] = i + 1
            sig['percentile_rank'] = (len(ranked_signatures) - i) / len(ranked_signatures)
        
        return final_signatures
    
    def _generate_signature_key(self, signature: Dict[str, Any]) -> str:
        """Generate a key for signature deduplication."""
        # Combine algorithm type, function name, and signature hash
        algo_type = signature.get('algorithm_classification', {}).get('type', 'unknown')
        func_name = signature.get('source_location', {}).get('function_name', '')
        sig_hash = signature.get('signature_hash', '')
        
        key_string = f"{algo_type}_{func_name}_{sig_hash[:16]}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_algorithm_key(self, signature: Dict[str, Any]) -> str:
        """Generate a key for algorithm-level grouping."""
        algo_classification = signature.get('algorithm_classification', {})
        algo_type = algo_classification.get('type', 'unknown')
        algo_subtype = algo_classification.get('subtype', 'unknown')
        
        return f"{algo_type}_{algo_subtype}"
    
    def _generate_aggregation_summary(self, aggregated_signatures: List[Dict[str, Any]], 
                                    tier_results: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate summary of aggregation process."""
        total_input_signatures = sum(len(sigs) for sigs in tier_results.values())
        final_signature_count = len(aggregated_signatures)
        
        # Calculate algorithm diversity
        algorithm_types = set()
        for sig in aggregated_signatures:
            algo_type = sig.get('algorithm_classification', {}).get('type', 'unknown')
            algorithm_types.add(algo_type)
        
        # Calculate confidence statistics
        confidences = [sig['ranking_score'] for sig in aggregated_signatures]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Tier representation
        tier_representation = {}
        for sig in aggregated_signatures:
            tier = sig['tier']
            tier_representation[tier] = tier_representation.get(tier, 0) + 1
        
        return {
            'total_input_signatures': total_input_signatures,
            'final_signature_count': final_signature_count,
            'reduction_rate': 1.0 - (final_signature_count / max(total_input_signatures, 1)),
            'algorithm_diversity': len(algorithm_types),
            'unique_algorithms': list(algorithm_types),
            'average_confidence': avg_confidence,
            'tier_representation': tier_representation,
            'strategy_used': self.strategy.value
        }
    
    def _calculate_tier_coverage(self, tier_results: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate coverage across tiers."""
        active_tiers = list(tier_results.keys())
        tier_sizes = {tier: len(sigs) for tier, sigs in tier_results.items()}
        
        return {
            'active_tiers': active_tiers,
            'tier_sizes': tier_sizes,
            'full_three_tier_coverage': len(active_tiers) == 3,
            'primary_tier': max(tier_sizes, key=tier_sizes.get) if tier_sizes else None
        }
    
    def _calculate_confidence_distribution(self, signatures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate distribution of confidence scores."""
        if not signatures:
            return {'count': 0}
        
        scores = [sig['ranking_score'] for sig in signatures]
        
        return {
            'count': len(scores),
            'mean': float(np.mean(scores)),
            'median': float(np.median(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'quartiles': {
                'q1': float(np.percentile(scores, 25)),
                'q2': float(np.percentile(scores, 50)),
                'q3': float(np.percentile(scores, 75))
            }
        }


class SignatureValidator:
    """Validates signature quality and consistency."""
    
    def validate_signature_set(self, signatures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a set of signatures for quality and consistency."""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'quality_score': 0.0,
            'consistency_score': 0.0
        }
        
        if not signatures:
            validation_results['errors'].append("No signatures provided")
            validation_results['is_valid'] = False
            return validation_results
        
        # Check for required fields
        required_fields = ['signature_hash', 'confidence_score', 'algorithm_classification']
        for i, sig in enumerate(signatures):
            for field in required_fields:
                if field not in sig:
                    validation_results['errors'].append(f"Signature {i}: Missing required field '{field}'")
                    validation_results['is_valid'] = False
        
        # Calculate quality metrics
        confidences = [sig.get('confidence_score', 0.0) for sig in signatures]
        avg_confidence = np.mean(confidences)
        validation_results['quality_score'] = avg_confidence
        
        # Check consistency across signatures
        algorithm_types = [sig.get('algorithm_classification', {}).get('type') for sig in signatures]
        unique_types = set(filter(None, algorithm_types))
        if len(unique_types) > 1:
            validation_results['warnings'].append(f"Multiple algorithm types detected: {unique_types}")
        
        validation_results['consistency_score'] = 1.0 - (len(unique_types) - 1) / max(len(signatures), 1)
        
        return validation_results