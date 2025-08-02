"""
Enhanced semantic analyzer with embeddings and graph matching.

This module combines AST embeddings, graph-based matching, and improved
weight distribution to achieve >85% cross-language similarity.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np

from .semantic_analyzer import SemanticAnalyzer, SemanticFingerprint
from .semantic_analyzer_fixed import FixedSemanticAnalyzer
from ..embeddings.ast_embeddings import ASTEmbeddings
from ..embeddings.ast_graph_matcher import ASTGraphMatcher
from ..hashing.ast_winnowing import ASTWinnowing
from ..embeddings.pattern_booster import AlgorithmPatternBooster

logger = logging.getLogger(__name__)


@dataclass 
class EnhancedFingerprint(SemanticFingerprint):
    """Enhanced fingerprint with embeddings and graph data."""
    # Additional fields for enhanced analysis
    ast_embedding: Optional[np.ndarray] = None
    ast_graph: Optional[Any] = None  # networkx graph
    semantic_patterns: Optional[Dict[str, int]] = None
    embedding_hash: Optional[str] = None
    detected_algorithm: Optional[str] = None  # Detected algorithm family
    algorithm_confidence: Optional[float] = None  # Confidence in detection


class EnhancedSemanticAnalyzer(FixedSemanticAnalyzer):
    """Enhanced analyzer with improved cross-language detection."""
    
    def __init__(self, reference_db_path: Optional[str] = None):
        """Initialize enhanced analyzer."""
        super().__init__(reference_db_path)
        
        # Initialize new components
        self.ast_embeddings = ASTEmbeddings()
        self.graph_matcher = ASTGraphMatcher()
        self.pattern_booster = AlgorithmPatternBooster()
        
        # Override weight configuration for better semantic matching
        self.similarity_weights = {
            # Minimal weight for syntactic similarity
            'winnowing_best': 0.02,  # Minimal
            
            # Heavy weight on semantic components
            'embedding': 0.40,       # Primary: AST embeddings
            'graph': 0.28,          # Secondary: Graph structure
            'semantic_patterns': 0.20, # Important: High-level patterns
            'math_sequence': 0.05,   # Keep small: Important for algorithms
            'constants': 0.03,      # Keep minimal
            'structure': 0.02,      # Keep minimal
            
            # Remove other components
            'cfg': 0.0,            # Remove: Too language-specific
            'dfg': 0.0,            # Remove: Too language-specific
            'transforms': 0.0,
            'ast': 0.0
        }
    
    def extract_semantic_fingerprint(self, code: str, language: str) -> EnhancedFingerprint:
        """Extract enhanced semantic fingerprint with embeddings."""
        # Get base fingerprint
        base_fp = super().extract_semantic_fingerprint(code, language)
        
        # Convert to enhanced fingerprint
        enhanced_fp = EnhancedFingerprint(
            winnowing_fine=base_fp.winnowing_fine,
            winnowing_medium=base_fp.winnowing_medium,
            winnowing_coarse=base_fp.winnowing_coarse,
            cfg_hash=base_fp.cfg_hash,
            dfg_hash=base_fp.dfg_hash,
            cfg_nodes=base_fp.cfg_nodes,
            dfg_edges=base_fp.dfg_edges,
            math_sequence=base_fp.math_sequence,
            math_patterns=base_fp.math_patterns,
            memory_access_patterns=base_fp.memory_access_patterns,
            array_dimensions=base_fp.array_dimensions,
            transforms=base_fp.transforms,
            quantization_ops=base_fp.quantization_ops,
            entropy_coding=base_fp.entropy_coding,
            crypto_ops=base_fp.crypto_ops,
            numeric_constants=base_fp.numeric_constants,
            string_constants=base_fp.string_constants,
            hex_constants=base_fp.hex_constants,
            function_signatures=base_fp.function_signatures,
            loop_nesting_depth=base_fp.loop_nesting_depth,
            cyclomatic_complexity=base_fp.cyclomatic_complexity,
            ast_depth=base_fp.ast_depth,
            ast_node_types=base_fp.ast_node_types,
            unique_ast_patterns=base_fp.unique_ast_patterns
        )
        
        # Parse AST if available
        try:
            ast_tree = self.parser.parse(code, language)
            if ast_tree and hasattr(ast_tree, 'root'):
                # Extract AST sequence for embeddings
                ast_winnowing = ASTWinnowing()
                ast_sequence = ast_winnowing.extract_ast_sequence(ast_tree.root)
                
                # Detect algorithm family
                algo_families = self.pattern_booster.detect_algorithm_family(code, ast_sequence)
                if algo_families:
                    # Get the highest confidence algorithm
                    enhanced_fp.detected_algorithm = max(algo_families, key=algo_families.get)
                    enhanced_fp.algorithm_confidence = algo_families[enhanced_fp.detected_algorithm]
                    
                    # Boost patterns if algorithm detected
                    if enhanced_fp.detected_algorithm:
                        boosted_sequence = self.pattern_booster.boost_embedding_patterns(
                            ast_sequence, enhanced_fp.detected_algorithm
                        )
                        ast_sequence = boosted_sequence
                
                # Generate embedding
                embedding_data = self.ast_embeddings.get_semantic_fingerprint(ast_sequence)
                enhanced_fp.ast_embedding = embedding_data['embedding']
                enhanced_fp.semantic_patterns = embedding_data['patterns']
                enhanced_fp.embedding_hash = embedding_data['embedding_hash']
                
                # Boost semantic patterns if algorithm detected
                if enhanced_fp.detected_algorithm and enhanced_fp.semantic_patterns:
                    enhanced_fp.semantic_patterns = self.pattern_booster.boost_graph_patterns(
                        enhanced_fp.semantic_patterns.copy(),
                        enhanced_fp.detected_algorithm
                    )
                
                # Convert AST to graph
                enhanced_fp.ast_graph = self.graph_matcher.ast_to_graph(ast_tree.root)
                
                logger.debug(f"Enhanced fingerprint with {len(ast_sequence)} AST nodes, "
                           f"{len(embedding_data['patterns'])} patterns"
                           + (f", detected: {enhanced_fp.detected_algorithm}" if enhanced_fp.detected_algorithm else ""))
        except Exception as e:
            logger.debug(f"Failed to enhance fingerprint: {e}")
        
        return enhanced_fp
    
    def calculate_similarity(self, fp1: EnhancedFingerprint, 
                           fp2: EnhancedFingerprint) -> Dict[str, float]:
        """Calculate enhanced similarity with embeddings and graph matching."""
        # Get base similarities
        similarities = super().calculate_similarity(fp1, fp2)
        
        # Add embedding similarity
        if fp1.ast_embedding is not None and fp2.ast_embedding is not None:
            # Cosine similarity
            dot_product = np.dot(fp1.ast_embedding, fp2.ast_embedding)
            norm1 = np.linalg.norm(fp1.ast_embedding)
            norm2 = np.linalg.norm(fp2.ast_embedding)
            
            if norm1 > 0 and norm2 > 0:
                cos_sim = dot_product / (norm1 * norm2)
                similarities['embedding'] = (cos_sim + 1) / 2  # Normalize to [0, 1]
            else:
                similarities['embedding'] = 0.0
        else:
            similarities['embedding'] = 0.0
        
        # Add graph similarity
        if fp1.ast_graph is not None and fp2.ast_graph is not None:
            similarities['graph'] = self.graph_matcher.graph_similarity(
                fp1.ast_graph, fp2.ast_graph
            )
        else:
            similarities['graph'] = 0.0
        
        # Add semantic pattern similarity
        if fp1.semantic_patterns and fp2.semantic_patterns:
            patterns1 = set(fp1.semantic_patterns.keys())
            patterns2 = set(fp2.semantic_patterns.keys())
            
            if patterns1 or patterns2:
                # Weighted Jaccard similarity
                intersection = patterns1 & patterns2
                union = patterns1 | patterns2
                
                if union:
                    # Weight by pattern frequency
                    weighted_intersection = sum(
                        min(fp1.semantic_patterns.get(p, 0), 
                            fp2.semantic_patterns.get(p, 0))
                        for p in intersection
                    )
                    weighted_union = sum(
                        max(fp1.semantic_patterns.get(p, 0), 
                            fp2.semantic_patterns.get(p, 0))
                        for p in union
                    )
                    similarities['semantic_patterns'] = weighted_intersection / weighted_union
                else:
                    similarities['semantic_patterns'] = 0.0
            else:
                similarities['semantic_patterns'] = 1.0  # Both empty
        else:
            similarities['semantic_patterns'] = 0.0
        
        # Recalculate overall with new weights
        overall = 0.0
        for key, weight in self.similarity_weights.items():
            if key in similarities:
                overall += similarities[key] * weight
        
        # Algorithm detection bonus
        if (fp1.detected_algorithm and fp2.detected_algorithm and 
            fp1.detected_algorithm == fp2.detected_algorithm):
            # Both detected same algorithm family - boost similarity
            boost = min(fp1.algorithm_confidence, fp2.algorithm_confidence)
            algorithm_bonus = 0.1 * boost  # Up to 12% bonus
            overall = min(1.0, overall + algorithm_bonus)
            similarities['algorithm_detection'] = 1.0
        else:
            similarities['algorithm_detection'] = 0.0
        
        similarities['overall'] = overall
        
        return similarities
    
    def explain_similarity(self, sim_results: Dict[str, float]) -> str:
        """Explain similarity results in human-readable format."""
        explanation = []
        
        explanation.append(f"Overall Similarity: {sim_results['overall']:.1%}")
        explanation.append("\nKey Components:")
        
        # Sort by contribution
        contributions = []
        for key, weight in self.similarity_weights.items():
            if key in sim_results and weight > 0:
                contribution = sim_results[key] * weight
                contributions.append((key, sim_results[key], weight, contribution))
        
        contributions.sort(key=lambda x: x[3], reverse=True)
        
        for key, score, weight, contrib in contributions:
            explanation.append(f"  {key}: {score:.1%} (weight: {weight:.0%}, contribution: {contrib:.1%})")
        
        # Provide interpretation
        overall = sim_results['overall']
        if overall >= 0.85:
            explanation.append("\n✓ HIGH CONFIDENCE: Same algorithm across languages")
        elif overall >= 0.70:
            explanation.append("\n⚠ MODERATE: Likely same algorithm with variations")
        elif overall >= 0.50:
            explanation.append("\n⚠ LOW: Similar patterns but different implementation")
        else:
            explanation.append("\n✗ DIFFERENT: Likely different algorithms")
        
        return "\n".join(explanation)