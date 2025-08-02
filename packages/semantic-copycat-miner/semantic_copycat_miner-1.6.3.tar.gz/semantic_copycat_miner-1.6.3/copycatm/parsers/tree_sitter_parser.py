"""
Tree-sitter parser implementation for CopycatM.
"""

import tree_sitter
import logging
from typing import Any, Dict, List
from .base import BaseParser

logger = logging.getLogger(__name__)

try:
    from tree_sitter_languages import get_language
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    get_language = None

# Try direct imports as fallback
DIRECT_IMPORTS = {}
try:
    import tree_sitter_javascript as tsjs
    DIRECT_IMPORTS['javascript'] = tsjs
except ImportError:
    pass

try:
    import tree_sitter_python as tspy
    DIRECT_IMPORTS['python'] = tspy
except ImportError:
    pass

try:
    import tree_sitter_c as tsc
    DIRECT_IMPORTS['c'] = tsc
except ImportError:
    pass

try:
    import tree_sitter_java as tsjava
    DIRECT_IMPORTS['java'] = tsjava
except ImportError:
    pass


class TreeSitterParser(BaseParser):
    """Tree-sitter based parser for multiple languages."""
    
    def __init__(self):
        self.parsers: Dict[str, tree_sitter.Parser] = {}
        self.languages: Dict[str, tree_sitter.Language] = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize tree-sitter parsers for supported languages."""
        language_map = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'typescript',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'go': 'go',
            'rust': 'rust'
        }
        
        # Try direct imports first
        for lang_name, module in DIRECT_IMPORTS.items():
            try:
                # Create language object from direct import
                # Get the language capsule
                language_capsule = module.language()
                
                # Convert PyCapsule to Language object
                language = tree_sitter.Language(language_capsule)
                    
                # Create parser with new API for tree-sitter 0.23+
                parser = tree_sitter.Parser()
                parser.language = language
                
                self.languages[lang_name] = language
                self.parsers[lang_name] = parser
                logger.debug(f"Initialized {lang_name} parser via direct import")
                
            except Exception as e:
                import traceback
                logger.debug(f"Failed to initialize {lang_name} via direct import: {e}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Try tree-sitter-languages if available
        if TREE_SITTER_AVAILABLE and get_language:
            for lang_name, ts_name in language_map.items():
                if lang_name in self.parsers:
                    continue  # Already loaded via direct import
                    
                try:
                    # Try to get the language
                    language_obj = get_language(ts_name)
                    
                    # Create Language object if needed
                    if hasattr(language_obj, '__class__') and 'PyCapsule' in str(type(language_obj)):
                        language = tree_sitter.Language(language_obj)
                    else:
                        language = language_obj
                    
                    # Create parser with new API for tree-sitter 0.23+
                    parser = tree_sitter.Parser()
                    parser.language = language
                    
                    self.languages[lang_name] = language
                    self.parsers[lang_name] = parser
                    
                except Exception as e:
                    # Log the error for debugging
                    logger.debug(f"Failed to initialize {lang_name}: {e}")
                    # Skip this language but continue with others
                    continue
    
    def parse(self, code: str, language: str) -> Any:
        """Parse code and return AST tree."""
        if not self.supports_language(language):
            raise ValueError(f"Language {language} not supported")
        
        # Try tree-sitter parsing if available
        if language in self.parsers:
            try:
                parser = self.parsers[language]
                tree = parser.parse(code.encode())
                
                class TreeSitterAST:
                    def __init__(self, tree, code: str, language: str):
                        self.tree = tree
                        self.code = code
                        self.language = language
                        self.root = tree.root_node
                    
                    def __str__(self):
                        return f"TreeSitterAST({self.language})"
                
                return TreeSitterAST(tree, code, language)
            except Exception as e:
                # Log the error for debugging
                logger.debug(f"Tree-sitter parse failed for {language}: {e}")
                # Fall through to text-based parsing
        
        # Fallback to text-based analysis
        return self._create_fallback_ast(code, language)
    
    def _create_fallback_ast(self, code: str, language: str) -> Any:
        """Create a fallback AST for text-based analysis."""
        class FallbackAST:
            def __init__(self, code: str, language: str):
                self.code = code
                self.language = language
                self.root = self._create_text_nodes(code)
            
            def __str__(self):
                return f"FallbackAST({self.language})"
            
            def _create_text_nodes(self, code: str):
                """Create simple nodes based on text analysis."""
                import re
                
                class FallbackNode:
                    def __init__(self, node_type: str, text: str = "", start_byte: int = 0, end_byte: int = 0):
                        self.type = node_type
                        self.text = text
                        self.start_byte = start_byte
                        self.end_byte = end_byte
                        self.start_point = (0, start_byte)
                        self.end_point = (0, end_byte)
                        self.children = []
                    
                    @property
                    def child_count(self):
                        return len(self.children)
                    
                    def child(self, index):
                        """Get child at index (tree-sitter compatibility)."""
                        if 0 <= index < len(self.children):
                            return self.children[index]
                        return None
                    
                    def child_by_field_name(self, field_name):
                        """Stub for tree-sitter compatibility."""
                        return None
                
                root = FallbackNode("module", code, 0, len(code))
                
                # Find function definitions with better parsing - language specific
                if self.language == 'python':
                    func_pattern = r'\b(?:def|function|func)\s+(\w+)[^:]*:'
                elif self.language in ['c', 'cpp', 'java']:
                    # Match C/C++/Java function definitions - more precise
                    # Include compound types like 'long long', 'unsigned int', etc.
                    func_pattern = r'^\s*(?:static\s+|inline\s+|extern\s+)?(?:void|int|char|float|double|long\s+long|unsigned\s+\w+|signed\s+\w+|short|long|bool|\w+\s*\*?)\s+(\w+)\s*\([^)]*\)\s*\{'
                elif self.language == 'javascript':
                    # Match various JavaScript function patterns including tslib style
                    func_pattern = r'(?:function\s+(\w+)|(?:var\s+|let\s+|const\s+)?(\w+)\s*=\s*(?:function\s*\([^)]*\)|(?:\w+\.)?\w+\s*\|\|\s*function\s*\([^)]*\))|\b(\w+)\s*=\s*\([^)]*\)\s*=>)'
                else:
                    func_pattern = r'\b(?:def|function|func)\s+(\w+)[^:]*:'
                
                for match in re.finditer(func_pattern, code, re.MULTILINE):
                    # Find the end of the function by looking for the next function or end of file
                    start_pos = match.start()
                    
                    # Find end of function (language-specific heuristics)
                    if self.language == 'python':
                        next_func = re.search(r'\ndef\s+\w+', code[match.end():])
                        if next_func:
                            end_pos = match.end() + next_func.start()
                        else:
                            end_pos = len(code)
                    elif self.language in ['c', 'cpp', 'java']:
                        # For C/C++/Java, find matching closing brace
                        brace_count = 0
                        in_function = False
                        end_pos = len(code)
                        
                        for i, char in enumerate(code[start_pos:], start_pos):
                            if char == '{':
                                brace_count += 1
                                in_function = True
                            elif char == '}' and in_function:
                                brace_count -= 1
                                if brace_count == 0:
                                    end_pos = i + 1
                                    break
                    else:
                        # Default fallback
                        end_pos = len(code)
                    
                    func_text = code[start_pos:end_pos]
                    func_node = FallbackNode("function_definition", func_text, start_pos, end_pos)
                    
                    # Create a child node for the function name
                    if self.language == 'python':
                        name_match = re.search(r'(?:def|function|func)\s+(\w+)', match.group(0))
                    elif self.language in ['c', 'cpp', 'java']:
                        # Extract function name from C/C++/Java pattern
                        name_match = re.search(r'(\w+)\s*\([^)]*\)\s*\{', match.group(0))
                    else:
                        name_match = re.search(r'(?:def|function|func)\s+(\w+)', match.group(0))
                    
                    if name_match:
                        name_start = match.start() + name_match.start(1)
                        name_end = match.start() + name_match.end(1)
                        name_node = FallbackNode("identifier", name_match.group(1), name_start, name_end)
                        func_node.children.append(name_node)
                    
                    root.children.append(func_node)
                
                # Find control structures
                control_patterns = {
                    'if_statement': r'\bif\b',
                    'for_statement': r'\bfor\b',
                    'while_statement': r'\bwhile\b'
                }
                
                for node_type, pattern in control_patterns.items():
                    for match in re.finditer(pattern, code):
                        control_node = FallbackNode(node_type, match.group(0),
                                                  match.start(), match.end())
                        root.children.append(control_node)
                
                return root
        
        return FallbackAST(code, language)
    
    def supports_language(self, language: str) -> bool:
        """Check if parser supports the given language."""
        # Always return True to enable text-based fallback analysis
        supported_languages = {
            "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"
        }
        return language in supported_languages
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.parsers.keys())
    
    def normalize_ast(self, ast_tree: Any) -> Any:
        """Normalize AST tree for consistent analysis."""
        if not hasattr(ast_tree, 'root'):
            return ast_tree
            
        normalized_nodes = []
        self._normalize_node(ast_tree.root, normalized_nodes)
        
        class NormalizedAST:
            def __init__(self, nodes, language):
                self.nodes = nodes
                self.language = language
                
        return NormalizedAST(normalized_nodes, ast_tree.language)
    
    def _normalize_node(self, node, normalized_nodes: List[str]):
        """Recursively normalize AST nodes."""
        # Skip certain node types that don't affect semantics
        skip_types = {'comment', 'whitespace', 'newline'}
        
        if node.type not in skip_types:
            # Normalize identifiers to generic names
            if node.type in {'identifier', 'variable_name', 'function_name'}:
                normalized_nodes.append('IDENTIFIER')
            # Normalize literals
            elif node.type in {'string_literal', 'number_literal', 'boolean_literal'}:
                normalized_nodes.append(f'{node.type.upper()}')
            else:
                normalized_nodes.append(node.type)
        
        # Recursively process children
        for child in node.children:
            self._normalize_node(child, normalized_nodes)
    
    def extract_functions(self, ast_tree: Any) -> List[Any]:
        """Extract function definitions from AST."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        functions = []
        self._find_functions(ast_tree.root, functions, ast_tree.code)
        return functions
    
    def _find_functions(self, node, functions: List[Any], code: str):
        """Recursively find function definitions."""
        # Language-specific function node types
        function_types = {
            'function_definition',  # Python
            'function_declaration', # JavaScript, C, Java
            'method_definition',    # Java, JavaScript classes
            'arrow_function',       # JavaScript
            'function_item',        # Rust
            'func_declaration',     # Go
        }
        
        if node.type in function_types:
            func_info = {
                'type': node.type,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'start_point': node.start_point,
                'end_point': node.end_point,
                'text': code[node.start_byte:node.end_byte],
                'name': self._extract_function_name(node, code)
            }
            functions.append(func_info)
        
        # Recursively search children
        for child in node.children:
            self._find_functions(child, functions, code)
    
    def _extract_function_name(self, func_node, code: str) -> str:
        """Extract function name from function node."""
        for child in func_node.children:
            if child.type in {'identifier', 'function_name', 'name'}:
                return code[child.start_byte:child.end_byte]
        return 'anonymous'
    
    def extract_variables(self, ast_tree: Any) -> List[str]:
        """Extract variable names from AST."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        variables = set()
        self._find_variables(ast_tree.root, variables, ast_tree.code)
        return list(variables)
    
    def _find_variables(self, node, variables: set, code: str):
        """Recursively find variable declarations and usages."""
        # Variable declaration types
        var_types = {
            'variable_declaration',
            'assignment',
            'identifier',
            'variable_name',
            'parameter',
            'argument'
        }
        
        if node.type in var_types and node.type == 'identifier':
            var_name = code[node.start_byte:node.end_byte]
            if var_name and not var_name.isnumeric():
                variables.add(var_name)
        
        # Recursively search children
        for child in node.children:
            self._find_variables(child, variables, code)
    
    def extract_imports(self, ast_tree: Any) -> List[str]:
        """Extract import statements from AST."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        imports = []
        self._find_imports(ast_tree.root, imports, ast_tree.code)
        return imports
    
    def _find_imports(self, node, imports: List[str], code: str):
        """Recursively find import statements."""
        import_types = {
            'import_statement',
            'import_from_statement', 
            'import_declaration',
            'use_declaration',  # Rust
            'package_clause'    # Go
        }
        
        if node.type in import_types:
            import_text = code[node.start_byte:node.end_byte].strip()
            imports.append(import_text)
        
        # Recursively search children
        for child in node.children:
            self._find_imports(child, imports, code)
    
    def get_node_type(self, node: Any) -> str:
        """Get the type of an AST node."""
        if hasattr(node, 'type'):
            return node.type
        return "unknown"
    
    def get_node_value(self, node: Any, code: str = None) -> str:
        """Get the value of an AST node."""
        if hasattr(node, 'text') and node.text:
            return node.text.decode() if isinstance(node.text, bytes) else node.text
        elif code and hasattr(node, 'start_byte') and hasattr(node, 'end_byte'):
            return code[node.start_byte:node.end_byte]
        return ""
    
    def get_node_children(self, node: Any) -> List[Any]:
        """Get children of an AST node."""
        if hasattr(node, 'children'):
            return node.children
        return []