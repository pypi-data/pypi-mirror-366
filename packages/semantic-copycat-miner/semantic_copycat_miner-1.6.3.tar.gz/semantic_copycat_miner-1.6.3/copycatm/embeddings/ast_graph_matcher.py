"""
Graph-based AST matching for improved cross-language similarity.

This module provides graph-based matching of AST structures, focusing on
semantic relationships rather than syntactic sequences.
"""

import networkx as nx
from typing import Dict, List, Tuple, Any, Set, Optional
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ASTGraphMatcher:
    """Match AST structures using graph-based algorithms."""
    
    def __init__(self):
        """Initialize the graph matcher."""
        self.node_mappings = {
            # Control flow
            'if_statement': 'COND',
            'conditional_expression': 'COND',
            'ternary_expression': 'COND',
            'for_statement': 'LOOP',
            'while_statement': 'LOOP',
            'do_statement': 'LOOP',
            
            # Operations
            'binary_expression': 'BINOP',
            'binary_operator': 'BINOP',
            'assignment': 'ASSIGN',
            'call': 'CALL',
            'call_expression': 'CALL',
            
            # Functions
            'function_definition': 'FUNC',
            'function_declaration': 'FUNC',
            'method_declaration': 'FUNC',
            
            # Data
            'identifier': 'VAR',
            'literal': 'CONST',
            'number': 'CONST',
            'string': 'CONST',
        }
    
    def ast_to_graph(self, ast_node: Any, graph: nx.DiGraph = None, parent_id: int = None) -> nx.DiGraph:
        """Convert AST to directed graph."""
        if graph is None:
            graph = nx.DiGraph()
            
        # Generate node ID
        node_id = len(graph.nodes)
        
        # Get node type and normalize
        node_type = self._get_node_type(ast_node)
        normalized_type = self.node_mappings.get(node_type, node_type.upper())
        
        # Extract semantic attributes
        attributes = self._extract_node_attributes(ast_node, normalized_type)
        
        # Add node to graph
        graph.add_node(node_id, type=normalized_type, **attributes)
        
        # Add edge from parent
        if parent_id is not None:
            graph.add_edge(parent_id, node_id, relation='child')
        
        # Process children
        if hasattr(ast_node, 'child_count'):
            for i in range(ast_node.child_count):
                child = ast_node.child(i)
                if child:
                    self.ast_to_graph(child, graph, node_id)
        elif hasattr(ast_node, 'children'):
            for child in ast_node.children:
                if child:
                    self.ast_to_graph(child, graph, node_id)
        
        return graph
    
    def _get_node_type(self, node: Any) -> str:
        """Get node type from AST node."""
        if hasattr(node, 'type'):
            return str(node.type)
        elif hasattr(node, 'kind'):
            return str(node.kind)
        elif hasattr(node, '__class__'):
            return node.__class__.__name__.lower()
        return 'unknown'
    
    def _extract_node_attributes(self, node: Any, normalized_type: str) -> Dict[str, Any]:
        """Extract semantic attributes from node."""
        attrs = {}
        
        # Extract operator for binary operations
        if normalized_type == 'BINOP':
            op = self._get_operator(node)
            if op:
                attrs['operator'] = self._normalize_operator(op)
        
        # Extract function/variable names for semantic matching
        if normalized_type in ['FUNC', 'CALL', 'VAR']:
            name = self._get_node_name(node)
            if name:
                attrs['semantic_name'] = self._normalize_name(name)
        
        # Extract literal values (normalized)
        if normalized_type == 'CONST':
            value = self._get_node_value(node)
            if value is not None:
                attrs['value_class'] = self._classify_value(value)
        
        return attrs
    
    def _get_operator(self, node: Any) -> Optional[str]:
        """Extract operator from node."""
        if hasattr(node, 'operator'):
            return str(node.operator)
        
        # Look for operator child in tree-sitter
        if hasattr(node, 'child_count'):
            for i in range(node.child_count):
                child = node.child(i)
                if child and hasattr(child, 'type'):
                    if child.type in ['<', '>', '==', '!=', '<=', '>=', '+', '-', '*', '/', '%']:
                        return child.type
        return None
    
    def _normalize_operator(self, op: str) -> str:
        """Normalize operator across languages."""
        op_map = {
            '<': 'LT', '>': 'GT', '<=': 'LTE', '>=': 'GTE',
            '==': 'EQ', '!=': 'NEQ', '===': 'EQ', '!==': 'NEQ',
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD'
        }
        return op_map.get(op, op)
    
    def _get_node_name(self, node: Any) -> Optional[str]:
        """Extract name from node."""
        if hasattr(node, 'text'):
            text = node.text
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            return text
        elif hasattr(node, 'name'):
            return str(node.name)
        elif hasattr(node, 'value'):
            return str(node.value)
        return None
    
    def _normalize_name(self, name: str) -> str:
        """Normalize common names across languages."""
        name_lower = name.lower()
        
        # Common mappings
        if name_lower in ['arr', 'array', 'list', 'nums', 'data']:
            return 'ARRAY'
        elif name_lower in ['left', 'low', 'start', 'lo', 'begin']:
            return 'LEFT'
        elif name_lower in ['right', 'high', 'end', 'hi']:
            return 'RIGHT'
        elif name_lower in ['pivot', 'mid', 'middle', 'center']:
            return 'PIVOT'
        elif name_lower in ['i', 'j', 'k', 'idx', 'index']:
            return 'INDEX'
        elif name_lower in ['partition', 'split']:
            return 'PARTITION'
        elif name_lower in ['quicksort', 'qsort', 'sort']:
            return 'QUICKSORT'
        
        return name_lower
    
    def _get_node_value(self, node: Any) -> Any:
        """Extract value from literal node."""
        if hasattr(node, 'value'):
            return node.value
        elif hasattr(node, 'text'):
            text = node.text
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            try:
                return int(text)
            except:
                try:
                    return float(text)
                except:
                    return text
        return None
    
    def _classify_value(self, value: Any) -> str:
        """Classify literal values."""
        if isinstance(value, (int, float)):
            if value == 0:
                return 'ZERO'
            elif value == 1:
                return 'ONE'
            elif value == -1:
                return 'NEG_ONE'
            elif value > 0:
                return 'POSITIVE'
            else:
                return 'NEGATIVE'
        return 'OTHER'
    
    def graph_similarity(self, g1: nx.DiGraph, g2: nx.DiGraph) -> float:
        """Calculate similarity between two AST graphs."""
        if g1.number_of_nodes() == 0 or g2.number_of_nodes() == 0:
            return 0.0
        
        # Multiple similarity metrics
        similarities = []
        
        # 1. Node type distribution similarity
        type_sim = self._node_type_similarity(g1, g2)
        similarities.append(type_sim)
        
        # 2. Structural similarity (graph edit distance approximation)
        struct_sim = self._structural_similarity(g1, g2)
        similarities.append(struct_sim)
        
        # 3. Semantic pattern similarity
        pattern_sim = self._pattern_similarity(g1, g2)
        similarities.append(pattern_sim)
        
        # 4. Control flow similarity
        cf_sim = self._control_flow_similarity(g1, g2)
        similarities.append(cf_sim)
        
        # Weighted average
        weights = [0.2, 0.3, 0.3, 0.2]  # Emphasize structural and pattern similarity
        return sum(s * w for s, w in zip(similarities, weights))
    
    def _node_type_similarity(self, g1: nx.DiGraph, g2: nx.DiGraph) -> float:
        """Compare node type distributions."""
        types1 = defaultdict(int)
        types2 = defaultdict(int)
        
        for _, data in g1.nodes(data=True):
            types1[data.get('type', 'UNKNOWN')] += 1
        
        for _, data in g2.nodes(data=True):
            types2[data.get('type', 'UNKNOWN')] += 1
        
        # Jaccard similarity of type sets
        all_types = set(types1.keys()) | set(types2.keys())
        if not all_types:
            return 0.0
        
        similarity = 0.0
        for t in all_types:
            count1 = types1.get(t, 0)
            count2 = types2.get(t, 0)
            similarity += min(count1, count2) / max(count1, count2, 1)
        
        return similarity / len(all_types)
    
    def _structural_similarity(self, g1: nx.DiGraph, g2: nx.DiGraph) -> float:
        """Compare graph structures with semantic awareness."""
        # Focus on semantic node types, not raw counts
        semantic_nodes1 = self._count_semantic_nodes(g1)
        semantic_nodes2 = self._count_semantic_nodes(g2)
        
        # Compare semantic node distributions
        all_types = set(semantic_nodes1.keys()) | set(semantic_nodes2.keys())
        if not all_types:
            return 0.5
            
        similarity = 0.0
        for node_type in all_types:
            count1 = semantic_nodes1.get(node_type, 0)
            count2 = semantic_nodes2.get(node_type, 0)
            # Use ratio similarity instead of exact match
            if count1 == count2:
                similarity += 1.0
            elif count1 == 0 or count2 == 0:
                similarity += 0.0
            else:
                ratio = min(count1, count2) / max(count1, count2)
                similarity += ratio
                
        return similarity / len(all_types)
    
    def _count_semantic_nodes(self, g: nx.DiGraph) -> Dict[str, int]:
        """Count semantically important nodes."""
        counts = defaultdict(int)
        
        for _, data in g.nodes(data=True):
            node_type = data.get('type', 'UNKNOWN')
            
            # Only count semantic nodes
            if node_type in ['FUNC', 'LOOP', 'COND', 'CALL', 'BINOP', 'ASSIGN']:
                counts[node_type] += 1
                
                # Add semantic attributes
                if 'operator' in data:
                    counts[f"{node_type}_{data['operator']}"] += 1
                if 'semantic_name' in data:
                    counts[f"{node_type}_{data['semantic_name']}"] += 1
                    
        return dict(counts)
    
    def _pattern_similarity(self, g1: nx.DiGraph, g2: nx.DiGraph) -> float:
        """Compare semantic patterns in graphs."""
        patterns1 = self._extract_patterns(g1)
        patterns2 = self._extract_patterns(g2)
        
        if not patterns1 and not patterns2:
            return 1.0
        if not patterns1 or not patterns2:
            return 0.0
        
        # Separate critical patterns from others
        critical_patterns = [
            'FUNC->COND', 'COND->BINOP', 'COND->CALL',
            'LOOP->BINOP', 'LOOP->ASSIGN', 'LOOP->CALL',
            'CALL_PARTITION', 'CALL_QUICKSORT', 'PIVOT_COMPARE',
            'ASSIGN->VAR', 'BINOP_LT', 'BINOP_GT'
        ]
        
        # Calculate similarity with emphasis on critical patterns
        critical_sim = 0.0
        critical_count = 0
        other_sim = 0.0
        other_count = 0
        
        all_patterns = set(patterns1.keys()) | set(patterns2.keys())
        
        for pattern in all_patterns:
            count1 = patterns1.get(pattern, 0)
            count2 = patterns2.get(pattern, 0)
            sim = min(count1, count2) / max(count1, count2, 1)
            
            if any(cp in pattern for cp in critical_patterns):
                critical_sim += sim
                critical_count += 1
            else:
                other_sim += sim
                other_count += 1
        
        # Weight critical patterns more heavily
        if critical_count > 0:
            critical_avg = critical_sim / critical_count
        else:
            critical_avg = 0.5
            
        if other_count > 0:
            other_avg = other_sim / other_count
        else:
            other_avg = 0.5
            
        # 70% weight on critical patterns
        return 0.7 * critical_avg + 0.3 * other_avg
    
    def _control_flow_similarity(self, g1: nx.DiGraph, g2: nx.DiGraph) -> float:
        """Compare control flow structures."""
        cf1 = self._extract_control_flow(g1)
        cf2 = self._extract_control_flow(g2)
        
        if not cf1 and not cf2:
            return 1.0
        if not cf1 or not cf2:
            return 0.0
        
        # Compare control flow patterns
        similarity = 0.0
        
        # Compare conditional patterns
        cond_sim = min(cf1['conditionals'], cf2['conditionals']) / max(cf1['conditionals'], cf2['conditionals'], 1)
        loop_sim = min(cf1['loops'], cf2['loops']) / max(cf1['loops'], cf2['loops'], 1)
        call_sim = min(cf1['calls'], cf2['calls']) / max(cf1['calls'], cf2['calls'], 1)
        
        # Check for recursion
        rec_sim = 1.0 if cf1['has_recursion'] == cf2['has_recursion'] else 0.5
        
        return (cond_sim + loop_sim + call_sim + rec_sim) / 4
    
    def _graph_depth(self, g: nx.DiGraph) -> int:
        """Calculate maximum depth of graph."""
        if g.number_of_nodes() == 0:
            return 0
        
        # Find root (node with no incoming edges)
        roots = [n for n in g.nodes() if g.in_degree(n) == 0]
        if not roots:
            roots = [0]  # Default to first node
        
        max_depth = 0
        for root in roots:
            depths = nx.single_source_shortest_path_length(g, root)
            if depths:
                max_depth = max(max_depth, max(depths.values()))
        
        return max_depth
    
    def _extract_patterns(self, g: nx.DiGraph) -> Dict[str, int]:
        """Extract semantic patterns from graph."""
        patterns = defaultdict(int)
        
        for node, data in g.nodes(data=True):
            node_type = data.get('type', 'UNKNOWN')
            
            # Single node patterns
            patterns[node_type] += 1
            
            # Node with attributes patterns
            if 'operator' in data:
                patterns[f"{node_type}_{data['operator']}"] += 1
            if 'semantic_name' in data:
                patterns[f"{node_type}_{data['semantic_name']}"] += 1
            
            # Parent-child patterns
            for child in g.successors(node):
                child_type = g.nodes[child].get('type', 'UNKNOWN')
                patterns[f"{node_type}->{child_type}"] += 1
                
                # Special patterns
                if node_type == 'COND' and child_type == 'BINOP':
                    op = g.nodes[child].get('operator', '')
                    patterns[f"COND_{op}"] += 1
                
                if node_type == 'CALL' and 'semantic_name' in data:
                    patterns[f"CALL_{data['semantic_name']}"] += 1
        
        return dict(patterns)
    
    def _extract_control_flow(self, g: nx.DiGraph) -> Dict[str, Any]:
        """Extract control flow metrics from graph."""
        cf = {
            'conditionals': 0,
            'loops': 0,
            'calls': 0,
            'has_recursion': False
        }
        
        function_names = set()
        
        for node, data in g.nodes(data=True):
            node_type = data.get('type', '')
            
            if node_type == 'COND':
                cf['conditionals'] += 1
            elif node_type == 'LOOP':
                cf['loops'] += 1
            elif node_type == 'CALL':
                cf['calls'] += 1
                # Check for recursion
                if 'semantic_name' in data:
                    call_name = data['semantic_name']
                    if call_name in function_names:
                        cf['has_recursion'] = True
            elif node_type == 'FUNC':
                if 'semantic_name' in data:
                    function_names.add(data['semantic_name'])
        
        return cf