"""
Signature-based pattern matching for improved algorithm detection.

This module implements signature matching with pre/post normalization
and domain-specific pattern recognition.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SignatureType(Enum):
    """Types of signatures for matching."""
    EXACT = "exact"                    # Exact string match
    REGEX = "regex"                    # Regular expression
    STRUCTURAL = "structural"          # AST structure pattern
    NORMALIZED = "normalized"          # Normalized code pattern
    SEMANTIC = "semantic"              # Semantic pattern
    DOMAIN_SPECIFIC = "domain_specific" # Domain-specific pattern


@dataclass
class AlgorithmSignature:
    """Represents an algorithm signature for matching."""
    name: str
    algorithm_type: str
    algorithm_subtype: str
    signature_type: SignatureType
    pattern: str
    confidence_boost: float = 0.0
    required_context: List[str] = None
    domain: str = "general"
    pre_normalized: bool = False
    post_normalized: bool = False
    min_matches: int = 1
    
    def __post_init__(self):
        if self.required_context is None:
            self.required_context = []


class SignatureMatcher:
    """
    Enhanced signature matching with domain-specific support.
    
    Features:
    - Pre/post normalization matching
    - Domain-specific patterns
    - Multi-level signature matching
    - Context-aware detection
    """
    
    def __init__(self):
        """Initialize signature matcher with pattern database."""
        self.signatures = self._load_signatures()
        self.domain_patterns = self._load_domain_patterns()
        self.normalization_cache = {}
        
    def _load_signatures(self) -> Dict[str, List[AlgorithmSignature]]:
        """Load algorithm signatures database."""
        signatures = {
            "multimedia": self._load_multimedia_signatures(),
            "cryptographic": self._load_crypto_signatures(),
            "mathematical": self._load_math_signatures(),
            "general": self._load_general_signatures(),
        }
        return signatures
    
    def _load_multimedia_signatures(self) -> List[AlgorithmSignature]:
        """Load multimedia codec-specific signatures."""
        return [
            # H.264 IDCT Signatures
            AlgorithmSignature(
                name="h264_idct_butterfly",
                algorithm_type="video_codec",
                algorithm_subtype="inverse_discrete_cosine_transform",
                signature_type=SignatureType.REGEX,
                pattern=r"z0\s*=\s*block\[.*?\]\s*\+.*?block\[.*?\].*?z1\s*=\s*block\[.*?\]\s*-.*?block\[.*?\]",
                confidence_boost=0.3,
                required_context=["block", "stride", "dst"],
                domain="h264",
                pre_normalized=False
            ),
            AlgorithmSignature(
                name="h264_idct_template",
                algorithm_type="mathematical_transform",
                algorithm_subtype="idct",
                signature_type=SignatureType.STRUCTURAL,
                pattern="FUNCTION(LOOP(ARITHMETIC(VAR[block], ADD/SUB, VAR[block])))",
                confidence_boost=0.4,
                domain="video",
                post_normalized=True
            ),
            
            # CABAC Entropy Coding
            AlgorithmSignature(
                name="cabac_context_init",
                algorithm_type="entropy_encoding",
                algorithm_subtype="cabac",
                signature_type=SignatureType.REGEX,
                pattern=r"cabac_context_init.*?\[\d+\]\[\d+\].*?=.*?\{",
                confidence_boost=0.5,
                required_context=["cabac", "context"],
                domain="h264"
            ),
            AlgorithmSignature(
                name="cabac_arithmetic_coding",
                algorithm_type="entropy_encoding",
                algorithm_subtype="arithmetic_coding",
                signature_type=SignatureType.NORMALIZED,
                pattern="LOOP(COMPARE(VAR[state], LT, VAR[mps]) ASSIGN(VAR[range], ARITHMETIC))",
                confidence_boost=0.3,
                domain="video",
                post_normalized=True
            ),
            
            # CAVLC Entropy Coding
            AlgorithmSignature(
                name="cavlc_decode",
                algorithm_type="entropy_encoding",
                algorithm_subtype="cavlc",
                signature_type=SignatureType.REGEX,
                pattern=r"(coeff_token|total_zeros|run_before).*?cavlc",
                confidence_boost=0.4,
                domain="h264"
            ),
            
            # Deblocking Filter
            AlgorithmSignature(
                name="h264_deblock_filter",
                algorithm_type="image_filtering",
                algorithm_subtype="deblocking_filter",
                signature_type=SignatureType.REGEX,
                pattern=r"(tc0|alpha|beta).*?(filter|deblock).*?strength",
                confidence_boost=0.3,
                required_context=["edge", "strength", "threshold"],
                domain="h264"
            ),
            
            # Motion Prediction
            AlgorithmSignature(
                name="motion_vector_prediction",
                algorithm_type="video_compression",
                algorithm_subtype="motion_prediction",
                signature_type=SignatureType.REGEX,
                pattern=r"(mv|motion_vector).*?(pred|median).*?(left|top|diag)",
                confidence_boost=0.3,
                domain="video"
            ),
            
            # AAC Psychoacoustic Model
            AlgorithmSignature(
                name="aac_psychoacoustic_spreading",
                algorithm_type="audio_codec",
                algorithm_subtype="psychoacoustic_model",
                signature_type=SignatureType.REGEX,
                pattern=r"PSY_.*?(SPREAD|THR).*?(HI|LOW).*?=.*?\d+\.\d+f",
                confidence_boost=0.5,
                domain="aac"
            ),
            AlgorithmSignature(
                name="perceptual_entropy",
                algorithm_type="audio_codec",
                algorithm_subtype="perceptual_coding",
                signature_type=SignatureType.REGEX,
                pattern=r"(pe|perceptual_entropy).*?(bits|threshold)",
                confidence_boost=0.3,
                domain="audio"
            ),
            
            # General Video Patterns
            AlgorithmSignature(
                name="dct_transform",
                algorithm_type="mathematical_transform",
                algorithm_subtype="discrete_cosine_transform",
                signature_type=SignatureType.REGEX,
                pattern=r"(dct|DCT).*?(coeff|block).*?(\[\d+\]|\*)",
                confidence_boost=0.2,
                domain="video"
            ),
            AlgorithmSignature(
                name="quantization_video",
                algorithm_type="video_compression",
                algorithm_subtype="quantization",
                signature_type=SignatureType.REGEX,
                pattern=r"(quant|qp|qscale).*?(matrix|table|offset)",
                confidence_boost=0.2,
                domain="video"
            ),
        ]
    
    def _load_crypto_signatures(self) -> List[AlgorithmSignature]:
        """Load cryptographic algorithm signatures."""
        return [
            AlgorithmSignature(
                name="aes_sbox",
                algorithm_type="cryptographic",
                algorithm_subtype="aes",
                signature_type=SignatureType.REGEX,
                pattern=r"(sbox|s_box|substitution).*?\[256\].*?=.*?\{.*?0x[0-9a-fA-F]+",
                confidence_boost=0.4,
                domain="crypto"
            ),
            AlgorithmSignature(
                name="sha256_constants",
                algorithm_type="cryptographic",
                algorithm_subtype="sha256",
                signature_type=SignatureType.REGEX,
                pattern=r"0x428a2f98|0x71374491|0xb5c0fbcf|0xe9b5dba5",
                confidence_boost=0.5,
                domain="crypto"
            ),
        ]
    
    def _load_math_signatures(self) -> List[AlgorithmSignature]:
        """Load mathematical algorithm signatures."""
        return [
            AlgorithmSignature(
                name="fft_butterfly",
                algorithm_type="mathematical_transform",
                algorithm_subtype="fast_fourier_transform",
                signature_type=SignatureType.REGEX,
                pattern=r"(butterfly|twiddle).*?(real|imag|complex)",
                confidence_boost=0.3,
                domain="dsp"
            ),
            AlgorithmSignature(
                name="matrix_multiply",
                algorithm_type="mathematical_algorithm",
                algorithm_subtype="matrix_multiplication",
                signature_type=SignatureType.NORMALIZED,
                pattern="LOOP(LOOP(LOOP(ASSIGN(ARRAY_ACCESS, ARITHMETIC(MULT)))))",
                confidence_boost=0.3,
                post_normalized=True
            ),
        ]
    
    def _load_general_signatures(self) -> List[AlgorithmSignature]:
        """Load general algorithm signatures."""
        return [
            AlgorithmSignature(
                name="quicksort_normalized",
                algorithm_type="sorting_algorithm",
                algorithm_subtype="quicksort",
                signature_type=SignatureType.NORMALIZED,
                pattern="FUNCTION(CONDITION(COMPARE(VAR, LT, VAR)) CALL(FUNC) CALL(FUNC))",
                confidence_boost=0.2,
                post_normalized=True
            ),
        ]
    
    def _load_domain_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load domain-specific pattern rules."""
        return {
            "h264": {
                "file_patterns": [r"h264", r"avc", r"x264"],
                "required_includes": ["h264", "cabac", "cavlc"],
                "context_keywords": ["macroblock", "slice", "nal", "sps", "pps"]
            },
            "aac": {
                "file_patterns": [r"aac", r"m4a"],
                "required_includes": ["aac", "psychoacoustic"],
                "context_keywords": ["spectral", "huffman", "temporal", "perceptual"]
            },
            "video": {
                "file_patterns": [r"video", r"codec", r"encode", r"decode"],
                "context_keywords": ["frame", "picture", "motion", "prediction", "transform"]
            },
            "audio": {
                "file_patterns": [r"audio", r"sound", r"pcm"],
                "context_keywords": ["sample", "channel", "frequency", "spectrum"]
            }
        }
    
    def match_signatures(self, code: str, normalized_code: str, 
                        language: str, file_path: str = "") -> List[Dict[str, Any]]:
        """
        Match code against signature database.
        
        Args:
            code: Original source code
            normalized_code: Normalized representation
            language: Programming language
            file_path: File path for domain detection
            
        Returns:
            List of matched algorithms with confidence scores
        """
        matches = []
        domain = self._detect_domain(code, file_path)
        
        # Get relevant signatures based on domain
        relevant_signatures = []
        if domain in self.signatures:
            relevant_signatures.extend(self.signatures[domain])
        relevant_signatures.extend(self.signatures["general"])
        
        # Match against each signature
        for signature in relevant_signatures:
            confidence = self._match_single_signature(
                signature, code, normalized_code, language, domain
            )
            
            if confidence > 0.5:  # Threshold for accepting match
                matches.append({
                    "algorithm_type": signature.algorithm_type,
                    "algorithm_subtype": signature.algorithm_subtype,
                    "confidence": confidence,
                    "signature_name": signature.name,
                    "domain": signature.domain,
                    "detection_method": "signature_matching"
                })
        
        # Deduplicate and merge similar matches
        return self._merge_matches(matches)
    
    def _detect_domain(self, code: str, file_path: str) -> str:
        """Detect the domain of the code."""
        code_lower = code.lower()
        file_lower = file_path.lower()
        
        # Check each domain's patterns
        for domain, patterns in self.domain_patterns.items():
            # Check file patterns
            if any(re.search(pattern, file_lower) for pattern in patterns.get("file_patterns", [])):
                return domain
            
            # Check context keywords
            keyword_count = sum(1 for keyword in patterns.get("context_keywords", []) 
                              if keyword in code_lower)
            if keyword_count >= 3:  # At least 3 context keywords
                return domain
        
        return "general"
    
    def _match_single_signature(self, signature: AlgorithmSignature, 
                               code: str, normalized_code: str, 
                               language: str, domain: str) -> float:
        """Match a single signature against code."""
        confidence = 0.0
        
        # Select appropriate code version
        if signature.pre_normalized and not signature.post_normalized:
            target_code = code
        elif signature.post_normalized and not signature.pre_normalized:
            target_code = normalized_code
        else:
            # Try both
            target_code = code + "\n" + normalized_code
        
        # Apply signature type specific matching
        if signature.signature_type == SignatureType.EXACT:
            if signature.pattern in target_code:
                confidence = 0.8
        
        elif signature.signature_type == SignatureType.REGEX:
            matches = re.findall(signature.pattern, target_code, re.IGNORECASE | re.DOTALL)
            if len(matches) >= signature.min_matches:
                confidence = min(0.6 + 0.1 * len(matches), 0.9)
        
        elif signature.signature_type == SignatureType.STRUCTURAL:
            # Simplified structural matching
            if all(component in normalized_code for component in signature.pattern.split()):
                confidence = 0.7
        
        elif signature.signature_type == SignatureType.NORMALIZED:
            # Match against normalized representation
            if signature.pattern in normalized_code:
                confidence = 0.75
        
        # Check required context
        if confidence > 0 and signature.required_context:
            context_matches = sum(1 for ctx in signature.required_context 
                                if ctx.lower() in code.lower())
            context_ratio = context_matches / len(signature.required_context)
            confidence *= (0.5 + 0.5 * context_ratio)
        
        # Apply confidence boost
        confidence += signature.confidence_boost
        
        # Domain matching bonus
        if domain == signature.domain:
            confidence *= 1.2
        
        return min(confidence, 1.0)
    
    def _merge_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge similar matches and deduplicate."""
        if not matches:
            return []
        
        # Group by algorithm type and subtype
        grouped = {}
        for match in matches:
            key = (match["algorithm_type"], match["algorithm_subtype"])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(match)
        
        # Merge each group
        merged = []
        for (algo_type, algo_subtype), group in grouped.items():
            # Take the highest confidence match
            best_match = max(group, key=lambda x: x.get("confidence", 0) if x.get("confidence") is not None else 0)
            
            # Aggregate evidence from all matches
            all_signatures = list(set(m["signature_name"] for m in group))
            best_match["matched_signatures"] = all_signatures
            best_match["match_count"] = len(group)
            
            # Boost confidence if multiple signatures matched
            if len(group) > 1:
                best_match["confidence"] = min(best_match["confidence"] * (1 + 0.1 * (len(group) - 1)), 1.0)
            
            merged.append(best_match)
        
        return sorted(merged, key=lambda x: x.get("confidence", 0) if x.get("confidence") is not None else 0, reverse=True)