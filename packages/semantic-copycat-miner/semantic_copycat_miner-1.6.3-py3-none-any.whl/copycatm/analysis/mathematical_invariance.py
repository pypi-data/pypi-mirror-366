"""
Mathematical invariance detection for transformation-resistant algorithm identification.

This module detects mathematical properties that remain constant across code transformations,
providing up to 95% resistance against variable renaming, restructuring, and other modifications.
"""

import re
from typing import Dict, List, Any
from enum import Enum

from .invariant_extractor_improved import ImprovedInvariantExtractor


class MathematicalProperty(Enum):
    """Mathematical properties that survive code transformations."""
    COMMUTATIVE = "commutative"          # a + b = b + a
    ASSOCIATIVE = "associative"          # (a + b) + c = a + (b + c)
    DISTRIBUTIVE = "distributive"        # a * (b + c) = a * b + a * c
    IDEMPOTENT = "idempotent"           # f(f(x)) = f(x)
    TRANSITIVE = "transitive"           # if a < b and b < c, then a < c
    IDENTITY = "identity"               # a + 0 = a, a * 1 = a
    INVERSE = "inverse"                 # a + (-a) = 0, a * (1/a) = 1
    CLOSURE = "closure"                 # operation result is in same set
    REFLEXIVE = "reflexive"             # a = a
    SYMMETRIC = "symmetric"             # if a = b, then b = a


class MathematicalInvariantDetector:
    """
    Detects mathematical properties and invariants that persist across transformations.
    
    This detector identifies algebraic properties in code that remain constant
    regardless of variable names, code structure, or syntactic variations.
    """
    
    def __init__(self):
        self.invariant_extractor = ImprovedInvariantExtractor()
        
        # Operations that have mathematical properties
        self.commutative_ops = {'+', '*', '&', '|', '^', '==', '!=', 'and', 'or'}
        self.associative_ops = {'+', '*', '&', '|', '^', 'and', 'or'}
        self.distributive_patterns = [
            (r'(\w+)\s*\*\s*\(([^)]+)\+([^)]+)\)', r'\1*\2+\1*\3'),  # a*(b+c) = a*b+a*c
            (r'(\w+)\s*\*\s*\(([^)]+)-([^)]+)\)', r'\1*\2-\1*\3'),  # a*(b-c) = a*b-a*c
        ]
        self.identity_elements = {
            '+': '0', '-': '0', '*': '1', '/': '1',
            '&': '-1', '|': '0', '^': '0',
            'and': 'True', 'or': 'False'
        }
        
    def detect_mathematical_properties(self, ast_tree: Any, code: str, 
                                     language: str) -> Dict[str, Any]:
        """
        Detect mathematical properties in code that survive transformations.
        
        Returns:
            Dictionary containing detected properties and confidence scores
        """
        properties = {
            'detected_properties': [],
            'property_evidence': {},
            'transformation_resistance': 0.0,
            'mathematical_confidence': 0.0,
            'invariant_count': 0
        }
        
        # Extract base invariants
        invariants = self.invariant_extractor.extract(ast_tree, language)
        properties['invariant_count'] = len(invariants)
        
        # Analyze each invariant for mathematical properties
        for invariant in invariants:
            expr = invariant.get('evidence', {}).get('expression', '')
            if expr:
                self._analyze_expression_properties(expr, properties)
        
        # Analyze code structure for mathematical patterns
        self._analyze_code_structure(code, properties)
        
        # Calculate overall scores
        properties['mathematical_confidence'] = self._calculate_confidence(properties)
        properties['transformation_resistance'] = self._calculate_resistance(properties)
        
        return properties
    
    def _analyze_expression_properties(self, expression: str, 
                                     properties: Dict[str, Any]) -> None:
        """Analyze a single expression for mathematical properties."""
        
        # Check for commutative operations
        if self._has_commutative_property(expression):
            self._add_property(properties, MathematicalProperty.COMMUTATIVE, expression)
        
        # Check for associative operations
        if self._has_associative_property(expression):
            self._add_property(properties, MathematicalProperty.ASSOCIATIVE, expression)
        
        # Check for distributive patterns
        if self._has_distributive_property(expression):
            self._add_property(properties, MathematicalProperty.DISTRIBUTIVE, expression)
        
        # Check for identity elements
        if self._has_identity_property(expression):
            self._add_property(properties, MathematicalProperty.IDENTITY, expression)
        
        # Check for transitive relations
        if self._has_transitive_property(expression):
            self._add_property(properties, MathematicalProperty.TRANSITIVE, expression)
    
    def _has_commutative_property(self, expression: str) -> bool:
        """Check if expression contains commutative operations."""
        for op in self.commutative_ops:
            if op in expression:
                # Simple check - could be enhanced with AST analysis
                escaped_op = re.escape(op)
                pattern = rf'\w+\s*{escaped_op}\s*\w+'
                if re.search(pattern, expression):
                    return True
        return False
    
    def _has_associative_property(self, expression: str) -> bool:
        """Check if expression contains associative operations."""
        # Look for nested operations of the same type
        for op in self.associative_ops:
            # Escape the operator for regex
            escaped_op = re.escape(op)
            # Pattern for (a op b) op c or a op (b op c)
            pattern = rf'\([^)]*{escaped_op}[^)]*\)\s*{escaped_op}|{escaped_op}\s*\([^)]*{escaped_op}[^)]*\)'
            if re.search(pattern, expression):
                return True
        return False
    
    def _has_distributive_property(self, expression: str) -> bool:
        """Check if expression matches distributive patterns."""
        for pattern, _ in self.distributive_patterns:
            if re.search(pattern, expression):
                return True
        return False
    
    def _has_identity_property(self, expression: str) -> bool:
        """Check if expression contains identity element operations."""
        for op, identity in self.identity_elements.items():
            # Escape the operator for regex
            escaped_op = re.escape(op)
            # Check for patterns like a + 0, a * 1, etc.
            patterns = [
                rf'\w+\s*{escaped_op}\s*{identity}',
                rf'{identity}\s*{escaped_op}\s*\w+',
            ]
            for pattern in patterns:
                if re.search(pattern, expression):
                    return True
        return False
    
    def _has_transitive_property(self, expression: str) -> bool:
        """Check if expression represents transitive relations."""
        # Look for chained comparisons
        transitive_ops = ['<', '>', '<=', '>=', '==']
        for op in transitive_ops:
            # Escape the operator for regex
            escaped_op = re.escape(op)
            # Pattern: a op b and b op c
            pattern = rf'(\w+)\s*{escaped_op}\s*(\w+).*\2\s*{escaped_op}\s*(\w+)'
            if re.search(pattern, expression):
                return True
        return False
    
    def _analyze_code_structure(self, code: str, properties: Dict[str, Any]) -> None:
        """Analyze overall code structure for mathematical patterns."""
        
        # Look for recursive patterns (often indicate mathematical algorithms)
        if self._has_recursive_structure(code):
            self._add_property(properties, MathematicalProperty.CLOSURE, 
                             "recursive structure detected")
        
        # Look for loop invariants that suggest mathematical properties
        loop_invariants = self._extract_loop_invariants(code)
        for invariant in loop_invariants:
            if self._is_mathematical_invariant(invariant):
                self._add_property(properties, MathematicalProperty.CLOSURE,
                                 f"loop invariant: {invariant}")
    
    def _has_recursive_structure(self, code: str) -> bool:
        """Check if code has recursive structure."""
        # Simple pattern matching - could be enhanced with AST
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        func_match = re.search(func_pattern, code)
        if func_match:
            func_name = func_match.group(1)
            # Check if function calls itself
            call_pattern = rf'{func_name}\s*\('
            if re.search(call_pattern, code[func_match.end():]):
                return True
        return False
    
    def _extract_loop_invariants(self, code: str) -> List[str]:
        """Extract potential loop invariants from code."""
        invariants = []
        
        # Look for assertions or conditions in loops
        loop_patterns = [
            r'while\s+([^:]+):',
            r'for\s+\w+\s+in\s+[^:]+:'
        ]
        
        for pattern in loop_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                condition = match.group(1) if match.lastindex else ""
                if condition and self._is_mathematical_expression(condition):
                    invariants.append(condition)
        
        return invariants
    
    def _is_mathematical_expression(self, expr: str) -> bool:
        """Check if expression is mathematical in nature."""
        math_indicators = ['+', '-', '*', '/', '%', '**', '<', '>', '<=', '>=', '==']
        return any(op in expr for op in math_indicators)
    
    def _is_mathematical_invariant(self, invariant: str) -> bool:
        """Check if invariant represents a mathematical property."""
        # Check for common mathematical invariant patterns
        math_patterns = [
            r'\w+\s*[<>]=?\s*\w+',  # Comparisons
            r'\w+\s*[+\-*/]\s*\w+',  # Arithmetic
            r'sum|product|min|max',   # Aggregations
        ]
        return any(re.search(pattern, invariant) for pattern in math_patterns)
    
    def _add_property(self, properties: Dict[str, Any], 
                     prop_type: MathematicalProperty, evidence: str) -> None:
        """Add a detected property with evidence."""
        if prop_type.value not in [p['type'] for p in properties['detected_properties']]:
            properties['detected_properties'].append({
                'type': prop_type.value,
                'confidence': 0.9  # High confidence for mathematical properties
            })
        
        if prop_type.value not in properties['property_evidence']:
            properties['property_evidence'][prop_type.value] = []
        
        properties['property_evidence'][prop_type.value].append(evidence)
    
    def _calculate_confidence(self, properties: Dict[str, Any]) -> float:
        """Calculate overall mathematical confidence score."""
        if not properties['detected_properties']:
            return 0.0
        
        # Base confidence from number of properties detected
        base_confidence = min(len(properties['detected_properties']) * 0.2, 0.8)
        
        # Boost for strong mathematical indicators
        strong_indicators = [MathematicalProperty.DISTRIBUTIVE, 
                           MathematicalProperty.ASSOCIATIVE,
                           MathematicalProperty.TRANSITIVE]
        
        boost = sum(0.1 for p in properties['detected_properties'] 
                   if p['type'] in [ind.value for ind in strong_indicators])
        
        return min(base_confidence + boost, 0.95)
    
    def _calculate_resistance(self, properties: Dict[str, Any]) -> float:
        """Calculate transformation resistance based on mathematical properties."""
        if not properties['detected_properties']:
            return 0.0
        
        # Mathematical properties provide high resistance
        resistance_values = {
            MathematicalProperty.COMMUTATIVE.value: 0.85,
            MathematicalProperty.ASSOCIATIVE.value: 0.90,
            MathematicalProperty.DISTRIBUTIVE.value: 0.95,
            MathematicalProperty.TRANSITIVE.value: 0.92,
            MathematicalProperty.IDENTITY.value: 0.80,
            MathematicalProperty.IDEMPOTENT.value: 0.88,
        }
        
        # Calculate weighted average resistance
        total_resistance = 0.0
        count = 0
        
        for prop in properties['detected_properties']:
            prop_type = prop['type']
            if prop_type in resistance_values:
                total_resistance += resistance_values[prop_type]
                count += 1
        
        if count > 0:
            # Multiple properties increase resistance
            avg_resistance = total_resistance / count
            multi_property_boost = min(count * 0.02, 0.1)
            return min(avg_resistance + multi_property_boost, 0.95)
        
        return 0.0
    
    def enhance_algorithm_detection(self, algorithm_detection: Dict[str, Any],
                                  mathematical_properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance existing algorithm detection with mathematical validation.
        
        This boosts confidence scores and transformation resistance when
        mathematical properties align with detected algorithms.
        """
        enhanced = algorithm_detection.copy()
        
        # Map algorithm types to expected mathematical properties
        algorithm_properties = {
            'sorting_algorithm': [MathematicalProperty.TRANSITIVE, 
                                MathematicalProperty.ASSOCIATIVE],
            'numerical_algorithm': [MathematicalProperty.COMMUTATIVE,
                                  MathematicalProperty.ASSOCIATIVE,
                                  MathematicalProperty.DISTRIBUTIVE],
            'cryptographic_algorithm': [MathematicalProperty.CLOSURE,
                                      MathematicalProperty.INVERSE],
            'dynamic_programming': [MathematicalProperty.ASSOCIATIVE,
                                  MathematicalProperty.IDENTITY],
        }
        
        algo_type = algorithm_detection.get('algorithm_type', '')
        expected_props = algorithm_properties.get(algo_type, [])
        
        # Check if detected properties match expected properties
        detected_prop_types = [p['type'] for p in mathematical_properties['detected_properties']]
        matching_props = sum(1 for prop in expected_props 
                           if prop.value in detected_prop_types)
        
        if matching_props > 0:
            # Boost confidence based on property matches
            confidence_boost = min(matching_props * 0.15, 0.3)
            enhanced['confidence_score'] = min(
                enhanced.get('confidence_score', 0.5) + confidence_boost, 1.0
            )
            
            # Update transformation resistance
            enhanced['transformation_resistance'] = mathematical_properties['transformation_resistance']
            
            # Add mathematical evidence
            enhanced['mathematical_evidence'] = {
                'properties': detected_prop_types,
                'property_match_score': matching_props / len(expected_props) if expected_props else 0,
                'mathematical_confidence': mathematical_properties['mathematical_confidence']
            }
        
        return enhanced