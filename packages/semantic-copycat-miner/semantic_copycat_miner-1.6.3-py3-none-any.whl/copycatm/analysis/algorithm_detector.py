"""
Algorithm detector with better specificity to reduce over-similarity.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
import hashlib

logger = logging.getLogger(__name__)

from .algorithm_types import AlgorithmType
from .algorithmic_normalizer import AlgorithmicNormalizer
from .unknown_algorithm_detector import UnknownAlgorithmDetector
from .transformation_resistance_calculator import TransformationResistanceCalculator
from .pattern_loader import pattern_loader
from .minified_detector import MinifiedCodeDetector
from .domain_detector import DomainSpecificDetector
from ..core.config import AnalysisConfig
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy_improved import ImprovedFuzzyHasher
from ..hashing.semantic import SemanticHasher
from ..data.language_configs import (
    get_language_config, 
    detect_oss_signatures,
    get_enhanced_patterns,
    ALGORITHM_PATTERNS
)
import uuid


class AlgorithmDetector:
    """Algorithm detector with improved pattern matching specificity."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        # Load patterns from external file
        self.external_patterns = self._load_external_patterns()
        # Initialize specific patterns as fallback
        self.patterns = self._initialize_specific_patterns()
        # Initialize minified code detector
        self.minified_detector = MinifiedCodeDetector()
        # Initialize domain-specific detector
        self.domain_detector = DomainSpecificDetector()
        
        # Define pattern checking priority (higher priority checked first)
        self.pattern_priority = [
            # Core algorithms have highest priority
            AlgorithmType.SORTING_ALGORITHM,       # Sorting algorithms first
            AlgorithmType.SEARCH_ALGORITHM,        # Search algorithms
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM, # Crypto patterns (high confidence)
            AlgorithmType.DYNAMIC_PROGRAMMING,     # DP patterns
            AlgorithmType.NUMERICAL_ALGORITHM,     # Mathematical patterns
            AlgorithmType.COMPRESSION_ALGORITHM,   # Compression algorithms
            
            # Media codecs and processing (require media context)
            AlgorithmType.AUDIO_CODEC,             # Audio codec patterns
            AlgorithmType.VIDEO_CODEC,             # Video codec patterns
            AlgorithmType.VIDEO_PROCESSING,        # Video processing algorithms
            AlgorithmType.AUDIO_PROCESSING,        # Audio processing algorithms  
            AlgorithmType.IMAGE_PROCESSING,        # Image processing algorithms
            AlgorithmType.SIGNAL_PROCESSING,       # Signal processing algorithms
            
            # General patterns
            AlgorithmType.ENCODING_ALGORITHM,      # Encoding algorithms
            AlgorithmType.ITERATOR_PATTERN,        # Iterator patterns
            AlgorithmType.POLYFILL_PATTERN,        # Polyfill patterns
            AlgorithmType.ARRAY_MANIPULATION,      # Array operations
            AlgorithmType.OBJECT_MANIPULATION,     # Object operations
        ]
        
        # Initialize components for hashing
        self.transformation_calculator = TransformationResistanceCalculator()
        
        # Store data for dynamic transformation resistance calculation
        self.last_algorithm_data = {}
        self.last_ast_data = {}
        self.last_hash_data = {}
        self.last_invariants = []
        self.normalizer = AlgorithmicNormalizer()
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = ImprovedFuzzyHasher()
        self.semantic_hasher = SemanticHasher(num_perm=128, lsh_bands=config.lsh_bands if config else 20)
        
        # Initialize unknown algorithm detector
        self.unknown_detector = UnknownAlgorithmDetector(min_complexity_score=0.6)
    
    def _load_external_patterns(self) -> Dict[str, Dict]:
        """Load algorithm patterns from external JSON file."""
        try:
            return pattern_loader.get_algorithm_patterns()
        except Exception as e:
            print(f"Warning: Could not load external patterns: {e}")
            return {}
    
    def _check_external_patterns_enhanced(self, func_text: str, func_name: str, normalized_text: str = "") -> Optional[Dict[str, Any]]:
        """Check function against external pattern definitions with transformation resistance."""
        best_match = None
        best_score = 0.0
        
        for algo_type, type_patterns in self.external_patterns.items():
            for algo_name, pattern_config in type_patterns.items():
                score = 0.0
                
                # Check keywords in both original and normalized text
                keywords = pattern_config.get('keywords', [])
                keyword_matches = sum(1 for kw in keywords 
                                    if kw in func_text or kw in func_name or (normalized_text and kw in normalized_text))
                if keyword_matches > 0:
                    score += min(keyword_matches * 0.2, 0.6)
                
                # Check required patterns in both texts
                required = pattern_config.get('required_patterns', [])
                required_matches = 0
                for pattern in required:
                    # Check if pattern is a regex (contains |, *, +, etc.)
                    if any(c in pattern for c in '|*+?[]()'):
                        if re.search(pattern, func_text, re.IGNORECASE) or (normalized_text and re.search(pattern, normalized_text, re.IGNORECASE)):
                            required_matches += 1
                    else:
                        if pattern in func_text or (normalized_text and pattern in normalized_text):
                            required_matches += 1
                if required and required_matches == len(required):
                    score += 0.3
                elif required and required_matches > 0:
                    score += 0.1 * (required_matches / len(required))
                
                # Special check for function name
                if pattern_config.get('check_function_name', False):
                    if algo_name in func_name or any(kw in func_name for kw in keywords[:3]):
                        score += 0.3
                
                # Apply confidence from pattern
                base_confidence = pattern_config.get('confidence', 0.7)
                final_score = min(score * base_confidence, 1.0)
                
                if final_score > best_score:
                    best_score = final_score
                    # Try to map to AlgorithmType enum
                    try:
                        algo_type_enum = AlgorithmType(algo_type)
                    except ValueError:
                        # If not a valid enum, use the string as-is
                        algo_type_enum = algo_type.upper()
                    
                    # Normalize audio codec subtypes
                    normalized_subtype = algo_name
                    if algo_type == 'audio_codec' and algo_name in ['pcm', 'pcm_codec', 'alaw', 'ulaw', 'g711a', 'g711u']:
                        normalized_subtype = 'audio_codec'
                    
                    best_match = {
                        'type': algo_type_enum,
                        'subtype': normalized_subtype,
                        'confidence': final_score,
                        'original_subtype': algo_name
                    }
        
        return best_match if best_score >= 0.5 else None
    
    def _check_external_patterns(self, func_text: str, func_name: str) -> Optional[Dict[str, Any]]:
        """Legacy method for backward compatibility."""
        return self._check_external_patterns_enhanced(func_text, func_name)
        
    def _initialize_specific_patterns(self) -> Dict[AlgorithmType, Dict]:
        """Initialize highly specific algorithm patterns to reduce false positives."""
        return {
            # Object manipulation algorithms
            AlgorithmType.OBJECT_MANIPULATION: {
                'subtypes': {
                    'object_merge': {
                        'keywords': ['assign', 'merge', 'extend'],
                        'required_patterns': ['property_iteration', 'property_copy', 'hasOwnProperty'],
                        'ast_patterns': ['for_in_loop', 'property_assignment'],
                        'confidence_boost': 0.3
                    },
                    'object_spread': {
                        'keywords': ['__rest', 'spread', 'getOwnPropertySymbols'],
                        'required_patterns': ['property_enumeration', 'symbol_handling'],
                        'ast_patterns': ['property_iteration', 'symbol_check'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Array manipulation algorithms
            AlgorithmType.ARRAY_MANIPULATION: {
                'subtypes': {
                    'array_spread': {
                        'keywords': ['__spread', '__spreadArrays', '__spreadArray'],
                        'required_patterns': ['nested_loops', 'array_indexing', 'length_accumulation'],
                        'ast_patterns': ['for_loop', 'array_assignment'],
                        'confidence_boost': 0.3
                    },
                    'array_concat': {
                        'keywords': ['concat', 'merge', 'flatten'],
                        'required_patterns': ['array_iteration', 'element_copy'],
                        'ast_patterns': ['loop', 'array_access'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Iterator patterns
            AlgorithmType.ITERATOR_PATTERN: {
                'subtypes': {
                    'iterator_protocol': {
                        'keywords': ['__values', 'Symbol.iterator', 'next', 'done'],
                        'required_patterns': ['iterator_interface', 'state_tracking'],
                        'ast_patterns': ['object_return', 'method_definition'],
                        'confidence_boost': 0.3
                    },
                    'async_generator': {
                        'keywords': ['__asyncGenerator', '__await', 'Promise'],
                        'required_patterns': ['state_machine', 'promise_handling'],
                        'ast_patterns': ['switch_statement', 'promise_call'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Polyfill patterns
            AlgorithmType.POLYFILL_PATTERN: {
                'subtypes': {
                    'object_assign_polyfill': {
                        'keywords': ['Object.assign', '__assign'],
                        'required_patterns': ['native_check', 'fallback_loop'],
                        'ast_patterns': ['or_operator', 'for_loop'],
                        'confidence_boost': 0.3
                    },
                    'runtime_helper': {
                        'keywords': ['__extends', '__decorate', '__param'],
                        'required_patterns': ['helper_pattern', 'prototype_chain'],
                        'ast_patterns': ['function_assignment', 'prototype_access'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Sorting algorithms - very specific patterns
            AlgorithmType.SORTING_ALGORITHM: {
                'subtypes': {
                    'quicksort': {
                        'keywords': ['quicksort', 'quick_sort', 'pivot', 'partition', 'QuickSort'],
                        'required_patterns': ['pivot_selection', 'partition_logic', 'recursive_calls'],
                        'ast_patterns': ['recursive_function', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'bubble_sort': {
                        'keywords': ['bubble_sort', 'bubble'],
                        'required_patterns': ['nested_loops', 'adjacent_comparison', 'swap_operation'],
                        'ast_patterns': ['double_for_loop', 'comparison', 'assignment'],
                        'confidence_boost': 0.4
                    },
                    'merge_sort': {
                        'keywords': ['merge_sort', 'merge', 'divide'],
                        'required_patterns': ['merge_function', 'divide_conquer', 'recursive_calls'],
                        'ast_patterns': ['recursive_function', 'array_split'],
                        'confidence_boost': 0.3
                    },
                    'heap_sort': {
                        'keywords': ['heap_sort', 'heapify', 'heap'],
                        'required_patterns': ['heapify_operation', 'parent_child_comparison', 'swap_operation'],
                        'ast_patterns': ['loop', 'comparison', 'assignment'],
                        'confidence_boost': 0.3
                    },
                    'generic_sort': {
                        'keywords': ['sort', 'compare'],
                        'required_patterns': ['comparison_operation', 'element_swap'],
                        'ast_patterns': ['loop', 'comparison', 'assignment'],
                        'confidence_boost': -0.1  # Penalty for generic
                    }
                }
            },
            
            # Search algorithms - distinct patterns
            AlgorithmType.SEARCH_ALGORITHM: {
                'subtypes': {
                    'binary_search': {
                        'keywords': ['binary', 'mid', 'middle', 'left', 'right'],
                        'required_patterns': ['mid_calculation', 'binary_division', 'comparison_with_target', 'range_adjustment'],
                        'ast_patterns': ['while_loop_or_recursion', 'arithmetic_operation', 'comparison', 'assignment'],
                        'confidence_boost': 0.3
                    },
                    'linear_search': {
                        'keywords': ['find', 'search', 'linear'],
                        'required_patterns': ['single_loop', 'element_comparison', 'return_on_match'],
                        'ast_patterns': ['for_loop', 'if_statement', 'return_statement'],
                        'confidence_boost': 0.2
                    },
                    'generic_search': {
                        'keywords': ['search', 'find', 'locate'],
                        'required_patterns': ['iteration', 'comparison'],
                        'ast_patterns': ['loop', 'comparison'],
                        'confidence_boost': -0.2  # Penalty for generic
                    }
                }
            },
            
            # Mathematical algorithms - unique patterns
            AlgorithmType.NUMERICAL_ALGORITHM: {
                'subtypes': {
                    'fibonacci': {
                        'keywords': ['fibonacci', 'fib'],
                        'required_patterns': ['n_minus_1', 'n_minus_2', 'addition'],
                        'ast_patterns': ['recursive_or_iterative', 'arithmetic_operation'],
                        'confidence_boost': 0.4
                    },
                    'factorial': {
                        'keywords': ['factorial', 'fact'],
                        'required_patterns': ['n_multiplication', 'decremental_loop_or_recursion'],
                        'ast_patterns': ['multiplication', 'decrement'],
                        'confidence_boost': 0.3
                    },
                    'prime': {
                        'keywords': ['prime', 'divisor'],
                        'required_patterns': ['modulo_operation', 'divisibility_check'],
                        'ast_patterns': ['modulo', 'loop', 'comparison'],
                        'confidence_boost': 0.2
                    },
                    'gcd': {
                        'keywords': ['gcd', 'greatest', 'common', 'divisor'],
                        'required_patterns': ['modulo_operation', 'swap_or_recursion', 'while_with_modulo'],
                        'ast_patterns': ['modulo', 'while_loop_or_recursion'],
                        'confidence_boost': 0.3
                    },
                    'lcm': {
                        'keywords': ['lcm', 'least', 'common', 'multiple'],
                        'required_patterns': ['multiplication', 'division', 'gcd_call_or_impl'],
                        'ast_patterns': ['multiplication', 'division'],
                        'confidence_boost': 0.3
                    },
                    'power': {
                        'keywords': ['power', 'pow', 'exponent', 'base'],
                        'required_patterns': ['exponent_check', 'recursive_multiplication', 'base_exponent'],
                        'ast_patterns': ['loop_or_recursion', 'multiplication', 'if_statement'],
                        'confidence_boost': 0.4
                    }
                }
            },
            
            # Compression algorithms
            AlgorithmType.COMPRESSION_ALGORITHM: {
                'subtypes': {
                    'huffman': {
                        'keywords': ['huffman', 'frequency', 'encoding'],
                        'required_patterns': ['frequency_counting', 'tree_building', 'encoding'],
                        'ast_patterns': ['hash_map', 'tree_structure'],
                        'confidence_boost': 0.3
                    },
                    'lzw': {
                        'keywords': ['lzw', 'dictionary', 'compress'],
                        'required_patterns': ['dictionary_building', 'pattern_matching'],
                        'ast_patterns': ['hash_map', 'string_manipulation'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Dynamic programming
            AlgorithmType.DYNAMIC_PROGRAMMING: {
                'subtypes': {
                    'memoization': {
                        'keywords': ['memo', 'cache', 'dp'],
                        'required_patterns': ['cache_check', 'cache_store', 'recursive_structure'],
                        'ast_patterns': ['hash_map', 'recursive_function'],
                        'confidence_boost': 0.3
                    },
                    'tabulation': {
                        'keywords': ['table', 'dp', 'dynamic'],
                        'required_patterns': ['table_initialization', 'iterative_filling'],
                        'ast_patterns': ['array_initialization', 'nested_loops'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Cryptographic algorithms
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM: {
                'subtypes': {
                    'rsa': {
                        'keywords': ['rsa', 'modulus', 'exponent', 'public_key', 'private_key', 'modpow', 'rsa_encrypt', 'rsa_decrypt'],
                        'required_patterns': ['modular_exponentiation', 'prime_generation_or_check', 'key_generation'],
                        'ast_patterns': ['modulo_operation', 'exponentiation', 'prime_check'],
                        'confidence_boost': 0.4
                    },
                    'aes': {
                        'keywords': ['aes', 'rijndael', 'block_cipher', 'sbox', 'subbytes', 'shiftrows', 'mixcolumns', 'addroundkey'],
                        'required_patterns': ['substitution_table', 'matrix_operations', 'xor_operations'],
                        'ast_patterns': ['array_lookup', 'bitwise_operations', 'for_loop'],
                        'confidence_boost': 0.4
                    },
                    'sha': {
                        'keywords': ['sha', 'sha1', 'sha256', 'sha512', 'digest', 'hash', 'message_digest'],
                        'required_patterns': ['bit_rotation', 'xor_operations', 'constant_array'],
                        'ast_patterns': ['bitwise_operations', 'array_constants', 'loop'],
                        'confidence_boost': 0.4
                    },
                    'md5': {
                        'keywords': ['md5', 'message_digest', 'hash'],
                        'required_patterns': ['bit_rotation', 'xor_operations', 'four_rounds'],
                        'ast_patterns': ['bitwise_operations', 'loop', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'hmac': {
                        'keywords': ['hmac', 'keyed_hash', 'message_authentication'],
                        'required_patterns': ['key_padding', 'inner_hash', 'outer_hash'],
                        'ast_patterns': ['xor_operations', 'hash_function_call', 'concatenation'],
                        'confidence_boost': 0.3
                    },
                    'diffie_hellman': {
                        'keywords': ['diffie', 'hellman', 'dh', 'key_exchange', 'shared_secret'],
                        'required_patterns': ['modular_exponentiation', 'prime_check', 'generator'],
                        'ast_patterns': ['modulo_operation', 'exponentiation'],
                        'confidence_boost': 0.3
                    },
                    'elliptic_curve': {
                        'keywords': ['elliptic', 'curve', 'ecc', 'ecdsa', 'ecdh', 'point_addition', 'scalar_multiplication'],
                        'required_patterns': ['point_operations', 'modular_arithmetic', 'curve_equation'],
                        'ast_patterns': ['coordinate_operations', 'modulo_operation'],
                        'confidence_boost': 0.4
                    },
                    'chacha20': {
                        'keywords': ['chacha', 'chacha20', 'quarter_round', 'stream_cipher'],
                        'required_patterns': ['quarter_round', 'bit_rotation', 'xor_operations'],
                        'ast_patterns': ['bitwise_operations', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'bcrypt': {
                        'keywords': ['bcrypt', 'blowfish', 'password_hash', 'salt'],
                        'required_patterns': ['salt_generation', 'key_expansion', 'blowfish_operations'],
                        'ast_patterns': ['loop', 'xor_operations', 'substitution'],
                        'confidence_boost': 0.3
                    },
                    'pbkdf2': {
                        'keywords': ['pbkdf2', 'key_derivation', 'iteration_count', 'salt'],
                        'required_patterns': ['hmac_iterations', 'salt_usage', 'xor_accumulation'],
                        'ast_patterns': ['loop', 'hmac_call', 'xor_operations'],
                        'confidence_boost': 0.3
                    },
                    'generic_crypto': {
                        'keywords': ['encrypt', 'decrypt', 'cipher', 'crypto', 'key'],
                        'required_patterns': ['key_usage', 'data_transformation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': -0.1  # Penalty for generic
                    }
                }
            },
            
            # Audio Codec Algorithms
            AlgorithmType.AUDIO_CODEC: {
                'subtypes': {
                    'mp3_codec': {
                        'keywords': ['mp3', 'mpeg', 'layer3', 'layer_3', 'psychoacoustic', 'mdct', 'huffman_decode', 'bit_reservoir', 'granule'],
                        'required_patterns': ['audio_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'aac_codec': {
                        'keywords': ['aac', 'advanced_audio', 'm4a', 'spectral', 'tns', 'pns', 'sbr', 'aac_encode', 'aac_decode'],
                        'required_patterns': ['audio_processing', 'spectral_processing'],
                        'ast_patterns': ['loop', 'transform_operation'],
                        'confidence_boost': 0.3
                    },
                    'opus_codec': {
                        'keywords': ['opus', 'celt', 'silk', 'hybrid_codec', 'opus_encode', 'opus_decode'],
                        'required_patterns': ['audio_processing', 'frame_processing'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'flac_codec': {
                        'keywords': ['flac', 'lossless', 'rice_encoding', 'linear_prediction', 'flac_encode'],
                        'required_patterns': ['audio_processing', 'prediction_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operation'],
                        'confidence_boost': 0.3
                    },
                    'pcm_codec': {
                        'keywords': ['pcm', 'audio_format_pcm', 'pcm_s16', 'pcm_s24', 'raw_audio', 'linear_pcm'],
                        'required_patterns': ['audio_processing'],
                        'ast_patterns': ['assignment', 'array_access'],
                        'confidence_boost': 0.1
                    },
                    'vorbis_codec': {
                        'keywords': ['vorbis', 'ogg', 'libvorbis', 'xiph'],
                        'required_patterns': ['audio_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'ac3_codec': {
                        'keywords': ['ac3', 'ac-3', 'dolby', 'a52'],
                        'required_patterns': ['audio_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.3
                    },
                    'dts_codec': {
                        'keywords': ['dts', 'dca', 'digital_theater'],
                        'required_patterns': ['audio_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'wma_codec': {
                        'keywords': ['wma', 'windows_media_audio', 'wmav'],
                        'required_patterns': ['audio_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'g711_codec': {
                        'keywords': ['g711', 'alaw', 'ulaw', 'mulaw', 'companding'],
                        'required_patterns': ['audio_processing', 'table_lookup'],
                        'ast_patterns': ['array_access', 'bitwise_operations'],
                        'confidence_boost': 0.3
                    },
                    'g722_codec': {
                        'keywords': ['g722', 'adpcm', 'sub_band'],
                        'required_patterns': ['audio_processing', 'filter_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'g729_codec': {
                        'keywords': ['g729', 'acelp', 'conjugate_structure'],
                        'required_patterns': ['audio_processing', 'lpc_analysis'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'amr_codec': {
                        'keywords': ['amr', 'adaptive_multi_rate', 'amrnb', 'amrwb'],
                        'required_patterns': ['audio_processing', 'speech_processing'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'speex_codec': {
                        'keywords': ['speex', 'speech_codec', 'xiph'],
                        'required_patterns': ['audio_processing', 'speech_processing'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'celp_codec': {
                        'keywords': ['celp', 'acelp', 'code_excited', 'lpc', 'linear_prediction'],
                        'required_patterns': ['audio_processing', 'lpc_analysis'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Video Codec Algorithms
            AlgorithmType.VIDEO_CODEC: {
                'subtypes': {
                    'h264': {
                        'keywords': ['h264', 'avc', 'cabac', 'cavlc', 'intra_prediction', 'deblocking_filter', 'h264_encode', 'h264_decode'],
                        'required_patterns': ['video_processing', 'prediction_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'h265': {
                        'keywords': ['h265', 'hevc', 'ctu', 'coding_tree', 'hevc_encode', 'hevc_decode'],
                        'required_patterns': ['video_processing', 'tree_structure'],
                        'ast_patterns': ['loop', 'recursive_structure'],
                        'confidence_boost': 0.3
                    },
                    'vp8': {
                        'keywords': ['vp8', 'webm', 'bool_decoder', 'dct_coefficients', 'vp8_decode'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.3
                    },
                    'vp9': {
                        'keywords': ['vp9', 'superblock', 'transform_size', 'vp9_decode', 'vp9_encode'],
                        'required_patterns': ['video_processing', 'block_processing'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'av1': {
                        'keywords': ['av1', 'aom', 'superres', 'cdef', 'restoration', 'av1_decode'],
                        'required_patterns': ['video_processing', 'filtering_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'mpeg2': {
                        'keywords': ['mpeg2', 'mpeg-2', 'mpegvideo'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'mpeg4': {
                        'keywords': ['mpeg4', 'mpeg-4', 'divx', 'xvid'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'theora': {
                        'keywords': ['theora', 'xiph', 'ogg_video'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.3
                    },
                    'h263_codec': {
                        'keywords': ['h263', 'h.263', 'flv'],
                        'required_patterns': ['video_processing', 'block_processing'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'realvideo': {
                        'keywords': ['real', 'realvideo', 'rv10', 'rv20', 'rv30', 'rv40'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'cinepak': {
                        'keywords': ['cinepak', 'cvid'],
                        'required_patterns': ['video_processing', 'vector_quantization'],
                        'ast_patterns': ['loop', 'array_access'],
                        'confidence_boost': 0.3
                    },
                    'indeo': {
                        'keywords': ['indeo', 'iv31', 'iv32', 'iv50'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'prores': {
                        'keywords': ['prores', 'apple_prores', '422hq', '4444'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'dnxhd': {
                        'keywords': ['dnxhd', 'dnxhr', 'avid'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Video Processing Algorithms
            AlgorithmType.VIDEO_PROCESSING: {
                'subtypes': {
                    'color_space_conversion': {
                        'keywords': ['yuv', 'rgb', 'color_space', 'colorspace', 'bt709', 'bt2020', 'srgb', 'rec709', 'gamma'],
                        'required_patterns': ['color_conversion', 'matrix_operations'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'rate_control': {
                        'keywords': ['rate_control', 'bitrate', 'cbr', 'vbr', 'abr', 'qp_modulation'],
                        'required_patterns': ['rate_calculation', 'control_logic'],
                        'ast_patterns': ['conditional', 'arithmetic_operations'],
                        'confidence_boost': 0.2
                    },
                    'segmentation': {
                        'keywords': ['segment', 'segment_update', 'spatial_segment', 'temporal_segment'],
                        'required_patterns': ['segment_processing', 'boundary_detection'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.2
                    },
                    'prediction': {
                        'keywords': ['intra_pred', 'inter_pred', 'spatial_pred', 'temporal_pred', 'motion_vector'],
                        'required_patterns': ['prediction_logic', 'vector_calculation'],
                        'ast_patterns': ['conditional', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'loop_filter': {
                        'keywords': ['loop_filter', 'deblock', 'filter_edge', 'filter_strength'],
                        'required_patterns': ['filtering_operation', 'edge_detection'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.2
                    },
                    'motion_estimation': {
                        'keywords': ['motion_estimation', 'motion_vector', 'block_matching'],
                        'required_patterns': ['video_processing', 'block_comparison', 'vector_calculation'],
                        'ast_patterns': ['nested_loops', 'comparison'],
                        'confidence_boost': 0.3
                    },
                    'dct_transform': {
                        'keywords': ['dct', 'idct', 'discrete_cosine', 'transform_coefficients'],
                        'required_patterns': ['transform_operation', 'matrix_multiplication'],
                        'ast_patterns': ['nested_loops', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'quantization': {
                        'keywords': ['quantiz', 'dequantiz', 'quant_table', 'quant_matrix', 'scalar_quant', 'vector_quant'],
                        'required_patterns': ['video_processing', 'division_operation', 'rounding_operation'],
                        'ast_patterns': ['arithmetic_operations', 'array_access'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Audio Processing Algorithms
            AlgorithmType.AUDIO_PROCESSING: {
                'subtypes': {
                    'fft_transform': {
                        'keywords': ['fft', 'fast_fourier', 'dft', 'frequency_domain', 'spectrum'],
                        'required_patterns': ['complex_arithmetic', 'butterfly_operation'],
                        'ast_patterns': ['nested_loops', 'complex_operations'],
                        'confidence_boost': 0.4
                    },
                    'psychoacoustic': {
                        'keywords': ['psychoacoustic', 'masking', 'perceptual', 'bark_scale', 'temporal_mask', 'spectral_mask'],
                        'required_patterns': ['frequency_analysis', 'threshold_calculation'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'resampling': {
                        'keywords': ['resample', 'sample_rate', 'upsample', 'downsample', 'interpolation', 'decimation'],
                        'required_patterns': ['filter_processing', 'sample_rate_conversion'],
                        'ast_patterns': ['loop', 'filter_operation'],
                        'confidence_boost': 0.3
                    },
                    'echo_effect': {
                        'keywords': ['echo', 'delay', 'reverb', 'feedback', 'delay_line'],
                        'required_patterns': ['delay_processing', 'feedback_loop'],
                        'ast_patterns': ['loop', 'buffer_operation'],
                        'confidence_boost': 0.2
                    },
                    'noise_reduction': {
                        'keywords': ['noise_reduction', 'denoise', 'noise_gate', 'spectral_subtraction'],
                        'required_patterns': ['spectral_analysis', 'threshold_operation'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.2
                    },
                    'audio_filter': {
                        'keywords': ['lowpass', 'highpass', 'bandpass', 'butterworth', 'chebyshev', 'iir', 'fir'],
                        'required_patterns': ['filter_coefficients', 'convolution'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Image Processing Algorithms
            AlgorithmType.IMAGE_PROCESSING: {
                'subtypes': {
                    'interpolation': {
                        'keywords': ['bilinear', 'bicubic', 'lanczos', 'spline', 'hermite', 'upscale', 'downscale'],
                        'required_patterns': ['pixel_interpolation', 'weight_calculation'],
                        'ast_patterns': ['nested_loops', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'morphological': {
                        'keywords': ['erosion', 'dilation', 'opening', 'closing', 'morpholog', 'structuring_element'],
                        'required_patterns': ['kernel_operation', 'pixel_comparison'],
                        'ast_patterns': ['nested_loops', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'edge_detection': {
                        'keywords': ['edge', 'canny', 'sobel', 'prewitt', 'laplacian', 'gradient'],
                        'required_patterns': ['convolution', 'gradient_calculation'],
                        'ast_patterns': ['nested_loops', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'histogram': {
                        'keywords': ['histogram', 'equalization', 'stretching', 'intensity', 'brightness'],
                        'required_patterns': ['pixel_counting', 'mapping_operation'],
                        'ast_patterns': ['loop', 'array_operations'],
                        'confidence_boost': 0.2
                    },
                    'convolution': {
                        'keywords': ['convolution', 'convolve', 'kernel', 'filter_kernel', 'blur', 'sharpen'],
                        'required_patterns': ['kernel_multiplication', 'accumulation'],
                        'ast_patterns': ['nested_loops', 'arithmetic_operations'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Signal Processing Algorithms
            AlgorithmType.SIGNAL_PROCESSING: {
                'subtypes': {
                    'signal_filter': {
                        'keywords': ['butterworth', 'chebyshev', 'bessel', 'fir_filter', 'iir_filter', 'low_pass', 'high_pass', 'band_pass'],
                        'required_patterns': ['filter_design', 'coefficient_calculation'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.3
                    },
                    'correlation': {
                        'keywords': ['correlation', 'cross_correlation', 'auto_correlation', 'convolution'],
                        'required_patterns': ['signal_multiplication', 'sliding_window'],
                        'ast_patterns': ['nested_loops', 'arithmetic_operations'],
                        'confidence_boost': 0.2
                    },
                    'windowing': {
                        'keywords': ['window', 'hamming', 'hanning', 'blackman', 'kaiser', 'rectangular'],
                        'required_patterns': ['window_function', 'multiplication'],
                        'ast_patterns': ['loop', 'arithmetic_operations'],
                        'confidence_boost': 0.2
                    },
                    'modulation': {
                        'keywords': ['modulation', 'demodulation', 'am', 'fm', 'qam', 'psk', 'carrier'],
                        'required_patterns': ['carrier_multiplication', 'phase_calculation'],
                        'ast_patterns': ['loop', 'trigonometric_operations'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Encoding Algorithms
            AlgorithmType.ENCODING_ALGORITHM: {
                'subtypes': {
                    'base64': {
                        'keywords': ['base64', 'b64', 'base_64'],
                        'required_patterns': ['bit_shifting', 'encoding_table'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.4
                    },
                    'url_encoding': {
                        'keywords': ['urlencode', 'urldecode', 'percent_encoding', 'escape'],
                        'required_patterns': ['character_checking', 'hex_conversion'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'hex_encoding': {
                        'keywords': ['hex', 'hexadecimal', 'tohex', 'fromhex'],
                        'required_patterns': ['nibble_operation', 'hex_digits'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.3
                    },
                    'ascii_encoding': {
                        'keywords': ['ascii', 'ord', 'chr', 'char_code'],
                        'required_patterns': ['character_conversion', 'range_check'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Add missing compression algorithms
            AlgorithmType.COMPRESSION_ALGORITHM: {
                'subtypes': {
                    'huffman': {
                        'keywords': ['huffman', 'frequency', 'encoding'],
                        'required_patterns': ['frequency_counting', 'tree_building', 'encoding'],
                        'ast_patterns': ['hash_map', 'tree_structure'],
                        'confidence_boost': 0.3
                    },
                    'lzw': {
                        'keywords': ['lzw', 'dictionary', 'compress'],
                        'required_patterns': ['dictionary_building', 'pattern_matching'],
                        'ast_patterns': ['hash_map', 'string_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'rle': {
                        'keywords': ['rle', 'run_length', 'runlength', 'consecutive', 'repeat'],
                        'required_patterns': ['consecutive_counting', 'run_detection', 'encoding_loop'],
                        'ast_patterns': ['loop', 'comparison', 'counter'],
                        'confidence_boost': 0.3
                    },
                    'lzo': {
                        'keywords': ['lzo', 'lzo1x', 'av_lzo'],
                        'required_patterns': ['byte_matching', 'copy_operation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.4
                    },
                    'deflate': {
                        'keywords': ['deflate', 'inflate', 'zlib', 'gzip'],
                        'required_patterns': ['lz77_matching', 'huffman_encoding'],
                        'ast_patterns': ['loop', 'hash_table'],
                        'confidence_boost': 0.3
                    }
                }
            }
        }
    
    def detect(self, ast_tree: Any, language: str, file_lines: Optional[int] = None) -> List[Dict[str, Any]]:
        """Detect algorithms with improved specificity."""
        return self.detect_algorithms(ast_tree, language, file_lines)
    
    def detect_algorithms(self, ast_tree: Any, language: str, file_lines: Optional[int] = None) -> List[Dict[str, Any]]:
        """Detect algorithms with improved specificity and unknown algorithm detection."""
        detected_algorithms = []
        
        # Check for minified code first
        if hasattr(self, 'content') and self.content:
            is_minified, confidence = self.minified_detector.is_minified(self.content, language)
            if is_minified:
                # Try to detect patterns in minified code
                minified_patterns = self.minified_detector.extract_patterns_from_minified(
                    self.content, language
                )
                for pattern in minified_patterns:
                    # Convert to standard algorithm format
                    algo = self._convert_minified_pattern_to_algorithm(pattern, ast_tree)
                    detected_algorithms.append(algo)
                
                # If we found patterns in minified code, we can still continue with regular detection
                # on the expanded version if needed
        
        # Get language configuration
        lang_config = get_language_config(language)
        min_lines = lang_config.get("min_lines", 20)
        min_func_lines = lang_config.get("min_function_lines", 2)
        unknown_threshold = lang_config.get("unknown_algorithm_threshold", 50)
        
        # Extract functions from AST
        functions = self._extract_functions_from_ast(ast_tree)
        
        # Phase 1: Pattern-based detection for known algorithms
        for func in functions:
            # Skip functions below language-specific threshold
            if func['lines']['total'] < min_func_lines:
                continue
                
            # Analyze each function for specific algorithm patterns
            algorithm = self._analyze_function_with_specificity(func, ast_tree, language)
            if algorithm:
                detected_algorithms.append(algorithm)
        
        # Phase 2: Enhanced pattern detection using language-specific patterns
        if hasattr(ast_tree, 'code'):
            enhanced_algorithms = self._detect_enhanced_patterns(
                ast_tree.code, functions, language, detected_algorithms
            )
            detected_algorithms.extend(enhanced_algorithms)
        
        # Phase 2.5: Domain-specific detection with signature matching
        if hasattr(ast_tree, 'code'):
            # Get file path if available
            file_path = getattr(ast_tree, 'file_path', '')
            
            # Run domain-specific detection
            domain_algorithms = self.domain_detector.detect_algorithms(
                ast_tree.code, language, file_path, ast_tree
            )
            
            # Merge with existing detections, avoiding duplicates
            for domain_algo in domain_algorithms:
                # Check if we already detected this algorithm
                duplicate = False
                for existing in detected_algorithms:
                    if (existing.get('algorithm_type') == domain_algo.get('algorithm_type') and
                        existing.get('algorithm_subtype') == domain_algo.get('algorithm_subtype')):
                        # Boost confidence if detected by multiple methods
                        existing['confidence'] = min(existing.get('confidence', 0) * 1.2, 1.0)
                        existing['detection_methods'] = list(set(
                            existing.get('detection_methods', ['pattern_matching']) + 
                            domain_algo.get('detection_methods', [])
                        ))
                        duplicate = True
                        break
                
                if not duplicate:
                    detected_algorithms.append(domain_algo)
        
        # Phase 3: Unknown algorithm detection for files above threshold
        if file_lines and file_lines >= unknown_threshold:
            # Get functions that need unknown algorithm detection:
            # 1. Functions not detected at all
            # 2. Functions with only low-confidence generic matches
            detected_func_names = {algo.get('function_name', '') for algo in detected_algorithms}
            unclassified_functions = [f for f in functions if f.get('name', '') not in detected_func_names]
            
            # Also check for low-confidence generic matches
            low_confidence_funcs = []
            for algo in detected_algorithms:
                func_name = algo.get('function_name', '')
                if func_name and algo.get('confidence', 0) < 0.5:
                    subtype = algo.get('subtype', 'generic')
                    if subtype.endswith('_generic') or subtype == 'generic':
                        low_confidence_funcs.append(func_name)
            
            # Remove low-confidence generic detections
            if low_confidence_funcs:
                detected_algorithms = [a for a in detected_algorithms 
                                     if a.get('function_name', '') not in low_confidence_funcs]
                unclassified_functions.extend([f for f in functions 
                                             if f.get('name', '') in low_confidence_funcs])
            
            # If we have unclassified functions, run unknown algorithm detection
            if unclassified_functions:
                unknown_algorithms = self.unknown_detector.detect_unknown_algorithms(
                    ast_tree, language, file_lines
                )
                detected_algorithms.extend(unknown_algorithms)
        
        # Phase 4: OSS library signature detection
        if hasattr(ast_tree, 'code'):
            oss_signatures = detect_oss_signatures(ast_tree.code, language)
            for sig in oss_signatures:
                # Add OSS signatures as metadata to algorithms or create synthetic entries
                if detected_algorithms:
                    # Boost confidence of algorithms if they match OSS patterns
                    for algo in detected_algorithms:
                        algo['oss_signatures'] = algo.get('oss_signatures', [])
                        algo['oss_signatures'].append(sig)
                        algo['confidence'] = min(algo.get('confidence', 0) + sig['confidence'] * 0.1, 1.0)
                else:
                    # Create a synthetic algorithm entry for OSS detection
                    detected_algorithms.append({
                        "algorithm_type": "OSS_LIBRARY_PATTERN",
                        "subtype": f"{sig['library']}_pattern",
                        "confidence": sig['confidence'],
                        "oss_signatures": [sig],
                        "function_name": f"oss_{sig['library']}_usage",
                        "file_lines": file_lines or 0
                    })
        
        # Filter out zero-confidence detections to reduce noise
        filtered_algorithms = []
        for algo in detected_algorithms:
            confidence = algo.get('confidence_score', algo.get('confidence', 0))
            # Keep algorithms with confidence > 0 or those with explicit evidence
            if confidence > 0.0 or algo.get('oss_signatures') or algo.get('evidence', {}).get('matched_keywords'):
                filtered_algorithms.append(algo)
        
        return filtered_algorithms
    
    def detect_algorithms_from_input(self, 
                                   input_data: Union[str, Any], 
                                   language: str) -> List[Dict[str, Any]]:
        """
        Detect algorithms from either raw content or pre-parsed AST.
        
        This is a convenience method that automatically determines whether the input
        is raw code content or a pre-parsed AST tree and processes it accordingly.
        
        Args:
            input_data: Either string content or pre-parsed AST tree
            language: Programming language (e.g., 'python', 'javascript', 'java')
            
        Returns:
            List of detected algorithms with their properties
            
        Examples:
            # Using with raw content
            content = "def quicksort(arr): ..."
            algorithms = detector.detect_algorithms_from_input(content, "python")
            
            # Using with pre-parsed AST
            ast_tree = parser.parse(content, "python")
            algorithms = detector.detect_algorithms_from_input(ast_tree, "python")
        """
        if isinstance(input_data, str):
            # It's raw content - parse it
            from ..parsers.tree_sitter_parser import TreeSitterParser
            parser = TreeSitterParser()
            ast_tree = parser.parse(input_data, language)
        else:
            # Assume it's already an AST
            ast_tree = input_data
        
        return self.detect_algorithms(ast_tree, language)
    
    def _detect_enhanced_patterns(self, code: str, functions: List[Dict], 
                                 language: str, existing_algorithms: List[Dict]) -> List[Dict[str, Any]]:
        """Detect algorithms using enhanced patterns from language configs."""
        detected = []
        existing_funcs = {algo.get('function_name', '') for algo in existing_algorithms}
        
        # Check each category of enhanced patterns
        for category, patterns in ALGORITHM_PATTERNS.items():
            category_patterns = get_enhanced_patterns(language, category)
            
            for algo_name, pattern_config in category_patterns.items():
                # Check each function against the pattern
                for func in functions:
                    if func['name'] in existing_funcs:
                        continue
                    
                    func_text = func['text'].lower()
                    score = 0
                    matches = []
                    
                    # Check patterns
                    for pattern in pattern_config.get('patterns', []):
                        if re.search(pattern, func_text, re.IGNORECASE | re.MULTILINE):
                            score += 0.15
                            matches.append(pattern)
                    
                    # Check required elements
                    required = pattern_config.get('required_elements', [])
                    if required:
                        required_found = 0
                        for req in required:
                            # Handle OR conditions in requirements
                            req_parts = req.split('|')
                            for part in req_parts:
                                if part in func_text:
                                    required_found += 1
                                    break
                        
                        if required_found < len(required):
                            continue  # Skip if not all required elements found
                    
                    # If we have enough matches, create algorithm entry
                    if score >= pattern_config.get('confidence', 0.5) * 0.5:
                        # Map algorithm type if needed (e.g., GRAPH_TRAVERSAL -> search_algorithm)
                        type_mapping = pattern_loader.get_type_mapping()
                        algo_type = category.upper()
                        if algo_type in type_mapping:
                            algo_type = type_mapping[algo_type]
                        
                        # Handle different line formats
                        start_line = func['lines'].get('start', 1)
                        end_line = func['lines'].get('end', func['lines'].get('total', 1))
                        
                        detected.append({
                            "algorithm_type": algo_type,
                            "subtype": algo_name,
                            "confidence": min(score + pattern_config.get('confidence', 0.5), 1.0),
                            "function_name": func['name'],
                            "pattern_matches": matches[:3],
                            "enhanced_detection": True,
                            "start_line": start_line,
                            "end_line": end_line,
                            "complexity": {
                                "cyclomatic": self._calculate_cyclomatic_complexity(func['node'])
                            }
                        })
        
        return detected
    
    def _analyze_function_with_specificity(self, func: Dict[str, Any], ast_tree: Any, language: str) -> Optional[Dict[str, Any]]:
        """Analyze function with specific pattern matching to reduce false positives."""
        func_text = func['text'].lower()
        func_name = func['name'].lower()
        
        # Generate normalized representation for transformation resistance
        normalized_text = ""
        try:
            normalized_text = self.normalizer.normalize_function(func['node'], func['text'], language).lower()
            logger.debug(f"Normalized representation: {normalized_text[:100]}...")
        except Exception as e:
            logger.debug(f"Normalization failed: {e}, using original text only")
        
        # Get language config for minimum lines
        lang_config = get_language_config(language)
        min_func_lines = lang_config.get("min_function_lines", 2)
        
        # Skip very small functions based on language config
        if func['lines']['total'] < min_func_lines:
            return None
        
        best_match = None
        best_confidence = 0.0
        best_subtype = None
        
        # First check external patterns with both original and normalized text
        external_match = self._check_external_patterns_enhanced(func_text, func_name, normalized_text)
        if external_match:
            best_match = external_match['type']
            best_confidence = external_match.get('confidence', 0.0)
            if best_confidence is None:
                best_confidence = 0.0
            best_subtype = external_match['subtype']
        
        # Then check internal patterns for anything not found
        if best_confidence < 0.7:  # Only check internal if external didn't find high confidence
            for algo_type in self.pattern_priority:
                if algo_type not in self.patterns:
                    continue
                
                type_config = self.patterns[algo_type]
                for subtype_name, subtype_pattern in type_config['subtypes'].items():
                    confidence = self._calculate_specific_confidence_enhanced(
                        func_text, func_name, func['node'], 
                        subtype_pattern, subtype_name, language, algo_type, normalized_text
                    )
                    
                    if confidence is None:
                        confidence = 0.0
                    
                    if confidence > best_confidence and confidence >= 0.3:  # Higher threshold
                        best_confidence = confidence
                        best_match = algo_type
                        best_subtype = subtype_name
        
        if best_match:
            return self._create_specific_algorithm_entry(
                func, best_match, best_subtype, best_confidence, 
                ast_tree, language
            )
        
        return None
    
    def _calculate_specific_confidence_enhanced(self, func_text: str, func_name: str, 
                                     func_node: Any, pattern: Dict, subtype: str, 
                                     language: str = None, algo_type: Any = None, normalized_text: str = "") -> float:
        """Calculate confidence with required pattern checking and transformation resistance."""
        confidence = 0.0
        
        # 1. Keyword matching in both texts (reduced weight)
        keyword_score = self._calculate_keyword_score_enhanced(func_text, func_name, pattern.get('keywords', []), normalized_text)
        confidence += keyword_score * 0.2  # Only 20% weight
        
        # 2. Required patterns in both texts (high weight)
        required_patterns = pattern.get('required_patterns', [])
        if required_patterns:
            required_score = self._check_required_patterns_enhanced(func_text, func_node, required_patterns, func_name, normalized_text)
            # If required patterns exist but score is too low, reject the match
            if required_score < 0.5:
                return 0.0  # Fail fast if required patterns aren't met
            confidence += required_score * 0.5  # 50% weight
        
        # 3. AST pattern matching
        ast_score = self._check_ast_patterns(func_node, pattern.get('ast_patterns', []))
        confidence += ast_score * 0.3  # 30% weight
        
        # 4. Apply confidence boost for highly specific patterns
        if confidence > 0.5:  # Only boost if base confidence is decent
            confidence += pattern.get('confidence_boost', 0)
        
        # 5. Penalty for generic subtypes
        if subtype.endswith('_generic') or subtype == 'generic':
            confidence *= 0.5  # Reduce confidence for generic matches
        
        # 6. Language-specific adjustments
        if language == 'c':
            # C code often has arithmetic/division in non-algorithm contexts (e.g., size calculations)
            if subtype in ['fibonacci', 'factorial', 'lcm', 'gcd'] and confidence < 0.6:
                confidence *= 0.5  # Reduce false positives for weak matches
        
        # 7. Codec-specific minimum thresholds
        if algo_type in [AlgorithmType.AUDIO_CODEC, AlgorithmType.VIDEO_CODEC]:
            # Codecs require higher confidence to avoid false positives
            if confidence < 0.6:
                return 0.0  # Reject weak codec matches
        
        return min(confidence, 1.0)
    
    def _calculate_specific_confidence(self, func_text: str, func_name: str, 
                                     func_node: Any, pattern: Dict, subtype: str, 
                                     language: str = None, algo_type: Any = None) -> float:
        """Legacy method for backward compatibility."""
        return self._calculate_specific_confidence_enhanced(func_text, func_name, func_node, pattern, subtype, language, algo_type)
    
    def _calculate_keyword_score_enhanced(self, func_text: str, func_name: str, keywords: List[str], normalized_text: str = "") -> float:
        """Calculate keyword matching score with context awareness and normalized text."""
        if not keywords:
            return 0.0
        
        score = 0.0
        matched_keywords = 0
        
        # Convert to lowercase for case-insensitive matching
        func_text_lower = func_text.lower()
        func_name_lower = func_name.lower()
        normalized_lower = normalized_text.lower() if normalized_text else ""
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check function name (higher weight)
            if keyword_lower in func_name_lower:
                score += 2.0
                matched_keywords += 1
            # Check function text
            elif re.search(rf'\b{keyword_lower}\b', func_text_lower):
                score += 1.0
                matched_keywords += 1
            # Check normalized text (medium weight)
            elif normalized_lower and keyword_lower in normalized_lower:
                score += 1.5
                matched_keywords += 1
        
        # Normalize and apply threshold
        if matched_keywords == 0:
            return 0.0
        
        normalized_score = score / (len(keywords) * 2)  # Max possible score
        
        # Require at least 30% keyword match
        return normalized_score if matched_keywords >= len(keywords) * 0.3 else normalized_score * 0.5
    
    def _calculate_keyword_score(self, func_text: str, func_name: str, keywords: List[str]) -> float:
        """Legacy method for backward compatibility."""
        return self._calculate_keyword_score_enhanced(func_text, func_name, keywords)
    
    def _check_required_patterns_enhanced(self, func_text: str, func_node: Any, required_patterns: List[str], func_name: str = "", normalized_text: str = "") -> float:
        """Check for required algorithmic patterns in both original and normalized text."""
        if not required_patterns:
            return 0.0
        
        func_text_lower = func_text.lower()
        normalized_lower = normalized_text.lower() if normalized_text else ""
        
        pattern_checks = {
            # Sorting patterns
            'pivot_selection': lambda: 'pivot' in func_text_lower or (normalized_lower and 'pivot' in normalized_lower),
            'partition_logic': lambda: (('left' in func_text_lower and 'right' in func_text_lower) or 
                                      'partition' in func_text_lower or
                                      (normalized_lower and ('left' in normalized_lower and 'right' in normalized_lower)) or
                                      (normalized_lower and 'partition' in normalized_lower) or
                                      re.search(r'comparator\.(less|greater|equal)', func_text) is not None),
            'nested_loops': lambda: self._has_nested_loops(func_node),
            'adjacent_comparison': lambda: (re.search(r'\[\s*\w+\s*\].*\[\s*\w+\s*\+\s*1\s*\]', func_text) is not None or
                                           re.search(r'arr\[j\].*arr\[j\s*\+\s*1\]', func_text) is not None or
                                           (normalized_lower and 'array_access' in normalized_lower and 'compare' in normalized_lower)),
            'swap_operation': lambda: (re.search(r'=.*,.*=|swap|temp.*=', func_text) is not None or
                                     re.search(r'.*,.*=.*,.*', func_text) is not None or  # Python tuple swap
                                     (normalized_lower and 'assign' in normalized_lower and 'var' in normalized_lower)),
            'merge_function': lambda: ('merge' in func_text_lower and ('left' in func_text_lower or 'right' in func_text_lower)) or
                                    (normalized_lower and 'merge' in normalized_lower),
            'divide_conquer': lambda: ('//2' in func_text or '/2' in func_text) or
                                    (normalized_lower and 'div' in normalized_lower),
            'heapify_operation': lambda: 'heapify' in func_text or ('largest' in func_text and 'parent' in func_text),
            'parent_child_comparison': lambda: re.search(r'2\s*\*\s*\w+|left.*right', func_text) is not None,
            
            # Search patterns - more restrictive
            'mid_calculation': lambda: re.search(r'(mid|middle)\s*=.*[+/].*2', func_text) is not None,
            'binary_division': lambda: 'left' in func_text and 'right' in func_text and 'mid' in func_text,
            'comparison_with_target': lambda: 'target' in func_text or 'key' in func_text or 'search' in func_text,
            'range_adjustment': lambda: re.search(r'(left|right)\s*=\s*(mid|middle)', func_text) is not None,
            'single_loop': lambda: self._count_loops(func_node) == 1,
            'return_on_match': lambda: re.search(r'if.*return', func_text) is not None,
            'element_comparison': lambda: re.search(r'==|!=', func_text) is not None,
            
            # Math patterns - more specific
            'n_minus_1': lambda: (
                (re.search(r'\b(n|num)\s*[-]\s*1\b', func_text) is not None and
                 ('fibonacci' in func_text.lower() or 'fibonacci' in func_name.lower() or 'fib' in func_name.lower())) or
                re.search(r'fib\s*\(\s*n\s*-\s*1', func_text) is not None
            ),
            'n_minus_2': lambda: re.search(r'\b(n|num)\s*[-]\s*2\b', func_text) is not None or
                                (('fibonacci' in func_text.lower() or 'fibonacci' in func_name.lower() or 'fib' in func_name.lower()) and ('- 2' in func_text or '-2' in func_text)),
            'n_multiplication': lambda: (
                re.search(r'\b(n|num|factorial)\s*\*', func_text) is not None or
                re.search(r'\*\s*\b(n|num|factorial)\b', func_text) is not None
            ),
            'modulo_operation': lambda: '%' in func_text or 'mod' in func_text,
            'decremental_loop_or_recursion': lambda: (
                self._has_decrement_pattern(func_text) and 
                ('factorial' in func_text.lower() or re.search(r'\bn\s*\*', func_text) is not None)
            ),
            'addition': lambda: '+' in func_text,
            'multiplication': lambda: '*' in func_text,
            'division': lambda: '/' in func_text or '//' in func_text,
            'divisibility_check': lambda: re.search(r'%.*==\s*0', func_text) is not None,
            'swap_or_recursion': lambda: 'swap' in func_text or self._has_recursive_pattern(func_text, func_node),
            'gcd_call_or_impl': lambda: 'gcd' in func_text or ('while' in func_text and '%' in func_text),
            'multiplication_loop': lambda: self._has_loops(func_node) and '*' in func_text,
            'base_exponent': lambda: 'base' in func_text or 'exp' in func_text or 'power' in func_text,
            'while_with_modulo': lambda: 'while' in func_text and '%' in func_text,
            'exponent_check': lambda: re.search(r'exponent\s*[=<>!]+\s*\d+', func_text) is not None,
            'recursive_multiplication': lambda: self._has_recursive_pattern(func_text, func_node) and '*' in func_text,
            
            # General patterns
            'recursive_calls': lambda: (self._has_recursive_pattern(func_text, func_node) or
                                      re.search(r'this\.\w+\s*\(', func_text) is not None or
                                      ('sort' in func_name.lower() and 'sort' in func_text.lower())),
            'iteration': lambda: self._has_loops(func_node),
            'comparison': lambda: re.search(r'[<>=!]=?', func_text) is not None,
            
            # Polyfill patterns
            'native_check': lambda: '||' in func_text and ('Object.' in func_text or 'Array.' in func_text),
            'fallback_loop': lambda: 'for' in func_text and ('function' in func_text or '=>' in func_text),
            'helper_pattern': lambda: func_text.startswith('__') or 'prototype' in func_text,
            'prototype_chain': lambda: 'prototype' in func_text,
            
            # Object manipulation patterns  
            'property_iteration': lambda: 'for' in func_text and ' in ' in func_text,
            'property_copy': lambda: re.search(r'\[\w+\]\s*=\s*\w+\[\w+\]', func_text) is not None,
            'hasOwnProperty_check': lambda: 'hasownproperty' in func_text,
            'hasOwnProperty': lambda: 'hasownproperty' in func_text,  # Alias for pattern matching
            'property_enumeration': lambda: 'getownpropertysymbols' in func_text or 'propertyisenumerable' in func_text,
            'symbol_handling': lambda: 'symbol' in func_text,
            
            # Array manipulation patterns
            'array_indexing': lambda: re.search(r'\[\s*\w+\s*\]', func_text) is not None,
            'length_accumulation': lambda: re.search(r'\w+\s*\+=.*\.length', func_text) is not None,
            'element_copy': lambda: re.search(r'\[\w+\]\s*=\s*\w+\[\w+\]', func_text) is not None,
            
            # Cryptographic patterns
            'modular_exponentiation': lambda: (('pow' in func_text or '**' in func_text) and '%' in func_text) or re.search(r'modpow|mod_pow|modular.*pow|pow\s*\([^,]+,[^,]+,[^)]+\)', func_text) is not None,
            'prime_generation_or_check': lambda: re.search(r'prime|is_prime|primality|miller_rabin|fermat', func_text) is not None,
            'key_generation': lambda: re.search(r'key|public|private|generate.*key|key.*gen', func_text) is not None,
            'substitution_table': lambda: re.search(r'sbox|s_box|substitution|lookup\s*\[|table\s*\[', func_text) is not None,
            'matrix_operations': lambda: re.search(r'matrix|row|column|state\[\d+\]\[\d+\]', func_text) is not None,
            'xor_operations': lambda: '^' in func_text or 'xor' in func_text,
            'bit_rotation': lambda: re.search(r'<<|>>|rotate|rot[lr]|circular.*shift', func_text) is not None,
            'constant_array': lambda: re.search(r'const.*\[.*\]|K\s*=\s*\[|constants?\s*=', func_text) is not None,
            'four_rounds': lambda: re.search(r'round|rounds|for.*4|range.*4', func_text) is not None,
            'key_padding': lambda: re.search(r'pad|padding|\\x36|\\x5c|ipad|opad', func_text) is not None,
            'inner_hash': lambda: re.search(r'inner|i_key_pad|ipad', func_text) is not None,
            'outer_hash': lambda: re.search(r'outer|o_key_pad|opad', func_text) is not None,
            'generator': lambda: re.search(r'generator|g\s*=\s*\d+|base.*point', func_text) is not None,
            'point_operations': lambda: re.search(r'point.*add|scalar.*mult|double.*point|ec_add|ecc', func_text) is not None,
            'modular_arithmetic': lambda: '%' in func_text and ('+' in func_text or '*' in func_text),
            'curve_equation': lambda: re.search(r'curve|elliptic|y\^2|x\^3|weierstrass', func_text) is not None,
            'quarter_round': lambda: re.search(r'quarter.*round|qr|rotl|rotr', func_text) is not None,
            'salt_generation': lambda: re.search(r'salt|random.*bytes|urandom|generate.*salt', func_text) is not None,
            'key_expansion': lambda: re.search(r'expand.*key|key.*schedule|round.*key', func_text) is not None,
            'blowfish_operations': lambda: re.search(r'blowfish|feistel|f_function', func_text) is not None,
            'hmac_iterations': lambda: re.search(r'iteration|rounds|pbkdf|kdf', func_text) is not None,
            'salt_usage': lambda: 'salt' in func_text,
            'xor_accumulation': lambda: re.search(r'\^=|xor.*=', func_text) is not None,
            'key_usage': lambda: 'key' in func_text,
            'data_transformation': lambda: re.search(r'transform|encrypt|decrypt|encode|decode', func_text) is not None,
            
            # Iterator patterns
            'iterator_interface': lambda: 'next' in func_text and 'done' in func_text,
            'state_tracking': lambda: 'state' in func_text or 'index' in func_text or 'i++' in func_text,
            
            # Audio processing patterns
            'audio_processing': lambda: (
                # Must have explicit audio-related terms
                re.search(r'audio|sound|pcm|sample_rate|audio_frame|audio_channel', func_text) is not None or
                # OR have codec-specific patterns with additional context
                (re.search(r'mp3|aac|opus|flac', func_text) is not None and 
                 re.search(r'bitrate|sample|frequency|channel|frame_size', func_text) is not None)
            ),
            
            # Enhanced audio resampling patterns
            'phase_count_or_type': lambda: re.search(r'phase_count|filter_type', func_text) is not None,
            'filter_processing': lambda: re.search(r'filter|build_filter|filter.*coef', func_text) is not None,
            'tap_or_coef': lambda: re.search(r'tap_count|taps|coef|coefficient', func_text) is not None,
            'resample_process': lambda: re.search(r'resample|resampler|resample_process', func_text) is not None,
            'interpolation': lambda: re.search(r'interp|interpolat|cubic|sinc', func_text) is not None,
            'cubic_or_sinc': lambda: re.search(r'cubic|sinc', func_text) is not None,
            'sample_rate_conversion': lambda: re.search(r'sample.*rate|upsample|downsample', func_text) is not None,
            'filtering': lambda: re.search(r'filter|fir|iir', func_text) is not None,
            
            # Enhanced codec patterns
            'lpc_or_rice': lambda: re.search(r'lpc|rice|linear.*predict', func_text) is not None,
            'subframe_encoding': lambda: re.search(r'subframe|frame.*type', func_text) is not None,
            'residual_coding': lambda: re.search(r'residual|coding', func_text) is not None,
            'mdct_transform': lambda: re.search(r'mdct|modified.*discrete.*cosine', func_text) is not None,
            'quantization': lambda: re.search(r'quantiz|quant', func_text) is not None,
            'psychoacoustic_model': lambda: re.search(r'psychoacoustic|psy.*model', func_text) is not None,
            'delay_processing': lambda: re.search(r'delay.*line|delay.*buffer|delay_time', func_text) is not None,
            'feedback_loop': lambda: re.search(r'feedback|decay', func_text) is not None,
            'transform_operation': lambda: re.search(r'mdct|fft|dct|transform|fourier', func_text) is not None,
            'spectral_processing': lambda: re.search(r'spectral|spectrum|frequency|coefficient', func_text) is not None,
            'frame_processing': lambda: re.search(r'frame|window|overlap|segment', func_text) is not None,
            'prediction_operation': lambda: re.search(r'predict|lpc|linear.*prediction|residual', func_text) is not None,
            
            # Video processing patterns - require explicit video context
            'video_processing': lambda: (
                re.search(r'video|yuv|rgb|h264|h265|vp[89]|av1|hevc|avc', func_text) is not None or
                (re.search(r'frame|pixel', func_text) is not None and 
                 re.search(r'video|codec|encode|decode|motion|prediction', func_text) is not None)
            ),
            'block_processing': lambda: re.search(r'block|macroblock|superblock|partition|tile', func_text) is not None,
            'tree_structure': lambda: re.search(r'tree|split|quadtree|coding.*tree|ctu', func_text) is not None,
            'filtering_operation': lambda: re.search(r'filter|deblock|smooth|blur|sharpen', func_text) is not None,
            'promise_handling': lambda: 'promise' in func_text or 'then' in func_text,
            'state_machine': lambda: 'switch' in func_text or 'case' in func_text,
            
            # Video processing patterns
            'color_conversion': lambda: re.search(r'yuv.*rgb|rgb.*yuv|color.*convert', func_text) is not None,
            'matrix_operations': lambda: re.search(r'matrix|\[\d+\]\[\d+\]|row.*col', func_text) is not None,
            'rate_calculation': lambda: re.search(r'rate|bitrate|bps|kbps', func_text) is not None,
            'control_logic': lambda: re.search(r'control|adjust|regulate', func_text) is not None,
            'segment_processing': lambda: re.search(r'segment|partition|split', func_text) is not None,
            'boundary_detection': lambda: re.search(r'boundary|edge|border', func_text) is not None,
            'prediction_logic': lambda: re.search(r'predict|estimate|extrapolat', func_text) is not None,
            'vector_calculation': lambda: re.search(r'vector|motion.*vector|mv', func_text) is not None,
            'edge_detection': lambda: re.search(r'edge|boundary|gradient', func_text) is not None,
            'block_comparison': lambda: re.search(r'compare.*block|sad|mad|diff', func_text) is not None,
            'transform_operation': lambda: re.search(r'transform|dct|fft|dwt', func_text) is not None,
            'matrix_multiplication': lambda: re.search(r'matrix.*mult|dot.*product', func_text) is not None,
            'division_operation': lambda: '/' in func_text or '//' in func_text,
            'rounding_operation': lambda: re.search(r'round|floor|ceil|int\(', func_text) is not None,
            
            # Audio processing patterns
            'complex_arithmetic': lambda: re.search(r'complex|real.*imag|phase|magnitude', func_text) is not None,
            'butterfly_operation': lambda: re.search(r'butterfly|twiddle|w_n', func_text) is not None,
            'frequency_analysis': lambda: re.search(r'frequenc|spectrum|spectral', func_text) is not None,
            'threshold_calculation': lambda: re.search(r'threshold|limit|cutoff', func_text) is not None,
            'filter_processing': lambda: re.search(r'filter|fir|iir|tap', func_text) is not None,
            'sample_rate_conversion': lambda: re.search(r'sample.*rate|resample|sr', func_text) is not None,
            'delay_processing': lambda: re.search(r'delay|buffer|circular', func_text) is not None,
            'feedback_loop': lambda: re.search(r'feedback|recurs|prev', func_text) is not None,
            'spectral_analysis': lambda: re.search(r'spectral|fft|frequency.*domain', func_text) is not None,
            'threshold_operation': lambda: re.search(r'threshold|gate|suppress', func_text) is not None,
            'filter_coefficients': lambda: re.search(r'coef|coefficient|b\[|a\[', func_text) is not None,
            'convolution': lambda: re.search(r'convolv|conv|filter.*kernel', func_text) is not None,
            
            # Image processing patterns
            'pixel_interpolation': lambda: re.search(r'interpolat|bilinear|bicubic', func_text) is not None,
            'weight_calculation': lambda: re.search(r'weight|coef|factor', func_text) is not None,
            'kernel_operation': lambda: re.search(r'kernel|mask|window', func_text) is not None,
            'pixel_comparison': lambda: re.search(r'pixel|neighbor|adjacent', func_text) is not None,
            'gradient_calculation': lambda: re.search(r'gradient|derivative|diff', func_text) is not None,
            'pixel_counting': lambda: re.search(r'histogram|count|bin', func_text) is not None,
            'mapping_operation': lambda: re.search(r'map|lookup|lut', func_text) is not None,
            'kernel_multiplication': lambda: re.search(r'kernel.*mult|convolv', func_text) is not None,
            'accumulation': lambda: re.search(r'sum|accum|total', func_text) is not None,
            
            # Signal processing patterns
            'filter_design': lambda: re.search(r'design|butterworth|chebyshev', func_text) is not None,
            'coefficient_calculation': lambda: re.search(r'coef|pole|zero', func_text) is not None,
            'signal_multiplication': lambda: re.search(r'signal.*mult|product', func_text) is not None,
            'sliding_window': lambda: re.search(r'window|slide|shift', func_text) is not None,
            'window_function': lambda: re.search(r'hamming|hanning|blackman', func_text) is not None,
            'carrier_multiplication': lambda: re.search(r'carrier|modulate', func_text) is not None,
            'phase_calculation': lambda: re.search(r'phase|angle|atan', func_text) is not None,
            
            # Encoding patterns
            'bit_shifting': lambda: re.search(r'<<|>>|shift', func_text) is not None,
            'encoding_table': lambda: re.search(r'table|alphabet|chars', func_text) is not None,
            'character_checking': lambda: re.search(r'isalpha|isdigit|char', func_text) is not None,
            'hex_conversion': lambda: re.search(r'hex|0x|%[0-9a-f]', func_text) is not None,
            'nibble_operation': lambda: re.search(r'nibble|0x0f|& *15', func_text) is not None,
            'hex_digits': lambda: re.search(r'0123456789abcdef|hex.*digit', func_text) is not None,
            'character_conversion': lambda: re.search(r'ord|chr|char.*code', func_text) is not None,
            'range_check': lambda: re.search(r'< *128|>= *32|ascii.*range', func_text) is not None,
            
            # Compression patterns
            'consecutive_counting': lambda: re.search(r'consecutive|count|repeat', func_text) is not None,
            'run_detection': lambda: re.search(r'run|same|equal', func_text) is not None,
            'encoding_loop': lambda: re.search(r'encode|compress|pack', func_text) is not None,
            'byte_matching': lambda: re.search(r'match|find|search', func_text) is not None,
            'copy_operation': lambda: re.search(r'copy|memcpy|duplicate', func_text) is not None,
            'lz77_matching': lambda: re.search(r'window|distance|length', func_text) is not None,
            'huffman_encoding': lambda: re.search(r'huffman|tree|frequency', func_text) is not None,
            
            # Additional codec patterns
            'table_lookup': lambda: re.search(r'table\[|lookup\[|lut\[', func_text) is not None,
            'lpc_analysis': lambda: re.search(r'lpc|linear.*predict|autocorr', func_text) is not None,
            'speech_processing': lambda: re.search(r'speech|voice|vocal|phoneme', func_text) is not None,
            'vector_quantization': lambda: re.search(r'vector.*quant|vq|codebook', func_text) is not None
        }
        
        matched = 0
        for pattern in required_patterns:
            if pattern in pattern_checks:
                try:
                    if pattern_checks[pattern]():
                        matched += 1
                except:
                    pass
        
        # Require at least 60% of required patterns
        return (matched / len(required_patterns)) if matched >= len(required_patterns) * 0.6 else 0.0
    
    def _check_required_patterns(self, func_text: str, func_node: Any, required_patterns: List[str], func_name: str = "") -> float:
        """Legacy method for backward compatibility."""
        return self._check_required_patterns_enhanced(func_text, func_node, required_patterns, func_name)
    
    def _check_ast_patterns(self, func_node: Any, ast_patterns: List[str]) -> float:
        """Check AST-based patterns."""
        if not ast_patterns or not func_node:
            return 0.0
        
        pattern_checks = {
            'recursive_function': lambda: self._has_function_calls(func_node),
            'double_for_loop': lambda: self._has_nested_loops(func_node),
            'while_loop_or_recursion': lambda: self._has_while_loop(func_node) or self._has_function_calls(func_node),
            'for_loop': lambda: self._has_for_loop(func_node),
            'loop': lambda: self._has_loops(func_node),
            'comparison': lambda: self._has_comparisons(func_node),
            'assignment': lambda: self._has_assignments(func_node),
            'arithmetic_operation': lambda: self._has_arithmetic(func_node),
            
            # Sorting specific patterns
            'array_manipulation': lambda: self._has_array_operations(func_node),
            'array_split': lambda: self._has_array_operations(func_node),
            
            # Search specific patterns
            'if_statement': lambda: self._has_conditionals(func_node),
            'return_statement': lambda: True,  # Most functions have returns
            
            # Math specific patterns
            'multiplication': lambda: self._has_specific_operator(func_node, '*'),
            'decrement': lambda: True,  # Handled in text patterns
            'modulo': lambda: self._has_specific_operator(func_node, '%'),
            'division': lambda: self._has_specific_operator(func_node, '/'),
            'loop_or_recursion': lambda: self._has_loops(func_node) or self._has_function_calls(func_node),
            'while_loop': lambda: self._has_while_loop(func_node),
            
            # Additional patterns for our new algorithm types
            'or_operator': lambda: self._has_binary_operator(func_node, '||'),
            'for_in_loop': lambda: self._has_for_in_loop(func_node),
            'property_assignment': lambda: self._has_property_assignment(func_node),
            'function_assignment': lambda: self._has_function_assignment(func_node),
            'prototype_access': lambda: self._has_prototype_access(func_node),
            'object_return': lambda: self._has_object_return(func_node),
            'method_definition': lambda: self._has_method_definition(func_node),
            'switch_statement': lambda: self._has_switch_statement(func_node),
            'promise_call': lambda: self._has_promise_call(func_node),
            'array_assignment': lambda: self._has_array_assignment(func_node),
            'array_access': lambda: self._has_array_access(func_node),
            
            # Cryptographic AST patterns
            'bitwise_operations': lambda: self._has_bitwise_operations(func_node),
            'modulo_operation': lambda: self._has_specific_operator(func_node, '%'),
            'exponentiation': lambda: self._has_exponentiation(func_node),
            'prime_check': lambda: True,  # Text-based check is sufficient
            'array_lookup': lambda: self._has_array_access(func_node),
            'array_constants': lambda: self._has_array_literals(func_node),
            'hash_function_call': lambda: self._has_function_calls(func_node),
            'concatenation': lambda: self._has_string_concatenation(func_node),
            'coordinate_operations': lambda: self._has_multiple_assignments(func_node),
            'substitution': lambda: self._has_array_access(func_node),
            'hmac_call': lambda: self._has_function_calls(func_node),
            
            # Multimedia AST patterns
            'arithmetic_operations': lambda: self._has_arithmetic(func_node),
            'nested_loops': lambda: self._has_nested_loops(func_node),
            'conditional': lambda: self._has_conditionals(func_node),
            'buffer_operation': lambda: self._has_array_access(func_node),
            'array_operations': lambda: self._has_array_operations(func_node),
            'complex_operations': lambda: self._has_arithmetic(func_node),
            'filter_operation': lambda: self._has_loops(func_node) and self._has_arithmetic(func_node),
            'trigonometric_operations': lambda: self._has_function_calls(func_node),
            'hash_table': lambda: self._has_object_operations(func_node) or self._has_map_operations(func_node)
        }
        
        matched = 0
        for pattern in ast_patterns:
            if pattern in pattern_checks:
                try:
                    if pattern_checks[pattern]():
                        matched += 1
                except:
                    pass
        
        return matched / len(ast_patterns) if ast_patterns else 0.0
    
    def _has_nested_loops(self, node: Any, depth: int = 0) -> bool:
        """Check if node contains nested loops."""
        if not node:
            return False
            
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            # Check if any child is also a loop
            for child in getattr(node, 'children', []):
                if self._has_loops_at_depth(child, depth + 1):
                    return True
        
        for child in getattr(node, 'children', []):
            if self._has_nested_loops(child, depth):
                return True
        
        return False
    
    def _has_loops_at_depth(self, node: Any, target_depth: int, current_depth: int = 0) -> bool:
        """Check if there are loops at a specific depth."""
        if not node:
            return False
            
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            if current_depth >= target_depth:
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_loops_at_depth(child, target_depth, current_depth):
                return True
        
        return False
    
    def _count_loops(self, node: Any) -> int:
        """Count total number of loops."""
        if not node:
            return 0
            
        count = 0
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            count += 1
        
        for child in getattr(node, 'children', []):
            count += self._count_loops(child)
        
        return count
    
    def _has_recursive_pattern(self, func_text: str, func_node: Any) -> bool:
        """Check for recursive patterns."""
        # Simple heuristic: function calls itself or has multiple function calls
        func_calls = self._count_function_calls(func_node)
        
        # Look for self-referential patterns
        if re.search(r'(\w+)\s*\([^)]*\1[^)]*\)', func_text):
            return True
        
        # Multiple function calls might indicate recursion
        return func_calls >= 2
    
    def _has_decrement_pattern(self, func_text: str) -> bool:
        """Check if function has decrement pattern (i--, i-=1, i = i - 1, etc)."""
        decrement_patterns = [
            r'\w+\s*-=\s*1',       # i -= 1
            r'\w+\s*=\s*\w+\s*-\s*1',  # i = i - 1
            r'\w+--',              # i--
            r'--\w+',              # --i
            r'range\s*\([^,)]+,\s*0',  # range(n, 0, -1) in Python
            r'for.*-1.*:',         # for loops with -1
        ]
        for pattern in decrement_patterns:
            if re.search(pattern, func_text):
                return True
        return False
    
    def _has_loops(self, node: Any) -> bool:
        """Check if node contains any loops."""
        return self._count_loops(node) > 0
    
    def _has_while_loop(self, node: Any) -> bool:
        """Check for while loops."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'while_statement':
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_while_loop(child):
                return True
        
        return False
    
    def _has_for_loop(self, node: Any) -> bool:
        """Check for for loops."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'for_statement':
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_for_loop(child):
                return True
        
        return False
    
    def _has_function_calls(self, node: Any) -> bool:
        """Check if node contains function calls."""
        return self._count_function_calls(node) > 0
    
    def _count_function_calls(self, node: Any) -> int:
        """Count function calls."""
        if not node:
            return 0
            
        count = 0
        call_types = {'call', 'call_expression', 'function_call'}
        
        if hasattr(node, 'type') and node.type in call_types:
            count += 1
        
        for child in getattr(node, 'children', []):
            count += self._count_function_calls(child)
        
        return count
    
    def _has_comparisons(self, node: Any) -> bool:
        """Check for comparison operations."""
        if not node:
            return False
            
        comparison_types = {'comparison', 'binary_operator', 'comparison_operator'}
        
        if hasattr(node, 'type') and node.type in comparison_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_comparisons(child):
                return True
        
        return False
    
    def _has_assignments(self, node: Any) -> bool:
        """Check for assignment operations."""
        if not node:
            return False
            
        assignment_types = {'assignment', 'assignment_expression', '='}
        
        if hasattr(node, 'type') and node.type in assignment_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_assignments(child):
                return True
        
        return False
    
    def _has_arithmetic(self, node: Any) -> bool:
        """Check for arithmetic operations."""
        if not node:
            return False
            
        arithmetic_types = {'binary_operator', 'arithmetic_operation', '+', '-', '*', '/', '%'}
        
        if hasattr(node, 'type') and node.type in arithmetic_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_arithmetic(child):
                return True
        
        return False
    
    def _has_array_operations(self, node: Any) -> bool:
        """Check for array operations like indexing, slicing."""
        if not node:
            return False
            
        array_types = {'subscript', 'array_access', 'index_expression', 'slice'}
        
        if hasattr(node, 'type') and node.type in array_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_array_operations(child):
                return True
        
        return False
    
    def _has_specific_operator(self, node: Any, operator: str) -> bool:
        """Check for specific operator in AST."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'binary_operator':
            if hasattr(node, 'operator') and node.operator == operator:
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_specific_operator(child, operator):
                return True
        
        return False
    
    def _has_bitwise_operations(self, node: Any) -> bool:
        """Check for bitwise operations in AST."""
        if not node:
            return False
            
        bitwise_types = {'binary_operator', 'bitwise_operation', 'shift_operation'}
        bitwise_ops = {'&', '|', '^', '<<', '>>', '~'}
        
        if hasattr(node, 'type') and node.type in bitwise_types:
            return True
            
        if hasattr(node, 'operator') and str(node.operator) in bitwise_ops:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_bitwise_operations(child):
                return True
        
        return False
    
    def _has_exponentiation(self, node: Any) -> bool:
        """Check for exponentiation operations."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type in {'power', 'exponentiation', 'binary_operator'}:
            if hasattr(node, 'operator') and str(node.operator) in {'**', 'pow'}:
                return True
                
        if hasattr(node, 'type') and node.type == 'call':
            # Check for pow() function calls
            for child in getattr(node, 'children', []):
                if hasattr(child, 'type') and child.type == 'identifier':
                    if hasattr(child, 'text') and 'pow' in str(child.text):
                        return True
        
        for child in getattr(node, 'children', []):
            if self._has_exponentiation(child):
                return True
        
        return False
    
    def _has_array_literals(self, node: Any) -> bool:
        """Check for array literal definitions."""
        if not node:
            return False
            
        array_types = {'array', 'list', 'array_literal', 'list_literal', 'array_expression'}
        
        if hasattr(node, 'type') and node.type in array_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_array_literals(child):
                return True
        
        return False
    
    def _has_string_concatenation(self, node: Any) -> bool:
        """Check for string concatenation operations."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'binary_operator':
            if hasattr(node, 'operator') and str(node.operator) == '+':
                # Check if operands are strings
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_string_concatenation(child):
                return True
        
        return False
    
    def _has_multiple_assignments(self, node: Any) -> bool:
        """Check for multiple assignment statements."""
        if not node:
            return False
            
        assignment_count = 0
        assignment_types = {'assignment', 'assignment_expression', 'augmented_assignment'}
        
        if hasattr(node, 'type') and node.type in assignment_types:
            assignment_count += 1
        
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and child.type in assignment_types:
                assignment_count += 1
        
        return assignment_count >= 2
    
    def _extract_functions_from_ast(self, ast_tree: Any) -> List[Dict[str, Any]]:
        """Extract functions from AST tree with better JavaScript support."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        functions = []
        
        # Special handling for fallback AST or when we have code
        # Check if using fallback AST
        is_fallback = hasattr(ast_tree, '__class__') and 'FallbackAST' in str(ast_tree.__class__)
        
        # Check language
        language = getattr(ast_tree, 'language', None)
        is_javascript = language == 'javascript'
        is_c = language in ['c', 'cpp']
        
        # Also check if code looks like JavaScript
        if hasattr(ast_tree, 'code') and not is_javascript and not is_c:
            code_snippet = ast_tree.code[:200].lower()
            if any(indicator in code_snippet for indicator in ['const ', 'let ', 'var ', '=>', 'function ', 'class ', 'export ', 'import ']):
                is_javascript = True
        
        # Use regex extraction for JavaScript or C with fallback AST
        if hasattr(ast_tree, 'code') and (is_javascript or (is_c and is_fallback)):
            code = ast_tree.code
            
            # Choose patterns based on language
            if is_javascript:
                # Enhanced JavaScript patterns - more specific
                patterns = [
                    # Function declaration: function quickSort() { ... }
                    (r'\bfunction\s+(\w+)\s*\([^)]*\)\s*\{', 'function'),
                    # Arrow function: const quickSort = () => { ... }
                    (r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>', 'arrow'),
                    # Function expression: const quickSort = function() { ... }
                    (r'(?:const|let|var)\s+(\w+)\s*=\s*function\s*\([^)]*\)\s*\{', 'expression'),
                    # Assigned function: quickSortlocal = function() { ... }
                    (r'^(?:\s*)(\w+)\s*=\s*function\s*\([^)]*\)\s*\{', 'assigned'),
                    # Class method: sort(originalArray) { ... } - must not be if/while/for
                    (r'^\s*(?!if\b|while\b|for\b|switch\b|catch\b|else\b)(\w+)\s*\([^)]*\)\s*\{', 'method'),
                ]
            elif is_c:
                # C/C++ function patterns
                patterns = [
                    # C function definition with various return types
                    (r'^\s*(?:static\s+|inline\s+|extern\s+)?(?:void|int|char|float|double|long\s+long|unsigned\s+\w+|signed\s+\w+|short|long|bool|\w+\s*\*?)\s+(\w+)\s*\([^)]*\)\s*\{', 'function'),
                ]
            else:
                patterns = []
            
            for pattern, func_type in patterns:
                for match in re.finditer(pattern, code, re.MULTILINE):
                    func_name = match.group(1)
                    start_pos = match.start()
                    
                    # Find end of function using brace matching
                    brace_count = 1  # Start with 1 because we already matched the opening brace
                    in_string = False
                    escape = False
                    string_char = None
                    end_pos = start_pos
                    
                    for i in range(match.end(), len(code)):
                        char = code[i]
                        
                        if escape:
                            escape = False
                            continue
                            
                        if char == '\\':
                            escape = True
                            continue
                            
                        if not in_string:
                            if char in ['"', "'", '`']:
                                in_string = True
                                string_char = char
                            elif char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                        else:
                            if char == string_char:
                                in_string = False
                                string_char = None
                    
                    # Check if we found a valid function (moved outside the loop)
                    if end_pos > start_pos:
                        func_text = code[start_pos:end_pos]
                        lines = func_text.count('\n') + 1
                        
                        # Calculate start and end line numbers
                        start_line = code[:start_pos].count('\n') + 1
                        end_line = code[:end_pos].count('\n') + 1
                        
                        # Create a simple node structure
                        class SimpleNode:
                            def __init__(self):
                                self.type = func_type
                                self.start_byte = start_pos
                                self.end_byte = end_pos
                                self.children = []
                        
                        func_info = {
                            'node': SimpleNode(),
                            'type': func_type,
                            'start_byte': start_pos,
                            'end_byte': end_pos,
                            'text': func_text,
                            'name': func_name,
                            'lines': {
                                'total': lines,
                                'start': start_line,
                                'end': end_line
                            }
                        }
                        functions.append(func_info)
        
        # If no functions found or not JavaScript, try the original method
        if not functions:
            if hasattr(ast_tree, 'code'):
                self._find_functions_recursive(ast_tree.root, functions, ast_tree.code)
        
        return functions
    
    def _find_functions_recursive(self, node: Any, functions: List[Dict], code: str):
        """Recursively find function definitions in AST."""
        if not node:
            return
            
        function_types = {
            'function_definition',  # Python
            'function_declaration', # JavaScript, C, Java
            'method_definition',    # Java, JavaScript classes
            'arrow_function',       # JavaScript
            'function_item',        # Rust
            'func_declaration',     # Go
            'function',            # JavaScript function expressions
            'function_expression', # JavaScript/TypeScript
        }
        
        if hasattr(node, 'type') and node.type in function_types:
            lines_info = self._calculate_lines(node, code)
            func_info = {
                'node': node,
                'type': node.type,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'text': code[node.start_byte:node.end_byte],
                'name': self._extract_function_name(node, code),
                'lines': lines_info,
                'start_line': lines_info['start'],
                'end_line': lines_info['end']
            }
            functions.append(func_info)
        
        # Also check for assignment patterns like: __assign = function() {...}
        elif hasattr(node, 'type') and node.type in {'assignment', 'assignment_expression', 'variable_declarator'}:
            # Check if any descendant is a function
            var_name = self._extract_assignment_name(node, code)
            self._find_functions_in_descendants(node, functions, code, var_name)
        
        # Recursively search children
        for child in getattr(node, 'children', []):
            self._find_functions_recursive(child, functions, code)
    
    def _extract_function_name(self, func_node: Any, code: str) -> str:
        """Extract function name from function node."""
        try:
            # Different languages have different AST structures
            for child in getattr(func_node, 'children', []):
                if hasattr(child, 'type'):
                    # Python: function name is often direct child with type 'identifier'
                    if child.type in {'identifier', 'function_name', 'name'}:
                        name = code[child.start_byte:child.end_byte].strip()
                        if name and not name.startswith('(') and not name.startswith('def'):
                            return name
                    # Some languages nest the name deeper
                    elif child.type in {'function_declarator', 'function_signature'}:
                        for subchild in getattr(child, 'children', []):
                            if hasattr(subchild, 'type') and subchild.type in {'identifier', 'function_name'}:
                                name = code[subchild.start_byte:subchild.end_byte].strip()
                                if name and not name.startswith('('):
                                    return name
        except (IndexError, AttributeError):
            pass
        return 'anonymous'
    
    def _extract_assignment_name(self, assignment_node: Any, code: str) -> str:
        """Extract variable name from assignment node."""
        # Look for identifier on the left side of assignment
        for child in getattr(assignment_node, 'children', []):
            if hasattr(child, 'type') and child.type == 'identifier':
                return code[child.start_byte:child.end_byte]
        return None
    
    def _find_functions_in_descendants(self, node: Any, functions: List[Dict], code: str, var_name: str = None):
        """Find function nodes in descendants of a node."""
        function_types = {
            'function_definition', 'function_declaration', 'method_definition',
            'arrow_function', 'function_item', 'func_declaration',
            'function', 'function_expression'
        }
        
        # Check direct children
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and child.type in function_types:
                func_info = {
                    'node': child,
                    'type': child.type,
                    'start_byte': child.start_byte,
                    'end_byte': child.end_byte,
                    'text': code[child.start_byte:child.end_byte],
                    'name': var_name or self._extract_function_name(child, code),
                    'lines': self._calculate_lines(child, code)
                }
                functions.append(func_info)
            else:
                # Recursively check descendants
                self._find_functions_in_descendants(child, functions, code, var_name)
    
    def _calculate_lines(self, node: Any, code: str) -> Dict[str, int]:
        """Calculate line information for a function."""
        start_line = code[:node.start_byte].count('\n') + 1
        end_line = code[:node.end_byte].count('\n') + 1
        return {
            "start": start_line,
            "end": end_line,
            "total": end_line - start_line + 1
        }
    
    def _create_specific_algorithm_entry(self, func: Dict[str, Any], algo_type: AlgorithmType, 
                                       subtype: str, confidence: float, 
                                       ast_tree: Any, language: str) -> Dict[str, Any]:
        """Create algorithm entry with specific subtype information."""
        # Generate unique ID
        algo_id = f"algo_{uuid.uuid4().hex[:8]}"
        
        # Calculate complexity and metrics
        complexity = self._calculate_cyclomatic_complexity(func['node'])
        metrics = self._calculate_algorithm_metrics(func, complexity)
        
        # Generate normalized representation and hashes
        hashes = self._generate_algorithm_hashes(func['node'], func['text'], language)
        
        # Extract mathematical invariants
        invariants = self._extract_mathematical_invariants(func['node'])
        
        # Store data for dynamic transformation resistance calculation
        self.last_algorithm_data = {
            'confidence': confidence,
            'algorithm_type': algo_type.value,
            'algorithm_subtype': subtype,
            'evidence': {
                'matched_keywords': self._get_matched_keywords(func['text'], func['name'], algo_type, subtype),
                'ast_patterns': [],  # Could be expanded
                'required_patterns': []  # Could be expanded
            }
        }
        
        # Extract comprehensive AST data
        ast_features = self._extract_ast_features(func['node'])
        identifiers = self._extract_identifiers(func['node'], func['text'])
        
        self.last_ast_data = {
            'depth': ast_features.get('depth', 1),
            'node_types': ast_features.get('node_types', []),
            'complexity': {'cyclomatic': complexity},
            'max_nesting_depth': self._calculate_nesting_depth(func['node']),
            'identifiers': identifiers,
            'functions': [{'name': func['name'], 'line_count': func['lines']['total']}],
            'imports': self._extract_imports(ast_tree) if ast_tree else []
        }
        
        self.last_hash_data = hashes
        self.last_invariants = invariants
        
        # Normalize audio codec subtypes to generic audio_codec for easier review
        normalized_subtype = subtype
        if algo_type == AlgorithmType.AUDIO_CODEC and subtype in ['pcm', 'pcm_codec', 'alaw', 'ulaw', 'g711a', 'g711u']:
            normalized_subtype = 'audio_codec'
        
        return {
            'id': algo_id,
            'type': 'algorithm',
            'name': f"{algo_type.value}_{normalized_subtype}_implementation",
            'algorithm_type': algo_type.value,
            'algorithm_subtype': normalized_subtype,
            'subtype_classification': normalized_subtype,  # Add this for compatibility
            'original_subtype': subtype,  # Keep original for detailed analysis
            'algorithm_category': self._get_algorithm_category(algo_type),
            'confidence': round(confidence, 3),
            'confidence_score': round(confidence, 3),  # Add this too
            'complexity_metric': complexity,
            'complexity': {'cyclomatic': complexity},  # Add for false positive filter compatibility
            'lines': func['lines'],
            'location': {  # Add location information
                'start': func.get('start_line', func['lines'].get('start', 1)),
                'end': func.get('end_line', func['lines'].get('end', func['lines'].get('total', 1)))
            },
            'metrics': metrics,  # Add comprehensive metrics
            'function_name': func['name'],  # Add function_name at top level
            'function_info': {  # Add function info
                'name': func['name'],
                'lines': func['lines'],
                'type': func['type']
            },
            'evidence': {
                'pattern_type': self._get_algorithm_category(algo_type),
                'algorithm_type': algo_type.value,
                'control_flow': 'complex' if complexity > 5 else 'linear',
                'ast_signature': hashlib.md5(str(func['node']).encode()).hexdigest()[:16],
                'cyclomatic_complexity': complexity,
                'matched_keywords': self._get_matched_keywords(func['text'], func['name'], algo_type, subtype),
                'pattern_confidence': confidence,
                'matched_subtype': subtype,
                'is_generic': subtype.endswith('_generic'),
                'specificity_score': confidence,
                'normalized_representation': hashes.get('normalized_representation', '')
            },
            'hashes': hashes,
            'transformation_resistance': self._calculate_transformation_resistance(),
            'ast_representation': {
                'normalized': func['node'].type if hasattr(func['node'], 'type') else 'unknown',
                'original': func['text'][:200] + '...' if len(func['text']) > 200 else func['text']
            },
            'control_flow_graph': f"branches:{complexity-1}_loops:{self._count_loops(func['node'])}_calls:{self._count_function_calls(func['node'])}",
            'mathematical_invariants': invariants
        }
    
    def _calculate_cyclomatic_complexity(self, node: Any) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        decision_types = {
            'if_statement', 'while_statement', 'for_statement',
            'case_statement', 'conditional_expression'
        }
        
        def count_decisions(n):
            count = 0
            if hasattr(n, 'type') and n.type in decision_types:
                count += 1
            for child in getattr(n, 'children', []):
                count += count_decisions(child)
            return count
        
        return complexity + count_decisions(node)
    
    def _calculate_algorithm_metrics(self, func: Dict[str, Any], complexity: int) -> Dict[str, Any]:
        """Calculate comprehensive metrics for algorithm analysis."""
        func_text = func['text']
        func_node = func['node']
        
        # Count various code elements
        metrics = {
            'size': {
                'lines_of_code': func['lines']['total'],
                'characters': len(func_text),
                'tokens': len(func_text.split()),
            },
            'complexity': {
                'cyclomatic': complexity,
                'cognitive': self._calculate_cognitive_complexity(func_node),
                'halstead': self._calculate_halstead_metrics(func_text),
                'nesting_depth': self._calculate_max_nesting_depth(func_node)
            },
            'structure': {
                'loops': self._count_loops(func_node),
                'conditionals': self._count_conditionals(func_node),
                'function_calls': self._count_function_calls(func_node),
                'returns': self._count_returns(func_node),
                'parameters': len(func.get('parameters', [])),
            },
            'operations': {
                'arithmetic': self._count_arithmetic_ops(func_text),
                'bitwise': self._count_bitwise_ops(func_text),
                'logical': self._count_logical_ops(func_text),
                'assignments': self._count_assignments(func_text),
                'comparisons': self._count_comparisons(func_text)
            }
        }
        
        # Calculate derived metrics
        metrics['derived'] = {
            'complexity_per_line': round(complexity / max(1, metrics['size']['lines_of_code']), 2),
            'tokens_per_line': round(metrics['size']['tokens'] / max(1, metrics['size']['lines_of_code']), 2),
            'operation_density': round(
                sum(metrics['operations'].values()) / max(1, metrics['size']['lines_of_code']), 2
            ),
            'structural_complexity': metrics['structure']['loops'] + metrics['structure']['conditionals']
        }
        
        return metrics
    
    def _calculate_cognitive_complexity(self, node: Any) -> int:
        """Calculate cognitive complexity (simplified version)."""
        complexity = 0
        nesting_level = 0
        
        def calculate(n, level):
            nonlocal complexity
            node_type = getattr(n, 'type', '')
            
            # Increment for control structures
            if node_type in ['if_statement', 'conditional_expression']:
                complexity += 1 + level
            elif node_type in ['for_statement', 'while_statement', 'do_statement']:
                complexity += 1 + level
            elif node_type == 'switch_statement':
                complexity += level
            
            # Increment nesting for nested structures
            new_level = level
            if node_type in ['if_statement', 'for_statement', 'while_statement', 'switch_statement']:
                new_level = level + 1
            
            # Recurse to children
            for child in getattr(n, 'children', []):
                calculate(child, new_level)
        
        calculate(node, 0)
        return complexity
    
    def _calculate_halstead_metrics(self, code: str) -> Dict[str, float]:
        """Calculate simplified Halstead metrics."""
        import re
        
        # Extract operators and operands
        operators = re.findall(r'[+\-*/%=<>!&|^~]+|if|else|for|while|return|def|class', code)
        operands = re.findall(r'\b[a-zA-Z_]\w*\b|[0-9]+', code)
        
        n1 = len(set(operators))  # Unique operators
        n2 = len(set(operands))   # Unique operands
        N1 = len(operators)       # Total operators
        N2 = len(operands)        # Total operands
        
        # Halstead metrics
        n = n1 + n2  # Vocabulary
        N = N1 + N2  # Length
        
        if n1 > 0 and n2 > 0 and N > 0:
            volume = N * (n.bit_length() if n > 0 else 1)
            difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
            effort = volume * difficulty
        else:
            volume = difficulty = effort = 0
        
        return {
            'vocabulary': n,
            'length': N,
            'volume': round(volume, 2),
            'difficulty': round(difficulty, 2),
            'effort': round(effort, 2)
        }
    
    def _calculate_max_nesting_depth(self, node: Any) -> int:
        """Calculate maximum nesting depth."""
        def get_depth(n, current_depth):
            node_type = getattr(n, 'type', '')
            
            # Increment depth for nesting structures
            if node_type in ['if_statement', 'for_statement', 'while_statement', 
                            'function_definition', 'class_definition']:
                current_depth += 1
            
            max_depth = current_depth
            for child in getattr(n, 'children', []):
                child_depth = get_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return get_depth(node, 0)
    
    def _count_loops(self, node: Any) -> int:
        """Count number of loops."""
        count = 0
        loop_types = {'for_statement', 'while_statement', 'do_statement', 
                     'for_in_statement', 'for_of_statement'}
        
        def count_recursive(n):
            nonlocal count
            if hasattr(n, 'type') and n.type in loop_types:
                count += 1
            for child in getattr(n, 'children', []):
                count_recursive(child)
        
        count_recursive(node)
        return count
    
    def _count_conditionals(self, node: Any) -> int:
        """Count conditional statements."""
        count = 0
        conditional_types = {'if_statement', 'switch_statement', 'conditional_expression'}
        
        def count_recursive(n):
            nonlocal count
            if hasattr(n, 'type') and n.type in conditional_types:
                count += 1
            for child in getattr(n, 'children', []):
                count_recursive(child)
        
        count_recursive(node)
        return count
    
    def _count_function_calls(self, node: Any) -> int:
        """Count function calls."""
        count = 0
        call_types = {'call_expression', 'method_call', 'function_call'}
        
        def count_recursive(n):
            nonlocal count
            if hasattr(n, 'type') and n.type in call_types:
                count += 1
            for child in getattr(n, 'children', []):
                count_recursive(child)
        
        count_recursive(node)
        return count
    
    def _count_returns(self, node: Any) -> int:
        """Count return statements."""
        count = 0
        
        def count_recursive(n):
            nonlocal count
            if hasattr(n, 'type') and n.type == 'return_statement':
                count += 1
            for child in getattr(n, 'children', []):
                count_recursive(child)
        
        count_recursive(node)
        return count
    
    def _count_arithmetic_ops(self, text: str) -> int:
        """Count arithmetic operations."""
        ops = re.findall(r'[+\-*/%](?!=)', text)
        return len(ops)
    
    def _count_bitwise_ops(self, text: str) -> int:
        """Count bitwise operations."""
        ops = re.findall(r'[&|^~](?![&|=])|<<|>>', text)
        return len(ops)
    
    def _count_logical_ops(self, text: str) -> int:
        """Count logical operations."""
        ops = re.findall(r'&&|\|\||!(?!=)|and\s|or\s|not\s', text)
        return len(ops)
    
    def _count_assignments(self, text: str) -> int:
        """Count assignment operations."""
        ops = re.findall(r'(?<![=!<>])=(?!=)', text)
        return len(ops)
    
    def _count_comparisons(self, text: str) -> int:
        """Count comparison operations."""
        ops = re.findall(r'[<>]=?|[!=]=', text)
        return len(ops)
    
    def _generate_algorithm_hashes(self, func_node: Any, func_text: str, language: str) -> Dict[str, Any]:
        """Generate hashes for the algorithm."""
        # Generate normalized representation
        normalized_repr = self.normalizer.normalize_function(func_node, func_text, language)
        
        return {
            "direct": self.direct_hasher.hash_text(normalized_repr),
            "fuzzy": {
                "tlsh": self.fuzzy_hasher.hash_text(normalized_repr),
                "tlsh_threshold": self.config.tlsh_threshold if self.config else 100
            },
            "semantic": {
                "minhash": self.semantic_hasher.generate_minhash(normalized_repr),
                "lsh_bands": self.config.lsh_bands if self.config else 20,
                "simhash": self.semantic_hasher.generate_simhash(normalized_repr)
            },
            "normalized_representation": normalized_repr,
            "ast_features": self._extract_ast_features(func_node)
        }
    
    def _extract_mathematical_invariants(self, node: Any) -> List[Dict[str, Any]]:
        """Extract mathematical invariants."""
        # Simplified extraction
        return []
    
    def _calculate_transformation_resistance(self) -> Dict[str, float]:
        """Calculate dynamic transformation resistance scores based on extracted data."""
        # Use stored data from last analysis
        return self.transformation_calculator.calculate_resistance(
            self.last_algorithm_data,
            self.last_ast_data,
            self.last_hash_data,
            self.last_invariants
        )
    
    def _extract_ast_features(self, func_node: Any) -> Dict[str, Any]:
        """Extract comprehensive AST features for transformation resistance."""
        if not func_node:
            return {
                "node_types": [],
                "depth": 0,
                "branching_factor": 0,
                "leaf_count": 0,
                "control_structures": 0,
                "avg_branching": 0.0,
                "control_density": 0.0
            }
        
        node_types = []
        max_depth = 0
        control_count = 0
        leaf_count = 0
        branch_counts = []
        
        control_types = {
            'if_statement', 'while_statement', 'for_statement', 'switch_statement',
            'conditional_expression', 'try_statement', 'catch_clause'
        }
        
        def traverse(node, depth=0):
            nonlocal max_depth, control_count, leaf_count
            
            if not node or not hasattr(node, 'type'):
                return
            
            node_types.append(node.type)
            max_depth = max(max_depth, depth)
            
            if node.type in control_types:
                control_count += 1
            
            children = getattr(node, 'children', [])
            if not children:
                leaf_count += 1
            else:
                branch_counts.append(len(children))
                for child in children:
                    traverse(child, depth + 1)
        
        traverse(func_node)
        
        avg_branching = sum(branch_counts) / len(branch_counts) if branch_counts else 0
        total_nodes = len(node_types)
        control_density = control_count / total_nodes if total_nodes > 0 else 0
        
        return {
            "node_types": node_types,
            "depth": max_depth,
            "branching_factor": max(branch_counts) if branch_counts else 0,
            "leaf_count": leaf_count,
            "control_structures": control_count,
            "avg_branching": avg_branching,
            "control_density": control_density
        }
    
    def _get_algorithm_category(self, algo_type: AlgorithmType) -> str:
        """Get algorithm category."""
        category_mapping = {
            AlgorithmType.SORTING_ALGORITHM: "core_algorithms",
            AlgorithmType.SEARCH_ALGORITHM: "core_algorithms",
            AlgorithmType.NUMERICAL_ALGORITHM: "mathematical_algorithms",
            AlgorithmType.COMPRESSION_ALGORITHM: "data_processing",
            AlgorithmType.DYNAMIC_PROGRAMMING: "optimization",
            AlgorithmType.OBJECT_MANIPULATION: "data_structures",
            AlgorithmType.ARRAY_MANIPULATION: "data_structures",
            AlgorithmType.ITERATOR_PATTERN: "design_patterns",
            AlgorithmType.POLYFILL_PATTERN: "runtime_helpers"
        }
        return category_mapping.get(algo_type, "unknown")
    
    def _get_matched_keywords(self, func_text: str, func_name: str, algo_type: AlgorithmType, subtype: str) -> List[str]:
        """Get matched keywords."""
        # Get pattern for this subtype
        type_config = self.patterns.get(algo_type, {})
        subtype_pattern = type_config.get('subtypes', {}).get(subtype, {})
        keywords = subtype_pattern.get('keywords', [])
        
        matched = []
        func_text_lower = func_text.lower()
        func_name_lower = func_name.lower()
        
        for keyword in keywords:
            if keyword in func_name_lower or keyword in func_text_lower:
                matched.append(keyword)
        
        return matched
    
    # Additional helper methods for new patterns
    def _has_binary_operator(self, node: Any, operator: str) -> bool:
        """Check if node contains specific binary operator."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'binary_expression':
            for child in getattr(node, 'children', []):
                if hasattr(child, 'type') and child.type == operator:
                    return True
        for child in getattr(node, 'children', []):
            if self._has_binary_operator(child, operator):
                return True
        return False
    
    def _has_for_in_loop(self, node: Any) -> bool:
        """Check if node contains for-in loop."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type in {'for_in_statement', 'for_of_statement'}:
            return True
        for child in getattr(node, 'children', []):
            if self._has_for_in_loop(child):
                return True
        return False
    
    def _has_property_assignment(self, node: Any) -> bool:
        """Check if node contains property assignment."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type in {'member_expression', 'subscript_expression'}:
            return True
        for child in getattr(node, 'children', []):
            if self._has_property_assignment(child):
                return True
        return False
    
    def _has_function_assignment(self, node: Any) -> bool:
        """Check if node contains function assignment."""
        return self._has_assignments(node) and self._has_function_expressions(node)
    
    def _has_function_expressions(self, node: Any) -> bool:
        """Check if node contains function expressions."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type in {'function_expression', 'arrow_function'}:
            return True
        for child in getattr(node, 'children', []):
            if self._has_function_expressions(child):
                return True
        return False
    
    def _has_prototype_access(self, node: Any) -> bool:
        """Check if node accesses prototype."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'member_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_prototype_access(child):
                return True
        return False
    
    def _has_object_return(self, node: Any) -> bool:
        """Check if function returns an object."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'return_statement':
            return True
        for child in getattr(node, 'children', []):
            if self._has_object_return(child):
                return True
        return False
    
    def _has_method_definition(self, node: Any) -> bool:
        """Check if node contains method definitions."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'method_definition':
            return True
        for child in getattr(node, 'children', []):
            if self._has_method_definition(child):
                return True
        return False
    
    def _has_switch_statement(self, node: Any) -> bool:
        """Check if node contains switch statement."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'switch_statement':
            return True
        for child in getattr(node, 'children', []):
            if self._has_switch_statement(child):
                return True
        return False
    
    def _has_promise_call(self, node: Any) -> bool:
        """Check if node contains Promise calls."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'call_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_promise_call(child):
                return True
        return False
    
    def _has_array_assignment(self, node: Any) -> bool:
        """Check if node contains array element assignment."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'subscript_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_array_assignment(child):
                return True
        return False
    
    def _has_array_access(self, node: Any) -> bool:
        """Check if node contains array access."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'subscript_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_array_access(child):
                return True
        return False
    
    def _has_object_operations(self, node: Any) -> bool:
        """Check for object operations like property access, object literals."""
        if not node:
            return False
            
        object_types = {'object', 'object_expression', 'object_literal', 'property_access', 'member_expression'}
        
        if hasattr(node, 'type') and node.type in object_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_object_operations(child):
                return True
        
        return False
    
    def _has_map_operations(self, node: Any) -> bool:
        """Check for map/dictionary operations."""
        if not node:
            return False
            
        map_types = {'map', 'hash_map', 'dictionary', 'call_expression'}
        
        if hasattr(node, 'type') and node.type in map_types:
            return True
            
        # Check for Map constructor or map method calls
        if hasattr(node, 'type') and node.type == 'call_expression':
            if hasattr(node, 'function'):
                func_text = str(node.function)
                if 'Map' in func_text or 'HashMap' in func_text or 'dict' in func_text:
                    return True
        
        for child in getattr(node, 'children', []):
            if self._has_map_operations(child):
                return True
        
        return False
    
    def _extract_identifiers(self, node: Any, code: str) -> List[str]:
        """Extract all identifiers from the AST node."""
        identifiers = []
        
        if not node:
            return identifiers
        
        # Common identifier node types across languages
        identifier_types = {'identifier', 'variable_name', 'function_name', 'parameter', 'field_identifier'}
        
        if hasattr(node, 'type') and node.type in identifier_types:
            # Extract text from node
            if hasattr(node, 'text'):
                text = node.text
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='ignore')
                identifiers.append(text)
            elif hasattr(node, 'start_byte') and hasattr(node, 'end_byte'):
                text = code[node.start_byte:node.end_byte]
                identifiers.append(text)
        
        # Recursively process children
        for child in getattr(node, 'children', []):
            identifiers.extend(self._extract_identifiers(child, code))
        
        return identifiers
    
    def _calculate_nesting_depth(self, node: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of control structures."""
        if not node:
            return current_depth
        
        # Control structure types that increase nesting
        nesting_types = {
            'if_statement', 'while_statement', 'for_statement', 'for_in_statement',
            'switch_statement', 'case_statement', 'try_statement', 'catch_clause',
            'function_definition', 'method_definition', 'class_definition',
            'do_statement', 'with_statement'
        }
        
        max_depth = current_depth
        next_depth = current_depth
        
        if hasattr(node, 'type') and node.type in nesting_types:
            next_depth = current_depth + 1
            max_depth = next_depth
        
        # Check all children
        for child in getattr(node, 'children', []):
            child_depth = self._calculate_nesting_depth(child, next_depth)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _extract_imports(self, ast_tree: Any) -> List[str]:
        """Extract import statements from the AST."""
        imports = []
        
        if not ast_tree:
            return imports
        
        # Import node types across languages
        import_types = {
            'import_statement', 'import_declaration', 'import_from_statement',
            'include_statement', 'require_statement', 'use_declaration',
            'import', 'from_import', 'module_import'
        }
        
        def extract_imports_recursive(node):
            if hasattr(node, 'type') and node.type in import_types:
                # Try to get the imported module/package name
                for child in getattr(node, 'children', []):
                    if hasattr(child, 'type') and child.type in {'string', 'identifier', 'dotted_name'}:
                        if hasattr(child, 'text'):
                            text = child.text
                            if isinstance(text, bytes):
                                text = text.decode('utf-8', errors='ignore')
                            imports.append(text.strip('"\''))
            
            # Recursively check children
            for child in getattr(node, 'children', []):
                extract_imports_recursive(child)
        
        extract_imports_recursive(ast_tree)
        return imports
    
    def _convert_minified_pattern_to_algorithm(self, pattern: Dict[str, Any], 
                                              ast_tree: Any) -> Dict[str, Any]:
        """Convert minified pattern detection to standard algorithm format."""
        algo_id = f"algo_{uuid.uuid4().hex[:8]}"
        
        # Get the whole file as the location for minified code
        location = {
            'start': 1,
            'end': 1,  # Minified is usually single line
            'type': 'minified_detection'
        }
        
        # Build evidence
        evidence = pattern.get('evidence', {})
        evidence.update({
            'detection_context': 'minified_code',
            'minified_confidence': pattern.get('confidence', 0.5)
        })
        
        # Calculate transformation resistance for minified code
        trans_resistance = {
            'variable_renaming': 0.9,  # Already minified
            'code_formatting': 0.9,    # Format already removed
            'comment_removal': 1.0,    # No comments
            'function_inlining': 0.7,  # May be inlined
            'dead_code_elimination': 0.8,  # Likely optimized
            'overall': 0.85
        }
        
        return {
            'id': algo_id,
            'type': 'algorithm',
            'name': f"{pattern['algorithm_type']}_{pattern['algorithm_subtype']}_minified",
            'algorithm_type': pattern['algorithm_type'],
            'algorithm_subtype': pattern['algorithm_subtype'],
            'subtype_classification': pattern['algorithm_subtype'],
            'original_subtype': pattern['algorithm_subtype'],
            'algorithm_category': 'core_algorithms',
            'confidence': pattern.get('confidence', 0.5),
            'location': location,
            'function_name': 'minified_function',
            'evidence': evidence,
            'hashes': {
                'direct': hashlib.sha256((self.content if hasattr(self, 'content') else '').encode()).hexdigest(),
                'fuzzy': {},  # Fuzzy hashes would be calculated by the main analyzer
                'semantic': {}
            },
            'transformation_resistance': trans_resistance,
            'control_flow_graph': 'minified',
            'mathematical_invariants': []
        }