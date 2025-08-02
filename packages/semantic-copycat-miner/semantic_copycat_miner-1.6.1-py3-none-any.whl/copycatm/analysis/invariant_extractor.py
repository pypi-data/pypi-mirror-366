"""
Mathematical invariant extraction for CopycatM.
"""

import uuid
import hashlib
import re
from typing import Dict, List, Any, Optional
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy import FuzzyHasher


class InvariantExtractor:
    """Extract mathematical invariants from code."""
    
    def __init__(self):
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = FuzzyHasher(threshold=100)
        self.mathematical_operators = {
            '+', '-', '*', '/', '%', '//', '**', '&', '|', '^', '<<', '>>', 
            '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!', '~'
        }
    
    def extract(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Extract mathematical invariants from the AST tree or source code."""
        invariants = []
        
        # Get source code
        code = None
        if hasattr(ast_tree, 'code'):
            code = ast_tree.code
        elif hasattr(ast_tree, 'text'):
            code = ast_tree.text
        else:
            # No code available
            return invariants
            
        # Try AST-based extraction first
        if hasattr(ast_tree, 'root'):
            # Find mathematical expressions
            math_expressions = self._find_mathematical_expressions(ast_tree)
            
            for expr in math_expressions:
                invariant = self._analyze_mathematical_expression(expr, ast_tree, language)
                if invariant:
                    invariants.append(invariant)
            
            # Find loop invariants
            loop_invariants = self._find_loop_invariants(ast_tree)
            invariants.extend(loop_invariants)
        
        # If no invariants found via AST, try direct source extraction
        if not invariants and code:
            source_invariants = self._extract_from_source_code(code, language)
            invariants.extend(source_invariants)
        
        return invariants
    
    def _find_mathematical_expressions(self, ast_tree: Any) -> List[Dict[str, Any]]:
        """Find mathematical expressions in the AST."""
        expressions = []
        self._traverse_for_math_expressions(ast_tree.root, expressions, ast_tree.code)
        return expressions
    
    def _traverse_for_math_expressions(self, node: Any, expressions: List[Dict], code: str):
        """Recursively traverse AST to find mathematical expressions."""
        # Node types vary by language - include common ones
        mathematical_node_types = {
            # Python node types
            'binary_operator', 'unary_operator', 'assignment', 'augmented_assignment',
            'call', 'attribute', 'comparison_operator',
            # Additional Python-specific
            'expression_statement', 'binary_expression', 'unary_expression',
            'assignment_expression', 'augmented_assignment_expression',
            # C/C++/Java node types  
            'binary_expression', 'unary_expression', 'assignment_expression',
            'call_expression', 'field_expression', 'relational_expression',
            # General math operations
            'arithmetic_expression', 'multiplicative_expression', 'additive_expression',
            'power_expression', 'parenthesized_expression'
        }
        
        # Always check if this node or its text contains math operations
        expr_text = code[node.start_byte:node.end_byte] if node.start_byte < len(code) else ""
        
        # Check by node type or by content
        if node.type in mathematical_node_types or self._is_mathematical_expression(expr_text):
            # Ensure it's actually mathematical with additional validation
            if self._is_mathematical_expression(expr_text) and len(expr_text.strip()) > 2:
                # Get the full line for context validation
                lines = code.split('\n')
                node_line = code[:node.start_byte].count('\n')
                full_line = lines[node_line] if node_line < len(lines) else expr_text
                
                # Validate the mathematical context
                if self._validate_mathematical_context(expr_text, full_line):
                    expr_info = {
                        'node': node,
                        'text': expr_text,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte,
                        'lines': self._calculate_lines(node, code),
                        'type': node.type
                    }
                    expressions.append(expr_info)
        
        # Recursively check children
        for child in node.children:
            self._traverse_for_math_expressions(child, expressions, code)
    
    def _is_mathematical_expression(self, text: str) -> bool:
        """Check if text contains mathematical operations."""
        # Early exclusion for obvious non-math content
        if len(text.strip()) < 3:
            return False
            
        # Exclude if it looks like HTML/XML or command syntax
        if re.match(r'^<[^>]+>$', text.strip()):
            return False
            
        # Remove whitespace and check for mathematical operators
        cleaned_text = text.replace(' ', '').replace('\n', '').replace('\t', '')
        
        # Must contain actual math operators, not just comparison
        math_ops = {'+', '-', '*', '/', '%', '//', '**', '^'}
        has_math_op = any(op in cleaned_text for op in math_ops)
        
        # Look for mathematical function calls
        math_functions = {'abs', 'sqrt', 'pow', 'sin', 'cos', 'tan', 'log', 'exp', 'min', 'max', 'sum', 
                         'ceil', 'floor', 'round', 'fabs', 'fmod', 'atan', 'asin', 'acos'}
        words = re.findall(r'\b\w+\b', text.lower())
        has_math_func = any(func in words for func in math_functions)
        
        # Look for numeric calculations (number op number)
        has_numeric_calc = bool(re.search(r'\d+\.?\d*\s*[+\-*/]\s*\d+\.?\d*', text))
        
        # Look for increment/decrement patterns
        has_inc_dec = bool(re.search(r'\b\w+\s*(\+\+|--|\+=|-=|\*=|/=|%=)', text))
        
        # Look for array indexing operations (common in algorithms)
        has_array_op = bool(re.search(r'\[[^\]]+\]\s*=|=\s*[^\[]+\[[^\]]+\]', text))
        
        # Look for length-based operations
        has_length_op = bool(re.search(r'\.length|\.size\(\)|\.count', text))
        
        # Must have at least one of these to be considered mathematical
        return has_math_op or has_math_func or has_numeric_calc or has_inc_dec or (has_array_op and has_length_op)
    
    def _calculate_lines(self, node: Any, code: str) -> Dict[str, int]:
        """Calculate line information for a node."""
        start_line = code[:node.start_byte].count('\n') + 1
        end_line = code[:node.end_byte].count('\n') + 1
        return {
            "start": start_line,
            "end": end_line,
            "total": end_line - start_line + 1
        }
    
    def _analyze_mathematical_expression(self, expr: Dict[str, Any], ast_tree: Any, language: str) -> Optional[Dict[str, Any]]:
        """Analyze a mathematical expression for invariant properties."""
        expr_text = expr['text']
        
        # Skip very simple expressions (single variables or constants)
        if len(expr_text.strip()) < 3:
            return None
        
        # Analyze expression complexity
        complexity = self._calculate_expression_complexity(expr['node'])
        if complexity < 2:  # Skip trivial expressions
            return None
        
        invariant_type = self._classify_mathematical_expression(expr['node'], expr_text)
        confidence = self._calculate_invariant_confidence(expr['node'], expr_text, invariant_type)
        
        if confidence < 0.3:  # Skip low-confidence invariants
            return None
        
        return self._create_invariant_entry(expr, invariant_type, confidence, complexity)
    
    def _calculate_expression_complexity(self, node: Any) -> int:
        """Calculate the complexity of a mathematical expression."""
        complexity = 0
        
        # Count operators
        operator_types = {'binary_operator', 'unary_operator', 'comparison_operator'}
        complexity += self._count_nodes_of_types(node, operator_types)
        
        # Count function calls
        if node.type == 'call':
            complexity += 2
        
        # Count nested expressions (parentheses)
        complexity += self._count_nested_expressions(node)
        
        return complexity
    
    def _count_nodes_of_types(self, node: Any, node_types: set) -> int:
        """Count nodes of specific types."""
        count = 0
        if node.type in node_types:
            count += 1
        for child in node.children:
            count += self._count_nodes_of_types(child, node_types)
        return count
    
    def _count_nested_expressions(self, node: Any) -> int:
        """Count nested expressions (parenthesized expressions)."""
        count = 0
        if node.type == 'parenthesized_expression':
            count += 1
        for child in node.children:
            count += self._count_nested_expressions(child)
        return count
    
    def _classify_mathematical_expression(self, node: Any, text: str) -> str:
        """Classify the type of mathematical expression."""
        text_lower = text.lower()
        
        # Arithmetic operations
        if any(op in text for op in ['+', '-', '*', '/', '%', '//', '**']):
            if any(func in text_lower for func in ['sqrt', 'pow', 'abs']):
                return "complex_arithmetic"
            else:
                return "arithmetic_calculation"
        
        # Comparison operations
        elif any(op in text for op in ['==', '!=', '<', '>', '<=', '>=']):
            return "comparison_expression"
        
        # Logical operations
        elif any(op in text for op in ['&&', '||', '!', 'and', 'or', 'not']):
            return "logical_expression"
        
        # Trigonometric functions
        elif any(func in text_lower for func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']):
            return "trigonometric_expression"
        
        # Mathematical functions
        elif any(func in text_lower for func in ['log', 'exp', 'sqrt', 'pow']):
            return "mathematical_function"
        
        # Bitwise operations
        elif any(op in text for op in ['&', '|', '^', '<<', '>>', '~']):
            return "bitwise_operation"
        
        else:
            return "generic_expression"
    
    def _calculate_invariant_confidence(self, node: Any, text: str, invariant_type: str) -> float:
        """Calculate confidence score for the invariant."""
        confidence = 0.0
        
        # Base confidence by type
        type_confidence = {
            "complex_arithmetic": 0.8,
            "arithmetic_calculation": 0.6,
            "comparison_expression": 0.7,
            "logical_expression": 0.5,
            "trigonometric_expression": 0.9,
            "mathematical_function": 0.8,
            "bitwise_operation": 0.6,
            "generic_expression": 0.4
        }
        
        confidence += type_confidence.get(invariant_type, 0.4)
        
        # Adjust based on complexity
        complexity = self._calculate_expression_complexity(node)
        complexity_bonus = min(complexity * 0.1, 0.2)
        confidence += complexity_bonus
        
        # Adjust based on length (more complex expressions are more likely to be meaningful)
        length_factor = min(len(text) / 50.0, 0.2)
        confidence += length_factor
        
        return min(confidence, 1.0)
    
    def _find_loop_invariants(self, ast_tree: Any) -> List[Dict[str, Any]]:
        """Find loop invariants in the code."""
        invariants = []
        loops = []
        
        self._find_loops(ast_tree.root, loops)
        
        for loop in loops:
            loop_invariants = self._analyze_loop_for_invariants(loop, ast_tree.code)
            invariants.extend(loop_invariants)
        
        return invariants
    
    def _find_loops(self, node: Any, loops: List[Any]):
        """Find all loop nodes in the AST."""
        loop_types = {'for_statement', 'while_statement', 'for_in_statement'}
        
        if node.type in loop_types:
            loops.append(node)
        
        for child in node.children:
            self._find_loops(child, loops)
    
    def _analyze_loop_for_invariants(self, loop_node: Any, code: str) -> List[Dict[str, Any]]:
        """Analyze a loop for potential invariants."""
        invariants = []
        
        # Extract loop condition
        loop_condition = self._extract_loop_condition(loop_node, code)
        if loop_condition:
            invariant = {
                "id": f"inv_{str(uuid.uuid4())[:8]}",
                "type": "loop_invariant",
                "confidence": 0.7,
                "complexity_metric": 2,
                "lines": self._calculate_lines(loop_node, code),
                "evidence": {
                    "expression_type": "loop_condition",
                    "loop_type": loop_node.type,
                    "condition": loop_condition
                },
                "hashes": self._generate_invariant_hashes(loop_condition),
                "transformation_resistance": {
                    "variable_renaming": 0.8,
                    "loop_restructuring": 0.6,
                    "condition_modification": 0.4
                }
            }
            invariants.append(invariant)
        
        # Look for assignments within the loop that might be invariants
        assignments = self._find_loop_assignments(loop_node, code)
        for assignment in assignments:
            if self._is_potential_invariant_assignment(assignment):
                invariant = self._create_assignment_invariant(assignment, loop_node, code)
                if invariant:
                    invariants.append(invariant)
        
        return invariants
    
    def _extract_loop_condition(self, loop_node: Any, code: str) -> Optional[str]:
        """Extract the condition from a loop node."""
        # Find condition node in loop structure
        for child in loop_node.children:
            if child.type in {'comparison_operator', 'binary_operator', 'identifier', 'call'}:
                condition_text = code[child.start_byte:child.end_byte].strip()
                if len(condition_text) > 0 and condition_text != ':':
                    return condition_text
        
        return None
    
    def _find_loop_assignments(self, loop_node: Any, code: str) -> List[Dict[str, Any]]:
        """Find assignment statements within a loop."""
        assignments = []
        self._traverse_for_assignments(loop_node, assignments, code)
        return assignments
    
    def _traverse_for_assignments(self, node: Any, assignments: List[Dict], code: str):
        """Recursively find assignment statements."""
        assignment_types = {'assignment', 'augmented_assignment'}
        
        if node.type in assignment_types:
            assignment_text = code[node.start_byte:node.end_byte]
            assignments.append({
                'node': node,
                'text': assignment_text,
                'type': node.type
            })
        
        for child in node.children:
            self._traverse_for_assignments(child, assignments, code)
    
    def _is_potential_invariant_assignment(self, assignment: Dict[str, Any]) -> bool:
        """Check if an assignment might represent an invariant."""
        text = assignment['text']
        
        # Look for mathematical operations in assignments
        if any(op in text for op in ['+', '-', '*', '/', '%']):
            return True
        
        # Look for accumulator patterns
        if '++' in text or '--' in text or '+=' in text or '-=' in text:
            return True
        
        return False
    
    def _create_assignment_invariant(self, assignment: Dict[str, Any], loop_node: Any, code: str) -> Optional[Dict[str, Any]]:
        """Create an invariant from a loop assignment."""
        assignment_text = assignment['text']
        
        # Analyze the assignment pattern
        if '+=' in assignment_text or '++' in assignment_text:
            invariant_type = "accumulator_invariant"
            confidence = 0.8
        elif '-=' in assignment_text or '--' in assignment_text:
            invariant_type = "decrement_invariant"
            confidence = 0.8
        elif any(op in assignment_text for op in ['*=', '/=', '%=']):
            invariant_type = "multiplicative_invariant"
            confidence = 0.7
        else:
            invariant_type = "assignment_invariant"
            confidence = 0.6
        
        return {
            "id": f"inv_{str(uuid.uuid4())[:8]}",
            "type": invariant_type,
            "confidence": confidence,
            "complexity_metric": 3,
            "lines": self._calculate_lines(assignment['node'], code),
            "evidence": {
                "expression_type": invariant_type,
                "assignment_pattern": assignment_text,
                "loop_context": True
            },
            "hashes": self._generate_invariant_hashes(assignment_text),
            "transformation_resistance": {
                "variable_renaming": 0.9,
                "operation_reordering": 0.7,
                "loop_unrolling": 0.5
            }
        }
    
    def _create_invariant_entry(self, expr: Dict[str, Any], invariant_type: str, confidence: float, complexity: int) -> Dict[str, Any]:
        """Create a mathematical invariant entry."""
        invariant_id = f"inv_{str(uuid.uuid4())[:8]}"
        expr_text = expr['text']
        
        return {
            "id": invariant_id,
            "type": "mathematical_expression",
            "confidence": confidence,
            "complexity_metric": complexity,
            "lines": expr['lines'],
            "evidence": {
                "expression_type": invariant_type,
                "mathematical_operators": self._extract_operators(expr_text),
                "has_constants": self._has_numeric_constants(expr_text),
                "has_variables": self._has_variables(expr_text)
            },
            "hashes": self._generate_invariant_hashes(expr_text),
            "transformation_resistance": {
                "variable_renaming": 0.9 if invariant_type == "comparison_expression" else 0.8,
                "constant_substitution": 0.6,
                "operator_precedence": 0.7,
                "expression_reordering": 0.5
            }
        }
    
    def _extract_operators(self, text: str) -> List[str]:
        """Extract mathematical operators from text."""
        operators = []
        for op in self.mathematical_operators:
            if op in text:
                operators.append(op)
        return operators
    
    def _has_numeric_constants(self, text: str) -> bool:
        """Check if text contains numeric constants."""
        return bool(re.search(r'\d+\.?\d*', text))
    
    def _has_variables(self, text: str) -> bool:
        """Check if text contains variable identifiers."""
        # Look for word characters that aren't numbers
        variables = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text)
        return len(variables) > 0
    
    def _generate_invariant_hashes(self, text: str) -> Dict[str, Any]:
        """Generate hashes for an invariant expression."""
        return {
            "direct": self.direct_hasher.hash_text(text),
            "fuzzy": {
                "tlsh": self.fuzzy_hasher.hash_text(text)
            },
            "normalized": {
                "sha256": hashlib.sha256(self._normalize_expression(text).encode()).hexdigest()
            }
        }
    
    def _normalize_expression(self, text: str) -> str:
        """Normalize mathematical expression for consistent hashing."""
        # Remove whitespace
        normalized = re.sub(r'\s+', '', text)
        
        # Replace variable names with generic placeholders
        normalized = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'VAR', normalized)
        
        # Normalize numeric constants
        normalized = re.sub(r'\d+\.?\d*', 'NUM', normalized)
        
        return normalized
    
    def _extract_from_source_code(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract mathematical invariants directly from source code."""
        invariants = []
        lines = code.split('\n')
        
        # Patterns for mathematical expressions across languages
        math_patterns = [
            # Basic arithmetic assignment: x = a + b * c (but not in strings)
            r'\b[a-zA-Z_]\w*\s*=\s*(?!["\'`])[^=;{}<>]*[+\-*/][^;{}]*(?<!["\'`])(?=;|$|\)|,)',
            # Power operations: x ** 2, pow(x, 2), Math.pow(x, 2)
            r'\b\w+\s*\*\*\s*[\d.]+|\bpow\s*\([^)]+\)|\b(Math|math)\.pow\s*\([^)]+\)',
            # Mathematical functions with proper word boundaries
            r'\b(math\.|Math\.|)(sqrt|sin|cos|tan|log|exp|abs|min|max|pow|ceil|floor|round|atan2?)\s*\([^)]+\)',
            # Increment/decrement patterns
            r'\b[a-zA-Z_]\w*\s*(\+\+|--|\+=|-=|\*=|/=|%=)(?=[;\s]|$)',
            # Array/matrix element operations
            r'\b[a-zA-Z_]\w*\[[^\]]+\]\s*[+\-*/]=?\s*[^;]+[+\-*/]',
            # Numeric calculations (avoid matching version numbers or dates)
            r'(?<!\d)\d+\.?\d*\s*[+\-*/]\s*\d+\.?\d*(?!\d|\.|/)',
            # Complex calculations in parentheses (but not function calls)
            r'\([^(),;{}]*[+\-*/][^(),;{}]*\)(?!\s*\{)',
            # Array element assignment with expressions: arr[i] = value
            r'\b[a-zA-Z_]\w*\[[^\]]+\]\s*=\s*[^;]+(?=;|$)',
            # Array indexing in loops: array[i++], array[j++, k++]
            r'\b[a-zA-Z_]\w*\[\s*[a-zA-Z_]\w*\s*(\+\+|--)\s*\]',
            # Length accumulation patterns: s += arr[i].length
            r'\b[a-zA-Z_]\w*\s*\+=\s*[^;]*\.length',
            # Loop variable operations in conditions: i < n, j < arr.length
            r'\b[a-zA-Z_]\w*\s*[<>]=?\s*[a-zA-Z_]\w*(?:\.length)?(?=\s*[;,)])',
        ]
        
        # Track found expressions to avoid duplicates
        found_expressions = set()
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            cleaned_line = self._remove_comments(line, language).strip()
            if not cleaned_line:
                continue
                
            for pattern in math_patterns:
                matches = re.finditer(pattern, cleaned_line, re.IGNORECASE)
                for match in matches:
                    expr_text = match.group(0).strip()
                    
                    # Skip if too short or already found
                    if len(expr_text) < 3 or expr_text in found_expressions:
                        continue
                    
                    # Check if it's actually mathematical
                    if not self._is_mathematical_expression(expr_text):
                        continue
                    
                    # Additional validation to reduce false positives
                    if not self._validate_mathematical_context(expr_text, cleaned_line):
                        continue
                        
                    found_expressions.add(expr_text)
                    
                    # Classify the expression
                    expr_type = self._classify_source_expression(expr_text)
                    
                    # Create invariant entry
                    invariant = {
                        "id": f"inv_{str(uuid.uuid4())[:8]}",
                        "type": "mathematical_expression",
                        "confidence": 0.7,  # Source-based extraction has moderate confidence
                        "complexity_metric": self._calculate_source_complexity(expr_text),
                        "lines": {
                            "start": line_num,
                            "end": line_num,
                            "total": 1
                        },
                        "evidence": {
                            "expression_type": expr_type,
                            "mathematical_operators": self._extract_operators(expr_text),
                            "has_constants": self._has_numeric_constants(expr_text),
                            "has_variables": self._has_variables(expr_text),
                            "source_based": True,
                            "original_expression": expr_text,
                            "normalized_expression": self._normalize_expression(expr_text)
                        },
                        "hashes": self._generate_invariant_hashes(expr_text),
                        "transformation_resistance": {
                            "variable_renaming": 0.9,
                            "constant_substitution": 0.6,
                            "operator_precedence": 0.7,
                            "expression_reordering": 0.5
                        }
                    }
                    
                    invariants.append(invariant)
        
        return invariants
    
    def _remove_comments(self, line: str, language: str) -> str:
        """Remove comments from a line of code."""
        if language in ['python']:
            # Remove Python comments
            if '#' in line:
                line = line[:line.index('#')]
        elif language in ['c', 'cpp', 'java', 'javascript', 'go', 'rust']:
            # Remove C-style comments
            if '//' in line:
                line = line[:line.index('//')]
        return line
    
    def _classify_source_expression(self, expr_text: str) -> str:
        """Classify mathematical expression from source code."""
        expr_lower = expr_text.lower()
        
        # Check for specific patterns
        if '**' in expr_text or 'pow' in expr_lower:
            return "power_expression"
        elif any(func in expr_lower for func in ['sqrt', 'sin', 'cos', 'tan', 'log', 'exp']):
            return "mathematical_function"
        elif any(op in expr_text for op in ['+=', '-=', '*=', '/=', '++', '--']):
            return "accumulator_expression"
        elif '[' in expr_text and ']' in expr_text:
            return "array_calculation"
        elif any(op in expr_text for op in ['<', '>', '<=', '>=', '==', '!=']):
            return "comparison_expression"
        elif '/' in expr_text or '*' in expr_text:
            return "multiplicative_expression"
        elif '+' in expr_text or '-' in expr_text:
            return "additive_expression"
        else:
            return "general_expression"
    
    def _calculate_source_complexity(self, expr_text: str) -> int:
        """Calculate complexity of expression from source."""
        complexity = 0
        
        # Count operators
        for op in self.mathematical_operators:
            complexity += expr_text.count(op)
        
        # Count function calls
        complexity += len(re.findall(r'\b\w+\s*\(', expr_text))
        
        # Count nested parentheses
        max_depth = 0
        current_depth = 0
        for char in expr_text:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth -= 1
        complexity += max_depth
        
        return max(complexity, 1)
    
    def _validate_mathematical_context(self, expr_text: str, full_line: str) -> bool:
        """Validate that the expression is in a mathematical context, not just text."""
        # Exclude common false positive patterns
        false_positive_patterns = [
            # HTML/XML tags or generic comparisons
            r'^<[^>]+>$',
            r'^<\w+\s*/?>$',
            # Command line arguments or options
            r'^<[^>]*options?[^>]*>$',
            r'^<[^>]*input[^>]*>$',
            r'^<[^>]*output[^>]*>$',
            # File paths with comparison operators
            r'^[<>]\s*[\w/\\.-]+$',
            # String literals with operators (common in print statements)
            r'^["\'][^"\']*(\+|-|\*|/)[^"\']$',
            # Template variables
            r'^\${[^}]+}$',
            r'^\{\{[^}]+\}\}$',
            # Import/require statements - these are NOT mathematical!
            r'^\s*\(["\'][^"\']*[/\\][^"\']*["\']\)\s*$',
            r'^["\'][^"\']*\.[^"\']+["\']\s*$',
        ]
        
        for pattern in false_positive_patterns:
            if re.match(pattern, expr_text, re.IGNORECASE):
                return False
        
        # Check if the line looks like documentation or comments
        doc_indicators = ['usage:', 'example:', 'note:', 'todo:', 'fixme:', 'hack:', 
                         'synopsis:', 'description:', 'parameter:', 'param:', 'args:',
                         'returns:', 'throws:', 'error:', 'warning:']
        line_lower = full_line.lower()
        for indicator in doc_indicators:
            if indicator in line_lower:
                return False
        
        # Exclude import/require statements
        import_patterns = [
            r'\bimport\s+', r'\brequire\s*\(', r'\bfrom\s+["\']',
            r'\bconst\s+\w+\s*=\s*require\s*\(', r'\bvar\s+\w+\s*=\s*require\s*\(',
            r'\blet\s+\w+\s*=\s*require\s*\(', r'\binclude\s*[<"]'
        ]
        for pattern in import_patterns:
            if re.search(pattern, full_line, re.IGNORECASE):
                return False
        
        # Exclude if it's inside a string literal
        # Check if the expression is within quotes in the full line
        in_string = False
        quote_pairs = [('"', '"'), ("'", "'"), ('`', '`')]
        for start_quote, end_quote in quote_pairs:
            if start_quote in full_line:
                # Simple check - if expr is between quotes
                parts = full_line.split(start_quote)
                for i in range(1, len(parts), 2):  # Check odd-indexed parts (inside quotes)
                    if expr_text in parts[i]:
                        in_string = True
                        break
        
        if in_string:
            return False
        
        # Validate that it contains actual mathematical operations
        # Must have at least one variable/identifier and one operator
        has_identifier = bool(re.search(r'\b[a-zA-Z_]\w*\b', expr_text))
        has_number = bool(re.search(r'\b\d+\.?\d*\b', expr_text))
        has_operator = any(op in expr_text for op in ['+', '-', '*', '/', '%', '**', '^'])
        
        # Should have identifier and (number or operator)
        if not (has_identifier and (has_number or has_operator)):
            # Exception for increment/decrement
            if not re.search(r'\b\w+\s*(\+\+|--|\+=|-=|\*=|/=)', expr_text):
                return False
        
        # Additional context checks
        # Exclude if surrounded by typical non-math contexts
        context_before = full_line[:full_line.find(expr_text)].strip() if expr_text in full_line else ""
        context_after = full_line[full_line.find(expr_text) + len(expr_text):].strip() if expr_text in full_line else ""
        
        # Common non-math contexts
        non_math_contexts = [
            # Print/log statements
            ('print', ''),
            ('printf', ''),
            ('console.log', ''),
            ('echo', ''),
            ('fprintf', ''),
            # Comments
            ('//', ''),
            ('/*', '*/'),
            ('#', ''),
            # Documentation
            ('*', ''),  # Common in doc blocks
            # String formatting
            ('%s', ''),
            ('format(', ')'),
        ]
        
        for prefix, suffix in non_math_contexts:
            if (prefix and context_before.endswith(prefix)) or (suffix and context_after.startswith(suffix)):
                return False
        
        return True