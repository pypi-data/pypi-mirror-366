"""
Multi-factor confidence scoring framework for similarity detection.
"""

try:
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for similarity assessment."""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"            # 75-89%
    MODERATE = "moderate"    # 60-74%
    LOW = "low"             # 40-59%
    VERY_LOW = "very_low"   # Below 40%


@dataclass
class ConfidenceScore:
    """Comprehensive confidence score with breakdown."""
    overall_score: float
    level: ConfidenceLevel
    factors: Dict[str, float]
    explanation: str
    recommendations: List[str]


class ConfidenceScorer:
    """Calculate multi-factor confidence scores for code similarity detection."""
    
    def __init__(self):
        # Factor weights for different evidence types
        self.factor_weights = {
            'hash_similarity': 0.20,
            'structural_similarity': 0.15,
            'semantic_similarity': 0.15,
            'algorithm_matching': 0.15,
            'call_graph_similarity': 0.10,
            'data_flow_similarity': 0.10,
            'clone_detection': 0.10,
            'wrapper_detection': 0.05
        }
        
        # Confidence thresholds
        self.thresholds = {
            ConfidenceLevel.VERY_HIGH: 0.90,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.MODERATE: 0.60,
            ConfidenceLevel.LOW: 0.40,
            ConfidenceLevel.VERY_LOW: 0.0
        }
    
    def calculate_confidence(self, similarity_results: Dict[str, Any]) -> ConfidenceScore:
        """Calculate comprehensive confidence score from similarity results."""
        factors = {}
        
        # 1. Hash-based similarity
        factors['hash_similarity'] = self._calculate_hash_factor(
            similarity_results.get('hashes', {})
        )
        
        # 2. Structural similarity
        factors['structural_similarity'] = self._calculate_structural_factor(
            similarity_results.get('ast_analysis', {}),
            similarity_results.get('structural_patterns', {})
        )
        
        # 3. Semantic similarity
        factors['semantic_similarity'] = self._calculate_semantic_factor(
            similarity_results.get('semantic_analysis', {})
        )
        
        # 4. Algorithm matching
        factors['algorithm_matching'] = self._calculate_algorithm_factor(
            similarity_results.get('algorithms', {}),
            similarity_results.get('algorithm_comparison', {})
        )
        
        # 5. Call graph similarity
        factors['call_graph_similarity'] = self._calculate_call_graph_factor(
            similarity_results.get('call_graph_analysis', {})
        )
        
        # 6. Data flow similarity
        factors['data_flow_similarity'] = self._calculate_data_flow_factor(
            similarity_results.get('data_flow_analysis', {})
        )
        
        # 7. Clone detection results
        factors['clone_detection'] = self._calculate_clone_factor(
            similarity_results.get('clone_analysis', {})
        )
        
        # 8. Wrapper detection
        factors['wrapper_detection'] = self._calculate_wrapper_factor(
            similarity_results.get('wrapper_analysis', {})
        )
        
        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(factors)
        
        # Determine confidence level
        level = self._determine_confidence_level(overall_score)
        
        # Generate explanation
        explanation = self._generate_explanation(factors, level)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(factors, similarity_results)
        
        return ConfidenceScore(
            overall_score=overall_score,
            level=level,
            factors=factors,
            explanation=explanation,
            recommendations=recommendations
        )
    
    def _calculate_hash_factor(self, hash_data: Dict) -> float:
        """Calculate hash similarity factor."""
        if not hash_data:
            return 0.0
        
        scores = []
        
        # Direct hash matching
        if hash_data.get('sha256_match'):
            scores.append(1.0)
        
        # Fuzzy hash similarity
        if 'tlsh_similarity' in hash_data:
            tlsh_sim = hash_data['tlsh_similarity']
            # TLSH distance to similarity: lower is better
            # Assuming distance 0-300 range
            scores.append(max(0, 1 - (tlsh_sim / 300)))
        
        # Semantic hash similarity
        if 'minhash_similarity' in hash_data:
            scores.append(hash_data['minhash_similarity'])
        
        if 'simhash_similarity' in hash_data:
            # Simhash distance to similarity
            simhash_dist = hash_data['simhash_similarity']
            scores.append(max(0, 1 - (simhash_dist / 64)))  # 64 bits max
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_structural_factor(self, ast_data: Dict, patterns: Dict) -> float:
        """Calculate structural similarity factor."""
        scores = []
        
        # AST similarity
        if 'ast_similarity' in ast_data:
            scores.append(ast_data['ast_similarity'])
        
        # Pattern matching
        if patterns:
            if 'common_patterns' in patterns and 'total_patterns' in patterns:
                pattern_ratio = patterns['common_patterns'] / max(patterns['total_patterns'], 1)
                scores.append(pattern_ratio)
        
        # Control flow similarity
        if 'control_flow_similarity' in ast_data:
            scores.append(ast_data['control_flow_similarity'])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_semantic_factor(self, semantic_data: Dict) -> float:
        """Calculate semantic similarity factor."""
        if not semantic_data:
            return 0.0
        
        # Use overall semantic similarity if available
        if 'overall_similarity' in semantic_data:
            return semantic_data['overall_similarity']
        
        # Otherwise aggregate individual metrics
        metrics = semantic_data.get('metrics', {})
        if metrics:
            values = list(metrics.values())
            return sum(values) / len(values) if values else 0.0
        
        return 0.0
    
    def _calculate_algorithm_factor(self, algorithms: Dict, comparison: Dict) -> float:
        """Calculate algorithm matching factor."""
        if comparison and 'similarity_score' in comparison:
            return comparison['similarity_score']
        
        if not algorithms:
            return 0.0
        
        # Simple presence check
        source_algos = set(algorithms.get('source', []))
        target_algos = set(algorithms.get('target', []))
        
        if not source_algos or not target_algos:
            return 0.0
        
        common = len(source_algos.intersection(target_algos))
        total = len(source_algos.union(target_algos))
        
        return common / total if total > 0 else 0.0
    
    def _calculate_call_graph_factor(self, call_graph_data: Dict) -> float:
        """Calculate call graph similarity factor."""
        if not call_graph_data:
            return 0.0
        
        if 'similarity' in call_graph_data:
            return call_graph_data['similarity']
        
        # Aggregate sub-metrics
        scores = []
        for metric in ['node_similarity', 'edge_similarity', 'pattern_similarity']:
            if metric in call_graph_data:
                scores.append(call_graph_data[metric])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_data_flow_factor(self, data_flow: Dict) -> float:
        """Calculate data flow similarity factor."""
        if not data_flow:
            return 0.0
        
        if 'similarity' in data_flow:
            return data_flow['similarity']
        
        # Check for common patterns
        if 'common_patterns' in data_flow:
            return min(data_flow['common_patterns'] / 5, 1.0)  # Normalize to max 5 patterns
        
        return 0.0
    
    def _calculate_clone_factor(self, clone_data: Dict) -> float:
        """Calculate clone detection factor."""
        if not clone_data:
            return 0.0
        
        # Map clone types to confidence scores
        clone_type_scores = {
            1: 1.0,    # Type 1 - Exact
            2: 0.85,   # Type 2 - Renamed
            3: 0.70,   # Type 3 - Modified
            4: 0.60    # Type 4 - Semantic
        }
        
        if 'clones' in clone_data:
            clones = clone_data['clones']
            if not clones:
                return 0.0
            
            # Use highest confidence clone
            best_score = max(
                clone_type_scores.get(clone.get('type', 4), 0.5) * clone.get('confidence', 0.5)
                for clone in clones
            )
            return best_score
        
        return 0.0
    
    def _calculate_wrapper_factor(self, wrapper_data: Dict) -> float:
        """Calculate wrapper detection factor."""
        if not wrapper_data:
            return 0.0
        
        if wrapper_data.get('is_wrapper'):
            # If it's a wrapper, it might indicate derived work
            return wrapper_data.get('confidence', 0.5)
        
        return 0.0
    
    def _calculate_weighted_score(self, factors: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        total_weight = 0
        weighted_sum = 0
        
        for factor, score in factors.items():
            weight = self.factor_weights.get(factor, 0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level from score."""
        for level in [
            ConfidenceLevel.VERY_HIGH,
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MODERATE,
            ConfidenceLevel.LOW
        ]:
            if score >= self.thresholds[level]:
                return level
        
        return ConfidenceLevel.VERY_LOW
    
    def _generate_explanation(self, factors: Dict[str, float], level: ConfidenceLevel) -> str:
        """Generate human-readable explanation."""
        # Find strongest evidence
        strong_factors = [(name, score) for name, score in factors.items() if score >= 0.8]
        moderate_factors = [(name, score) for name, score in factors.items() if 0.5 <= score < 0.8]
        
        explanation_parts = []
        
        if level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]:
            explanation_parts.append(f"{level.value.replace('_', ' ').title()} confidence of code similarity.")
            
            if strong_factors:
                strong_names = [name.replace('_', ' ') for name, _ in strong_factors]
                explanation_parts.append(f"Strong evidence from: {', '.join(strong_names)}.")
        
        elif level == ConfidenceLevel.MODERATE:
            explanation_parts.append("Moderate confidence of code similarity.")
            
            if moderate_factors:
                mod_names = [name.replace('_', ' ') for name, _ in moderate_factors]
                explanation_parts.append(f"Evidence from: {', '.join(mod_names)}.")
        
        else:
            explanation_parts.append(f"{level.value.replace('_', ' ').title()} confidence of code similarity.")
            explanation_parts.append("Limited evidence of direct code reuse.")
        
        return " ".join(explanation_parts)
    
    def _generate_recommendations(self, factors: Dict[str, float], 
                                results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for weak factors
        weak_factors = [(name, score) for name, score in factors.items() if score < 0.3]
        
        if any(name == 'hash_similarity' for name, _ in weak_factors):
            recommendations.append("Consider normalizing code before hashing to improve detection")
        
        if any(name == 'structural_similarity' for name, _ in weak_factors):
            recommendations.append("Analyze AST patterns for better structural comparison")
        
        if any(name == 'semantic_similarity' for name, _ in weak_factors):
            recommendations.append("Use semantic analysis for functionally equivalent code")
        
        # Check for specific patterns
        if results.get('wrapper_analysis', {}).get('is_wrapper'):
            recommendations.append("Detected wrapper pattern - check wrapped library for original source")
        
        clone_data = results.get('clone_analysis', {})
        if clone_data.get('clones'):
            clone_types = {c.get('type') for c in clone_data['clones']}
            if 4 in clone_types:
                recommendations.append("Semantic clones detected - manual review recommended")
        
        # General recommendations based on confidence
        overall_score = self._calculate_weighted_score(factors)
        
        if overall_score >= 0.9:
            recommendations.append("Very high similarity - likely direct code reuse")
        elif overall_score >= 0.75:
            recommendations.append("High similarity - probable derived work")
        elif overall_score >= 0.6:
            recommendations.append("Moderate similarity - possible inspiration or common patterns")
        else:
            recommendations.append("Low similarity - unlikely to be derived work")
        
        return recommendations
    
    def calculate_batch_confidence(self, similarity_matrix: Dict[str, Dict[str, Any]]) -> Dict[str, ConfidenceScore]:
        """Calculate confidence scores for multiple file comparisons."""
        results = {}
        
        for file_pair, similarity_data in similarity_matrix.items():
            confidence = self.calculate_confidence(similarity_data)
            results[file_pair] = confidence
        
        return results
    
    def aggregate_project_confidence(self, file_scores: Dict[str, ConfidenceScore]) -> ConfidenceScore:
        """Aggregate multiple file confidence scores into project-level score."""
        if not file_scores:
            return ConfidenceScore(
                overall_score=0.0,
                level=ConfidenceLevel.VERY_LOW,
                factors={},
                explanation="No files to compare",
                recommendations=[]
            )
        
        # Aggregate scores
        all_scores = [score.overall_score for score in file_scores.values()]
        
        # Use different aggregation strategies
        max_score = max(all_scores)
        avg_score = sum(all_scores) / len(all_scores)
        high_confidence_ratio = sum(1 for s in all_scores if s >= 0.75) / len(all_scores)
        
        # Weight towards maximum (most suspicious file)
        overall_score = 0.6 * max_score + 0.3 * avg_score + 0.1 * high_confidence_ratio
        
        # Aggregate factors
        aggregated_factors = {}
        for factor_name in self.factor_weights:
            factor_scores = [
                score.factors.get(factor_name, 0) 
                for score in file_scores.values()
            ]
            aggregated_factors[factor_name] = max(factor_scores)  # Use max for each factor
        
        level = self._determine_confidence_level(overall_score)
        
        # Generate project-level explanation
        high_conf_files = sum(1 for s in file_scores.values() if s.level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH])
        
        explanation = f"Project analysis: {high_conf_files}/{len(file_scores)} files show high similarity. "
        explanation += f"Maximum file similarity: {max_score:.1%}. "
        explanation += self._generate_explanation(aggregated_factors, level)
        
        # Aggregate recommendations
        all_recommendations = set()
        for score in file_scores.values():
            all_recommendations.update(score.recommendations)
        
        return ConfidenceScore(
            overall_score=overall_score,
            level=level,
            factors=aggregated_factors,
            explanation=explanation,
            recommendations=list(all_recommendations)[:5]  # Top 5 recommendations
        )