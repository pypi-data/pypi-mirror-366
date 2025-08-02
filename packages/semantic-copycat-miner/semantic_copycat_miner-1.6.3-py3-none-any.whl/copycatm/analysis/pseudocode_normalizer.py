"""
Cross-language pseudocode normalizer for semantic analysis.

This module converts AST nodes from different programming languages into
a standardized pseudocode representation, enabling cross-language algorithm
detection and comparison.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PseudocodeNormalizer:
    """
    Converts AST nodes into normalized pseudocode representation.
    
    Standardized constructs:
    - LOOP(condition, operation)
    - IF(condition, then_block, else_block)
    - FUNCTION(name, parameters, body)
    - ITERATE_TRANSFORM(collection, operation)
    - RECURSIVE_CALL(base_case, recursive_case)
    - ASSIGN(variable, expression)
    - RETURN(expression)
    - COMPARE(left, operator, right)
    - ARITHMETIC(left, operator, right)
    - ARRAY_ACCESS(array, index)
    - CALL(function, arguments)
    """
    
    def __init__(self):
        """Initialize the normalizer with language mappings."""
        self.language_mappings = self._initialize_language_mappings()
        self.node_handlers = self._initialize_node_handlers()
    
    def _initialize_language_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize language-specific mappings to normalized forms."""
        return {
            'python': {
                # Control structures
                'for_statement': 'LOOP',
                'while_statement': 'LOOP',
                'if_statement': 'IF',
                'elif_clause': 'ELIF',
                'else_clause': 'ELSE',
                'list_comprehension': 'ITERATE_TRANSFORM',
                'generator_expression': 'ITERATE_TRANSFORM',
                
                # Functions
                'function_definition': 'FUNCTION',
                'lambda': 'ANONYMOUS_FUNCTION',
                'return_statement': 'RETURN',
                'yield_statement': 'YIELD',
                
                # Operations
                'assignment': 'ASSIGN',
                'augmented_assignment': 'ASSIGN',
                'comparison_operator': 'COMPARE',
                'binary_operator': 'ARITHMETIC',
                'call': 'CALL',
                'subscript': 'ARRAY_ACCESS',
                
                # Special constructs
                'with_statement': 'WITH_CONTEXT',
                'try_statement': 'TRY_CATCH',
                'raise_statement': 'THROW',
            },
            'javascript': {
                # Control structures
                'for_statement': 'LOOP',
                'for_in_statement': 'LOOP',
                'for_of_statement': 'LOOP',
                'while_statement': 'LOOP',
                'do_statement': 'LOOP',
                'if_statement': 'IF',
                'ternary_expression': 'IF',
                
                # Functions
                'function_declaration': 'FUNCTION',
                'function_expression': 'FUNCTION',
                'arrow_function': 'ANONYMOUS_FUNCTION',
                'return_statement': 'RETURN',
                
                # Operations
                'assignment_expression': 'ASSIGN',
                'binary_expression': 'ARITHMETIC',
                'comparison_expression': 'COMPARE',
                'call_expression': 'CALL',
                'member_expression': 'ARRAY_ACCESS',
                
                # Special constructs
                'try_statement': 'TRY_CATCH',
                'throw_statement': 'THROW',
                'await_expression': 'AWAIT',
                'promise': 'ASYNC',
            },
            'java': {
                # Control structures
                'for_statement': 'LOOP',
                'enhanced_for_statement': 'LOOP',
                'while_statement': 'LOOP',
                'do_statement': 'LOOP',
                'if_statement': 'IF',
                
                # Functions
                'method_declaration': 'FUNCTION',
                'lambda_expression': 'ANONYMOUS_FUNCTION',
                'return_statement': 'RETURN',
                
                # Operations
                'assignment': 'ASSIGN',
                'binary_expression': 'ARITHMETIC',
                'comparison_expression': 'COMPARE',
                'method_invocation': 'CALL',
                'array_access': 'ARRAY_ACCESS',
                
                # Special constructs
                'try_statement': 'TRY_CATCH',
                'throw_statement': 'THROW',
                'stream_operation': 'ITERATE_TRANSFORM',
            }
        }
    
    def _initialize_node_handlers(self) -> Dict[str, callable]:
        """Initialize handlers for different node types."""
        return {
            'LOOP': self._normalize_loop,
            'IF': self._normalize_conditional,
            'FUNCTION': self._normalize_function,
            'ASSIGN': self._normalize_assignment,
            'COMPARE': self._normalize_comparison,
            'ARITHMETIC': self._normalize_arithmetic,
            'CALL': self._normalize_call,
            'ARRAY_ACCESS': self._normalize_array_access,
            'RETURN': self._normalize_return,
            'ITERATE_TRANSFORM': self._normalize_iterate_transform,
        }
    
    def extract_and_normalize_blocks(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """
        Extract code blocks from AST and normalize them to pseudocode.
        
        Returns:
            List of normalized blocks with metadata
        """
        normalized_blocks = []
        
        # Extract functions/methods first
        functions = self._extract_functions(ast_tree, language)
        
        for func in functions:
            try:
                # Normalize the function
                normalized = self._normalize_node(func['node'], language)
                
                # Calculate complexity and characteristics
                complexity_info = self._analyze_normalized_code(normalized)
                
                # Classify the algorithm based on normalized structure
                classification = self._classify_from_normalized(normalized, complexity_info)
                
                block = {
                    'block_type': 'function',
                    'name': func['name'],
                    'normalized_code': normalized,
                    'original_code': func['text'],
                    'location': {
                        'start_line': func['start_line'],
                        'end_line': func['end_line']
                    },
                    'complexity': complexity_info,
                    'classification': classification,
                    'confidence': self._calculate_confidence(normalized, complexity_info),
                    'function_name': func['name'],
                    'is_primary': True
                }
                
                normalized_blocks.append(block)
                
            except Exception as e:
                logger.warning(f"Failed to normalize function {func['name']}: {e}")
        
        # Also extract complex control structures outside functions
        control_structures = self._extract_control_structures(ast_tree, language)
        
        for struct in control_structures:
            try:
                normalized = self._normalize_node(struct['node'], language)
                complexity_info = self._analyze_normalized_code(normalized)
                
                block = {
                    'block_type': 'control_structure',
                    'name': f"{struct['type']}_{struct['start_line']}",
                    'normalized_code': normalized,
                    'original_code': struct['text'],
                    'location': {
                        'start_line': struct['start_line'],
                        'end_line': struct['end_line']
                    },
                    'complexity': complexity_info,
                    'classification': 'complex_code',
                    'confidence': 0.7,
                    'is_primary': False
                }
                
                normalized_blocks.append(block)
                
            except Exception as e:
                logger.warning(f"Failed to normalize control structure: {e}")
        
        return normalized_blocks
    
    def _normalize_node(self, node: Any, language: str) -> str:
        """Normalize an AST node to pseudocode."""
        if not node:
            return ""
        
        # Get node type and map to normalized form
        node_type = self._get_node_type(node)
        mappings = self.language_mappings.get(language, {})
        normalized_type = mappings.get(node_type, node_type.upper())
        
        # Handle based on normalized type
        if normalized_type in self.node_handlers:
            return self.node_handlers[normalized_type](node, language)
        else:
            # Default handling for unknown nodes
            return self._default_normalize(node, language)
    
    def _normalize_loop(self, node: Any, language: str) -> str:
        """Normalize loop constructs."""
        loop_type = self._get_node_type(node)
        
        if 'for' in loop_type:
            # Extract initialization, condition, update
            if language == 'python':
                # for item in collection:
                target = self._get_child_text(node, 'left')
                collection = self._get_child_text(node, 'right')
                body = self._normalize_children(node, language, 'body')
                return f"LOOP(ITERATE({target} in {collection}), {body})"
            
            elif language in ['javascript', 'java']:
                # for (init; condition; update)
                init = self._get_child_text(node, 'init')
                condition = self._get_child_text(node, 'condition')
                update = self._get_child_text(node, 'update')
                body = self._normalize_children(node, language, 'body')
                return f"LOOP(FOR({init}; {condition}; {update}), {body})"
        
        elif 'while' in loop_type:
            condition = self._get_child_text(node, 'condition')
            body = self._normalize_children(node, language, 'body')
            return f"LOOP(WHILE({condition}), {body})"
        
        return f"LOOP(UNKNOWN, {self._normalize_children(node, language)})"
    
    def _normalize_conditional(self, node: Any, language: str) -> str:
        """Normalize conditional statements."""
        condition = self._normalize_node(self._get_child(node, 'condition'), language)
        then_block = self._normalize_children(node, language, 'consequence')
        else_block = self._normalize_children(node, language, 'alternative')
        
        if else_block:
            return f"IF({condition}, {then_block}, {else_block})"
        else:
            return f"IF({condition}, {then_block})"
    
    def _normalize_function(self, node: Any, language: str) -> str:
        """Normalize function definitions."""
        name = self._get_function_name(node, language)
        params = self._get_function_params(node, language)
        body = self._normalize_children(node, language, 'body')
        
        # Check for recursion
        if self._is_recursive(name, body):
            base_case = self._extract_base_case(body)
            recursive_case = self._extract_recursive_case(body)
            return f"FUNCTION({name}, {params}, RECURSIVE_CALL({base_case}, {recursive_case}))"
        
        return f"FUNCTION({name}, {params}, {body})"
    
    def _normalize_assignment(self, node: Any, language: str) -> str:
        """Normalize assignment operations."""
        left = self._get_child_text(node, 'left')
        right = self._normalize_node(self._get_child(node, 'right'), language)
        return f"ASSIGN({left}, {right})"
    
    def _normalize_comparison(self, node: Any, language: str) -> str:
        """Normalize comparison operations."""
        left = self._normalize_node(self._get_child(node, 'left'), language)
        operator = self._get_child_text(node, 'operator')
        right = self._normalize_node(self._get_child(node, 'right'), language)
        
        # Normalize operators
        operator_map = {
            '==': 'EQ', '!=': 'NEQ', '<': 'LT', '>': 'GT',
            '<=': 'LTE', '>=': 'GTE', '===': 'EQ', '!==': 'NEQ'
        }
        normalized_op = operator_map.get(operator, operator)
        
        return f"COMPARE({left}, {normalized_op}, {right})"
    
    def _normalize_arithmetic(self, node: Any, language: str) -> str:
        """Normalize arithmetic operations."""
        left = self._normalize_node(self._get_child(node, 'left'), language)
        operator = self._get_child_text(node, 'operator')
        right = self._normalize_node(self._get_child(node, 'right'), language)
        
        # Normalize operators
        operator_map = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
            '%': 'MOD', '**': 'POW', '//': 'INTDIV'
        }
        normalized_op = operator_map.get(operator, operator)
        
        return f"ARITHMETIC({left}, {normalized_op}, {right})"
    
    def _normalize_call(self, node: Any, language: str) -> str:
        """Normalize function calls."""
        function = self._get_child_text(node, 'function')
        args = self._get_call_arguments(node, language)
        return f"CALL({function}, [{', '.join(args)}])"
    
    def _normalize_array_access(self, node: Any, language: str) -> str:
        """Normalize array/subscript access."""
        array = self._get_child_text(node, 'object')
        index = self._normalize_node(self._get_child(node, 'index'), language)
        return f"ARRAY_ACCESS({array}, {index})"
    
    def _normalize_return(self, node: Any, language: str) -> str:
        """Normalize return statements."""
        value = self._normalize_node(self._get_child(node, 'value'), language)
        return f"RETURN({value})"
    
    def _normalize_iterate_transform(self, node: Any, language: str) -> str:
        """Normalize iteration with transformation (list comprehensions, map, etc.)."""
        if language == 'python':
            # List comprehension: [expr for item in collection if condition]
            expr = self._get_child_text(node, 'element')
            target = self._get_child_text(node, 'target')
            iter_expr = self._get_child_text(node, 'iter')
            condition = self._get_child_text(node, 'ifs')
            
            if condition:
                return f"ITERATE_TRANSFORM({iter_expr}, LAMBDA({target}, IF({condition}, {expr})))"
            else:
                return f"ITERATE_TRANSFORM({iter_expr}, LAMBDA({target}, {expr}))"
        
        return f"ITERATE_TRANSFORM(UNKNOWN)"
    
    def _normalize_children(self, node: Any, language: str, field: Optional[str] = None) -> str:
        """Normalize all children of a node."""
        children = []
        
        if field and hasattr(node, field):
            target = getattr(node, field)
            if isinstance(target, list):
                for child in target:
                    normalized = self._normalize_node(child, language)
                    if normalized:
                        children.append(normalized)
            else:
                normalized = self._normalize_node(target, language)
                if normalized:
                    children.append(normalized)
        else:
            # Process all children
            for child in self._get_children(node):
                normalized = self._normalize_node(child, language)
                if normalized:
                    children.append(normalized)
        
        return f"BLOCK({'; '.join(children)})" if children else ""
    
    def _default_normalize(self, node: Any, language: str) -> str:
        """Default normalization for unknown nodes."""
        node_type = self._get_node_type(node)
        
        # Handle literals
        if 'literal' in node_type or 'constant' in node_type:
            return self._get_node_text(node)
        
        # Handle identifiers
        if 'identifier' in node_type:
            return self._get_node_text(node)
        
        # For complex nodes, normalize children
        children = self._normalize_children(node, language)
        if children:
            return f"{node_type.upper()}({children})"
        
        return self._get_node_text(node)
    
    def _analyze_normalized_code(self, normalized_code: str) -> Dict[str, Any]:
        """Analyze normalized code for complexity and patterns."""
        # Count different constructs
        loop_count = normalized_code.count('LOOP(')
        if_count = normalized_code.count('IF(')
        call_count = normalized_code.count('CALL(')
        arithmetic_count = normalized_code.count('ARITHMETIC(')
        compare_count = normalized_code.count('COMPARE(')
        
        # Detect nested structures
        nested_loops = self._count_nested_pattern(normalized_code, 'LOOP')
        nested_ifs = self._count_nested_pattern(normalized_code, 'IF')
        
        # Detect recursion
        has_recursion = 'RECURSIVE_CALL' in normalized_code
        
        # Detect iteration with transformation
        has_transform = 'ITERATE_TRANSFORM' in normalized_code
        
        return {
            'loop_count': loop_count,
            'conditional_count': if_count,
            'call_count': call_count,
            'arithmetic_operations': arithmetic_count,
            'comparisons': compare_count,
            'max_nesting_depth': max(nested_loops, nested_ifs),
            'has_recursion': has_recursion,
            'has_iteration_transform': has_transform,
            'complexity_score': self._calculate_complexity_score(
                loop_count, if_count, nested_loops, nested_ifs, has_recursion
            )
        }
    
    def _classify_from_normalized(self, normalized_code: str, complexity_info: Dict[str, Any]) -> str:
        """Classify algorithm based on normalized structure."""
        # Check for specific patterns in normalized code
        patterns = {
            'sorting': [
                ('COMPARE', 'LOOP', 'ASSIGN'),  # Basic sorting pattern
                ('RECURSIVE_CALL', 'COMPARE', 'partition'),  # Quicksort
                ('RECURSIVE_CALL', 'merge'),  # Merge sort
                ('LOOP', 'LOOP', 'COMPARE', 'swap'),  # Bubble sort
            ],
            'searching': [
                ('COMPARE', 'ARITHMETIC(', 'DIV'),  # Binary search (mid calculation)
                ('LOOP', 'COMPARE', 'RETURN'),  # Linear search
            ],
            'dynamic_programming': [
                ('RECURSIVE_CALL', 'memoization'),
                ('LOOP', 'LOOP', 'ARRAY_ACCESS', 'previous'),  # DP table
            ],
            'graph_algorithm': [
                ('queue', 'visited', 'LOOP'),  # BFS
                ('stack', 'visited', 'LOOP'),  # DFS
                ('RECURSIVE_CALL', 'visited'),  # DFS recursive
            ],
        }
        
        for algo_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if all(p in normalized_code for p in pattern):
                    return f"{algo_type}_algorithm"
        
        # Check complexity for unknown algorithm detection
        if complexity_info['complexity_score'] > 0.7:
            if complexity_info['has_recursion']:
                return 'unknown_recursive_algorithm'
            elif complexity_info['max_nesting_depth'] >= 3:
                return 'unknown_complex_algorithm'
            else:
                return 'unknown_algorithm'
        
        return 'complex_code'
    
    def _calculate_confidence(self, normalized_code: str, complexity_info: Dict[str, Any]) -> float:
        """Calculate confidence score for the normalized code."""
        # Base confidence from successful normalization
        confidence = 0.7
        
        # Boost for common patterns
        if any(pattern in normalized_code for pattern in ['RECURSIVE_CALL', 'ITERATE_TRANSFORM']):
            confidence += 0.1
        
        # Boost for high complexity
        if complexity_info['complexity_score'] > 0.5:
            confidence += 0.1
        
        # Penalty for very simple code
        if complexity_info['loop_count'] == 0 and complexity_info['conditional_count'] <= 1:
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _count_nested_pattern(self, code: str, pattern: str) -> int:
        """Count maximum nesting depth of a pattern."""
        max_depth = 0
        current_depth = 0
        
        i = 0
        while i < len(code):
            if code[i:i+len(pattern)+1] == f"{pattern}(":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                # Find matching closing parenthesis
                paren_count = 1
                j = i + len(pattern) + 1
                while j < len(code) and paren_count > 0:
                    if code[j] == '(':
                        paren_count += 1
                    elif code[j] == ')':
                        paren_count -= 1
                    j += 1
                i = j
                current_depth -= 1
            else:
                i += 1
        
        return max_depth
    
    def _calculate_complexity_score(self, loops: int, conditionals: int, 
                                   nested_loops: int, nested_ifs: int, 
                                   has_recursion: bool) -> float:
        """Calculate normalized complexity score (0.0 - 1.0)."""
        score = 0.0
        
        # Base complexity from counts
        score += min(loops * 0.1, 0.3)
        score += min(conditionals * 0.05, 0.2)
        
        # Nesting adds significant complexity
        score += min(nested_loops * 0.15, 0.3)
        score += min(nested_ifs * 0.1, 0.2)
        
        # Recursion indicates complex algorithm
        if has_recursion:
            score += 0.2
        
        return min(score, 1.0)
    
    # Helper methods for AST traversal (language-agnostic)
    
    def _extract_functions(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        
        # Handle tree-sitter AST
        if hasattr(ast_tree, 'root'):
            root = ast_tree.root
            
            # Check if it's a FallbackAST
            if hasattr(ast_tree, 'language') and hasattr(root, 'type') and root.type == 'module':
                # Handle FallbackAST - extract functions using regex
                import re
                
                if language == 'python':
                    # Find Python functions
                    pattern = r'^def\s+(\w+)\s*\([^)]*\):\s*$'
                    lines = ast_tree.code.splitlines()
                    
                    for i, line in enumerate(lines):
                        match = re.match(pattern, line)
                        if match:
                            func_name = match.group(1)
                            # Find the end of the function
                            start_line = i + 1
                            end_line = start_line
                            
                            # Simple heuristic: find next def or end of file
                            for j in range(i + 1, len(lines)):
                                if re.match(r'^def\s+\w+', lines[j]) or (j < len(lines) - 1 and not lines[j].strip() and not lines[j+1].startswith(' ')):
                                    end_line = j
                                    break
                            else:
                                end_line = len(lines)
                            
                            func_text = '\n'.join(lines[start_line-1:end_line])
                            func_info = {
                                'node': root,  # Use root as placeholder
                                'name': func_name,
                                'text': func_text,
                                'start_line': start_line,
                                'end_line': end_line,
                                'start_byte': 0,
                                'end_byte': len(func_text)
                            }
                            functions.append(func_info)
                
                return functions
            
            # Regular tree-sitter AST handling
            if hasattr(root, 'child_count'):
                # Define function node types per language
                function_types = {
                    'python': ['function_definition', 'lambda'],
                    'javascript': ['function_declaration', 'function_expression', 'arrow_function'],
                    'java': ['method_declaration'],
                    'c': ['function_definition'],
                    'cpp': ['function_definition'],
                }
                
                node_types = function_types.get(language, ['function_definition'])
                
                # Traverse and find function nodes
                def traverse(node, depth=0):
                    if hasattr(node, 'type') and node.type in node_types:
                        # Extract function info
                        func_info = {
                            'node': node,
                            'name': self._get_function_name_from_node(node, language),
                            'text': node.text.decode() if hasattr(node.text, 'decode') else str(node.text),
                            'start_line': node.start_point[0] + 1,  # Convert to 1-based
                            'end_line': node.end_point[0] + 1,
                            'start_byte': node.start_byte,
                            'end_byte': node.end_byte
                        }
                        functions.append(func_info)
                    
                    # Traverse children
                    if hasattr(node, 'child_count'):
                        for i in range(node.child_count):
                            child = node.child(i)
                            traverse(child, depth + 1)
                
                traverse(root)
        
        return functions
    
    def _extract_control_structures(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Extract complex control structures from AST."""
        structures = []
        
        # Handle tree-sitter AST
        if hasattr(ast_tree, 'root'):
            root = ast_tree.root
            
            # Define control structure types per language
            control_types = {
                'python': ['for_statement', 'while_statement', 'with_statement'],
                'javascript': ['for_statement', 'for_in_statement', 'while_statement', 'do_statement'],
                'java': ['for_statement', 'enhanced_for_statement', 'while_statement', 'do_statement'],
                'c': ['for_statement', 'while_statement', 'do_statement'],
                'cpp': ['for_statement', 'while_statement', 'do_statement', 'range_based_for_statement'],
            }
            
            node_types = control_types.get(language, ['for_statement', 'while_statement'])
            
            # Track which nodes are inside functions to avoid duplication
            function_nodes = set()
            
            def find_functions(node):
                function_types = {
                    'python': ['function_definition'],
                    'javascript': ['function_declaration', 'function_expression'],
                    'java': ['method_declaration'],
                }.get(language, ['function_definition'])
                
                if node.type in function_types:
                    function_nodes.add(node)
                
                for i in range(node.child_count):
                    find_functions(node.child(i))
            
            find_functions(root)
            
            # Traverse and find control structures
            def traverse(node, parent_function=None):
                # Check if this node is inside a function
                for func_node in function_nodes:
                    if (node.start_byte >= func_node.start_byte and 
                        node.end_byte <= func_node.end_byte):
                        parent_function = func_node
                        break
                
                # Only extract if not inside a function (to avoid duplication)
                if node.type in node_types and parent_function is None:
                    struct_info = {
                        'node': node,
                        'type': node.type,
                        'text': node.text.decode() if hasattr(node.text, 'decode') else str(node.text),
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte
                    }
                    
                    # Only add if it's complex enough
                    if node.end_point[0] - node.start_point[0] > 5:  # More than 5 lines
                        structures.append(struct_info)
                
                # Traverse children
                for i in range(node.child_count):
                    child = node.child(i)
                    traverse(child, parent_function)
            
            traverse(root)
        
        return structures
    
    def _get_function_name_from_node(self, node: Any, language: str) -> str:
        """Extract function name from a function node."""
        # Look for identifier child
        for i in range(node.child_count):
            child = node.child(i)
            if child.type == 'identifier':
                return child.text.decode() if hasattr(child.text, 'decode') else str(child.text)
        
        # Language-specific handling
        if language == 'python':
            # For Python, function name comes after 'def'
            for i in range(node.child_count):
                child = node.child(i)
                if child.type == 'identifier':
                    return child.text.decode() if hasattr(child.text, 'decode') else str(child.text)
        
        elif language in ['javascript', 'java']:
            # Look for name field
            name_node = node.child_by_field_name('name')
            if name_node:
                return name_node.text.decode() if hasattr(name_node.text, 'decode') else str(name_node.text)
        
        return 'anonymous'
    
    def _get_node_type(self, node: Any) -> str:
        """Get the type of an AST node."""
        if hasattr(node, 'type'):
            return node.type
        elif hasattr(node, 'kind'):
            return node.kind
        else:
            return 'unknown'
    
    def _get_node_text(self, node: Any) -> str:
        """Get the text content of a node."""
        if hasattr(node, 'text'):
            return node.text.decode() if isinstance(node.text, bytes) else str(node.text)
        elif hasattr(node, 'value'):
            return str(node.value)
        else:
            return ''
    
    def _get_child(self, node: Any, field: str) -> Any:
        """Get a specific child field from a node."""
        # Try tree-sitter field access first
        if hasattr(node, 'child_by_field_name'):
            child = node.child_by_field_name(field)
            if child:
                return child
        
        # Try attribute access
        if hasattr(node, field):
            return getattr(node, field)
        
        # For common field mappings
        field_mappings = {
            'condition': ['condition', 'test'],
            'body': ['body', 'consequence', 'block'],
            'left': ['left', 'left_operand'],
            'right': ['right', 'right_operand', 'iter'],
            'operator': ['operator'],
            'value': ['value', 'argument', 'expression'],
            'function': ['function', 'callee'],
            'arguments': ['arguments', 'args'],
            'init': ['init', 'initializer'],
            'update': ['update', 'increment'],
            'consequence': ['consequence', 'then'],
            'alternative': ['alternative', 'else']
        }
        
        # Try mapped fields
        if field in field_mappings:
            for mapped in field_mappings[field]:
                if hasattr(node, 'child_by_field_name'):
                    child = node.child_by_field_name(mapped)
                    if child:
                        return child
        
        return None
    
    def _get_child_text(self, node: Any, field: str) -> str:
        """Get text of a specific child field."""
        child = self._get_child(node, field)
        return self._get_node_text(child) if child else ''
    
    def _get_children(self, node: Any) -> List[Any]:
        """Get all children of a node."""
        if hasattr(node, 'child_count'):
            # Tree-sitter node
            return [node.child(i) for i in range(node.child_count)]
        elif hasattr(node, 'children'):
            return node.children
        else:
            return []
    
    def _get_function_name(self, node: Any, language: str) -> str:
        """Extract function name from function node."""
        name_field = {
            'python': 'name',
            'javascript': 'name',
            'java': 'name',
        }.get(language, 'name')
        
        return self._get_child_text(node, name_field) or 'anonymous'
    
    def _get_function_params(self, node: Any, language: str) -> str:
        """Extract function parameters."""
        params_field = {
            'python': 'parameters',
            'javascript': 'parameters',
            'java': 'parameters',
        }.get(language, 'parameters')
        
        params = self._get_child_text(node, params_field)
        return params or '[]'
    
    def _is_recursive(self, function_name: str, body: str) -> bool:
        """Check if a function is recursive."""
        return f"CALL({function_name}" in body
    
    def _extract_base_case(self, body: str) -> str:
        """Extract base case from recursive function."""
        # Look for IF statement with RETURN
        if_start = body.find('IF(')
        if if_start != -1:
            # Find the matching closing parenthesis
            paren_count = 1
            i = if_start + 3
            while i < len(body) and paren_count > 0:
                if body[i] == '(':
                    paren_count += 1
                elif body[i] == ')':
                    paren_count -= 1
                i += 1
            
            if_content = body[if_start:i]
            if 'RETURN' in if_content and 'CALL' not in if_content:
                return if_content
        
        return 'BASE_CASE'
    
    def _extract_recursive_case(self, body: str) -> str:
        """Extract recursive case from recursive function."""
        # Look for CALL within the function
        call_start = body.find('CALL(')
        if call_start != -1:
            # Extract the context around the recursive call
            # This is simplified - real implementation would be more sophisticated
            return 'RECURSIVE_CASE'
        
        return 'RECURSIVE_CASE'
    
    def _get_call_arguments(self, node: Any, language: str) -> List[str]:
        """Extract function call arguments."""
        args_field = {
            'python': 'arguments',
            'javascript': 'arguments',
            'java': 'arguments',
        }.get(language, 'arguments')
        
        args_node = self._get_child(node, args_field)
        if not args_node:
            return []
        
        # Extract individual arguments
        args = []
        for arg in self._get_children(args_node):
            args.append(self._normalize_node(arg, language))
        
        return args