"""
Call graph and data flow analysis for enhanced code similarity detection.
"""

import ast
import re
import networkx as nx
from typing import Dict, List, Any, Optional
from collections import defaultdict
import hashlib


class CallGraphAnalyzer:
    """Analyze call graphs and data flow patterns in code."""
    
    def __init__(self):
        self.call_graph = nx.DiGraph()
        self.data_flow_graph = nx.DiGraph()
        self.function_signatures = {}
        self.variable_scopes = defaultdict(set)
        
    def analyze_code(self, code: str, language: str, ast_tree: Optional[Any] = None) -> Dict[str, Any]:
        """Analyze code to extract call graph and data flow information."""
        self.call_graph.clear()
        self.data_flow_graph.clear()
        self.function_signatures.clear()
        self.variable_scopes.clear()
        
        if language == "python" and ast_tree is None:
            try:
                ast_tree = ast.parse(code)
            except:
                pass
        
        if ast_tree:
            if hasattr(ast_tree, '__class__') and ast_tree.__class__.__module__ == 'ast':
                self._analyze_python_ast(ast_tree)
            else:
                self._analyze_generic_ast(ast_tree, code, language)
        else:
            # Fallback to pattern-based analysis
            self._analyze_with_patterns(code, language)
        
        return {
            'call_graph': self._serialize_call_graph(),
            'data_flow': self._serialize_data_flow(),
            'function_signatures': self.function_signatures,
            'call_patterns': self._extract_call_patterns(),
            'data_flow_patterns': self._extract_data_flow_patterns(),
            'graph_metrics': self._calculate_graph_metrics()
        }
    
    def _analyze_python_ast(self, tree: ast.AST):
        """Analyze Python AST for call graph and data flow."""
        
        class CallGraphVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.current_function = None
                self.current_scope = []
                
            def visit_FunctionDef(self, node):
                func_name = node.name
                self.analyzer.call_graph.add_node(func_name)
                
                # Extract function signature
                params = [arg.arg for arg in node.args.args]
                returns = None
                if node.returns:
                    returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
                
                self.analyzer.function_signatures[func_name] = {
                    'params': params,
                    'returns': returns,
                    'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else str(d) 
                                 for d in node.decorator_list]
                }
                
                # Track scope
                old_function = self.current_function
                self.current_function = func_name
                self.current_scope.append(func_name)
                
                self.generic_visit(node)
                
                self.current_function = old_function
                self.current_scope.pop()
            
            def visit_Call(self, node):
                if self.current_function:
                    # Extract called function name
                    if isinstance(node.func, ast.Name):
                        called_func = node.func.id
                        self.analyzer.call_graph.add_edge(self.current_function, called_func)
                    elif isinstance(node.func, ast.Attribute):
                        called_func = f"{ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'obj'}.{node.func.attr}"
                        self.analyzer.call_graph.add_edge(self.current_function, called_func)
                
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                # Track data flow
                if self.current_function:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            self.analyzer.variable_scopes[self.current_function].add(var_name)
                            
                            # Add data flow edge
                            if isinstance(node.value, ast.Name):
                                source = node.value.id
                                self.analyzer.data_flow_graph.add_edge(source, var_name)
                            elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                                source = f"call_{node.value.func.id}"
                                self.analyzer.data_flow_graph.add_edge(source, var_name)
                
                self.generic_visit(node)
        
        visitor = CallGraphVisitor(self)
        visitor.visit(tree)
    
    def _analyze_generic_ast(self, tree: Any, code: str, language: str):
        """Analyze generic AST (tree-sitter) for call graph."""
        # Extract functions and calls using tree traversal
        functions = self._extract_functions_generic(tree, code)
        calls = self._extract_calls_generic(tree, code)
        
        # Build call graph
        for func_name, func_info in functions.items():
            self.call_graph.add_node(func_name)
            self.function_signatures[func_name] = func_info
        
        # Add edges for calls
        current_function = None
        for call in calls:
            # Determine which function contains this call
            for func_name, func_info in functions.items():
                if func_info.get('start', 0) <= call['position'] <= func_info.get('end', float('inf')):
                    current_function = func_name
                    break
            
            if current_function:
                self.call_graph.add_edge(current_function, call['name'])
    
    def _extract_functions_generic(self, tree: Any, code: str) -> Dict[str, Dict]:
        """Extract function information from generic AST."""
        functions = {}
        
        def traverse(node):
            if hasattr(node, 'type'):
                if node.type in ['function_definition', 'method_definition', 'function_declaration']:
                    # Extract function name
                    name_node = self._find_child_by_type(node, ['identifier', 'function_name'])
                    if name_node and hasattr(name_node, 'text'):
                        func_name = name_node.text.decode() if isinstance(name_node.text, bytes) else name_node.text
                        
                        # Extract parameters
                        params = []
                        param_list = self._find_child_by_type(node, ['parameter_list', 'formal_parameters'])
                        if param_list:
                            for child in getattr(param_list, 'children', []):
                                if hasattr(child, 'type') and 'parameter' in child.type:
                                    param_name = self._extract_identifier(child)
                                    if param_name:
                                        params.append(param_name)
                        
                        functions[func_name] = {
                            'params': params,
                            'start': node.start_byte if hasattr(node, 'start_byte') else 0,
                            'end': node.end_byte if hasattr(node, 'end_byte') else len(code)
                        }
                
                # Traverse children
                for child in getattr(node, 'children', []):
                    traverse(child)
        
        traverse(tree)
        return functions
    
    def _extract_calls_generic(self, tree: Any, code: str) -> List[Dict]:
        """Extract function calls from generic AST."""
        calls = []
        
        def traverse(node, position=0):
            if hasattr(node, 'type'):
                if node.type in ['call_expression', 'function_call', 'method_call']:
                    # Extract called function name
                    func_node = self._find_child_by_type(node, ['identifier', 'member_expression'])
                    if func_node:
                        if hasattr(func_node, 'text'):
                            func_name = func_node.text.decode() if isinstance(func_node.text, bytes) else func_node.text
                        else:
                            func_name = self._extract_identifier(func_node)
                        
                        if func_name:
                            calls.append({
                                'name': func_name,
                                'position': node.start_byte if hasattr(node, 'start_byte') else position
                            })
                
                # Traverse children
                for child in getattr(node, 'children', []):
                    traverse(child, position)
        
        traverse(tree)
        return calls
    
    def _find_child_by_type(self, node: Any, types: List[str]) -> Optional[Any]:
        """Find first child node with matching type."""
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and child.type in types:
                return child
        return None
    
    def _extract_identifier(self, node: Any) -> Optional[str]:
        """Extract identifier from node."""
        if hasattr(node, 'type') and node.type == 'identifier':
            if hasattr(node, 'text'):
                return node.text.decode() if isinstance(node.text, bytes) else node.text
        
        # Look for identifier child
        id_node = self._find_child_by_type(node, ['identifier'])
        if id_node and hasattr(id_node, 'text'):
            return id_node.text.decode() if isinstance(id_node.text, bytes) else id_node.text
        
        return None
    
    def _analyze_with_patterns(self, code: str, language: str):
        """Fallback pattern-based analysis."""
        # Extract functions
        if language == "python":
            func_pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        elif language in ["javascript", "typescript"]:
            func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=.*?function|\w+\s*:\s*function)\s*\(([^)]*)\)'
        elif language in ["java", "c", "cpp"]:
            func_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)'
        else:
            func_pattern = r'(?:def|function|func)\s+(\w+)\s*\(([^)]*)\)'
        
        matches = re.finditer(func_pattern, code)
        for match in matches:
            func_name = match.group(1) or match.group(2)
            if func_name:
                params = match.group(2) if match.lastindex >= 2 else ""
                param_list = [p.strip().split()[-1] for p in params.split(',') if p.strip()]
                
                self.call_graph.add_node(func_name)
                self.function_signatures[func_name] = {
                    'params': param_list,
                    'start': match.start(),
                    'end': match.end()
                }
        
        # Extract function calls
        call_pattern = r'(\w+)\s*\('
        for func_name in self.function_signatures:
            func_info = self.function_signatures[func_name]
            # Find calls within this function
            func_code = code[func_info.get('start', 0):func_info.get('end', len(code))]
            
            for match in re.finditer(call_pattern, func_code):
                called = match.group(1)
                if called != func_name:  # Avoid self-reference from definition
                    self.call_graph.add_edge(func_name, called)
    
    def _serialize_call_graph(self) -> Dict[str, Any]:
        """Serialize call graph to dictionary."""
        return {
            'nodes': list(self.call_graph.nodes()),
            'edges': list(self.call_graph.edges()),
            'node_count': self.call_graph.number_of_nodes(),
            'edge_count': self.call_graph.number_of_edges(),
            'signature': self._generate_graph_signature(self.call_graph)
        }
    
    def _serialize_data_flow(self) -> Dict[str, Any]:
        """Serialize data flow graph to dictionary."""
        return {
            'nodes': list(self.data_flow_graph.nodes()),
            'edges': list(self.data_flow_graph.edges()),
            'variable_scopes': dict(self.variable_scopes),
            'signature': self._generate_graph_signature(self.data_flow_graph)
        }
    
    def _generate_graph_signature(self, graph: nx.DiGraph) -> str:
        """Generate a signature for a graph."""
        # Create a canonical representation
        edges = sorted(graph.edges())
        edge_str = ';'.join([f"{u}->{v}" for u, v in edges])
        
        # Add node degrees
        degrees = sorted([graph.degree(n) for n in graph.nodes()])
        degree_str = ','.join(map(str, degrees))
        
        signature_str = f"{edge_str}|{degree_str}"
        return hashlib.md5(signature_str.encode()).hexdigest()[:16]
    
    def _extract_call_patterns(self) -> List[Dict[str, Any]]:
        """Extract patterns from call graph."""
        patterns = []
        
        # Find recursive calls
        for node in self.call_graph.nodes():
            if self.call_graph.has_edge(node, node):
                patterns.append({
                    'type': 'recursion',
                    'function': node
                })
        
        # Find call chains
        chains = self._find_call_chains()
        for chain in chains:
            if len(chain) >= 3:
                patterns.append({
                    'type': 'call_chain',
                    'chain': chain,
                    'length': len(chain)
                })
        
        # Find hub functions (high in/out degree)
        for node in self.call_graph.nodes():
            in_degree = self.call_graph.in_degree(node)
            out_degree = self.call_graph.out_degree(node)
            
            if in_degree >= 3:
                patterns.append({
                    'type': 'hub_callee',
                    'function': node,
                    'in_degree': in_degree
                })
            
            if out_degree >= 3:
                patterns.append({
                    'type': 'hub_caller',
                    'function': node,
                    'out_degree': out_degree
                })
        
        return patterns
    
    def _find_call_chains(self) -> List[List[str]]:
        """Find call chains in the graph."""
        chains = []
        
        # Find all simple paths up to length 5
        for source in self.call_graph.nodes():
            for target in self.call_graph.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(self.call_graph, source, target, cutoff=5))
                        chains.extend(paths)
                    except:
                        pass
        
        # Remove duplicates and sort by length
        unique_chains = []
        seen = set()
        for chain in chains:
            chain_tuple = tuple(chain)
            if chain_tuple not in seen:
                seen.add(chain_tuple)
                unique_chains.append(chain)
        
        unique_chains.sort(key=len, reverse=True)
        return unique_chains[:10]  # Top 10 longest chains
    
    def _extract_data_flow_patterns(self) -> List[Dict[str, Any]]:
        """Extract patterns from data flow."""
        patterns = []
        
        # Find variable chains
        for source in self.data_flow_graph.nodes():
            descendants = nx.descendants(self.data_flow_graph, source)
            if len(descendants) >= 3:
                patterns.append({
                    'type': 'data_chain',
                    'source': source,
                    'chain_length': len(descendants)
                })
        
        # Find data hubs
        for node in self.data_flow_graph.nodes():
            in_degree = self.data_flow_graph.in_degree(node)
            out_degree = self.data_flow_graph.out_degree(node)
            
            if in_degree >= 3 or out_degree >= 3:
                patterns.append({
                    'type': 'data_hub',
                    'variable': node,
                    'in_degree': in_degree,
                    'out_degree': out_degree
                })
        
        return patterns
    
    def _calculate_graph_metrics(self) -> Dict[str, Any]:
        """Calculate graph metrics for similarity comparison."""
        metrics = {}
        
        if self.call_graph.number_of_nodes() > 0:
            # Call graph metrics
            metrics['call_graph'] = {
                'density': nx.density(self.call_graph),
                'avg_degree': sum(dict(self.call_graph.degree()).values()) / self.call_graph.number_of_nodes(),
                'max_degree': max(dict(self.call_graph.degree()).values()) if self.call_graph.degree() else 0,
                'components': nx.number_weakly_connected_components(self.call_graph),
                'has_cycles': not nx.is_directed_acyclic_graph(self.call_graph)
            }
        
        if self.data_flow_graph.number_of_nodes() > 0:
            # Data flow metrics
            metrics['data_flow'] = {
                'density': nx.density(self.data_flow_graph),
                'avg_degree': sum(dict(self.data_flow_graph.degree()).values()) / self.data_flow_graph.number_of_nodes(),
                'max_degree': max(dict(self.data_flow_graph.degree()).values()) if self.data_flow_graph.degree() else 0,
                'components': nx.number_weakly_connected_components(self.data_flow_graph)
            }
        
        return metrics
    
    def compare_call_graphs(self, graph1_data: Dict, graph2_data: Dict) -> Dict[str, float]:
        """Compare two call graphs for similarity."""
        # Rebuild graphs from data
        g1 = nx.DiGraph()
        g1.add_edges_from(graph1_data['edges'])
        
        g2 = nx.DiGraph()
        g2.add_edges_from(graph2_data['edges'])
        
        if g1.number_of_nodes() == 0 or g2.number_of_nodes() == 0:
            return {'similarity': 0.0}
        
        # Calculate various similarity metrics
        
        # 1. Signature similarity
        sig_similarity = 1.0 if graph1_data['signature'] == graph2_data['signature'] else 0.0
        
        # 2. Structural similarity
        node_overlap = len(set(g1.nodes()).intersection(set(g2.nodes())))
        edge_overlap = len(set(g1.edges()).intersection(set(g2.edges())))
        
        node_similarity = (2 * node_overlap) / (g1.number_of_nodes() + g2.number_of_nodes())
        edge_similarity = (2 * edge_overlap) / (g1.number_of_edges() + g2.number_of_edges()) if (g1.number_of_edges() + g2.number_of_edges()) > 0 else 0
        
        # 3. Degree distribution similarity
        deg1 = sorted([d for n, d in g1.degree()])
        deg2 = sorted([d for n, d in g2.degree()])
        
        # Normalize degree sequences
        max_len = max(len(deg1), len(deg2))
        deg1_norm = deg1 + [0] * (max_len - len(deg1))
        deg2_norm = deg2 + [0] * (max_len - len(deg2))
        
        degree_similarity = 1 - (sum(abs(a - b) for a, b in zip(deg1_norm, deg2_norm)) / (sum(deg1_norm) + sum(deg2_norm) + 1))
        
        # 4. Pattern similarity (simplified)
        set(graph1_data.get('call_patterns', []))
        set(graph2_data.get('call_patterns', []))
        
        pattern_types1 = {p.get('type') for p in graph1_data.get('call_patterns', [])}
        pattern_types2 = {p.get('type') for p in graph2_data.get('call_patterns', [])}
        
        pattern_similarity = len(pattern_types1.intersection(pattern_types2)) / max(len(pattern_types1.union(pattern_types2)), 1)
        
        # Weighted average
        similarity = (
            0.2 * sig_similarity +
            0.3 * node_similarity +
            0.2 * edge_similarity +
            0.2 * degree_similarity +
            0.1 * pattern_similarity
        )
        
        return {
            'similarity': similarity,
            'signature_match': sig_similarity,
            'node_similarity': node_similarity,
            'edge_similarity': edge_similarity,
            'degree_similarity': degree_similarity,
            'pattern_similarity': pattern_similarity
        }