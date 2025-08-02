"""
AST normalization and structural pattern matching for improved similarity detection.
"""

import ast
import hashlib
from typing import Dict, List, Any, Optional


class ASTNormalizer:
    """Normalize AST structures for better cross-version and cross-modification matching."""
    
    def __init__(self):
        # Define node types that represent similar operations
        self.equivalent_nodes = {
            # Control flow equivalents
            'control_flow': {
                'if_statement', 'conditional_expression', 'ternary_expression',
                'if', 'conditional', 'selection_statement'
            },
            'loop': {
                'for_statement', 'while_statement', 'do_statement',
                'for_in_statement', 'for_of_statement', 'foreach_statement',
                'for', 'while', 'do_while', 'repeat_statement'
            },
            'function': {
                'function_definition', 'function_declaration', 'method_definition',
                'lambda_expression', 'arrow_function', 'anonymous_function',
                'func', 'def', 'lambda'
            },
            'call': {
                'call_expression', 'function_call', 'method_call',
                'invocation_expression', 'call'
            }
        }
        
        # Build reverse mapping
        self.node_to_category = {}
        for category, nodes in self.equivalent_nodes.items():
            for node in nodes:
                self.node_to_category[node] = category
    
    def normalize_ast(self, tree: Any, language: str) -> Dict[str, Any]:
        """Normalize AST to a common representation."""
        if hasattr(tree, '__class__') and tree.__class__.__module__ == 'ast':
            # Python AST
            return self._normalize_python_ast(tree)
        else:
            # Tree-sitter or other AST
            return self._normalize_generic_ast(tree, language)
    
    def _normalize_python_ast(self, node: ast.AST) -> Dict[str, Any]:
        """Normalize Python AST nodes."""
        normalized = {
            'type': self._normalize_node_type(node.__class__.__name__),
            'children': []
        }
        
        # Handle specific node types
        if isinstance(node, ast.FunctionDef):
            normalized['name'] = 'FUNC'
            normalized['params'] = len(node.args.args)
            normalized['has_decorators'] = len(node.decorator_list) > 0
            
        elif isinstance(node, ast.If):
            normalized['has_else'] = bool(node.orelse)
            
        elif isinstance(node, (ast.For, ast.While)):
            normalized['is_loop'] = True
            
        elif isinstance(node, ast.Call):
            normalized['num_args'] = len(node.args)
            normalized['has_kwargs'] = bool(node.keywords)
        
        # Recursively normalize children
        for child in ast.iter_child_nodes(node):
            child_norm = self._normalize_python_ast(child)
            if child_norm:
                normalized['children'].append(child_norm)
        
        return normalized
    
    def _normalize_generic_ast(self, node: Any, language: str) -> Dict[str, Any]:
        """Normalize tree-sitter or generic AST nodes."""
        if not hasattr(node, 'type'):
            return {}
        
        normalized = {
            'type': self._normalize_node_type(node.type),
            'children': []
        }
        
        # Extract structural properties
        if node.type in ['function_definition', 'method_definition']:
            normalized['name'] = 'FUNC'
            # Count parameters if available
            params = self._count_parameters(node)
            if params is not None:
                normalized['params'] = params
        
        elif node.type in ['if_statement', 'conditional_expression']:
            normalized['has_else'] = self._has_else_branch(node)
        
        elif node.type in ['for_statement', 'while_statement']:
            normalized['is_loop'] = True
        
        # Recursively normalize children
        for child in getattr(node, 'children', []):
            child_norm = self._normalize_generic_ast(child, language)
            if child_norm:
                normalized['children'].append(child_norm)
        
        return normalized
    
    def _normalize_node_type(self, node_type: str) -> str:
        """Normalize node type to common categories."""
        node_type_lower = node_type.lower()
        
        # Check if it belongs to a category
        category = self.node_to_category.get(node_type_lower)
        if category:
            return category
        
        # Additional normalizations
        if 'if' in node_type_lower or 'conditional' in node_type_lower:
            return 'control_flow'
        elif 'for' in node_type_lower or 'while' in node_type_lower or 'loop' in node_type_lower:
            return 'loop'
        elif 'function' in node_type_lower or 'method' in node_type_lower or 'def' in node_type_lower:
            return 'function'
        elif 'call' in node_type_lower or 'invoke' in node_type_lower:
            return 'call'
        elif 'return' in node_type_lower:
            return 'return'
        elif 'assign' in node_type_lower or '=' in node_type:
            return 'assignment'
        elif 'binary' in node_type_lower or 'operator' in node_type_lower:
            return 'operation'
        else:
            return node_type_lower
    
    def _count_parameters(self, node: Any) -> Optional[int]:
        """Count function parameters from AST node."""
        # Look for parameter list
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and 'parameter' in child.type:
                return len([c for c in child.children if c.type == 'identifier'])
        return None
    
    def _has_else_branch(self, node: Any) -> bool:
        """Check if conditional has else branch."""
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and 'else' in child.type:
                return True
        return False
    
    def structural_hash(self, normalized_ast: Dict[str, Any]) -> str:
        """Generate hash from normalized AST structure."""
        structure_str = self._ast_to_string(normalized_ast)
        return hashlib.sha256(structure_str.encode()).hexdigest()[:16]
    
    def _ast_to_string(self, node: Dict[str, Any], depth: int = 0) -> str:
        """Convert normalized AST to string representation."""
        parts = []
        
        # Add node type
        parts.append(node['type'])
        
        # Add structural properties
        if 'params' in node:
            parts.append(f"p{node['params']}")
        if node.get('has_else'):
            parts.append("else")
        if node.get('is_loop'):
            parts.append("loop")
        if 'num_args' in node:
            parts.append(f"a{node['num_args']}")
        
        # Add children recursively
        child_parts = []
        for child in node.get('children', []):
            child_str = self._ast_to_string(child, depth + 1)
            if child_str:
                child_parts.append(child_str)
        
        if child_parts:
            parts.append(f"[{','.join(child_parts)}]")
        
        return f"({' '.join(parts)})"
    
    def extract_structural_patterns(self, normalized_ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structural patterns from normalized AST."""
        patterns = []
        
        # Extract function patterns
        self._extract_patterns_recursive(normalized_ast, patterns, pattern_type='structure')
        
        # Extract control flow patterns
        cf_pattern = self._extract_control_flow_pattern(normalized_ast)
        if cf_pattern:
            patterns.append({
                'type': 'control_flow',
                'pattern': cf_pattern,
                'hash': hashlib.md5(str(cf_pattern).encode()).hexdigest()[:8]
            })
        
        # Extract loop patterns
        loop_pattern = self._extract_loop_pattern(normalized_ast)
        if loop_pattern:
            patterns.append({
                'type': 'loop_structure',
                'pattern': loop_pattern,
                'hash': hashlib.md5(str(loop_pattern).encode()).hexdigest()[:8]
            })
        
        return patterns
    
    def _extract_patterns_recursive(self, node: Dict[str, Any], patterns: List[Dict], 
                                   pattern_type: str, path: List[str] = None):
        """Recursively extract patterns from AST."""
        if path is None:
            path = []
        
        current_path = path + [node['type']]
        
        # Extract pattern for current node
        if len(current_path) >= 2:  # Minimum pattern length
            pattern = {
                'type': pattern_type,
                'path': current_path,
                'properties': {}
            }
            
            # Add node properties
            for key in ['params', 'has_else', 'is_loop', 'num_args']:
                if key in node:
                    pattern['properties'][key] = node[key]
            
            if pattern['properties']:  # Only add if has properties
                pattern['hash'] = hashlib.md5(str(pattern).encode()).hexdigest()[:8]
                patterns.append(pattern)
        
        # Recurse to children
        for child in node.get('children', []):
            self._extract_patterns_recursive(child, patterns, pattern_type, current_path)
    
    def _extract_control_flow_pattern(self, node: Dict[str, Any]) -> Optional[str]:
        """Extract control flow pattern."""
        cf_sequence = []
        
        def extract_cf(n: Dict, seq: List):
            if n['type'] == 'control_flow':
                seq.append('if')
                if n.get('has_else'):
                    seq.append('else')
            elif n['type'] == 'loop':
                seq.append('loop')
            elif n['type'] == 'return':
                seq.append('return')
            
            for child in n.get('children', []):
                extract_cf(child, seq)
        
        extract_cf(node, cf_sequence)
        
        return '-'.join(cf_sequence) if cf_sequence else None
    
    def _extract_loop_pattern(self, node: Dict[str, Any]) -> Optional[Dict]:
        """Extract loop nesting pattern."""
        loop_info = {
            'max_depth': 0,
            'total_loops': 0,
            'nested_loops': 0
        }
        
        def count_loops(n: Dict, depth: int = 0):
            if n['type'] == 'loop':
                loop_info['total_loops'] += 1
                if depth > 0:
                    loop_info['nested_loops'] += 1
                loop_info['max_depth'] = max(loop_info['max_depth'], depth + 1)
                
                # Check children with increased depth
                for child in n.get('children', []):
                    count_loops(child, depth + 1)
            else:
                # Check children with same depth
                for child in n.get('children', []):
                    count_loops(child, depth)
        
        count_loops(node)
        
        return loop_info if loop_info['total_loops'] > 0 else None
    
    def pattern_similarity(self, patterns1: List[Dict], patterns2: List[Dict]) -> float:
        """Calculate similarity between two sets of patterns."""
        if not patterns1 or not patterns2:
            return 0.0
        
        # Create pattern sets by hash
        hashes1 = {p['hash'] for p in patterns1 if 'hash' in p}
        hashes2 = {p['hash'] for p in patterns2 if 'hash' in p}
        
        if not hashes1 or not hashes2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(hashes1.intersection(hashes2))
        union = len(hashes1.union(hashes2))
        
        return intersection / union if union > 0 else 0.0
    
    def structural_similarity(self, ast1: Any, ast2: Any, language1: str, language2: str) -> Dict[str, float]:
        """Calculate structural similarity between two ASTs."""
        # Normalize both ASTs
        norm1 = self.normalize_ast(ast1, language1)
        norm2 = self.normalize_ast(ast2, language2)
        
        # Generate structural hashes
        hash1 = self.structural_hash(norm1)
        hash2 = self.structural_hash(norm2)
        
        # Extract patterns
        patterns1 = self.extract_structural_patterns(norm1)
        patterns2 = self.extract_structural_patterns(norm2)
        
        # Calculate similarities
        return {
            'hash_match': 1.0 if hash1 == hash2 else 0.0,
            'pattern_similarity': self.pattern_similarity(patterns1, patterns2),
            'structure_similarity': self._calculate_tree_similarity(norm1, norm2),
            'size_ratio': self._calculate_size_ratio(norm1, norm2)
        }
    
    def _calculate_tree_similarity(self, tree1: Dict, tree2: Dict) -> float:
        """Calculate tree structure similarity."""
        # Simple tree edit distance approximation
        if tree1['type'] != tree2['type']:
            return 0.0
        
        similarity = 0.5  # Base similarity for matching node types
        
        # Compare properties
        props1 = {k: v for k, v in tree1.items() if k not in ['type', 'children']}
        props2 = {k: v for k, v in tree2.items() if k not in ['type', 'children']}
        
        if props1 == props2:
            similarity += 0.2
        
        # Compare children recursively
        children1 = tree1.get('children', [])
        children2 = tree2.get('children', [])
        
        if len(children1) == len(children2):
            similarity += 0.1
            
            if children1 and children2:
                child_similarities = []
                for c1, c2 in zip(children1, children2):
                    child_sim = self._calculate_tree_similarity(c1, c2)
                    child_similarities.append(child_sim)
                
                avg_child_sim = sum(child_similarities) / len(child_similarities)
                similarity += 0.2 * avg_child_sim
        
        return min(similarity, 1.0)
    
    def _calculate_size_ratio(self, tree1: Dict, tree2: Dict) -> float:
        """Calculate size ratio between trees."""
        size1 = self._count_nodes(tree1)
        size2 = self._count_nodes(tree2)
        
        if size1 == 0 or size2 == 0:
            return 0.0
        
        return min(size1, size2) / max(size1, size2)
    
    def _count_nodes(self, tree: Dict) -> int:
        """Count total nodes in tree."""
        count = 1
        for child in tree.get('children', []):
            count += self._count_nodes(child)
        return count