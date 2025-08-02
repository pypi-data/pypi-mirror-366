"""
Domain-specific algorithm detection with enhanced pattern matching.

This module provides specialized detection for multimedia codecs,
cryptographic algorithms, and other domain-specific implementations.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .signature_matcher import SignatureMatcher
from .algorithmic_normalizer import AlgorithmicNormalizer
from .domain_patterns import get_pattern_manager

logger = logging.getLogger(__name__)


class DomainSpecificDetector:
    """
    Enhanced algorithm detection with domain-specific knowledge.
    
    Features:
    - Multimedia codec pattern recognition
    - Mathematical transform detection
    - Cryptographic algorithm identification
    - Pre/post normalization matching
    """
    
    def __init__(self):
        """Initialize domain-specific detector."""
        self.signature_matcher = SignatureMatcher()
        self.normalizer = AlgorithmicNormalizer()
        self.pattern_manager = get_pattern_manager()
        # Initialize analyzers after pattern manager is created
        self.domain_analyzers = {
            "video": VideoCodecAnalyzer(),
            "audio": AudioCodecAnalyzer(),
            "crypto": CryptoAnalyzer(),
            "math": MathematicalAnalyzer()
        }
    
    def detect_algorithms(self, code: str, language: str, 
                         file_path: str = "", ast_tree: Any = None) -> List[Dict[str, Any]]:
        """
        Detect algorithms using domain-specific knowledge.
        
        Args:
            code: Source code to analyze
            language: Programming language
            file_path: File path for context
            ast_tree: Optional AST for structural analysis
            
        Returns:
            List of detected algorithms with high confidence
        """
        logger.debug(f"DomainSpecificDetector called with file_path: {file_path}, language: {language}")
        results = []
        
        # Generate normalized representation
        normalized_code = ""
        if ast_tree:
            try:
                normalized_code = self.normalizer.normalize_function(None, code, language)
            except:
                pass
        
        # Signature-based matching
        signature_matches = self.signature_matcher.match_signatures(
            code, normalized_code, language, file_path
        )
        results.extend(signature_matches)
        
        # Domain-specific analysis
        for domain, analyzer in self.domain_analyzers.items():
            is_applicable = analyzer.is_applicable(code, file_path)
            logger.debug(f"  {domain} analyzer is_applicable: {is_applicable}")
            if is_applicable:
                domain_matches = analyzer.analyze(code, normalized_code, language)
                logger.info(f"  {domain} analyzer detected {len(domain_matches)} algorithms")
                results.extend(domain_matches)
        
        # Merge and deduplicate results
        return self._merge_results(results)
    
    def _merge_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate detection results."""
        if not results:
            return []
        
        # Group by algorithm
        grouped = defaultdict(list)
        for result in results:
            key = (result.get("algorithm_type"), result.get("algorithm_subtype"))
            grouped[key].append(result)
        
        # Merge each group
        merged = []
        for (algo_type, algo_subtype), group in grouped.items():
            # Combine evidence and take highest confidence
            best = max(group, key=lambda x: x.get("confidence", 0) if x.get("confidence") is not None else 0)
            
            # Aggregate detection methods
            methods = list(set(r.get("detection_method", "unknown") for r in group))
            best["detection_methods"] = methods
            best["detection_count"] = len(group)
            
            # Boost confidence for multiple detections
            if len(group) > 1:
                best["confidence"] = min(best["confidence"] * 1.2, 1.0)
            
            merged.append(best)
        
        return sorted(merged, key=lambda x: x.get("confidence", 0), reverse=True)


class VideoCodecAnalyzer:
    """Specialized analyzer for video codec algorithms."""
    
    def __init__(self):
        self.pattern_manager = get_pattern_manager()
    
    def is_applicable(self, code: str, file_path: str) -> bool:
        """Check if this analyzer should be used."""
        indicators = ["h264", "h265", "hevc", "avc", "video", "codec", "yuv", "macroblock", "cavlc", "cabac"]
        code_lower = code.lower()
        path_lower = file_path.lower()
        
        return any(ind in code_lower or ind in path_lower for ind in indicators)
    
    def analyze(self, code: str, normalized_code: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code for video codec algorithms."""
        results = []
        
        # Video codec IDCT patterns (H.264/VP9/HEVC)
        if self._detect_h264_idct(code):
            results.append({
                "algorithm_type": "mathematical_transform",
                "algorithm_subtype": "inverse_discrete_cosine_transform",
                "confidence": 0.85,
                "domain": "video",
                "detection_method": "domain_specific_video",
                "evidence": "Video IDCT butterfly operations detected (H.264/VP9/HEVC style)"
            })
        
        if self._detect_cabac(code):
            results.append({
                "algorithm_type": "entropy_encoding",
                "algorithm_subtype": "cabac",
                "confidence": 0.9,
                "domain": "h264",
                "detection_method": "domain_specific_video",
                "evidence": "CABAC context tables and arithmetic coding detected"
            })
        
        if self._detect_cavlc(code):
            results.append({
                "algorithm_type": "entropy_encoding",
                "algorithm_subtype": "cavlc",
                "confidence": 0.85,
                "domain": "h264",
                "detection_method": "domain_specific_video",
                "evidence": "CAVLC variable length coding detected"
            })
        
        if self._detect_deblocking_filter(code):
            results.append({
                "algorithm_type": "image_filtering",
                "algorithm_subtype": "deblocking_filter",
                "confidence": 0.8,
                "domain": "video",
                "detection_method": "domain_specific_video",
                "evidence": "Deblocking filter with strength calculation detected"
            })
        
        if self._detect_motion_prediction(code):
            results.append({
                "algorithm_type": "video_compression",
                "algorithm_subtype": "motion_prediction",
                "confidence": 0.75,
                "domain": "video",
                "detection_method": "domain_specific_video",
                "evidence": "Motion vector prediction detected"
            })
        
        # HEVC-specific transforms
        if self._detect_hevc_transform(code):
            results.append({
                "algorithm_type": "mathematical_transform",
                "algorithm_subtype": "hevc_transform",
                "confidence": 0.8,
                "domain": "hevc",
                "detection_method": "domain_specific_video",
                "evidence": "HEVC transform with even/odd decomposition detected"
            })
        
        # SAO filter (HEVC/AV1)
        if self._detect_sao_filter(code):
            results.append({
                "algorithm_type": "video_filter",
                "algorithm_subtype": "sample_adaptive_offset",
                "confidence": 0.85,
                "domain": "hevc",
                "detection_method": "domain_specific_video",
                "evidence": "Sample Adaptive Offset (SAO) filter detected"
            })
        
        return results
    
    def _detect_h264_idct(self, code: str) -> bool:
        """Detect video IDCT implementation (H.264/VP9/HEVC)."""
        # Check for known IDCT function names first
        if self.pattern_manager.check_function_names(code, "video_codec", "idct"):
            logger.debug(f"    IDCT detected via function name")
            return True
        
        # Look for characteristic butterfly operations
        patterns = [
            r"[zt][0-3]\s*=.*?(block|tmp|coeffs).*?\+.*?(block|tmp|coeffs)",
            r"[zt][0-3]\s*=.*?(block|tmp|coeffs).*?\-.*?(block|tmp|coeffs)",
            r"(SUINT|int|int16_t|int32_t)\s+[zt][0-3]\s*[,;=]",
            r"(block|coeffs)\[.*?\+.*?\*.*?\d+\]",
            r"(dst|out)\[.*?(stride|\*).*?\].*?=.*?(av_)?clip"
        ]
        
        # Also check variable patterns from config
        identifier_matches = self.pattern_manager.check_all_identifiers(code, "video_codec", "idct")
        config_matches = sum(v for v in identifier_matches.values())
        
        pattern_matches = sum(1 for p in patterns if re.search(p, code))
        total_matches = pattern_matches + (1 if config_matches > 0 else 0)
        
        logger.debug(f"    IDCT pattern matches: {pattern_matches}/5 patterns, {config_matches} identifiers")
        return total_matches >= 3
    
    def _detect_cabac(self, code: str) -> bool:
        """Detect CABAC entropy coding."""
        patterns = [
            r"cabac_context_init.*?\[.*?\]\[.*?\]",
            r"(cabac|CABAC).*?(state|context)",
            r"get_cabac|put_cabac",
            r"ff_h264_cabac_tables",
            r"(range|low).*?<<.*?CABAC_BITS"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_cavlc(self, code: str) -> bool:
        """Detect CAVLC entropy coding."""
        patterns = [
            r"(cavlc|CAVLC)",
            r"coeff_token",
            r"total_zeros",
            r"run_before",
            r"level_prefix"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_deblocking_filter(self, code: str) -> bool:
        """Detect deblocking filter."""
        patterns = [
            r"deblock|loop_?filter",
            r"(alpha|beta|tc0).*?(filter|strength)",
            r"filter_mb_edge",
            r"bs\s*\[.*?\].*?=.*?strength"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_motion_prediction(self, code: str) -> bool:
        """Detect motion prediction algorithms."""
        patterns = [
            r"(mv|motion).*?(pred|vector)",
            r"median.*?(mv|motion)",
            r"(left|top|diag).*?mv",
            r"motion.*?compensation"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_hevc_transform(self, code: str) -> bool:
        """Detect HEVC-specific transform."""
        patterns = [
            r"[eo]\[?\d*\]?\s*=.*?coeffs.*?[+-].*?coeffs",  # e[0] = coeffs[0] + coeffs[3]
            r"hevc_transform",
            r"(e|o)\[0\].*?\+.*?(e|o)\[1\]",  # Even/odd decomposition
            r"transform.*?luma|chroma",
            r"\*\s*\d+\s*[+-]\s*.*?\*\s*\d+"  # Transform coefficients like 83*x + 36*y
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_sao_filter(self, code: str) -> bool:
        """Detect Sample Adaptive Offset filter."""
        patterns = [
            r"sao_filter|SAO",
            r"sao_offset|sao_tab",
            r"(edge|band).*?offset",
            r"CTB.*?filter",
            r"av_clip.*?sao"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2


class AudioCodecAnalyzer:
    """Specialized analyzer for audio codec algorithms."""
    
    def __init__(self):
        self.pattern_manager = get_pattern_manager()
    
    def is_applicable(self, code: str, file_path: str) -> bool:
        """Check if this analyzer should be used."""
        indicators = ["aac", "mp3", "audio", "pcm", "psychoacoustic", "spectral"]
        code_lower = code.lower()
        path_lower = file_path.lower()
        
        return any(ind in code_lower or ind in path_lower for ind in indicators)
    
    def analyze(self, code: str, normalized_code: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code for audio codec algorithms."""
        results = []
        
        if self._detect_psychoacoustic_model(code):
            results.append({
                "algorithm_type": "audio_codec",
                "algorithm_subtype": "psychoacoustic_model",
                "confidence": 0.85,
                "domain": "audio",
                "detection_method": "domain_specific_audio",
                "evidence": "Psychoacoustic model with spreading functions detected"
            })
        
        if self._detect_mdct(code):
            results.append({
                "algorithm_type": "mathematical_transform",
                "algorithm_subtype": "modified_discrete_cosine_transform",
                "confidence": 0.8,
                "domain": "audio",
                "detection_method": "domain_specific_audio",
                "evidence": "MDCT transform for audio detected"
            })
        
        return results
    
    def _detect_psychoacoustic_model(self, code: str) -> bool:
        """Detect psychoacoustic model implementation."""
        patterns = [
            r"PSY_.*?(SPREAD|THR|MASK)",
            r"psychoacoustic|perceptual",
            r"bark.*?scale",
            r"masking.*?threshold",
            r"spreading.*?function"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_mdct(self, code: str) -> bool:
        """Detect MDCT transform."""
        # Check for known MDCT function names first
        if self.pattern_manager.check_function_names(code, "audio_codec", "mdct"):
            logger.debug(f"    MDCT detected via function name")
            return True
        
        patterns = [
            r"mdct|MDCT",
            r"imdct|IMDCT",  # Inverse MDCT
            r"modified.*?discrete.*?cosine",
            r"(vector_fmul_)?window",  # Windowing operations
            r"window.*?(overlap|sequence)",
            r"time.*?frequency.*?transform",
            r"spectral.*?to.*?sample",  # Common in audio codecs
            r"buf_mdct|mdct.*?half"  # MDCT-specific buffer/function names
        ]
        
        # Also check identifiers from config
        identifier_matches = self.pattern_manager.check_all_identifiers(code, "audio_codec", "mdct")
        config_matches = sum(v for v in identifier_matches.values())
        
        pattern_matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        total_matches = pattern_matches + (1 if config_matches > 0 else 0)
        
        logger.debug(f"    MDCT pattern matches: {pattern_matches} patterns, {config_matches} identifiers")
        # More lenient: require only 2 matches since MDCT is often implicit
        return total_matches >= 2


class CryptoAnalyzer:
    """Specialized analyzer for cryptographic algorithms."""
    
    def __init__(self):
        self.pattern_manager = get_pattern_manager()
    
    def is_applicable(self, code: str, file_path: str) -> bool:
        """Check if this analyzer should be used."""
        indicators = ["crypto", "cipher", "hash", "sha", "aes", "rsa", "encrypt"]
        code_lower = code.lower()
        path_lower = file_path.lower()
        
        return any(ind in code_lower or ind in path_lower for ind in indicators)
    
    def analyze(self, code: str, normalized_code: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code for cryptographic algorithms."""
        results = []
        
        if self._detect_aes(code):
            results.append({
                "algorithm_type": "cryptographic",
                "algorithm_subtype": "aes",
                "confidence": 0.9,
                "domain": "crypto",
                "detection_method": "domain_specific_crypto",
                "evidence": "AES S-box and round operations detected"
            })
        
        if self._detect_sha256(code):
            results.append({
                "algorithm_type": "cryptographic",
                "algorithm_subtype": "sha256",
                "confidence": 0.95,
                "domain": "crypto",
                "detection_method": "domain_specific_crypto",
                "evidence": "SHA-256 constants and operations detected"
            })
        
        return results
    
    def _detect_aes(self, code: str) -> bool:
        """Detect AES implementation."""
        patterns = [
            r"(sbox|s_box).*?\[256\]",
            r"(SubBytes|ShiftRows|MixColumns|AddRoundKey)",
            r"aes_(encrypt|decrypt|key_schedule)",
            r"rijndael"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_sha256(self, code: str) -> bool:
        """Detect SHA-256 implementation."""
        # SHA-256 constants
        sha256_constants = [
            "0x428a2f98", "0x71374491", "0xb5c0fbcf", "0xe9b5dba5"
        ]
        
        constant_matches = sum(1 for c in sha256_constants if c in code)
        
        patterns = [
            r"sha256|SHA256",
            r"(Ch|Maj|Sigma0|Sigma1).*?\(",
            r"(rotate_right|rotr).*?(2|6|7|11|13|17|18|19|22|25)"
        ]
        
        pattern_matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        
        return constant_matches >= 2 or pattern_matches >= 2


class MathematicalAnalyzer:
    """Specialized analyzer for mathematical algorithms."""
    
    def __init__(self):
        self.pattern_manager = get_pattern_manager()
    
    def is_applicable(self, code: str, file_path: str) -> bool:
        """Check if this analyzer should be used."""
        indicators = ["fft", "dct", "transform", "matrix", "convolution"]
        code_lower = code.lower()
        path_lower = file_path.lower()
        
        return any(ind in code_lower or ind in path_lower for ind in indicators)
    
    def analyze(self, code: str, normalized_code: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code for mathematical algorithms."""
        results = []
        
        if self._detect_fft(code):
            results.append({
                "algorithm_type": "mathematical_transform",
                "algorithm_subtype": "fast_fourier_transform",
                "confidence": 0.85,
                "domain": "dsp",
                "detection_method": "domain_specific_math",
                "evidence": "FFT butterfly operations detected"
            })
        
        if self._detect_matrix_multiplication(code, normalized_code):
            results.append({
                "algorithm_type": "mathematical_algorithm",
                "algorithm_subtype": "matrix_multiplication",
                "confidence": 0.8,
                "domain": "math",
                "detection_method": "domain_specific_math",
                "evidence": "Triple nested loops with matrix indexing detected"
            })
        
        return results
    
    def _detect_fft(self, code: str) -> bool:
        """Detect FFT implementation."""
        patterns = [
            r"(fft|FFT)",
            r"butterfly.*?(real|imag)",
            r"twiddle.*?factor",
            r"bit.*?reverse",
            r"cooley.*?tukey"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2
    
    def _detect_matrix_multiplication(self, code: str, normalized_code: str) -> bool:
        """Detect matrix multiplication."""
        # Check normalized pattern
        if "LOOP(LOOP(LOOP(" in normalized_code and "MULT" in normalized_code:
            return True
        
        # Check original code patterns
        patterns = [
            r"for.*?for.*?for.*?(\+=|\*=)",
            r"matrix.*?multiply",
            r"\[i\].*?\[j\].*?\[k\]",
            r"(row|col).*?\*.*?(row|col)"
        ]
        
        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2