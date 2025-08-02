"""
Improved Tree-sitter parser with better language detection and line tracking.
"""

import tree_sitter
import logging
import re
from typing import Any, Optional, Dict, List, Tuple
from pathlib import Path
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


class ImprovedTreeSitterParser(BaseParser):
    """Improved tree-sitter parser with better fallback and line tracking."""
    
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
                language = module.language()
                parser = tree_sitter.Parser(language)
                
                self.languages[lang_name] = language
                self.parsers[lang_name] = parser
                logger.debug(f"Initialized {lang_name} parser via direct import")
                
            except Exception as e:
                logger.debug(f"Failed to initialize {lang_name} via direct import: {e}")
        
        # Try tree-sitter-languages if available
        if TREE_SITTER_AVAILABLE and get_language:
            for lang_name, ts_name in language_map.items():
                if lang_name in self.parsers:
                    continue  # Already loaded
                    
                try:
                    language = get_language(ts_name)
                    parser = tree_sitter.Parser(language)
                    
                    self.languages[lang_name] = language
                    self.parsers[lang_name] = parser
                    
                except Exception as e:
                    logger.debug(f"Failed to initialize {lang_name}: {e}")
                    continue
    
    def detect_language_from_content(self, code: str, file_path: Optional[str] = None) -> str:
        """Detect language from code content using heuristics."""
        # First try file extension if available
        if file_path:
            ext = Path(file_path).suffix.lower()
            ext_map = {
                '.py': 'python',
                '.pyx': 'python',
                '.pyi': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.jsx': 'javascript',
                '.tsx': 'typescript',
                '.java': 'java',
                '.c': 'c',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.cxx': 'cpp',
                '.h': 'c',  # Could be C or C++, default to C
                '.hpp': 'cpp',
                '.go': 'go',
                '.rs': 'rust',
            }
            if ext in ext_map:
                return ext_map[ext]
        
        # Content-based detection heuristics
        lines = code.split('\n')[:20]  # Check first 20 lines
        content = '\n'.join(lines)
        
        # Python detection
        if re.search(r'^\s*(def|class|import|from\s+\w+\s+import|if\s+__name__)', content, re.M):
            return 'python'
        
        # JavaScript/TypeScript detection
        if re.search(r'^\s*(function|const|let|var|export|import\s+{|require\(|module\.exports)', content, re.M):
            if re.search(r':\s*(string|number|boolean|any|void|interface|type\s+\w+\s*=)', content):
                return 'typescript'
            return 'javascript'
        
        # Java detection
        if re.search(r'^\s*(public|private|protected)?\s*(class|interface|enum)\s+\w+', content, re.M):
            return 'java'
        
        # Go detection (check before C/C++ as it might have similar patterns)
        if re.search(r'^package\s+\w+', content, re.M) and re.search(r'func\s+\w+\s*\(', content):
            return 'go'
        
        # C/C++ detection
        if re.search(r'#include\s*[<"]|^\s*int\s+main\s*\(', content, re.M):
            if re.search(r'(class\s+\w+|namespace\s+\w+|using\s+namespace|template\s*<|std::)', content):
                return 'cpp'
            return 'c'
        
        # Rust detection
        if re.search(r'^\s*(fn\s+\w+|impl\s+\w+|use\s+\w+|pub\s+fn|struct\s+\w+|enum\s+\w+)', content, re.M):
            return 'rust'
        
        return 'unknown'
    
    def _calculate_line_positions(self, code: str) -> List[Tuple[int, int]]:
        """Calculate byte positions for each line in the code."""
        line_positions = []
        start = 0
        
        for line in code.split('\n'):
            end = start + len(line)
            line_positions.append((start, end))
            start = end + 1  # +1 for newline
        
        return line_positions
    
    def _byte_to_line_number(self, byte_pos: int, line_positions: List[Tuple[int, int]]) -> int:
        """Convert byte position to line number (1-indexed)."""
        for i, (start, end) in enumerate(line_positions):
            if start <= byte_pos <= end:
                return i + 1
        return len(line_positions)  # Default to last line
    
    def parse(self, code: str, language: str) -> Any:
        """Parse code and return AST tree with improved line tracking."""
        # Auto-detect language if unknown
        if language == 'unknown' or not language:
            language = self.detect_language_from_content(code)
            logger.debug(f"Auto-detected language: {language}")
        
        if not self.supports_language(language):
            raise ValueError(f"Language {language} not supported")
        
        # Calculate line positions for accurate line number tracking
        line_positions = self._calculate_line_positions(code)
        
        # Try tree-sitter parsing if available
        if language in self.parsers:
            try:
                parser = self.parsers[language]
                tree = parser.parse(code.encode())
                
                class ImprovedTreeSitterAST:
                    def __init__(self, tree, code: str, language: str, line_positions: List[Tuple[int, int]]):
                        self.tree = tree
                        self.code = code
                        self.language = language
                        self.root = tree.root_node
                        self.line_positions = line_positions
                    
                    def get_line_for_position(self, byte_pos: int) -> int:
                        """Get line number for byte position."""
                        for i, (start, end) in enumerate(self.line_positions):
                            if start <= byte_pos <= end:
                                return i + 1
                        return len(self.line_positions)
                    
                    def __str__(self):
                        return f"TreeSitterAST({self.language})"
                
                return ImprovedTreeSitterAST(tree, code, language, line_positions)
            except Exception as e:
                logger.debug(f"Tree-sitter parse failed for {language}: {e}")
                # Fall through to improved fallback
        
        # Use improved fallback parser
        return self._create_improved_fallback_ast(code, language, line_positions)
    
    def _create_improved_fallback_ast(self, code: str, language: str, line_positions: List[Tuple[int, int]]) -> Any:
        """Create an improved fallback AST with better line tracking."""
        class ImprovedFallbackAST:
            def __init__(self, code: str, language: str, line_positions: List[Tuple[int, int]]):
                self.code = code
                self.language = language
                self.line_positions = line_positions
                self.root = self._create_text_nodes(code)
            
            def get_line_for_position(self, byte_pos: int) -> int:
                """Get line number for byte position."""
                for i, (start, end) in enumerate(self.line_positions):
                    if start <= byte_pos <= end:
                        return i + 1
                return len(self.line_positions)
            
            def __str__(self):
                return f"ImprovedFallbackAST({self.language})"
            
            def _create_text_nodes(self, code: str):
                """Create nodes with accurate line tracking."""
                class ImprovedFallbackNode:
                    def __init__(self, node_type: str, text: str = "", start_byte: int = 0, 
                               end_byte: int = 0, start_line: int = 1, end_line: int = 1):
                        self.type = node_type
                        self.text = text
                        self.start_byte = start_byte
                        self.end_byte = end_byte
                        self.start_line = start_line
                        self.end_line = end_line
                        self.start_point = (start_line - 1, 0)  # Tree-sitter uses 0-indexed
                        self.end_point = (end_line - 1, 0)
                        self.children = []
                    
                    @property
                    def child_count(self):
                        return len(self.children)
                    
                    def child(self, index):
                        if 0 <= index < len(self.children):
                            return self.children[index]
                        return None
                    
                    def child_by_field_name(self, field_name):
                        return None
                
                root = ImprovedFallbackNode("module", code, 0, len(code), 1, len(self.line_positions))
                
                # Language-specific patterns with improved accuracy
                func_patterns = {
                    'python': r'^(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[^:]+)?:',
                    'javascript': r'(?:^|\n)\s*(?:async\s+)?(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
                    'typescript': r'(?:^|\n)\s*(?:async\s+)?(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
                    'java': r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+(?:\[\])?(?:\s*<[^>]+>)?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{',
                    'c': r'^\s*(?:static\s+|inline\s+)?(?:\w+(?:\s*\*)*)\s+(\w+)\s*\([^)]*\)\s*\{',
                    'cpp': r'^\s*(?:template\s*<[^>]+>\s*)?(?:static\s+|inline\s+|virtual\s+)?(?:\w+(?:\s*\*)*)\s+(\w+)\s*\([^)]*\)(?:\s*const)?\s*\{',
                    'go': r'^\s*func\s+(?:\(\s*\w+\s+[^)]+\)\s+)?(\w+)\s*\([^)]*\)(?:\s*[^{]+)?\s*\{',
                    'rust': r'^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)(?:<[^>]+>)?\s*\([^)]*\)(?:\s*->\s*[^{]+)?\s*\{'
                }
                
                pattern = func_patterns.get(self.language, func_patterns['python'])
                
                for match in re.finditer(pattern, code, re.MULTILINE):
                    start_pos = match.start()
                    start_line = self.get_line_for_position(start_pos)
                    
                    # Find function end using brace/indentation matching
                    if self.language == 'python':
                        # Python: find next function or dedent
                        indent_match = re.match(r'^(\s*)', code[start_pos:])
                        indent_level = len(indent_match.group(1)) if indent_match else 0
                        
                        lines = code[start_pos:].split('\n')
                        end_offset = len(lines[0])
                        
                        for i, line in enumerate(lines[1:], 1):
                            if line.strip() and not line.startswith(' ' * (indent_level + 1)):
                                break
                            end_offset += len(line) + 1
                        
                        end_pos = start_pos + end_offset
                    else:
                        # Brace-based languages: count braces
                        brace_count = 0
                        in_string = False
                        escape = False
                        end_pos = start_pos
                        
                        for i, char in enumerate(code[start_pos:], start_pos):
                            if escape:
                                escape = False
                                continue
                            
                            if char == '\\':
                                escape = True
                                continue
                            
                            if char in '"\'':
                                in_string = not in_string
                                continue
                            
                            if not in_string:
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_pos = i + 1
                                        break
                        
                        if end_pos == start_pos:  # No closing brace found
                            end_pos = len(code)
                    
                    end_line = self.get_line_for_position(end_pos - 1)
                    func_text = code[start_pos:end_pos]
                    
                    # Extract function name from match groups
                    func_name = None
                    groups = match.groups()
                    
                    # Language-specific group extraction
                    if self.language == 'python':
                        # Group 2 is the function name (group 1 is optional async)
                        func_name = groups[1] if len(groups) > 1 and groups[1] else None
                    elif self.language in ['javascript', 'typescript']:
                        # Groups 1 or 2 might have the function name
                        func_name = groups[0] if groups[0] else (groups[1] if len(groups) > 1 else None)
                    else:
                        # For other languages, take the first non-None group
                        for group in groups:
                            if group:
                                func_name = group
                                break
                    
                    if not func_name:
                        func_name = 'anonymous'
                    
                    func_node = ImprovedFallbackNode(
                        "function_definition", 
                        func_text, 
                        start_pos, 
                        end_pos,
                        start_line,
                        end_line
                    )
                    
                    # Create name node with correct byte positions
                    # Find the actual position of the function name in the code
                    name_start = start_pos
                    name_end = start_pos
                    
                    # For Python, find "def <name>"
                    if self.language == 'python':
                        def_match = re.search(r'def\s+(\w+)', func_text)
                        if def_match:
                            name_start = start_pos + def_match.start(1)
                            name_end = start_pos + def_match.end(1)
                    else:
                        # For other languages, try to find the function name position
                        if func_name and func_name != 'anonymous':
                            name_pos = func_text.find(func_name)
                            if name_pos >= 0:
                                name_start = start_pos + name_pos
                                name_end = name_start + len(func_name)
                    
                    name_node = ImprovedFallbackNode(
                        "identifier",
                        func_name,
                        name_start,
                        name_end,
                        start_line,
                        start_line
                    )
                    func_node.children.append(name_node)
                    
                    root.children.append(func_node)
                
                return root
        
        return ImprovedFallbackAST(code, language, line_positions)
    
    def supports_language(self, language: str) -> bool:
        """Check if parser supports the given language."""
        supported_languages = {
            "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"
        }
        return language in supported_languages
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(set(list(self.parsers.keys()) + ["python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"]))
    
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
        skip_types = {'comment', 'whitespace', 'newline'}
        
        if node.type not in skip_types:
            if node.type in {'identifier', 'variable_name', 'function_name'}:
                normalized_nodes.append('IDENTIFIER')
            elif node.type in {'string_literal', 'number_literal', 'boolean_literal'}:
                normalized_nodes.append(f'{node.type.upper()}')
            else:
                normalized_nodes.append(node.type)
        
        for child in node.children:
            self._normalize_node(child, normalized_nodes)
    
    def extract_functions(self, ast_tree: Any) -> List[Any]:
        """Extract function definitions from AST with line numbers."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        functions = []
        self._find_functions(ast_tree.root, functions, ast_tree)
        return functions
    
    def _find_functions(self, node, functions: List[Any], ast_tree):
        """Recursively find function definitions with accurate line tracking."""
        function_types = {
            'function_definition',
            'function_declaration',
            'method_definition',
            'arrow_function',
            'function_item',
            'func_declaration',
        }
        
        if node.type in function_types:
            # Calculate line numbers
            start_line = node.start_line if hasattr(node, 'start_line') else \
                        ast_tree.get_line_for_position(node.start_byte) if hasattr(ast_tree, 'get_line_for_position') else 1
            end_line = node.end_line if hasattr(node, 'end_line') else \
                      ast_tree.get_line_for_position(node.end_byte) if hasattr(ast_tree, 'get_line_for_position') else 1
            
            func_info = {
                'type': node.type,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'start_line': start_line,
                'end_line': end_line,
                'line_count': end_line - start_line + 1,
                'text': ast_tree.code[node.start_byte:node.end_byte],
                'name': self._extract_function_name(node, ast_tree.code)
            }
            functions.append(func_info)
        
        for child in node.children:
            self._find_functions(child, functions, ast_tree)
    
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
        """Recursively find variable declarations."""
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
            'use_declaration',
            'package_clause'
        }
        
        if node.type in import_types:
            import_text = code[node.start_byte:node.end_byte].strip()
            imports.append(import_text)
        
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