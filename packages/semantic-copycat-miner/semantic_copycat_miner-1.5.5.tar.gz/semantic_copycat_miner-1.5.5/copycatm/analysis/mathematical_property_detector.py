"""
Mathematical property detector for identifying mathematical patterns and properties.

This module detects mathematical properties like commutativity, associativity,
distributivity, and other mathematical relationships in code, generating hashes
for each detected property.
"""

import logging
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum

from ..hashing import DirectHasher, SemanticHasher

logger = logging.getLogger(__name__)


class MathematicalProperty(Enum):
    """Types of mathematical properties."""
    COMMUTATIVE = "commutative"
    ASSOCIATIVE = "associative"
    DISTRIBUTIVE = "distributive"
    IDENTITY = "identity"
    INVERSE = "inverse"
    IDEMPOTENT = "idempotent"
    CLOSURE = "closure"
    TRANSITIVE = "transitive"
    SYMMETRIC = "symmetric"
    REFLEXIVE = "reflexive"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    POLYNOMIAL = "polynomial"
    RECURSIVE = "recursive"
    ITERATIVE = "iterative"


class MathematicalPropertyDetector:
    """
    Detects mathematical properties in code for enhanced similarity detection.
    
    Mathematical properties are important for:
    - Algorithm classification
    - Optimization detection
    - Mathematical proof verification
    - Code equivalence checking
    """
    
    def __init__(self):
        """Initialize mathematical property detector."""
        self.direct_hasher = DirectHasher()
        self.semantic_hasher = SemanticHasher()
        
        # Common mathematical operations
        self.math_operators = {
            '+': 'addition',
            '-': 'subtraction',
            '*': 'multiplication',
            '/': 'division',
            '//': 'integer_division',
            '%': 'modulo',
            '**': 'exponentiation',
            '^': 'bitwise_xor',
            '&': 'bitwise_and',
            '|': 'bitwise_or',
            '<<': 'left_shift',
            '>>': 'right_shift'
        }
        
        # Mathematical function patterns
        self.math_functions = {
            'sqrt': 'square_root',
            'pow': 'power',
            'exp': 'exponential',
            'log': 'logarithm',
            'sin': 'sine',
            'cos': 'cosine',
            'tan': 'tangent',
            'abs': 'absolute',
            'min': 'minimum',
            'max': 'maximum',
            'gcd': 'greatest_common_divisor',
            'lcm': 'least_common_multiple',
            'factorial': 'factorial',
            'fibonacci': 'fibonacci_sequence'
        }
    
    def detect_properties(self, ast_tree: Any, language: str, 
                         invariants: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Detect mathematical properties in AST.
        
        Args:
            ast_tree: AST tree from parser
            language: Programming language
            invariants: Optional mathematical invariants already extracted
            
        Returns:
            List of detected mathematical properties with hashes
        """
        properties = []
        
        if not hasattr(ast_tree, 'root'):
            logger.debug("AST tree has no root")
            return properties
        
        # Extract expressions from AST
        expressions = self._extract_mathematical_expressions(ast_tree.root, language)
        
        # Analyze expressions for properties
        for expr in expressions:
            detected_props = self._analyze_expression_properties(expr, language)
            properties.extend(detected_props)
        
        # Analyze invariants if provided
        if invariants:
            invariant_props = self._analyze_invariant_properties(invariants)
            properties.extend(invariant_props)
        
        # Generate hashes for each property
        for prop in properties:
            self._generate_property_hashes(prop)
        
        # Deduplicate properties
        properties = self._deduplicate_properties(properties)
        
        return properties
    
    def _extract_mathematical_expressions(self, node: Any, language: str, 
                                        expressions: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Extract mathematical expressions from AST."""
        if expressions is None:
            expressions = []
        
        if not node:
            return expressions
        
        # Check if this node is a mathematical expression
        node_type = getattr(node, 'type', '')
        
        # Common mathematical expression types
        math_expr_types = [
            'binary_expression', 'binary_operator', 'arithmetic_expression',
            'assignment', 'assignment_expression', 'augmented_assignment',
            'comparison', 'comparison_operator', 'relational_expression',
            'call', 'call_expression', 'function_call'
        ]
        
        if any(expr_type in node_type for expr_type in math_expr_types):
            expr_info = self._create_expression_info(node, language)
            if expr_info:
                expressions.append(expr_info)
        
        # Process children
        if hasattr(node, 'children'):
            for child in node.children:
                self._extract_mathematical_expressions(child, language, expressions)
        
        return expressions
    
    def _create_expression_info(self, node: Any, language: str) -> Optional[Dict[str, Any]]:
        """Create expression information from AST node."""
        node_text = getattr(node, 'text', '')
        if isinstance(node_text, bytes):
            text = node_text.decode('utf-8', errors='ignore')
        else:
            text = str(node_text) if node_text else ''
        
        if not text:
            return None
        
        # Extract operator if binary expression
        operator = self._extract_operator(node, text)
        
        # Extract operands
        operands = self._extract_operands(node)
        
        # Get location
        start_point = getattr(node, 'start_point', (0, 0))
        end_point = getattr(node, 'end_point', (0, 0))
        
        return {
            'type': getattr(node, 'type', 'unknown'),
            'text': text,
            'operator': operator,
            'operands': operands,
            'location': {
                'start_line': start_point[0] + 1,
                'end_line': end_point[0] + 1
            },
            'ast_node': node
        }
    
    def _extract_operator(self, node: Any, text: str) -> Optional[str]:
        """Extract operator from expression."""
        # Try to find operator child node
        if hasattr(node, 'children'):
            for child in node.children:
                child_type = getattr(child, 'type', '')
                if 'operator' in child_type or child_type in self.math_operators.values():
                    child_text = getattr(child, 'text', '')
                    if isinstance(child_text, bytes):
                        child_text = child_text.decode('utf-8', errors='ignore')
                    return str(child_text)
        
        # Fall back to regex extraction
        for op in self.math_operators:
            if op in text:
                return op
        
        return None
    
    def _extract_operands(self, node: Any) -> List[str]:
        """Extract operands from expression."""
        operands = []
        
        if not hasattr(node, 'children'):
            return operands
        
        for child in node.children:
            child_type = getattr(child, 'type', '')
            
            # Skip operator nodes
            if 'operator' in child_type:
                continue
            
            # Extract operand text
            child_text = getattr(child, 'text', '')
            if isinstance(child_text, bytes):
                child_text = child_text.decode('utf-8', errors='ignore')
            
            if child_text and str(child_text).strip():
                operands.append(str(child_text).strip())
        
        return operands
    
    def _analyze_expression_properties(self, expr: Dict[str, Any], 
                                     language: str) -> List[Dict[str, Any]]:
        """Analyze an expression for mathematical properties."""
        properties = []
        
        operator = expr.get('operator')
        operands = expr.get('operands', [])
        text = expr.get('text', '')
        
        if not operator:
            return properties
        
        # Check for commutative property
        if self._is_commutative_operation(operator, operands):
            properties.append(self._create_property(
                MathematicalProperty.COMMUTATIVE,
                expr,
                f"Commutative operation: {operator}",
                confidence=0.9
            ))
        
        # Check for associative property
        if self._is_associative_operation(operator, text):
            properties.append(self._create_property(
                MathematicalProperty.ASSOCIATIVE,
                expr,
                f"Associative operation: {operator}",
                confidence=0.85
            ))
        
        # Check for distributive property
        if self._is_distributive_pattern(text):
            properties.append(self._create_property(
                MathematicalProperty.DISTRIBUTIVE,
                expr,
                "Distributive pattern detected",
                confidence=0.8
            ))
        
        # Check for identity property
        if self._has_identity_element(operator, operands):
            properties.append(self._create_property(
                MathematicalProperty.IDENTITY,
                expr,
                f"Identity element for {operator}",
                confidence=0.9
            ))
        
        # Check for mathematical function properties
        function_props = self._check_function_properties(text)
        properties.extend(function_props)
        
        # Check for growth patterns
        growth_props = self._check_growth_patterns(expr)
        properties.extend(growth_props)
        
        return properties
    
    def _is_commutative_operation(self, operator: str, operands: List[str]) -> bool:
        """Check if operation is commutative."""
        commutative_ops = ['+', '*', '&', '|', '^', '==', '!=']
        return operator in commutative_ops and len(operands) >= 2
    
    def _is_associative_operation(self, operator: str, text: str) -> bool:
        """Check if operation is associative."""
        associative_ops = ['+', '*', '&', '|', '^']
        
        if operator not in associative_ops:
            return False
        
        # Check for patterns like (a + b) + c or a + (b + c)
        pattern = rf'\([^)]*\{operator}[^)]*\)[^{operator}]*\{operator}|\{operator}[^(]*\([^)]*\{operator}[^)]*\)'
        return bool(re.search(pattern, text))
    
    def _is_distributive_pattern(self, text: str) -> bool:
        """Check for distributive patterns."""
        # Patterns like a * (b + c) or (a + b) * c
        distributive_patterns = [
            r'\w+\s*\*\s*\([^)]*\+[^)]*\)',  # a * (b + c)
            r'\([^)]*\+[^)]*\)\s*\*\s*\w+',  # (a + b) * c
            r'\w+\s*\*\s*\([^)]*-[^)]*\)',   # a * (b - c)
            r'\([^)]*-[^)]*\)\s*\*\s*\w+'    # (a - b) * c
        ]
        
        return any(re.search(pattern, text) for pattern in distributive_patterns)
    
    def _has_identity_element(self, operator: str, operands: List[str]) -> bool:
        """Check if expression has identity element."""
        identity_elements = {
            '+': ['0', '0.0'],
            '*': ['1', '1.0'],
            '&': ['-1', '~0'],
            '|': ['0'],
            '^': ['0']
        }
        
        if operator in identity_elements:
            identities = identity_elements[operator]
            return any(op in identities for op in operands)
        
        return False
    
    def _check_function_properties(self, text: str) -> List[Dict[str, Any]]:
        """Check for mathematical function properties."""
        properties = []
        
        # Check for known mathematical functions
        for func_name, func_type in self.math_functions.items():
            if func_name in text:
                # Create a dummy expression for the function
                func_expr = {
                    'text': text,
                    'type': 'function_call',
                    'function': func_name
                }
                
                # Add properties based on function type
                if func_type in ['square_root', 'absolute']:
                    properties.append(self._create_property(
                        MathematicalProperty.IDEMPOTENT,
                        func_expr,
                        f"Idempotent function: {func_name}",
                        confidence=0.8
                    ))
                
                elif func_type in ['exponential', 'power']:
                    properties.append(self._create_property(
                        MathematicalProperty.EXPONENTIAL,
                        func_expr,
                        f"Exponential growth: {func_name}",
                        confidence=0.85
                    ))
                
                elif func_type == 'logarithm':
                    properties.append(self._create_property(
                        MathematicalProperty.LOGARITHMIC,
                        func_expr,
                        f"Logarithmic growth: {func_name}",
                        confidence=0.85
                    ))
        
        return properties
    
    def _check_growth_patterns(self, expr: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for growth pattern properties."""
        properties = []
        text = expr.get('text', '')
        
        # Linear patterns (ax + b)
        if re.search(r'\w+\s*\*\s*\w+\s*[+-]\s*\w+', text):
            properties.append(self._create_property(
                MathematicalProperty.LINEAR,
                expr,
                "Linear growth pattern",
                confidence=0.7
            ))
        
        # Polynomial patterns (x^n)
        if re.search(r'\w+\s*\*\*\s*\d+|\w+\s*\^\s*\d+', text):
            properties.append(self._create_property(
                MathematicalProperty.POLYNOMIAL,
                expr,
                "Polynomial growth pattern",
                confidence=0.75
            ))
        
        # Recursive patterns (function calls itself)
        if 'call' in expr.get('type', '') and self._is_recursive_call(expr):
            properties.append(self._create_property(
                MathematicalProperty.RECURSIVE,
                expr,
                "Recursive pattern",
                confidence=0.8
            ))
        
        return properties
    
    def _is_recursive_call(self, expr: Dict[str, Any]) -> bool:
        """Check if expression is a recursive call."""
        # This is a simplified check - would need function context for accuracy
        text = expr.get('text', '')
        
        # Look for common recursive patterns
        recursive_patterns = [
            r'return\s+\w+\([^)]*\w+\s*-\s*1[^)]*\)',  # f(n-1)
            r'return\s+\w+\([^)]*\w+\s*\+\s*1[^)]*\)',  # f(n+1)
            r'self\.\w+\(',  # self.function()
        ]
        
        return any(re.search(pattern, text) for pattern in recursive_patterns)
    
    def _analyze_invariant_properties(self, invariants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze mathematical invariants for properties."""
        properties = []
        
        for inv in invariants:
            inv_type = inv.get('invariant_type', '')
            evidence = inv.get('evidence', {})
            
            # Create expression-like structure for invariant
            expr = {
                'text': evidence.get('expression', ''),
                'type': inv_type,
                'location': {
                    'start_line': min(inv.get('lines', [0])),
                    'end_line': max(inv.get('lines', [0]))
                }
            }
            
            # Check invariant type
            if inv_type == 'loop_invariant':
                properties.append(self._create_property(
                    MathematicalProperty.ITERATIVE,
                    expr,
                    "Loop invariant property",
                    confidence=0.85
                ))
            
            elif inv_type == 'recursion_invariant':
                properties.append(self._create_property(
                    MathematicalProperty.RECURSIVE,
                    expr,
                    "Recursion invariant property",
                    confidence=0.9
                ))
            
            elif inv_type == 'mathematical_relation':
                # Analyze the mathematical relation
                relation_props = self._analyze_mathematical_relation(evidence)
                for prop in relation_props:
                    properties.append(self._create_property(
                        prop['type'],
                        expr,
                        prop['description'],
                        confidence=prop['confidence']
                    ))
        
        return properties
    
    def _analyze_mathematical_relation(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a mathematical relation for properties."""
        props = []
        expression = evidence.get('expression', '')
        operators = evidence.get('mathematical_operators', [])
        
        # Check for specific relation types
        if any(op in ['==', '='] for op in operators):
            # Equality relation - check for symmetry
            props.append({
                'type': MathematicalProperty.SYMMETRIC,
                'description': 'Symmetric equality relation',
                'confidence': 0.8
            })
        
        if any(op in ['<', '>', '<=', '>='] for op in operators):
            # Order relation - check for transitivity
            props.append({
                'type': MathematicalProperty.TRANSITIVE,
                'description': 'Transitive ordering relation',
                'confidence': 0.75
            })
        
        return props
    
    def _create_property(self, prop_type: MathematicalProperty, 
                        expression: Dict[str, Any],
                        description: str,
                        confidence: float = 0.8) -> Dict[str, Any]:
        """Create a mathematical property entry."""
        return {
            'property_type': prop_type.value,
            'description': description,
            'confidence': confidence,
            'expression': {
                'text': expression.get('text', ''),
                'type': expression.get('type', ''),
                'location': expression.get('location', {})
            },
            'evidence': {
                'operator': expression.get('operator'),
                'operands': expression.get('operands', []),
                'pattern': self._extract_pattern(expression)
            }
        }
    
    def _extract_pattern(self, expression: Dict[str, Any]) -> str:
        """Extract a normalized pattern from expression."""
        text = expression.get('text', '')
        
        # Replace variables with generic placeholders
        pattern = re.sub(r'\b[a-zA-Z_]\w*\b', 'VAR', text)
        
        # Replace numbers with generic placeholders
        pattern = re.sub(r'\b\d+\.?\d*\b', 'NUM', pattern)
        
        # Normalize whitespace
        pattern = ' '.join(pattern.split())
        
        return pattern
    
    def _generate_property_hashes(self, property_entry: Dict[str, Any]) -> None:
        """Generate hashes for a mathematical property."""
        # Create canonical representation
        canonical = f"{property_entry['property_type']}:{property_entry['evidence']['pattern']}"
        
        # Generate hashes
        property_entry['hashes'] = {
            'property_hash': hashlib.sha256(canonical.encode()).hexdigest()[:16],
            'pattern_hash': hashlib.md5(property_entry['evidence']['pattern'].encode()).hexdigest()[:16],
            'semantic_hash': self.semantic_hasher.generate_simhash(canonical)
        }
        
        # Add expression hash
        expr_text = property_entry['expression']['text']
        if expr_text:
            property_entry['hashes']['expression_hash'] = hashlib.sha256(expr_text.encode()).hexdigest()[:16]
    
    def _deduplicate_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate properties based on hashes."""
        seen_hashes = set()
        unique_properties = []
        
        for prop in properties:
            prop_hash = prop['hashes']['property_hash']
            if prop_hash not in seen_hashes:
                seen_hashes.add(prop_hash)
                unique_properties.append(prop)
        
        return unique_properties
    
    def generate_composite_hash(self, properties: List[Dict[str, Any]]) -> str:
        """Generate a composite hash for all mathematical properties."""
        if not properties:
            return hashlib.sha256(b'no_properties').hexdigest()[:16]
        
        # Sort properties by type for consistent hashing
        sorted_props = sorted(properties, key=lambda p: p['property_type'])
        
        # Combine property hashes
        combined = ''.join(p['hashes']['property_hash'] for p in sorted_props)
        
        return hashlib.sha256(combined.encode()).hexdigest()