"""
Improved mathematical invariant extraction with type classification.
"""

import uuid
import hashlib
import re
from typing import Dict, List, Any, Optional
from enum import Enum


class InvariantType(Enum):
    """Types of mathematical invariants."""
    LOOP_INVARIANT = "loop_invariant"
    PRECONDITION = "precondition"
    POSTCONDITION = "postcondition"
    MATHEMATICAL_RELATION = "mathematical_relation"
    COMPARISON_INVARIANT = "comparison_invariant"
    RECURSION_INVARIANT = "recursion_invariant"
    ASSIGNMENT_INVARIANT = "assignment_invariant"
    CONSTRAINT_INVARIANT = "constraint_invariant"
    ALGEBRAIC_INVARIANT = "algebraic_invariant"
    BOUNDARY_CONDITION = "boundary_condition"
    UNKNOWN = "unknown"


class ImprovedInvariantExtractor:
    """Extract and classify mathematical invariants from code."""
    
    def __init__(self):
        self.mathematical_operators = {
            '+', '-', '*', '/', '%', '//', '**', '&', '|', '^', '<<', '>>', 
            '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!', '~'
        }
        
        # Patterns for different invariant types
        self.invariant_patterns = {
            InvariantType.LOOP_INVARIANT: [
                r'while\s*\([^)]*\)',
                r'for\s*\([^;]*;[^;]*;[^)]*\)',
                r'do\s*{[^}]*}\s*while',
                r'for\s+\w+\s+in\s+range'
            ],
            InvariantType.PRECONDITION: [
                r'assert\s+[^,]+(?:,|$)',
                r'if\s+not\s+[^:]+:\s*raise',
                r'require\s*\([^)]+\)',
                r'@pre\s*\([^)]+\)'
            ],
            InvariantType.POSTCONDITION: [
                r'@post\s*\([^)]+\)',
                r'ensure\s*\([^)]+\)',
                r'return.*assert',
                r'assert.*return'
            ],
            InvariantType.RECURSION_INVARIANT: [
                r'if\s+[^:]+:\s*return\s+\w+\s*\(',
                r'return\s+\w+\s*\([^)]*\w+\s*[-+]\s*\d+',
                r'base\s+case|base_case'
            ],
            InvariantType.BOUNDARY_CONDITION: [
                r'if\s+\w+\s*[<>=]+\s*0',
                r'if\s+\w+\s*[<>=]+\s*len\(',
                r'if\s+\w+\s*==\s*\w+\.length',
                r'boundary|edge\s+case'
            ]
        }
    
    def extract(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Extract and classify mathematical invariants."""
        invariants = []
        
        # Get source code
        code = self._get_source_code(ast_tree)
        if not code:
            return invariants
        
        # Extract different types of invariants
        invariants.extend(self._extract_loop_invariants(ast_tree, code, language))
        invariants.extend(self._extract_mathematical_relations(ast_tree, code, language))
        invariants.extend(self._extract_comparison_invariants(ast_tree, code, language))
        invariants.extend(self._extract_recursion_invariants(ast_tree, code, language))
        invariants.extend(self._extract_boundary_conditions(ast_tree, code, language))
        invariants.extend(self._extract_assignment_invariants(ast_tree, code, language))
        
        # Deduplicate and validate
        invariants = self._deduplicate_invariants(invariants)
        
        return invariants
    
    def _get_source_code(self, ast_tree: Any) -> Optional[str]:
        """Extract source code from AST tree."""
        if hasattr(ast_tree, 'code'):
            return ast_tree.code
        elif hasattr(ast_tree, 'text'):
            return ast_tree.text
        return None
    
    def _extract_loop_invariants(self, ast_tree: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract loop invariants."""
        invariants = []
        
        # Find loops in AST
        if hasattr(ast_tree, 'root'):
            loops = self._find_loops(ast_tree.root, code)
            
            for loop in loops:
                # Extract loop condition
                condition = self._extract_loop_condition(loop, code)
                if condition:
                    invariant = self._create_invariant(
                        InvariantType.LOOP_INVARIANT,
                        condition,
                        loop,
                        code,
                        {
                            'loop_type': loop['type'],
                            'iteration_variable': loop.get('variable'),
                            'bounds': loop.get('bounds')
                        }
                    )
                    invariants.append(invariant)
                
                # Extract loop body invariants
                body_invariants = self._extract_loop_body_invariants(loop, code)
                invariants.extend(body_invariants)
        
        return invariants
    
    def _find_loops(self, node: Any, code: str, loops: List[Dict] = None) -> List[Dict]:
        """Find all loops in the AST."""
        if loops is None:
            loops = []
        
        loop_types = {
            'while_statement', 'for_statement', 'do_statement',
            'for_in_statement', 'for_of_statement', 'foreach_statement'
        }
        
        if hasattr(node, 'type') and node.type in loop_types:
            loop_info = {
                'node': node,
                'type': node.type,
                'start': node.start_byte,
                'end': node.end_byte,
                'text': code[node.start_byte:node.end_byte]
            }
            
            # Extract loop variable and bounds if possible
            if node.type in ['for_statement', 'for_in_statement']:
                loop_info['variable'] = self._extract_loop_variable(node, code)
                loop_info['bounds'] = self._extract_loop_bounds(node, code)
            
            loops.append(loop_info)
        
        # Recurse through children
        if hasattr(node, 'children'):
            for child in node.children:
                self._find_loops(child, code, loops)
        
        return loops
    
    def _extract_loop_condition(self, loop: Dict, code: str) -> Optional[str]:
        """Extract the condition from a loop."""
        loop_text = loop['text']
        loop_type = loop['type']
        
        if loop_type == 'while_statement':
            match = re.search(r'while\s*\(([^)]+)\)', loop_text)
            if match:
                return match.group(1).strip()
        
        elif loop_type == 'for_statement':
            match = re.search(r'for\s*\([^;]*;([^;]+);[^)]*\)', loop_text)
            if match:
                return match.group(1).strip()
        
        elif loop_type == 'do_statement':
            match = re.search(r'while\s*\(([^)]+)\)\s*;?\s*$', loop_text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_loop_variable(self, node: Any, code: str) -> Optional[str]:
        """Extract loop iteration variable."""
        node_text = code[node.start_byte:node.end_byte]
        
        # For loop patterns
        patterns = [
            r'for\s*\(\s*(?:int|var|let|const)?\s*(\w+)\s*=',  # for (int i = ...)
            r'for\s+(\w+)\s+in\s+',  # for i in ...
            r'for\s*\(\s*(\w+)\s+of\s+',  # for (item of ...)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, node_text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_loop_bounds(self, node: Any, code: str) -> Optional[Dict[str, str]]:
        """Extract loop bounds."""
        node_text = code[node.start_byte:node.end_byte]
        bounds = {}
        
        # For loop with numeric bounds
        match = re.search(r'for\s*\([^=]+=\s*([^;]+);[^<>=]*([<>=]+)\s*([^;]+)', node_text)
        if match:
            bounds['start'] = match.group(1).strip()
            bounds['operator'] = match.group(2)
            bounds['end'] = match.group(3).strip()
        
        # Python range pattern
        match = re.search(r'range\s*\(([^,)]+)(?:,\s*([^,)]+))?', node_text)
        if match:
            if match.group(2):
                bounds['start'] = match.group(1).strip()
                bounds['end'] = match.group(2).strip()
            else:
                bounds['start'] = '0'
                bounds['end'] = match.group(1).strip()
        
        return bounds if bounds else None
    
    def _extract_loop_body_invariants(self, loop: Dict, code: str) -> List[Dict[str, Any]]:
        """Extract invariants from loop body."""
        invariants = []
        loop_body = self._extract_loop_body(loop, code)
        
        if loop_body:
            # Look for accumulator patterns
            accum_pattern = r'(\w+)\s*([+\-*/])=\s*(.+)'
            matches = re.findall(accum_pattern, loop_body)
            
            for var, op, expr in matches:
                invariant = self._create_invariant(
                    InvariantType.LOOP_INVARIANT,
                    f"{var} {op}= {expr}",
                    loop['node'],
                    code,
                    {
                        'accumulator': var,
                        'operation': op,
                        'expression': expr,
                        'invariant_subtype': 'accumulator'
                    }
                )
                invariants.append(invariant)
        
        return invariants
    
    def _extract_loop_body(self, loop: Dict, code: str) -> Optional[str]:
        """Extract the body of a loop."""
        loop_text = loop['text']
        
        # Find the opening brace or colon
        start_markers = ['{', ':']
        body_start = -1
        
        for marker in start_markers:
            pos = loop_text.find(marker)
            if pos > 0:
                body_start = pos + 1
                break
        
        if body_start > 0:
            # Extract body based on language
            if ':' in loop_text and '{' not in loop_text:
                # Python-style
                lines = loop_text[body_start:].split('\n')
                # Get indented lines
                if lines:
                    base_indent = len(lines[0]) - len(lines[0].lstrip())
                    body_lines = []
                    for line in lines:
                        if line.strip() and (len(line) - len(line.lstrip())) > base_indent:
                            body_lines.append(line)
                        elif line.strip():
                            break
                    return '\n'.join(body_lines)
            else:
                # Brace-style
                brace_count = 1
                i = body_start
                while i < len(loop_text) and brace_count > 0:
                    if loop_text[i] == '{':
                        brace_count += 1
                    elif loop_text[i] == '}':
                        brace_count -= 1
                    i += 1
                return loop_text[body_start:i-1]
        
        return None
    
    def _extract_mathematical_relations(self, ast_tree: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract mathematical relations and equations."""
        invariants = []
        
        # Mathematical relation patterns
        math_patterns = [
            # Algebraic relations
            (r'(\w+)\s*=\s*([^;,\n]+[+\-*/][^;,\n]+)', 'algebraic_equation'),
            # Modular arithmetic
            (r'(\w+)\s*%\s*(\w+)\s*==\s*(\d+)', 'modular_relation'),
            # Power relations
            (r'(\w+)\s*\*\*\s*(\w+)', 'power_relation'),
            # Factorial patterns
            (r'(\w+)\s*\*\s*\(?\s*\1\s*-\s*1\s*\)?', 'factorial_relation'),
            # Fibonacci patterns
            (r'(\w+)\s*=\s*\w+\[[^\]]*-\s*1\s*\]\s*\+\s*\w+\[[^\]]*-\s*2\s*\]', 'fibonacci_relation'),
        ]
        
        for pattern, relation_type in math_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                expression = match.group(0)
                
                # Skip if it's an import or similar
                if self._is_import_statement(expression, code):
                    continue
                
                invariant = self._create_invariant(
                    InvariantType.MATHEMATICAL_RELATION,
                    expression,
                    None,
                    code,
                    {
                        'relation_type': relation_type,
                        'variables': self._extract_variables(expression)
                    }
                )
                invariants.append(invariant)
        
        return invariants
    
    def _extract_comparison_invariants(self, ast_tree: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract comparison-based invariants."""
        invariants = []
        
        # Comparison patterns
        comp_patterns = [
            # Range checks
            (r'(\w+)\s*>=?\s*(\w+)\s*and\s*\1\s*<=?\s*(\w+)', 'range_check'),
            # Equality/inequality
            (r'(\w+)\s*([!=]=)\s*([^&|;,\n]+)', 'equality_check'),
            # Ordering
            (r'(\w+)\s*([<>]=?)\s*([^&|;,\n]+)', 'ordering_check'),
        ]
        
        for pattern, check_type in comp_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                expression = match.group(0)
                
                invariant = self._create_invariant(
                    InvariantType.COMPARISON_INVARIANT,
                    expression,
                    None,
                    code,
                    {
                        'check_type': check_type,
                        'operator': match.group(2) if match.lastindex >= 2 else None
                    }
                )
                invariants.append(invariant)
        
        return invariants
    
    def _extract_recursion_invariants(self, ast_tree: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract recursion-related invariants."""
        invariants = []
        
        # Find function definitions
        func_pattern = r'(?:def|function|func)\s+(\w+)\s*\([^)]*\)'
        functions = re.finditer(func_pattern, code)
        
        for func_match in functions:
            func_name = func_match.group(1)
            func_start = func_match.start()
            
            # Find the function body
            func_body = self._extract_function_body(code[func_start:])
            
            if func_body and func_name in func_body:
                # It's recursive - look for base cases
                base_patterns = [
                    rf'if\s+[^:]+:\s*return\s+(?!.*{func_name})',
                    rf'if\s+[^{{]+\{{\s*return\s+(?!.*{func_name})',
                    r'if\s+\w+\s*[<>=]+\s*\d+\s*:\s*return',
                ]
                
                for pattern in base_patterns:
                    base_matches = re.finditer(pattern, func_body)
                    for base_match in base_matches:
                        base_case = base_match.group(0)
                        
                        invariant = self._create_invariant(
                            InvariantType.RECURSION_INVARIANT,
                            base_case,
                            None,
                            code,
                            {
                                'function_name': func_name,
                                'invariant_subtype': 'base_case'
                            }
                        )
                        invariants.append(invariant)
                
                # Look for recursive calls with decreasing arguments
                rec_pattern = rf'{func_name}\s*\([^)]*[-+]\s*\d+[^)]*\)'
                rec_matches = re.finditer(rec_pattern, func_body)
                
                for rec_match in rec_matches:
                    rec_call = rec_match.group(0)
                    
                    invariant = self._create_invariant(
                        InvariantType.RECURSION_INVARIANT,
                        rec_call,
                        None,
                        code,
                        {
                            'function_name': func_name,
                            'invariant_subtype': 'recursive_call',
                            'decreasing': '-' in rec_call
                        }
                    )
                    invariants.append(invariant)
        
        return invariants
    
    def _extract_function_body(self, code: str) -> Optional[str]:
        """Extract function body from code."""
        # Python style
        if ':' in code[:50]:
            lines = code.split('\n')
            if lines:
                # Find indentation level
                for i, line in enumerate(lines[1:], 1):
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        # Extract all lines with this indent or more
                        body_lines = []
                        for j in range(i, len(lines)):
                            if lines[j].strip():
                                if len(lines[j]) - len(lines[j].lstrip()) >= indent:
                                    body_lines.append(lines[j])
                                else:
                                    break
                        return '\n'.join(body_lines)
        
        # Brace style
        elif '{' in code[:50]:
            start = code.find('{')
            if start >= 0:
                brace_count = 1
                i = start + 1
                while i < len(code) and brace_count > 0:
                    if code[i] == '{':
                        brace_count += 1
                    elif code[i] == '}':
                        brace_count -= 1
                    i += 1
                return code[start+1:i-1]
        
        return None
    
    def _extract_boundary_conditions(self, ast_tree: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract boundary condition checks."""
        invariants = []
        
        # Boundary patterns
        boundary_patterns = [
            # Array bounds
            (r'if\s+(\w+)\s*>=?\s*0\s*and\s*\1\s*<\s*len\(([^)]+)\)', 'array_bounds'),
            (r'if\s+(\w+)\s*<\s*(\w+)\.length', 'array_bounds'),
            # Null/None checks
            (r'if\s+(\w+)\s*(?:is\s+not\s+None|!=\s*None|!=\s*null)', 'null_check'),
            # Empty checks
            (r'if\s+(?:not\s+)?(\w+)', 'empty_check'),
            # Size checks
            (r'if\s+len\(([^)]+)\)\s*([<>=]+)\s*(\d+)', 'size_check'),
        ]
        
        for pattern, condition_type in boundary_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                expression = match.group(0)
                
                invariant = self._create_invariant(
                    InvariantType.BOUNDARY_CONDITION,
                    expression,
                    None,
                    code,
                    {
                        'condition_type': condition_type,
                        'variable': match.group(1) if match.lastindex >= 1 else None
                    }
                )
                invariants.append(invariant)
        
        return invariants
    
    def _extract_assignment_invariants(self, ast_tree: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract assignment-based invariants."""
        invariants = []
        
        # Assignment patterns that maintain invariants
        assignment_patterns = [
            # Swap operations
            (r'(\w+)\s*,\s*(\w+)\s*=\s*\2\s*,\s*\1', 'swap_invariant'),
            # Increment/decrement
            (r'(\w+)\s*([+\-*/])=\s*(\d+)', 'accumulator_invariant'),
            # State transitions
            (r'(\w+)\s*=\s*\1\s*([+\-*/&|^])\s*(.+)', 'state_transition'),
        ]
        
        for pattern, inv_type in assignment_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                expression = match.group(0)
                
                invariant = self._create_invariant(
                    InvariantType.ASSIGNMENT_INVARIANT,
                    expression,
                    None,
                    code,
                    {
                        'invariant_subtype': inv_type,
                        'variable': match.group(1) if match.lastindex >= 1 else None,
                        'operation': match.group(2) if match.lastindex >= 2 else None
                    }
                )
                invariants.append(invariant)
        
        return invariants
    
    def _create_invariant(self, inv_type: InvariantType, expression: str, 
                         node: Any, code: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized invariant entry."""
        # Generate unique ID
        inv_id = f"inv_{uuid.uuid4().hex[:8]}"
        
        # Calculate position and lines
        lines = [1, 1]
        if node and hasattr(node, 'start_byte'):
            lines_before = code[:node.start_byte].count('\n')
            lines_after = code[:node.end_byte].count('\n') if hasattr(node, 'end_byte') else lines_before
            lines = [lines_before + 1, lines_after + 1]
        elif expression in code:
            pos = code.find(expression)
            lines_before = code[:pos].count('\n')
            lines_after = code[:pos + len(expression)].count('\n')
            lines = [lines_before + 1, lines_after + 1]
        
        # Generate hashes
        expr_hash = hashlib.md5(expression.encode('utf-8')).hexdigest()[:16]
        
        # Extract operators and variables
        operators = self._extract_operators(expression)
        variables = self._extract_variables(expression)
        
        invariant = {
            'id': inv_id,
            'type': 'mathematical_expression',  # Keep consistent with original format
            'invariant_type': inv_type.value,  # Add the actual invariant type
            'confidence': self._calculate_confidence(inv_type, expression, metadata),
            'complexity_metric': len(operators) + len(variables),
            'lines': lines,
            'evidence': {
                'expression_type': metadata.get('invariant_subtype', 'mathematical_expression'),
                'invariant_type': inv_type.value,  # Add classified type here
                'expression': expression.strip(),
                'context': metadata.get('context', 'code_analysis'),
                'mathematical_operators': operators,
                'has_constants': bool(re.search(r'\b\d+\b', expression)),
                'has_variables': len(variables) > 0
            },
            'hashes': {
                'direct': {'md5': expr_hash},
                'semantic': {'expression_hash': expr_hash}
            },
            'transformation_resistance': {
                'variable_renaming': 0.9 if inv_type == InvariantType.COMPARISON_INVARIANT else 0.8,
                'constant_substitution': 0.6,
                'operator_precedence': 0.7,
                'expression_reordering': 0.5
            }
        }
        
        return invariant
    
    def _extract_operators(self, expression: str) -> List[str]:
        """Extract mathematical operators from expression."""
        operators = []
        for op in sorted(self.mathematical_operators, key=len, reverse=True):
            if op in expression:
                operators.append(op)
        return operators
    
    def _calculate_confidence(self, inv_type: InvariantType, expression: str, metadata: Dict) -> float:
        """Calculate confidence score for an invariant."""
        base_confidence = {
            InvariantType.LOOP_INVARIANT: 0.9,
            InvariantType.PRECONDITION: 0.85,
            InvariantType.POSTCONDITION: 0.85,
            InvariantType.MATHEMATICAL_RELATION: 0.8,
            InvariantType.COMPARISON_INVARIANT: 0.75,
            InvariantType.RECURSION_INVARIANT: 0.9,
            InvariantType.ASSIGNMENT_INVARIANT: 0.7,
            InvariantType.BOUNDARY_CONDITION: 0.8,
            InvariantType.CONSTRAINT_INVARIANT: 0.75,
            InvariantType.ALGEBRAIC_INVARIANT: 0.85,
            InvariantType.UNKNOWN: 0.5
        }
        
        confidence = base_confidence.get(inv_type, 0.5)
        
        # Adjust based on expression complexity
        if len(expression) > 50:
            confidence *= 0.9  # Slightly lower for complex expressions
        
        # Boost for specific patterns
        if metadata.get('invariant_subtype') in ['base_case', 'accumulator']:
            confidence *= 1.1
        
        return min(confidence, 1.0)
    
    def _extract_variables(self, expression: str) -> List[str]:
        """Extract variable names from an expression."""
        # Remove operators and numbers
        tokens = re.findall(r'\b[a-zA-Z_]\w*\b', expression)
        # Filter out keywords
        keywords = {'if', 'else', 'for', 'while', 'return', 'def', 'function', 'var', 'let', 'const'}
        variables = [t for t in tokens if t not in keywords]
        return list(set(variables))
    
    def _is_import_statement(self, expression: str, code: str) -> bool:
        """Check if expression is part of an import statement."""
        # Find the line containing the expression
        expr_pos = code.find(expression)
        if expr_pos < 0:
            return False
        
        # Get the full line
        line_start = code.rfind('\n', 0, expr_pos) + 1
        line_end = code.find('\n', expr_pos)
        if line_end < 0:
            line_end = len(code)
        
        full_line = code[line_start:line_end].strip()
        
        # Check for import patterns
        import_patterns = [
            r'^\s*import\s+',
            r'^\s*from\s+.*\s+import\s+',
            r'^\s*require\s*\(',
            r'^\s*#include\s*[<"]',
            r'^\s*using\s+',
        ]
        
        for pattern in import_patterns:
            if re.match(pattern, full_line):
                return True
        
        return False
    
    def _deduplicate_invariants(self, invariants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate invariants."""
        seen_hashes = set()
        unique_invariants = []
        
        for inv in invariants:
            # Get hash from hashes.direct.md5 or generate one
            inv_hash = None
            if 'hashes' in inv and 'direct' in inv['hashes'] and 'md5' in inv['hashes']['direct']:
                inv_hash = inv['hashes']['direct']['md5']
            elif 'evidence' in inv and 'expression' in inv['evidence']:
                inv_hash = hashlib.md5(inv['evidence']['expression'].encode()).hexdigest()[:16]
            else:
                inv_hash = str(uuid.uuid4())[:8]
            
            if inv_hash not in seen_hashes:
                seen_hashes.add(inv_hash)
                unique_invariants.append(inv)
        
        return unique_invariants