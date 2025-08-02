"""
Semantic-aware graph builder for improved algorithm similarity detection.

This enhanced approach focuses on algorithmic patterns rather than just syntactic structure.
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Set
import hashlib
import re
from collections import defaultdict


class SemanticGraphBuilder:
    """Enhanced graph builder focusing on algorithmic semantics."""
    
    def __init__(self):
        self.algorithmic_patterns = {
            # Divide and conquer patterns
            'divide_conquer': {
                'recursive_call': r'(\w+)\s*\([^)]*\)',
                'base_case': r'if\s+.*(?:<=|<|==|>=|>)',
                'partition': r'(?:partition|split|divide)',
                'combine': r'(?:\+|merge|combine|concat)'
            },
            
            # Sorting patterns
            'sorting': {
                'comparison': r'(?:[<>=!]=?|compare)',
                'swap': r'(?:swap|exchange|\w+,\s*\w+\s*=\s*\w+,\s*\w+)',
                'pivot': r'(?:pivot|median)',
                'array_access': r'\w+\[.*\]'
            },
            
            # Search patterns  
            'search': {
                'binary_search': r'(?:mid|middle|left|right|high|low)',
                'linear_scan': r'for.*in.*(?:range|array|list)',
                'comparison': r'(?:==|equals|target)'
            },
            
            # Dynamic programming
            'dynamic_programming': {
                'memoization': r'(?:memo|cache|dp|table)',
                'subproblem': r'(?:sub|smaller|previous)',
                'optimal_substructure': r'(?:min|max|optimal)'
            }
        }
        
        # Semantic node types based on algorithmic purpose
        self.semantic_node_types = {
            'RECURSIVE_CALL': 'recursive_operation',
            'BASE_CASE': 'termination_condition', 
            'PARTITION': 'divide_operation',
            'COMPARISON': 'decision_point',
            'SWAP': 'data_exchange',
            'LOOP': 'iteration_control',
            'CONDITIONAL': 'branching_logic',
            'ARRAY_ACCESS': 'data_access',
            'FUNCTION_DEF': 'algorithm_entry',
            'RETURN': 'result_output'
        }
    
    def build_semantic_graph(self, code_text: str, ast_tree: Any, language: str) -> nx.DiGraph:
        """
        Build semantic graph focusing on algorithmic patterns.
        
        Args:
            code_text: Raw source code
            ast_tree: AST tree from parser
            language: Programming language
            
        Returns:
            Directed graph with semantic algorithm features
        """
        graph = nx.DiGraph()
        
        # Extract algorithmic patterns from text
        algorithmic_features = self._extract_algorithmic_patterns(code_text)
        
        # Build control flow graph
        control_flow = self._build_control_flow(ast_tree, language)
        
        # Create semantic nodes based on algorithmic patterns
        semantic_nodes = self._create_semantic_nodes(algorithmic_features, control_flow)
        
        # Add nodes and edges to graph
        for node_id, node_data in semantic_nodes.items():
            graph.add_node(node_id, **node_data)
        
        # Add semantic edges (data flow, control flow, dependency)
        self._add_semantic_edges(graph, semantic_nodes, control_flow)
        
        return graph
    
    def _extract_algorithmic_patterns(self, code_text: str) -> Dict[str, List[Dict]]:
        """Extract algorithmic patterns from source code."""
        patterns = defaultdict(list)
        
        lines = code_text.split('\n')
        
        for line_num, line in enumerate(lines):
            line_clean = line.strip()
            
            # Skip comments and empty lines
            if not line_clean or line_clean.startswith(('#', '//', '/*')):
                continue
            
            # Detect algorithmic patterns
            for pattern_type, pattern_dict in self.algorithmic_patterns.items():
                for pattern_name, regex in pattern_dict.items():
                    matches = re.findall(regex, line_clean, re.IGNORECASE)
                    if matches:
                        patterns[pattern_type].append({
                            'pattern': pattern_name,
                            'line': line_num,
                            'text': line_clean,
                            'matches': matches,
                            'semantic_weight': self._calculate_semantic_weight(pattern_type, pattern_name)
                        })
        
        return patterns
    
    def _calculate_semantic_weight(self, pattern_type: str, pattern_name: str) -> float:
        """Calculate semantic importance weight for pattern."""
        weights = {
            'divide_conquer': {
                'recursive_call': 0.9,
                'base_case': 0.8,
                'partition': 0.7,
                'combine': 0.6
            },
            'sorting': {
                'comparison': 0.6,
                'swap': 0.8,
                'pivot': 0.7,
                'array_access': 0.5
            },
            'search': {
                'binary_search': 0.8,
                'linear_scan': 0.5,
                'comparison': 0.6
            },
            'dynamic_programming': {
                'memoization': 0.9,
                'subproblem': 0.7,
                'optimal_substructure': 0.8
            }
        }
        
        return weights.get(pattern_type, {}).get(pattern_name, 0.3)
    
    def _build_control_flow(self, ast_tree: Any, language: str) -> Dict[str, Any]:
        """Build control flow representation."""
        control_flow = {
            'functions': [],
            'loops': [],
            'conditionals': [],
            'recursive_calls': [],
            'returns': []
        }
        
        # This would be enhanced with proper AST traversal
        # For now, simplified extraction
        
        return control_flow
    
    def _create_semantic_nodes(self, algorithmic_features: Dict, control_flow: Dict) -> Dict[str, Dict]:
        """Create semantic nodes based on algorithmic patterns."""
        nodes = {}
        node_id = 0
        
        # Create nodes for each algorithmic pattern
        for pattern_type, pattern_list in algorithmic_features.items():
            for pattern_data in pattern_list:
                node_id += 1
                node_key = f"semantic_{node_id}"
                
                nodes[node_key] = {
                    'type': 'semantic_pattern',
                    'pattern_type': pattern_type,
                    'pattern_name': pattern_data['pattern'],
                    'semantic_weight': pattern_data['semantic_weight'],
                    'line_number': pattern_data['line'],
                    'text_context': pattern_data['text'],
                    'algorithmic_significance': self._get_algorithmic_significance(pattern_type)
                }
        
        return nodes
    
    def _get_algorithmic_significance(self, pattern_type: str) -> str:
        """Get algorithmic significance description."""
        significance = {
            'divide_conquer': 'Fundamental divide-and-conquer operation',
            'sorting': 'Core sorting algorithm component',
            'search': 'Essential search algorithm element',
            'dynamic_programming': 'Optimization strategy component'
        }
        return significance.get(pattern_type, 'Generic algorithmic pattern')
    
    def _add_semantic_edges(self, graph: nx.DiGraph, nodes: Dict, control_flow: Dict):
        """Add semantic edges representing algorithmic relationships."""
        node_list = list(nodes.keys())
        
        for i, node1 in enumerate(node_list):
            for j, node2 in enumerate(node_list):
                if i != j:
                    # Add edge if nodes are semantically related
                    relation_strength = self._calculate_semantic_relation(
                        nodes[node1], nodes[node2]
                    )
                    
                    if relation_strength > 0.3:  # Threshold for semantic relationship
                        graph.add_edge(node1, node2, 
                                     weight=relation_strength,
                                     relation_type='semantic_dependency')
    
    def _calculate_semantic_relation(self, node1: Dict, node2: Dict) -> float:
        """Calculate semantic relationship strength between two nodes."""
        # Same pattern type = strong relationship
        if node1['pattern_type'] == node2['pattern_type']:
            return 0.8
        
        # Related patterns (e.g., divide_conquer + sorting)
        related_patterns = {
            ('divide_conquer', 'sorting'): 0.7,
            ('sorting', 'search'): 0.5,
            ('dynamic_programming', 'search'): 0.4
        }
        
        pattern_pair = (node1['pattern_type'], node2['pattern_type'])
        reverse_pair = (node2['pattern_type'], node1['pattern_type'])
        
        return related_patterns.get(pattern_pair, related_patterns.get(reverse_pair, 0.0))
    
    def extract_semantic_features(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Extract high-level semantic features from the graph."""
        features = {
            'algorithmic_complexity': self._measure_algorithmic_complexity(graph),
            'pattern_diversity': self._measure_pattern_diversity(graph),
            'semantic_density': self._measure_semantic_density(graph),
            'algorithmic_signature': self._generate_algorithmic_signature(graph),
            'dominant_patterns': self._identify_dominant_patterns(graph)
        }
        
        return features
    
    def _measure_algorithmic_complexity(self, graph: nx.DiGraph) -> float:
        """Measure algorithmic complexity based on pattern weights."""
        total_weight = 0
        node_count = 0
        
        for node, data in graph.nodes(data=True):
            if 'semantic_weight' in data:
                total_weight += data['semantic_weight']
                node_count += 1
        
        return total_weight / max(node_count, 1)
    
    def _measure_pattern_diversity(self, graph: nx.DiGraph) -> float:
        """Measure diversity of algorithmic patterns."""
        pattern_types = set()
        
        for node, data in graph.nodes(data=True):
            if 'pattern_type' in data:
                pattern_types.add(data['pattern_type'])
        
        return len(pattern_types) / 4.0  # Normalize by max expected patterns
    
    def _measure_semantic_density(self, graph: nx.DiGraph) -> float:
        """Measure density of semantic relationships."""
        if graph.number_of_nodes() < 2:
            return 0.0
        
        actual_edges = graph.number_of_edges()
        max_possible_edges = graph.number_of_nodes() * (graph.number_of_nodes() - 1)
        
        return actual_edges / max(max_possible_edges, 1)
    
    def _generate_algorithmic_signature(self, graph: nx.DiGraph) -> str:
        """Generate unique signature based on algorithmic patterns."""
        pattern_counts = defaultdict(int)
        
        for node, data in graph.nodes(data=True):
            if 'pattern_type' in data:
                pattern_counts[data['pattern_type']] += 1
        
        # Create signature from pattern distribution
        signature_parts = []
        for pattern_type in sorted(pattern_counts.keys()):
            count = pattern_counts[pattern_type]
            signature_parts.append(f"{pattern_type[:3]}{count}")
        
        signature_string = "_".join(signature_parts)
        return hashlib.md5(signature_string.encode()).hexdigest()[:16]
    
    def _identify_dominant_patterns(self, graph: nx.DiGraph) -> List[str]:
        """Identify the most prominent algorithmic patterns."""
        pattern_weights = defaultdict(float)
        
        for node, data in graph.nodes(data=True):
            if 'pattern_type' in data and 'semantic_weight' in data:
                pattern_weights[data['pattern_type']] += data['semantic_weight']
        
        # Sort by weight and return top patterns
        sorted_patterns = sorted(pattern_weights.items(), 
                               key=lambda x: x[1], reverse=True)
        
        return [pattern for pattern, weight in sorted_patterns[:3]]
    
    def compare_semantic_graphs(self, graph1: nx.DiGraph, graph2: nx.DiGraph) -> Dict[str, float]:
        """Compare two semantic graphs for algorithmic similarity."""
        features1 = self.extract_semantic_features(graph1)
        features2 = self.extract_semantic_features(graph2)
        
        # Compare algorithmic signatures
        signature_similarity = 1.0 if features1['algorithmic_signature'] == features2['algorithmic_signature'] else 0.0
        
        # Compare dominant patterns
        patterns1 = set(features1['dominant_patterns'])
        patterns2 = set(features2['dominant_patterns'])
        pattern_similarity = len(patterns1 & patterns2) / max(len(patterns1 | patterns2), 1)
        
        # Compare complexity
        complexity_diff = abs(features1['algorithmic_complexity'] - features2['algorithmic_complexity'])
        complexity_similarity = 1.0 - complexity_diff
        
        # Compare diversity  
        diversity_diff = abs(features1['pattern_diversity'] - features2['pattern_diversity'])
        diversity_similarity = 1.0 - diversity_diff
        
        return {
            'overall_similarity': (signature_similarity * 0.3 + 
                                 pattern_similarity * 0.4 + 
                                 complexity_similarity * 0.2 + 
                                 diversity_similarity * 0.1),
            'signature_similarity': signature_similarity,
            'pattern_similarity': pattern_similarity,
            'complexity_similarity': complexity_similarity,
            'diversity_similarity': diversity_similarity
        }