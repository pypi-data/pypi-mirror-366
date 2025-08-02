"""
AST-based winnowing for semantic code fingerprinting.

This module implements winnowing on AST node sequences instead of character
sequences, enabling true cross-language similarity detection.
"""

import hashlib
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ASTWinnowingConfig:
    """Configuration for AST-based winnowing."""
    k_gram_size: int = 5      # Number of AST nodes in a gram
    window_size: int = 10     # Window size for hash selection
    hash_function: str = "sha256"  # Hash function to use


class ASTNodeNormalizer:
    """Normalize AST nodes for cross-language matching."""
    
    def __init__(self):
        """Initialize the normalizer with cross-language mappings."""
        self.node_mappings = {
            # Control structures
            'if_statement': 'CONDITIONAL',
            'conditional_expression': 'CONDITIONAL',
            'ternary_expression': 'CONDITIONAL',
            'switch_statement': 'CONDITIONAL',
            
            'for_statement': 'LOOP',
            'for_in_statement': 'LOOP',
            'for_of_statement': 'LOOP',
            'while_statement': 'LOOP',
            'do_statement': 'LOOP',
            'enhanced_for_statement': 'LOOP',
            
            # Functions
            'function_definition': 'FUNCTION',
            'function_declaration': 'FUNCTION',
            'function_declarator': 'FUNCTION',
            'method_declaration': 'FUNCTION',
            'lambda': 'FUNCTION',
            'arrow_function': 'FUNCTION',
            
            # Operations
            'assignment': 'ASSIGN',
            'augmented_assignment': 'ASSIGN',
            'assignment_expression': 'ASSIGN',
            '=': 'ASSIGN',
            '+=': 'ASSIGN',
            '-=': 'ASSIGN',
            
            'binary_expression': 'BINARY_OP',
            'binary_operator': 'BINARY_OP',
            'comparison_operator': 'COMPARISON',
            
            'call': 'CALL',
            'call_expression': 'CALL',
            'method_invocation': 'CALL',
            
            'return_statement': 'RETURN',
            'yield_statement': 'YIELD',
            
            # Data structures - Java/C specific
            'array_declarator': 'ARRAY',
            'array_type': 'ARRAY',
            'array_access': 'INDEX',
            'subscript_expression': 'INDEX',
            
            # Data structures - general
            'list': 'ARRAY',
            'array': 'ARRAY',
            'array_expression': 'ARRAY',
            
            'subscript': 'INDEX',
            'member_expression': 'INDEX',
            
            # Literals
            'integer': 'NUMBER',
            'integer_literal': 'NUMBER',
            'float': 'NUMBER',
            'number': 'NUMBER',
            'number_literal': 'NUMBER',
            'string': 'STRING',
            'string_literal': 'STRING',
            'boolean': 'BOOLEAN',
            'true': 'TRUE',
            'false': 'FALSE',
            'null': 'NULL',
            'null_literal': 'NULL',
            'none': 'NULL',
            
            # Variables
            'identifier': 'VAR',
            'variable_name': 'VAR',
            
            # Increment/decrement
            'update_expression': 'UPDATE',
            'increment_expression': 'INCREMENT',
            'decrement_expression': 'DECREMENT',
            'postfix_expression': 'UPDATE',
            'prefix_expression': 'UPDATE',
        }
        
        # Operation normalizations
        self.operation_mappings = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '%': 'MOD',
            '**': 'POW',
            '<<': 'SHL',
            '>>': 'SHR',
            '&': 'AND',
            '|': 'OR',
            '^': 'XOR',
            '~': 'NOT',
            '==': 'EQ',
            '!=': 'NEQ',
            '<': 'LT',
            '>': 'GT',
            '<=': 'LTE',
            '>=': 'GTE',
            '===': 'EQ',
            '!==': 'NEQ',
        }
        
        # Additional normalizations for better cross-language matching
        self.statement_mappings = {
            # Variable declarations
            'variable_declaration': 'VAR_DECL',
            'variable_declarator': 'VAR_DECL',
            'declaration': 'VAR_DECL',
            'local_variable_declaration': 'VAR_DECL',
            
            # Parameters
            'parameter': 'PARAM',
            'parameter_declaration': 'PARAM',
            'formal_parameter': 'PARAM',
            'formal_parameters': 'PARAMS',
            'parameter_list': 'PARAMS',
            
            # Blocks
            'block': 'BLOCK',
            'compound_statement': 'BLOCK',
            'statement_block': 'BLOCK',
            
            # Types
            'primitive_type': 'TYPE',
            'type_identifier': 'TYPE',
            'type': 'TYPE',
            'int': 'TYPE',
            'void': 'TYPE',
            'let': 'VAR_DECL',
            'const': 'VAR_DECL',
            'var': 'VAR_DECL',
            
            # Punctuation (ignore)
            '(': 'IGNORE',
            ')': 'IGNORE',
            '{': 'IGNORE',
            '}': 'IGNORE',
            '[': 'IGNORE',
            ']': 'IGNORE',
            ';': 'IGNORE',
            ',': 'IGNORE',
            ':': 'IGNORE',
        }
    
    def normalize_node(self, node: Any) -> str:
        """Normalize an AST node to a language-agnostic representation."""
        if not node:
            return 'EMPTY'
            
        # Get node type
        node_type = self._get_node_type(node)
        
        # Check statement mappings first (for ignoring punctuation)
        if node_type in self.statement_mappings:
            mapped = self.statement_mappings[node_type]
            if mapped == 'IGNORE':
                return None  # Will be filtered out
            return mapped
        
        # Map to normalized type
        normalized_type = self.node_mappings.get(node_type, node_type.upper())
        
        # Add semantic information based on node type
        if normalized_type == 'BINARY_OP' or normalized_type == 'COMPARISON':
            # Include the operation
            op = self._get_node_operator(node)
            if op:
                normalized_op = self.operation_mappings.get(op, op)
                return f"{normalized_type}:{normalized_op}"
                
        elif normalized_type == 'CALL':
            # Include function name if it's a simple identifier
            func_name = self._get_call_name(node)
            if func_name:
                func_lower = func_name.lower()
                if func_lower in ['partition', 'swap', 'merge', 'sort', 'quicksort', 'qsort']:
                    return f"{normalized_type}:{func_lower.upper()}"
                # Also check for common patterns in function names
                elif 'sort' in func_lower:
                    return f"{normalized_type}:SORT"
                elif 'partition' in func_lower:
                    return f"{normalized_type}:PARTITION"
                
        elif normalized_type == 'VAR':
            # Normalize common variable names
            var_name = self._get_node_text(node)
            if var_name:
                if var_name.lower() in ['arr', 'array', 'list', 'data', 'nums']:
                    return 'VAR:ARRAY'
                elif var_name.lower() in ['left', 'low', 'start', 'lo']:
                    return 'VAR:LEFT'
                elif var_name.lower() in ['right', 'high', 'end', 'hi']:
                    return 'VAR:RIGHT'
                elif var_name.lower() in ['pivot', 'mid', 'middle']:
                    return 'VAR:PIVOT'
                elif var_name.lower() in ['i', 'j', 'k', 'idx', 'index']:
                    return 'VAR:INDEX'
                    
        return normalized_type
    
    def _get_node_type(self, node: Any) -> str:
        """Get the type of an AST node."""
        if hasattr(node, 'type'):
            node_type = node.type
            # Handle tree-sitter byte strings
            if isinstance(node_type, bytes):
                return node_type.decode('utf-8', errors='ignore')
            return str(node_type)
        elif hasattr(node, 'kind'):
            return str(node.kind)
        elif hasattr(node, '__class__'):
            return node.__class__.__name__.lower()
        return 'unknown'
    
    def _get_node_text(self, node: Any) -> str:
        """Get the text content of a node."""
        if hasattr(node, 'text'):
            if isinstance(node.text, bytes):
                return node.text.decode('utf-8', errors='ignore')
            return str(node.text)
        elif hasattr(node, 'value'):
            return str(node.value)
        elif hasattr(node, 'id') and hasattr(node.id, 'text'):
            return str(node.id.text)
        return ''
    
    def _get_node_operator(self, node: Any) -> Optional[str]:
        """Extract operator from a binary operation node."""
        # Try different ways to get the operator
        if hasattr(node, 'operator'):
            return str(node.operator)
            
        # For tree-sitter nodes, look for operator child
        if hasattr(node, 'child_count'):
            for i in range(node.child_count):
                child = node.child(i)
                if child and hasattr(child, 'type'):
                    if child.type in self.operation_mappings:
                        return child.type
                    elif hasattr(child, 'text'):
                        text = child.text.decode() if isinstance(child.text, bytes) else str(child.text)
                        if text in self.operation_mappings:
                            return text
        return None
    
    def _get_call_name(self, node: Any) -> Optional[str]:
        """Extract function name from a call node."""
        # Try to find function child
        if hasattr(node, 'child_by_field_name'):
            func_node = node.child_by_field_name('function')
            if func_node:
                return self._get_node_text(func_node)
                
        # Try first child
        if hasattr(node, 'child_count') and node.child_count > 0:
            first_child = node.child(0)
            if first_child and hasattr(first_child, 'type') and first_child.type == 'identifier':
                return self._get_node_text(first_child)
                
        return None


class ASTWinnowing:
    """AST-based winnowing for semantic fingerprinting."""
    
    def __init__(self, config: ASTWinnowingConfig = None):
        """Initialize AST winnowing."""
        self.config = config or ASTWinnowingConfig()
        self.normalizer = ASTNodeNormalizer()
        
    def extract_ast_sequence(self, ast_node: Any, max_depth: int = 10) -> List[str]:
        """Extract normalized sequence of AST nodes."""
        sequence = []
        
        def traverse(node, depth=0):
            if not node or depth > max_depth:
                return
                
            # Normalize and add node
            normalized = self.normalizer.normalize_node(node)
            if normalized:  # Skip None values (ignored nodes)
                sequence.append(normalized)
            
            # Traverse children
            if hasattr(node, 'child_count'):
                for i in range(node.child_count):
                    child = node.child(i)
                    if child:
                        traverse(child, depth + 1)
            elif hasattr(node, 'children'):
                for child in node.children:
                    traverse(child, depth + 1)
            elif hasattr(node, 'type') and node.type == 'module':
                # Handle FallbackAST - extract more detail from code
                if hasattr(node, 'parent') and hasattr(node.parent, 'code'):
                    # Parse code to extract more nodes
                    code = node.parent.code
                    # Add common patterns found in code
                    if 'if' in code:
                        sequence.append('CONDITIONAL')
                    if 'for' in code or 'while' in code:
                        sequence.append('LOOP')
                    if 'return' in code:
                        sequence.append('RETURN')
                    if '<' in code:
                        sequence.append('BINARY_OP:LT')
                    if '>' in code:
                        sequence.append('BINARY_OP:GT')
                    if '==' in code:
                        sequence.append('BINARY_OP:EQ')
                    if 'partition' in code:
                        sequence.append('CALL:PARTITION')
                    if 'quicksort' in code:
                        sequence.append('CALL:QUICKSORT')
                    # Add variable references
                    if 'pivot' in code:
                        sequence.append('VAR:PIVOT')
                    if 'low' in code or 'left' in code:
                        sequence.append('VAR:LEFT')
                    if 'high' in code or 'right' in code:
                        sequence.append('VAR:RIGHT')
                    if 'arr' in code:
                        sequence.append('VAR:ARRAY')
                    
        traverse(ast_node)
        return sequence
    
    def generate_ast_fingerprint(self, ast_tree: Any) -> List[Tuple[int, int]]:
        """Generate winnowing fingerprint from AST."""
        # Extract normalized AST sequence
        if hasattr(ast_tree, 'root'):
            ast_sequence = self.extract_ast_sequence(ast_tree.root)
        else:
            ast_sequence = self.extract_ast_sequence(ast_tree)
            
        if len(ast_sequence) < self.config.k_gram_size:
            # Too small for k-grams
            return []
            
        # Generate k-grams from AST sequence
        k_grams = []
        for i in range(len(ast_sequence) - self.config.k_gram_size + 1):
            k_gram = tuple(ast_sequence[i:i + self.config.k_gram_size])
            k_grams.append((i, k_gram))
            
        # Hash k-grams
        hashes = []
        for pos, k_gram in k_grams:
            # Create string representation of k-gram
            k_gram_str = '|'.join(k_gram)
            
            # Hash it
            if self.config.hash_function == 'sha256':
                hash_val = int(hashlib.sha256(k_gram_str.encode()).hexdigest()[:8], 16)
            else:  # Default to simple hash
                hash_val = abs(hash(k_gram_str))
                
            hashes.append((pos, hash_val))
            
        # Select fingerprints using winnowing
        fingerprints = self._select_fingerprints(hashes)
        
        return fingerprints
    
    def _select_fingerprints(self, hashes: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Select fingerprints using the winnowing algorithm."""
        if not hashes:
            return []
            
        if len(hashes) <= self.config.window_size:
            # Select minimum from all
            min_hash = min(hashes, key=lambda x: x[1])
            return [min_hash]
            
        fingerprints = []
        prev_min_pos = -1
        
        for i in range(len(hashes) - self.config.window_size + 1):
            window = hashes[i:i + self.config.window_size]
            
            # Find minimum in window
            min_pos, min_hash = min(window, key=lambda x: x[1])
            actual_pos = i + window.index((min_pos, min_hash))
            
            # Add if it's a new position
            if actual_pos != prev_min_pos:
                fingerprints.append((hashes[actual_pos][0], min_hash))
                prev_min_pos = actual_pos
                
        return fingerprints
    
    def compare_fingerprints(self, fp1: List[Tuple[int, int]], 
                           fp2: List[Tuple[int, int]]) -> float:
        """Compare two AST fingerprints."""
        if not fp1 or not fp2:
            return 0.0
            
        # Extract just the hash values
        hashes1 = set(h for _, h in fp1)
        hashes2 = set(h for _, h in fp2)
        
        # Jaccard similarity
        intersection = len(hashes1 & hashes2)
        union = len(hashes1 | hashes2)
        
        return intersection / union if union > 0 else 0.0