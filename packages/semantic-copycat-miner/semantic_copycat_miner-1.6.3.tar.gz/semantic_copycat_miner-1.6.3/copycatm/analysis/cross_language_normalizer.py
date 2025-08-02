"""
Enhanced cross-language normalization for unified code representation.

This module provides comprehensive normalization rules to convert language-specific
idioms, frameworks, and library calls into a unified representation.
"""

import re
import logging
from typing import Dict, List, Any
from enum import Enum

logger = logging.getLogger(__name__)


class NormalizationType(Enum):
    """Types of normalizations."""
    IDIOM = "idiom"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    TYPE_SYSTEM = "type_system"
    CONTROL_FLOW = "control_flow"
    DATA_STRUCTURE = "data_structure"


class CrossLanguageNormalizer:
    """
    Comprehensive cross-language normalization for better code comparison.
    
    Normalizes:
    - Language idioms (list comprehensions, lambda functions)
    - Framework patterns (React hooks, Django views)
    - Library calls (HTTP, file I/O, database)
    - Type systems (static vs dynamic)
    - Control flow patterns
    - Data structure operations
    """
    
    def __init__(self):
        """Initialize normalizer with comprehensive rules."""
        self.idiom_rules = self._initialize_idiom_rules()
        self.framework_rules = self._initialize_framework_rules()
        self.library_rules = self._initialize_library_rules()
        self.type_rules = self._initialize_type_rules()
        self.control_flow_rules = self._initialize_control_flow_rules()
        self.data_structure_rules = self._initialize_data_structure_rules()
    
    def _initialize_idiom_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize language-specific idiom normalization rules."""
        return {
            'python': {
                'list_comprehension': {
                    'pattern': r'\[\s*(.+?)\s+for\s+(\w+)\s+in\s+(.+?)\s*(?:if\s+(.+?))?\s*\]',
                    'normalize': 'LOOP(ITERATE($3, $2), TRANSFORM($1)' + ', CONDITION($4))' if '$4' else ')'
                },
                'dict_comprehension': {
                    'pattern': r'\{\s*(.+?):\s*(.+?)\s+for\s+(\w+)\s+in\s+(.+?)\s*\}',
                    'normalize': 'LOOP(ITERATE($4, $3), MAP($1, $2))'
                },
                'lambda': {
                    'pattern': r'lambda\s+(.+?):\s*(.+)',
                    'normalize': 'FUNCTION(ANONYMOUS, [$1], $2)'
                },
                'with_statement': {
                    'pattern': r'with\s+(.+?)\s+as\s+(\w+):',
                    'normalize': 'CONTEXT_MANAGER($1, $2)'
                },
                'decorator': {
                    'pattern': r'@(\w+)(?:\(([^)]*)\))?',
                    'normalize': 'DECORATOR($1, $2)'
                },
                'f_string': {
                    'pattern': r'f["\'](.+?)["\']',
                    'normalize': 'STRING_INTERPOLATION($1)'
                },
                'walrus_operator': {
                    'pattern': r'(\w+)\s*:=\s*(.+)',
                    'normalize': 'ASSIGN_AND_RETURN($1, $2)'
                }
            },
            'javascript': {
                'arrow_function': {
                    'pattern': r'(?:const|let|var)?\s*(\w+)?\s*=?\s*\(([^)]*)\)\s*=>\s*(.+)',
                    'normalize': 'FUNCTION($1, [$2], $3)'
                },
                'template_literal': {
                    'pattern': r'`([^`]+)`',
                    'normalize': 'STRING_INTERPOLATION($1)'
                },
                'destructuring': {
                    'pattern': r'(?:const|let|var)\s*\{([^}]+)\}\s*=\s*(.+)',
                    'normalize': 'DESTRUCTURE_ASSIGN($1, $2)'
                },
                'spread_operator': {
                    'pattern': r'\.\.\.(\w+)',
                    'normalize': 'SPREAD($1)'
                },
                'optional_chaining': {
                    'pattern': r'(\w+)\?\.(\w+)',
                    'normalize': 'SAFE_ACCESS($1, $2)'
                },
                'nullish_coalescing': {
                    'pattern': r'(.+?)\s*\?\?\s*(.+)',
                    'normalize': 'COALESCE($1, $2)'
                }
            },
            'java': {
                'stream_api': {
                    'pattern': r'(\w+)\.stream\(\)(.+?)\.collect\((.+?)\)',
                    'normalize': 'STREAM_PROCESS($1, $2, $3)'
                },
                'optional': {
                    'pattern': r'Optional\.(?:of|ofNullable)\((.+?)\)',
                    'normalize': 'OPTIONAL($1)'
                },
                'lambda': {
                    'pattern': r'\(([^)]*)\)\s*->\s*(.+)',
                    'normalize': 'FUNCTION(ANONYMOUS, [$1], $2)'
                },
                'method_reference': {
                    'pattern': r'(\w+)::(\w+)',
                    'normalize': 'METHOD_REF($1, $2)'
                }
            },
            'cpp': {
                'auto': {
                    'pattern': r'auto\s+(\w+)\s*=\s*(.+);',
                    'normalize': 'INFERRED_TYPE_ASSIGN($1, $2)'
                },
                'range_for': {
                    'pattern': r'for\s*\(\s*(?:auto|[\w:]+)\s+(\w+)\s*:\s*(.+?)\s*\)',
                    'normalize': 'FOREACH($2, $1)'
                },
                'lambda': {
                    'pattern': r'\[([^\]]*)\]\s*\(([^)]*)\)\s*(?:->\s*(\w+))?\s*\{',
                    'normalize': 'FUNCTION(LAMBDA, [$2], CAPTURE($1))'
                },
                'smart_pointer': {
                    'pattern': r'(?:std::)?(?:unique_ptr|shared_ptr|weak_ptr)<(.+?)>',
                    'normalize': 'SMART_POINTER($1)'
                }
            },
            'go': {
                'goroutine': {
                    'pattern': r'go\s+(\w+)\s*\(',
                    'normalize': 'ASYNC_EXECUTE($1)'
                },
                'channel': {
                    'pattern': r'(\w+)\s*<-\s*(.+)',
                    'normalize': 'CHANNEL_SEND($1, $2)'
                },
                'defer': {
                    'pattern': r'defer\s+(.+)',
                    'normalize': 'DEFER($1)'
                },
                'short_declaration': {
                    'pattern': r'(\w+)\s*:=\s*(.+)',
                    'normalize': 'INFERRED_TYPE_ASSIGN($1, $2)'
                }
            },
            'rust': {
                'match_expression': {
                    'pattern': r'match\s+(.+?)\s*\{',
                    'normalize': 'PATTERN_MATCH($1)'
                },
                'option': {
                    'pattern': r'(?:Some|None)\(([^)]*)\)',
                    'normalize': 'OPTIONAL($1)'
                },
                'result': {
                    'pattern': r'(?:Ok|Err)\(([^)]*)\)',
                    'normalize': 'RESULT($1)'
                },
                'closure': {
                    'pattern': r'\|([^|]*)\|\s*(.+)',
                    'normalize': 'FUNCTION(CLOSURE, [$1], $2)'
                }
            }
        }
    
    def _initialize_framework_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize framework-specific pattern normalization rules."""
        return {
            'react': {
                'useState': {
                    'pattern': r'(?:const\s*)?\[(\w+),\s*(\w+)\]\s*=\s*useState\(([^)]*)\)',
                    'normalize': 'STATE_HOOK($1, $2, $3)'
                },
                'useEffect': {
                    'pattern': r'useEffect\(\s*\(\)\s*=>\s*\{([^}]+)\},\s*\[([^\]]*)\]\)',
                    'normalize': 'EFFECT_HOOK($1, DEPS($2))'
                },
                'useContext': {
                    'pattern': r'(?:const\s*)?(\w+)\s*=\s*useContext\((\w+)\)',
                    'normalize': 'CONTEXT_HOOK($1, $2)'
                },
                'component': {
                    'pattern': r'(?:function|const)\s+(\w+)\s*(?:=\s*)?(?:\([^)]*\))?\s*(?:=>)?\s*\{?\s*return\s*\(',
                    'normalize': 'REACT_COMPONENT($1)'
                }
            },
            'django': {
                'view': {
                    'pattern': r'def\s+(\w+)\(request(?:,\s*[^)]+)?\):',
                    'normalize': 'WEB_VIEW($1)'
                },
                'model': {
                    'pattern': r'class\s+(\w+)\((?:models\.)?Model\):',
                    'normalize': 'DB_MODEL($1)'
                },
                'form': {
                    'pattern': r'class\s+(\w+)\((?:forms\.)?Form\):',
                    'normalize': 'WEB_FORM($1)'
                },
                'queryset': {
                    'pattern': r'(\w+)\.objects\.(?:all|filter|get)\(',
                    'normalize': 'DB_QUERY($1)'
                }
            },
            'express': {
                'route': {
                    'pattern': r'app\.(?:get|post|put|delete)\(["\'](.+?)["\']\s*,',
                    'normalize': 'HTTP_ROUTE($1)'
                },
                'middleware': {
                    'pattern': r'app\.use\((.+?)\)',
                    'normalize': 'MIDDLEWARE($1)'
                },
                'handler': {
                    'pattern': r'\(req,\s*res(?:,\s*next)?\)\s*=>\s*\{',
                    'normalize': 'REQUEST_HANDLER()'
                }
            },
            'spring': {
                'controller': {
                    'pattern': r'@(?:Rest)?Controller',
                    'normalize': 'WEB_CONTROLLER'
                },
                'mapping': {
                    'pattern': r'@(?:Get|Post|Put|Delete|Request)Mapping\(["\'](.+?)["\']\)',
                    'normalize': 'HTTP_ROUTE($1)'
                },
                'autowired': {
                    'pattern': r'@Autowired',
                    'normalize': 'DEPENDENCY_INJECT'
                },
                'service': {
                    'pattern': r'@Service',
                    'normalize': 'SERVICE_COMPONENT'
                }
            }
        }
    
    def _initialize_library_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize library call normalization rules."""
        return {
            'http': {
                'requests_get': {
                    'pattern': r'requests\.get\((.+?)\)',
                    'normalize': 'HTTP_GET($1)'
                },
                'axios_get': {
                    'pattern': r'axios\.get\((.+?)\)',
                    'normalize': 'HTTP_GET($1)'
                },
                'fetch': {
                    'pattern': r'fetch\((.+?)\)',
                    'normalize': 'HTTP_REQUEST($1)'
                },
                'urllib': {
                    'pattern': r'urllib\.request\.urlopen\((.+?)\)',
                    'normalize': 'HTTP_REQUEST($1)'
                },
                'http_client': {
                    'pattern': r'http\.Get\((.+?)\)',
                    'normalize': 'HTTP_GET($1)'
                }
            },
            'database': {
                'sql_query': {
                    'pattern': r'(?:execute|query)\(["\']SELECT\s+(.+?)["\']',
                    'normalize': 'DB_SELECT($1)'
                },
                'orm_query': {
                    'pattern': r'(\w+)\.find(?:One|All|By\w+)?\(',
                    'normalize': 'DB_FIND($1)'
                },
                'mongo_query': {
                    'pattern': r'(\w+)\.(?:find|findOne|aggregate)\(',
                    'normalize': 'DB_QUERY($1)'
                }
            },
            'file_io': {
                'open_file': {
                    'pattern': r'open\(["\'](.+?)["\']\s*,\s*["\'](\w)["\']',
                    'normalize': 'FILE_OPEN($1, $2)'
                },
                'fs_read': {
                    'pattern': r'fs\.(?:readFile|readFileSync)\(["\'](.+?)["\']\)',
                    'normalize': 'FILE_READ($1)'
                },
                'path_join': {
                    'pattern': r'(?:path\.join|os\.path\.join)\((.+?)\)',
                    'normalize': 'PATH_JOIN($1)'
                }
            },
            'json': {
                'parse': {
                    'pattern': r'(?:JSON\.parse|json\.loads)\((.+?)\)',
                    'normalize': 'JSON_PARSE($1)'
                },
                'stringify': {
                    'pattern': r'(?:JSON\.stringify|json\.dumps)\((.+?)\)',
                    'normalize': 'JSON_STRINGIFY($1)'
                }
            },
            'logging': {
                'console_log': {
                    'pattern': r'console\.log\((.+?)\)',
                    'normalize': 'LOG($1)'
                },
                'print': {
                    'pattern': r'print\((.+?)\)',
                    'normalize': 'LOG($1)'
                },
                'logger': {
                    'pattern': r'(?:logger|log)\.(?:info|debug|error|warn)\((.+?)\)',
                    'normalize': 'LOG($1)'
                }
            }
        }
    
    def _initialize_type_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize type system normalization rules."""
        return {
            'type_annotations': {
                'python': {
                    'pattern': r'(\w+)\s*:\s*([\w\[\]]+)\s*=',
                    'normalize': 'TYPED_VAR($1, $2)'
                },
                'typescript': {
                    'pattern': r'(?:let|const|var)\s+(\w+)\s*:\s*([\w<>]+)',
                    'normalize': 'TYPED_VAR($1, $2)'
                },
                'java': {
                    'pattern': r'([\w<>]+)\s+(\w+)\s*=',
                    'normalize': 'TYPED_VAR($2, $1)'
                },
                'cpp': {
                    'pattern': r'([\w:]+)\s+(\w+)\s*=',
                    'normalize': 'TYPED_VAR($2, $1)'
                }
            },
            'generics': {
                'pattern': r'(\w+)<(.+?)>',
                'normalize': 'GENERIC_TYPE($1, $2)'
            },
            'nullable': {
                'pattern': r'(\w+)\s*\?\s*',
                'normalize': 'NULLABLE($1)'
            }
        }
    
    def _initialize_control_flow_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize control flow normalization rules."""
        return {
            'error_handling': {
                'try_catch': {
                    'pattern': r'try\s*\{([^}]+)\}\s*catch\s*(?:\((\w+)\))?\s*\{([^}]+)\}',
                    'normalize': 'TRY_CATCH(TRY($1), CATCH($2, $3))'
                },
                'try_except': {
                    'pattern': r'try:\s*(.+?)\s*except\s*(\w+)?(?:\s+as\s+(\w+))?:',
                    'normalize': 'TRY_CATCH(TRY($1), CATCH($2, $3))'
                },
                'error_check': {
                    'pattern': r'if\s+err\s*!=\s*nil\s*\{',
                    'normalize': 'ERROR_CHECK()'
                }
            },
            'async': {
                'async_await': {
                    'pattern': r'(?:async\s+)?(?:function\s+)?(\w+)?\s*\([^)]*\)\s*\{[^}]*await\s+',
                    'normalize': 'ASYNC_FUNCTION($1)'
                },
                'promise': {
                    'pattern': r'\.then\((.+?)\)\.catch\((.+?)\)',
                    'normalize': 'PROMISE_CHAIN(THEN($1), CATCH($2))'
                },
                'callback': {
                    'pattern': r'\((?:err|error),\s*(\w+)\)\s*=>\s*\{',
                    'normalize': 'CALLBACK_PATTERN($1)'
                }
            }
        }
    
    def _initialize_data_structure_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data structure operation normalization rules."""
        return {
            'array_operations': {
                'map': {
                    'pattern': r'(\w+)\.map\((.+?)\)',
                    'normalize': 'ARRAY_MAP($1, $2)'
                },
                'filter': {
                    'pattern': r'(\w+)\.filter\((.+?)\)',
                    'normalize': 'ARRAY_FILTER($1, $2)'
                },
                'reduce': {
                    'pattern': r'(\w+)\.reduce\((.+?)\)',
                    'normalize': 'ARRAY_REDUCE($1, $2)'
                },
                'slice': {
                    'pattern': r'(\w+)\[(\d+)?:(\d+)?\]',
                    'normalize': 'ARRAY_SLICE($1, $2, $3)'
                }
            },
            'dict_operations': {
                'get': {
                    'pattern': r'(\w+)\.get\(["\'](\w+)["\']\)',
                    'normalize': 'DICT_GET($1, $2)'
                },
                'keys': {
                    'pattern': r'(?:Object\.keys|\.keys)\((\w+)\)',
                    'normalize': 'DICT_KEYS($1)'
                },
                'values': {
                    'pattern': r'(?:Object\.values|\.values)\((\w+)\)',
                    'normalize': 'DICT_VALUES($1)'
                }
            }
        }
    
    def normalize_code(self, code: str, language: str) -> str:
        """
        Apply all normalization rules to code.
        
        Args:
            code: Source code to normalize
            language: Programming language
            
        Returns:
            Normalized code representation
        """
        normalized = code
        
        # Apply idiom rules
        if language in self.idiom_rules:
            for rule_name, rule in self.idiom_rules[language].items():
                pattern = rule['pattern']
                replacement = rule['normalize']
                normalized = self._apply_rule(normalized, pattern, replacement)
        
        # Apply framework rules (language-agnostic)
        for framework, rules in self.framework_rules.items():
            for rule_name, rule in rules.items():
                pattern = rule['pattern']
                replacement = rule['normalize']
                normalized = self._apply_rule(normalized, pattern, replacement)
        
        # Apply library rules
        for category, rules in self.library_rules.items():
            for rule_name, rule in rules.items():
                pattern = rule['pattern']
                replacement = rule['normalize']
                normalized = self._apply_rule(normalized, pattern, replacement)
        
        # Apply type rules
        if language in self.type_rules['type_annotations']:
            rule = self.type_rules['type_annotations'][language]
            normalized = self._apply_rule(normalized, rule['pattern'], rule['normalize'])
        
        # Apply generic type rules
        normalized = self._apply_rule(
            normalized, 
            self.type_rules['generics']['pattern'],
            self.type_rules['generics']['normalize']
        )
        
        # Apply control flow rules
        for category, rules in self.control_flow_rules.items():
            for rule_name, rule in rules.items():
                pattern = rule['pattern']
                replacement = rule['normalize']
                normalized = self._apply_rule(normalized, pattern, replacement)
        
        # Apply data structure rules
        for category, rules in self.data_structure_rules.items():
            for rule_name, rule in rules.items():
                pattern = rule['pattern']
                replacement = rule['normalize']
                normalized = self._apply_rule(normalized, pattern, replacement)
        
        return normalized
    
    def _apply_rule(self, code: str, pattern: str, replacement: str) -> str:
        """Apply a single normalization rule."""
        try:
            # Handle replacement with captured groups
            def replace_func(match):
                result = replacement
                for i, group in enumerate(match.groups(), 1):
                    result = result.replace(f'${i}', group or '')
                return result
            
            return re.sub(pattern, replace_func, code, flags=re.MULTILINE | re.DOTALL)
        except Exception as e:
            logger.debug(f"Failed to apply rule {pattern}: {e}")
            return code
    
    def extract_normalized_patterns(self, code: str, language: str) -> List[Dict[str, Any]]:
        """
        Extract normalized patterns with their types and locations.
        
        Returns list of patterns with type, normalized form, and original text.
        """
        patterns = []
        
        # Check each rule category
        rule_categories = [
            (NormalizationType.IDIOM, self.idiom_rules.get(language, {})),
            (NormalizationType.FRAMEWORK, self._flatten_framework_rules()),
            (NormalizationType.LIBRARY, self._flatten_library_rules()),
            (NormalizationType.TYPE_SYSTEM, self._flatten_type_rules(language)),
            (NormalizationType.CONTROL_FLOW, self._flatten_control_flow_rules()),
            (NormalizationType.DATA_STRUCTURE, self._flatten_data_structure_rules())
        ]
        
        for norm_type, rules in rule_categories:
            for rule_name, rule in rules.items():
                matches = list(re.finditer(rule['pattern'], code, re.MULTILINE | re.DOTALL))
                for match in matches:
                    patterns.append({
                        'type': norm_type.value,
                        'rule': rule_name,
                        'original': match.group(0),
                        'normalized': self._apply_rule(match.group(0), rule['pattern'], rule['normalize']),
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return patterns
    
    def _flatten_framework_rules(self) -> Dict[str, Any]:
        """Flatten framework rules for easier iteration."""
        flattened = {}
        for framework, rules in self.framework_rules.items():
            for rule_name, rule in rules.items():
                flattened[f"{framework}_{rule_name}"] = rule
        return flattened
    
    def _flatten_library_rules(self) -> Dict[str, Any]:
        """Flatten library rules for easier iteration."""
        flattened = {}
        for category, rules in self.library_rules.items():
            for rule_name, rule in rules.items():
                flattened[f"{category}_{rule_name}"] = rule
        return flattened
    
    def _flatten_type_rules(self, language: str) -> Dict[str, Any]:
        """Flatten type rules for specific language."""
        flattened = {}
        if language in self.type_rules['type_annotations']:
            flattened['type_annotation'] = self.type_rules['type_annotations'][language]
        flattened['generics'] = self.type_rules['generics']
        flattened['nullable'] = self.type_rules['nullable']
        return flattened
    
    def _flatten_control_flow_rules(self) -> Dict[str, Any]:
        """Flatten control flow rules."""
        flattened = {}
        for category, rules in self.control_flow_rules.items():
            for rule_name, rule in rules.items():
                flattened[f"{category}_{rule_name}"] = rule
        return flattened
    
    def _flatten_data_structure_rules(self) -> Dict[str, Any]:
        """Flatten data structure rules."""
        flattened = {}
        for category, rules in self.data_structure_rules.items():
            for rule_name, rule in rules.items():
                flattened[f"{category}_{rule_name}"] = rule
        return flattened
    
    def normalize_algorithm_signature(self, code: str, language: str, algorithm_type: str) -> str:
        """
        Specialized normalization for algorithm signatures.
        
        This creates a canonical representation of algorithms that's consistent
        across languages and coding styles.
        """
        # First apply general normalization
        normalized = self.normalize_code(code, language)
        
        # Apply algorithm-specific normalization patterns
        algorithm_patterns = self._get_algorithm_normalization_patterns(algorithm_type)
        
        for pattern, replacement in algorithm_patterns.items():
            normalized = self._apply_rule(normalized, pattern, replacement)
        
        # Apply cross-language algorithmic normalization
        normalized = self._apply_algorithmic_normalization(normalized, language, algorithm_type)
        
        return normalized
    
    def _get_algorithm_normalization_patterns(self, algorithm_type: str) -> Dict[str, str]:
        """Get normalization patterns specific to algorithm types."""
        patterns = {
            'sorting_algorithm': {
                # Normalize common sorting patterns
                r'for\s+\w+\s+in\s+range\(len\((\w+)\)\)': 'FOR_ARRAY_LENGTH($1)',
                r'while\s+\w+\s*<\s*len\((\w+)\)': 'WHILE_ARRAY_BOUNDS($1)',
                r'(\w+)\[(\w+)\]\s*>\s*\1\[(\w+)\]': 'COMPARE_ELEMENTS($1, $2, $3)',
                r'(\w+)\[(\w+)\],\s*\1\[(\w+)\]\s*=\s*\1\[(\w+)\],\s*\1\[(\w+)\]': 'SWAP_ELEMENTS($1, $2, $3)',
            },
            'search_algorithm': {
                # Normalize search patterns
                r'if\s+(\w+)\[(\w+)\]\s*==\s*(\w+)': 'IF_FOUND($1, $2, $3)',
                r'(\w+)\s*=\s*\((\w+)\s*\+\s*(\w+)\)\s*//?\s*2': 'CALCULATE_MID($1, $2, $3)',
                r'return\s+(\w+)': 'RETURN_INDEX($1)',
                r'return\s+-1': 'RETURN_NOT_FOUND',
            },
            'graph_algorithm': {
                # Normalize graph traversal patterns
                r'visited\[(\w+)\]\s*=\s*True': 'MARK_VISITED($1)',
                r'(\w+)\.append\((\w+)\)': 'ADD_TO_COLLECTION($1, $2)',
                r'(\w+)\.popleft\(\)': 'DEQUEUE($1)',
                r'(\w+)\.pop\(\)': 'POP_STACK($1)',
            },
            'dynamic_programming': {
                # Normalize DP patterns
                r'dp\[(\w+)\]\[(\w+)\]': 'DP_TABLE($1, $2)',
                r'memo\[(\w+)\]': 'MEMOIZE($1)',
                r'if\s+(\w+)\s+in\s+memo': 'IF_MEMOIZED($1)',
            }
        }
        
        return patterns.get(algorithm_type, {})
    
    def _apply_algorithmic_normalization(self, code: str, language: str, algorithm_type: str) -> str:
        """Apply algorithm-specific cross-language normalization."""
        normalized = code
        
        # Language-specific algorithmic patterns
        if language == 'python':
            # Python list comprehensions to loops
            if 'sorting' in algorithm_type:
                normalized = re.sub(
                    r'\[([^]]+)\s+for\s+(\w+)\s+in\s+(\w+)\s+if\s+([^]]+)\]',
                    r'FILTERED_TRANSFORM($3, $2, $1, $4)',
                    normalized
                )
            
            # Python enumerate to indexed loop
            normalized = re.sub(
                r'for\s+(\w+),\s*(\w+)\s+in\s+enumerate\(([^)]+)\)',
                r'FOR_INDEXED($1, $2, $3)',
                normalized
            )
            
        elif language == 'javascript':
            # JavaScript array methods to standard loops
            if 'sorting' in algorithm_type:
                normalized = re.sub(
                    r'(\w+)\.forEach\(([^)]+)\)',
                    r'FOR_EACH($1, $2)',
                    normalized
                )
            
            # JavaScript arrow functions to standard functions
            normalized = re.sub(
                r'\(([^)]*)\)\s*=>\s*\{([^}]+)\}',
                r'FUNCTION([$1], $2)',
                normalized
            )
            
        elif language in ['c', 'cpp']:
            # C-style for loops to standard form
            normalized = re.sub(
                r'for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<\s*(\w+)\s*;\s*\1\+\+\s*\)',
                r'FOR_RANGE($1, $2, $3)',
                normalized
            )
            
            # Pointer arithmetic to array access
            normalized = re.sub(
                r'\*\((\w+)\s*\+\s*(\w+)\)',
                r'ARRAY_ACCESS($1, $2)',
                normalized
            )
        
        return normalized
    
    def extract_algorithmic_features(self, code: str, language: str) -> Dict[str, Any]:
        """
        Extract language-agnostic algorithmic features for better cross-language matching.
        
        Returns features that should be consistent across language implementations
        of the same algorithm.
        """
        features = {
            'control_structures': [],
            'data_operations': [],
            'algorithmic_patterns': [],
            'complexity_indicators': [],
            'mathematical_operations': []
        }
        
        # Extract control structures (loops, conditions, recursion)
        control_patterns = [
            (r'(?:for|while)\s*\([^)]*\)', 'LOOP'),
            (r'if\s*\([^)]*\)', 'CONDITIONAL'),
            (r'(?:return\s+)?(\w+)\([^)]*\)', 'FUNCTION_CALL'),
            (r'recursion|recursive', 'RECURSIVE'),
        ]
        
        for pattern, structure_type in control_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                features['control_structures'].append({
                    'type': structure_type,
                    'pattern': match if isinstance(match, str) else match[0] if match else ''
                })
        
        # Extract data operations
        data_patterns = [
            (r'(?:swap|exchange)', 'SWAP'),
            (r'(?:compare|comparison)', 'COMPARE'),
            (r'(?:sort|sorted|sorting)', 'SORT'),
            (r'(?:search|find|locate)', 'SEARCH'),
            (r'(?:append|add|insert)', 'INSERT'),
            (r'(?:remove|delete|pop)', 'REMOVE'),
        ]
        
        for pattern, operation_type in data_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                features['data_operations'].append(operation_type)
        
        # Extract algorithmic patterns
        algo_patterns = [
            (r'divide.*conquer|partition', 'DIVIDE_AND_CONQUER'),
            (r'dynamic.*programming|memoization', 'DYNAMIC_PROGRAMMING'),
            (r'greedy|optimal.*substructure', 'GREEDY'),
            (r'backtrack|recursive.*search', 'BACKTRACKING'),
            (r'breadth.*first|queue', 'BFS'),
            (r'depth.*first|stack', 'DFS'),
        ]
        
        for pattern, algo_type in algo_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                features['algorithmic_patterns'].append(algo_type)
        
        # Extract complexity indicators
        complexity_patterns = [
            (r'nested.*loop|loop.*loop', 'NESTED_LOOPS'),
            (r'recursive.*call', 'RECURSIVE_CALLS'),
            (r'exponential|factorial', 'EXPONENTIAL_GROWTH'),
            (r'logarithmic|binary.*search', 'LOGARITHMIC'),
        ]
        
        for pattern, complexity_type in complexity_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                features['complexity_indicators'].append(complexity_type)
        
        # Extract mathematical operations
        math_patterns = [
            (r'[\+\-\*/]\s*=|[\+\-\*/]{2}', 'ARITHMETIC'),
            (r'%|mod|modulo', 'MODULAR'),
            (r'pow|power|\*\*|\^', 'EXPONENTIATION'),
            (r'sqrt|square.*root', 'SQUARE_ROOT'),
            (r'abs|absolute', 'ABSOLUTE_VALUE'),
        ]
        
        for pattern, math_type in math_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                features['mathematical_operations'].append(math_type)
        
        return features
    
    def calculate_cross_language_similarity(self, code1: str, lang1: str, 
                                          code2: str, lang2: str) -> float:
        """
        Calculate similarity between code snippets in different languages.
        
        Returns a similarity score from 0.0 to 1.0 based on normalized representations.
        """
        # Normalize both code snippets
        norm1 = self.normalize_code(code1, lang1)
        norm2 = self.normalize_code(code2, lang2)
        
        # Extract algorithmic features
        features1 = self.extract_algorithmic_features(code1, lang1)
        features2 = self.extract_algorithmic_features(code2, lang2)
        
        # Calculate feature similarity
        feature_similarity = self._calculate_feature_similarity(features1, features2)
        
        # Calculate normalized text similarity (simple Jaccard for now)
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        text_similarity = len(words1 & words2) / len(words1 | words2) if (words1 | words2) else 0.0
        
        # Combine similarities with weights
        overall_similarity = (
            feature_similarity * 0.7 +  # Features are more important
            text_similarity * 0.3       # Text similarity as backup
        )
        
        return overall_similarity
    
    def _calculate_feature_similarity(self, features1: Dict[str, Any], 
                                    features2: Dict[str, Any]) -> float:
        """Calculate similarity between algorithmic features."""
        similarities = []
        
        for feature_type in features1.keys():
            list1 = features1.get(feature_type, [])
            list2 = features2.get(feature_type, [])
            
            if not list1 and not list2:
                similarities.append(1.0)  # Both empty
            elif not list1 or not list2:
                similarities.append(0.0)  # One empty
            else:
                # Calculate Jaccard similarity for this feature type
                set1 = set(item['type'] if isinstance(item, dict) else item for item in list1)
                set2 = set(item['type'] if isinstance(item, dict) else item for item in list2)
                jaccard = len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0.0
                similarities.append(jaccard)
        
        return sum(similarities) / len(similarities) if similarities else 0.0