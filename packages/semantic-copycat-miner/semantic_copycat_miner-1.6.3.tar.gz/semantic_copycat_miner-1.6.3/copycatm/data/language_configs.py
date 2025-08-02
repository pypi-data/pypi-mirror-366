"""
Language-specific configurations for CopycatM.

Each language has tailored settings for optimal algorithm detection
and signature generation, especially for identifying derived work
from OSS libraries.
"""

from typing import Dict, Any, List


def get_language_config(language: str) -> Dict[str, Any]:
    """Get configuration for a specific language."""
    configs = {
        "python": {
            "extensions": [".py", ".pyx", ".pyi"],
            "mime_type": "text/x-python",
            "parser": "tree_sitter_python",
            "fallback_parser": "ast",
            "complexity_threshold": 3,
            "min_lines": 3,  # Traditional threshold (Python functions are often compact)
            "min_function_lines": 2,
            "semantic_threshold": 100,  # Semantic analysis threshold
            "traditional_threshold": 25,  # Traditional analysis threshold
            "unknown_algorithm_threshold": 30,  # Lower threshold for Python
            "block_extractors": ["function", "class", "loop", "conditional", "with_statement"],
            "normalization_rules": {
                "list_comprehension": "ITERATE_TRANSFORM",
                "lambda": "ANONYMOUS_FUNCTION",
                "generator": "LAZY_ITERATOR"
            },
            "known_algorithm_patterns": ["quicksort_recursive", "merge_sort", "binary_search"],
            "keywords": [
                "def", "class", "if", "else", "elif", "for", "while", "try", "except",
                "finally", "with", "import", "from", "as", "return", "yield", "lambda"
            ],
            "operators": [
                "+", "-", "*", "/", "//", "%", "**", "==", "!=", "<", ">", "<=", ">=",
                "and", "or", "not", "in", "is", "&", "|", "^", "~", "<<", ">>"
            ]
        },
        "javascript": {
            "extensions": [".js", ".jsx"],
            "mime_type": "text/javascript",
            "parser": "tree_sitter_javascript",
            "fallback_parser": "esprima",
            "complexity_threshold": 3,
            "min_lines": 2,  # Traditional threshold (JavaScript utility functions are often small)
            "min_function_lines": 2,
            "semantic_threshold": 150,  # Semantic analysis threshold
            "traditional_threshold": 30,  # Traditional analysis threshold
            "unknown_algorithm_threshold": 50,  # Standard threshold
            "block_extractors": ["function", "arrow_function", "loop", "conditional", "try_catch"],
            "normalization_rules": {
                "arrow_function": "ANONYMOUS_FUNCTION",
                "promise": "ASYNC_OPERATION",
                "async_await": "ASYNC_OPERATION",
                "map_filter_reduce": "ITERATE_TRANSFORM"
            },
            "known_algorithm_patterns": ["quicksort_functional", "merge_sort", "binary_search"],
            "keywords": [
                "function", "var", "let", "const", "if", "else", "for", "while", "do",
                "switch", "case", "default", "try", "catch", "finally", "throw", "return",
                "class", "extends", "super", "new", "delete", "typeof", "instanceof"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "**", "==", "===", "!=", "!==", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", ">>>"
            ]
        },
        "typescript": {
            "extensions": [".ts", ".tsx"],
            "mime_type": "text/typescript",
            "parser": "tree_sitter_typescript",
            "fallback_parser": "esprima",
            "complexity_threshold": 3,
            "min_lines": 2,  # TypeScript utility functions are often small
            "min_function_lines": 2,
            "unknown_algorithm_threshold": 50,
            "keywords": [
                "function", "var", "let", "const", "if", "else", "for", "while", "do",
                "switch", "case", "default", "try", "catch", "finally", "throw", "return",
                "class", "extends", "super", "new", "delete", "typeof", "instanceof",
                "interface", "type", "enum", "namespace", "module", "export", "import"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "**", "==", "===", "!=", "!==", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", ">>>"
            ]
        },
        "java": {
            "extensions": [".java"],
            "mime_type": "text/x-java-source",
            "parser": "tree_sitter_java",
            "fallback_parser": "javalang",
            "complexity_threshold": 3,
            "min_lines": 5,  # Traditional threshold (Java methods tend to be more verbose)
            "min_function_lines": 3,
            "semantic_threshold": 150,  # Semantic analysis threshold
            "traditional_threshold": 30,  # Traditional analysis threshold
            "unknown_algorithm_threshold": 50,
            "block_extractors": ["method", "class", "loop", "try_catch", "lambda"],
            "normalization_rules": {
                "stream_api": "ITERATE_TRANSFORM",
                "anonymous_class": "ANONYMOUS_FUNCTION",
                "optional": "NULLABLE_TYPE"
            },
            "known_algorithm_patterns": ["quicksort_iterative", "heap_sort", "dijkstra"],
            "keywords": [
                "public", "private", "protected", "static", "final", "abstract", "class",
                "interface", "extends", "implements", "if", "else", "for", "while", "do",
                "switch", "case", "default", "try", "catch", "finally", "throw", "return",
                "new", "this", "super", "import", "package"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", ">>>"
            ]
        },
        "c": {
            "extensions": [".c", ".h"],
            "mime_type": "text/x-csrc",
            "parser": "tree_sitter_c",
            "fallback_parser": "pycparser",
            "complexity_threshold": 3,
            "min_lines": 5,  # C functions can be compact but often have setup
            "min_function_lines": 3,
            "unknown_algorithm_threshold": 50,
            "keywords": [
                "auto", "break", "case", "char", "const", "continue", "default", "do",
                "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
                "long", "register", "return", "short", "signed", "sizeof", "static",
                "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"
            ]
        },
        "cpp": {
            "extensions": [".cpp", ".cc", ".cxx", ".hpp"],
            "mime_type": "text/x-c++src",
            "parser": "tree_sitter_cpp",
            "fallback_parser": "pycparser",
            "complexity_threshold": 3,
            "min_lines": 5,  # C++ methods with templates can be verbose
            "min_function_lines": 3,
            "unknown_algorithm_threshold": 50,
            "keywords": [
                "auto", "break", "case", "char", "const", "continue", "default", "do",
                "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
                "long", "register", "return", "short", "signed", "sizeof", "static",
                "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
                "class", "namespace", "template", "typename", "virtual", "public", "private",
                "protected", "friend", "inline", "explicit", "mutable", "operator", "new", "delete"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", "::", "->", "."
            ]
        },
        "go": {
            "extensions": [".go"],
            "mime_type": "text/x-go",
            "parser": "tree_sitter_go",
            "fallback_parser": None,
            "complexity_threshold": 3,
            "min_lines": 3,  # Go functions are often concise
            "min_function_lines": 2,
            "unknown_algorithm_threshold": 50,
            "keywords": [
                "break", "case", "chan", "const", "continue", "default", "defer", "else",
                "fallthrough", "for", "func", "go", "goto", "if", "import", "interface",
                "map", "package", "range", "return", "select", "struct", "switch", "type", "var"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", "&^"
            ]
        },
        "rust": {
            "extensions": [".rs"],
            "mime_type": "text/x-rust",
            "parser": "tree_sitter_rust",
            "fallback_parser": None,
            "complexity_threshold": 3,
            "min_lines": 3,  # Rust functions can be compact with expressions
            "min_function_lines": 2,
            "unknown_algorithm_threshold": 50,
            "keywords": [
                "as", "break", "const", "continue", "crate", "else", "enum", "extern",
                "false", "fn", "for", "if", "impl", "in", "let", "loop", "match", "mod",
                "move", "mut", "pub", "ref", "return", "self", "Self", "static", "struct",
                "super", "trait", "true", "type", "unsafe", "use", "where", "while"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"
            ]
        }
    }
    
    return configs.get(language, {})


def get_supported_languages() -> list[str]:
    """Get list of all supported languages."""
    return [
        "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"
    ]


def get_language_extensions() -> Dict[str, list[str]]:
    """Get file extensions for each supported language."""
    extensions = {}
    for language in get_supported_languages():
        config = get_language_config(language)
        extensions[language] = config.get("extensions", [])
    return extensions


# OSS Library Signature Patterns
OSS_SIGNATURES = {
    "python": {
        "numpy": {
            "patterns": [
                r"np\.array\s*\(",
                r"numpy\.ndarray",
                r"np\.zeros\s*\(",
                r"np\.ones\s*\(",
                r"np\.linspace\s*\(",
                r"np\.random\.",
                r"np\.dot\s*\(",
                r"np\.matmul\s*\(",
                r"\.reshape\s*\(",
                r"\.transpose\s*\(",
            ],
            "imports": ["import numpy", "from numpy import"],
            "confidence_boost": 0.2
        },
        "pandas": {
            "patterns": [
                r"pd\.DataFrame\s*\(",
                r"\.read_csv\s*\(",
                r"\.groupby\s*\(",
                r"\.merge\s*\(",
                r"\.pivot_table\s*\(",
                r"\.apply\s*\(",
                r"\.loc\[",
                r"\.iloc\[",
                r"\.dropna\s*\(",
                r"\.fillna\s*\(",
            ],
            "imports": ["import pandas", "from pandas import"],
            "confidence_boost": 0.2
        },
        "tensorflow": {
            "patterns": [
                r"tf\.keras\.",
                r"tf\.nn\.",
                r"tf\.Variable\s*\(",
                r"tf\.constant\s*\(",
                r"tf\.placeholder\s*\(",
                r"\.fit\s*\(",
                r"\.predict\s*\(",
                r"\.compile\s*\(",
                r"Sequential\s*\(",
                r"Dense\s*\(",
            ],
            "imports": ["import tensorflow", "from tensorflow import"],
            "confidence_boost": 0.3
        },
        "pytorch": {
            "patterns": [
                r"torch\.tensor\s*\(",
                r"nn\.Module",
                r"nn\.Linear\s*\(",
                r"nn\.Conv2d\s*\(",
                r"\.forward\s*\(",
                r"\.backward\s*\(",
                r"torch\.optim\.",
                r"DataLoader\s*\(",
                r"\.cuda\s*\(",
                r"\.to\s*\(\s*device\s*\)",
            ],
            "imports": ["import torch", "from torch import"],
            "confidence_boost": 0.3
        },
        "sklearn": {
            "patterns": [
                r"\.fit\s*\(",
                r"\.predict\s*\(",
                r"\.transform\s*\(",
                r"\.fit_transform\s*\(",
                r"train_test_split\s*\(",
                r"cross_val_score\s*\(",
                r"GridSearchCV\s*\(",
                r"RandomForestClassifier\s*\(",
                r"LinearRegression\s*\(",
            ],
            "imports": ["from sklearn", "import sklearn"],
            "confidence_boost": 0.2
        }
    },
    "javascript": {
        "react": {
            "patterns": [
                r"React\.Component",
                r"React\.useState",
                r"React\.useEffect",
                r"React\.createContext",
                r"<[A-Z]\w+\s*\/?>",  # JSX components
                r"\.jsx\s*\(",
                r"render\s*\(\s*\)",
                r"componentDidMount",
                r"componentWillUnmount",
                r"props\.",
                r"this\.state",
            ],
            "imports": ["import React", "from 'react'", 'from "react"'],
            "confidence_boost": 0.3
        },
        "express": {
            "patterns": [
                r"app\.get\s*\(",
                r"app\.post\s*\(",
                r"app\.put\s*\(",
                r"app\.delete\s*\(",
                r"app\.use\s*\(",
                r"express\(\s*\)",
                r"\.listen\s*\(",
                r"req\.",
                r"res\.",
                r"next\s*\(\s*\)",
            ],
            "imports": ["require('express')", 'require("express")', "import express"],
            "confidence_boost": 0.2
        },
        "lodash": {
            "patterns": [
                r"_\.\w+\s*\(",
                r"lodash\.\w+\s*\(",
                r"\.debounce\s*\(",
                r"\.throttle\s*\(",
                r"\.cloneDeep\s*\(",
                r"\.merge\s*\(",
                r"\.get\s*\(",
                r"\.set\s*\(",
                r"\.map\s*\(",
                r"\.filter\s*\(",
            ],
            "imports": ["require('lodash')", "import _ from", "import lodash"],
            "confidence_boost": 0.1
        },
        "angular": {
            "patterns": [
                r"@Component\s*\(",
                r"@Injectable\s*\(",
                r"@NgModule\s*\(",
                r"@Input\s*\(",
                r"@Output\s*\(",
                r"EventEmitter\s*\(",
                r"ngOnInit\s*\(",
                r"ngOnDestroy\s*\(",
                r"\*ngFor\s*=",
                r"\*ngIf\s*=",
            ],
            "imports": ["from '@angular", "import { Component"],
            "confidence_boost": 0.3
        }
    },
    "typescript": {
        # TypeScript inherits JavaScript patterns
        "react": {
            "patterns": [
                r"React\.FC",
                r"React\.Component<",
                r"interface\s+\w+Props",
                r"type\s+\w+Props\s*=",
                r"useState<",
                r"useEffect\(",
                r":\s*JSX\.Element",
            ],
            "imports": ["import React", "from 'react'"],
            "confidence_boost": 0.3
        }
    },
    "c": {
        "openssl": {
            "patterns": [
                r"EVP_\w+\s*\(",
                r"SSL_\w+\s*\(",
                r"RSA_\w+\s*\(",
                r"AES_\w+\s*\(",
                r"SHA\d+_\w+\s*\(",
                r"HMAC_\w+\s*\(",
                r"X509_\w+\s*\(",
                r"BIO_\w+\s*\(",
                r"ENGINE_\w+\s*\(",
            ],
            "imports": ["#include <openssl/"],
            "confidence_boost": 0.3
        },
        "ffmpeg": {
            "patterns": [
                r"av_\w+\s*\(",
                r"avcodec_\w+\s*\(",
                r"avformat_\w+\s*\(",
                r"AVCodec\s*\*",
                r"AVFrame\s*\*",
                r"AVPacket\s+",
                r"sws_scale\s*\(",
                r"av_read_frame\s*\(",
            ],
            "imports": ["#include <libavcodec/", "#include <libavformat/"],
            "confidence_boost": 0.3
        }
    },
    "cpp": {
        "opencv": {
            "patterns": [
                r"cv::\w+\s*\(",
                r"cv::Mat\s+",
                r"cv::VideoCapture",
                r"cv::imread\s*\(",
                r"cv::imshow\s*\(",
                r"cv::waitKey\s*\(",
                r"cv::Canny\s*\(",
                r"cv::threshold\s*\(",
            ],
            "imports": ["#include <opencv2/", "using namespace cv"],
            "confidence_boost": 0.3
        },
        "boost": {
            "patterns": [
                r"boost::\w+",
                r"boost::shared_ptr",
                r"boost::unique_ptr",
                r"boost::thread",
                r"boost::filesystem",
                r"boost::regex",
                r"boost::asio",
            ],
            "imports": ["#include <boost/"],
            "confidence_boost": 0.2
        }
    }
}


# Enhanced Algorithm Patterns
ALGORITHM_PATTERNS = {
    "search_algorithm": {
        "dfs": {
            "patterns": [
                r"(def|function)\s+(dfs|depth_first_search)\s*\(",
                r"visited\s*(\[|\.add|\.append)",
                r"stack\s*\.\s*(append|push)\s*\(",
                r"stack\s*\.\s*pop\s*\(",
                r"for\s+neighbor\s+in\s+graph",
                r"recursion.*graph",
                r"if\s+neighbor\s+not\s+in\s+visited",
            ],
            "required_elements": ["visited", "neighbor"],
            "confidence": 0.8
        },
        "bfs": {
            "patterns": [
                r"def\s+bfs\s*\(",
                r"function\s+bfs\s*\(",
                r"queue\s*\.\s*append\s*\(",
                r"queue\s*\.\s*popleft\s*\(",
                r"deque\s*\(",
                r"while\s+queue",
                r"for\s+neighbor\s+in",
            ],
            "required_elements": ["queue", "visited"],
            "confidence": 0.8
        },
        "dijkstra": {
            "patterns": [
                r"dijkstra",
                r"distances?\s*(\[|=)",
                r"(heapq\s*\.\s*heappush|priority_queue|min\s*\(.*key\s*=)",
                r"(float\s*\(\s*['\"]inf|infinity)",
                r"shortest_path",
                r"min_distance",
                r"(unvisited|visited)\s*\.",
                r"distances?\[current\]\s*\+\s*weight",
            ],
            "required_elements": ["distance", "weight|infinity"],
            "confidence": 0.85
        },
        "a_star": {
            "patterns": [
                r"a_star|astar",
                r"heuristic\s*\(",
                r"f_score",
                r"g_score",
                r"h_score",
                r"came_from",
                r"open_set",
                r"closed_set",
            ],
            "required_elements": ["heuristic", "score"],
            "confidence": 0.9
        }
    },
    "sorting": {
        "bubble_sort": {
            "patterns": [
                r"bubble_sort",
                r"for.*range.*len\s*\(",
                r"for.*range.*n\s*-\s*i\s*-\s*1",
                r"if\s+\w+\[j\]\s*>\s*\w+\[j\s*\+\s*1\]",
                r"swap.*\[j\].*\[j\s*\+\s*1\]",
            ],
            "required_elements": ["nested_loop", "swap|exchange"],
            "confidence": 0.85
        },
        "merge_sort": {
            "patterns": [
                r"merge_sort",
                r"def\s+merge\s*\(",
                r"mid\s*=\s*len.*//\s*2",
                r"left\s*=.*\[:mid\]",
                r"right\s*=.*\[mid:\]",
                r"while.*left.*right",
            ],
            "required_elements": ["merge", "recursion|divide"],
            "confidence": 0.85
        },
        "quick_sort": {
            "patterns": [
                r"quick_sort",
                r"pivot",
                r"partition",
                r"left\s*=\s*\[.*for.*if.*<\s*pivot",
                r"right\s*=\s*\[.*for.*if.*>\s*pivot",
            ],
            "required_elements": ["pivot", "partition|recursion"],
            "confidence": 0.85
        },
        "heap_sort": {
            "patterns": [
                r"heap_sort",
                r"heapify",
                r"largest\s*=",
                r"left\s*=\s*2\s*\*\s*i",
                r"right\s*=\s*2\s*\*\s*i\s*\+\s*1",
                r"parent.*child",
            ],
            "required_elements": ["heapify", "swap"],
            "confidence": 0.85
        }
    },
    "media_processing": {
        "audio_codec": {
            "patterns": [
                r"audio.*codec",
                r"pcm_|PCM_",
                r"sample_rate",
                r"channels",
                r"bits_per_sample",
                r"encode_frame|decode_frame",
                r"audio_format",
                r"endian",
            ],
            "required_elements": ["sample|audio", "encode|decode"],
            "confidence": 0.8
        },
        "video_codec": {
            "patterns": [
                r"video.*codec",
                r"h264|h265|hevc|vp8|vp9",
                r"frame_rate|fps",
                r"width.*height",
                r"encode_frame|decode_frame",
                r"keyframe|i_frame",
                r"motion_vector",
            ],
            "required_elements": ["frame", "encode|decode"],
            "confidence": 0.8
        }
    }
}


def detect_oss_signatures(content: str, language: str) -> List[Dict[str, Any]]:
    """Detect OSS library usage patterns in code."""
    detected = []
    
    if language not in OSS_SIGNATURES:
        return detected
    
    for library, config in OSS_SIGNATURES[language].items():
        score = 0
        matches = []
        
        # Check imports
        for import_pattern in config.get("imports", []):
            if import_pattern in content:
                score += 0.3
                matches.append(f"import: {import_pattern}")
                break
        
        # Check patterns
        pattern_count = 0
        for pattern in config.get("patterns", []):
            import re
            if re.search(pattern, content, re.MULTILINE):
                pattern_count += 1
                matches.append(f"pattern: {pattern}")
        
        if pattern_count > 0:
            # Score based on number of patterns found
            pattern_score = min(pattern_count * 0.1, 0.7)
            score += pattern_score
        
        if score > 0.3:  # Threshold for detection
            detected.append({
                "library": library,
                "confidence": min(score + config.get("confidence_boost", 0), 1.0),
                "matches": matches[:5]  # Limit matches for brevity
            })
    
    return detected


def get_enhanced_patterns(language: str, algorithm_type: str) -> Dict[str, Any]:
    """Get enhanced algorithm patterns for specific language and type."""
    base_patterns = ALGORITHM_PATTERNS.get(algorithm_type, {})
    
    # Language-specific adjustments
    if language in ["c", "cpp"] and algorithm_type in base_patterns:
        # Adjust patterns for C/C++ syntax
        adjusted = {}
        for name, config in base_patterns.items():
            adjusted[name] = config.copy()
            # Add C/C++ specific patterns
            if "patterns" in adjusted[name]:
                c_patterns = []
                for pattern in adjusted[name]["patterns"]:
                    # Convert Python patterns to C/C++
                    c_pattern = pattern.replace(r"def\s+", r"(void|int|bool)\s+")
                    c_pattern = c_pattern.replace(r"for.*in", r"for\s*\(")
                    c_patterns.append(c_pattern)
                adjusted[name]["patterns"].extend(c_patterns)
        return adjusted
    
    return base_patterns 