"""
Analysis components for CopycatM.
"""

from .metadata import MetadataExtractor
from .complexity import ComplexityAnalyzer
from .algorithm_detector import AlgorithmDetector
from .invariant_extractor import InvariantExtractor
from .algorithmic_normalizer import AlgorithmicNormalizer
from .algorithm_types import AlgorithmType
from .invariant_extractor_improved import ImprovedInvariantExtractor, InvariantType
from .mathematical_invariance import MathematicalInvariantDetector, MathematicalProperty
from .coherence_validator import CoherenceValidator, CoherenceLevel, CoherenceResult
from .ast_normalizer import ASTNormalizer
from .semantic_similarity import SemanticSimilarityDetector
from .call_graph import CallGraphAnalyzer
from .code_clone_detector import CodeCloneDetector, CodeClone
from .wrapper_detector import WrapperDetector
from .confidence_scorer import ConfidenceScorer, ConfidenceScore, ConfidenceLevel
from .pseudocode_normalizer import PseudocodeNormalizer

__all__ = [
    "MetadataExtractor",
    "ComplexityAnalyzer", 
    "AlgorithmDetector",
    "InvariantExtractor",
    "AlgorithmicNormalizer",
    "AlgorithmType",
    "ImprovedInvariantExtractor",
    "InvariantType",
    "MathematicalInvariantDetector",
    "MathematicalProperty",
    "CoherenceValidator",
    "CoherenceLevel",
    "CoherenceResult",
    "ASTNormalizer",
    "SemanticSimilarityDetector",
    "CallGraphAnalyzer",
    "CodeCloneDetector",
    "CodeClone",
    "WrapperDetector",
    "ConfidenceScorer",
    "ConfidenceScore",
    "ConfidenceLevel",
    "PseudocodeNormalizer",
] 