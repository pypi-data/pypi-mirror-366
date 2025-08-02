"""
AST-based algorithm detection for CopycatM.

This module uses Abstract Syntax Tree analysis to identify algorithms
based on structural patterns rather than text matching.
"""

from typing import Dict, List, Any, Set
import ast
import re
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class AlgorithmSignature:
    """Represents an algorithm's structural signature"""
    name: str
    category: str
    required_structures: Set[str]
    optional_structures: Set[str]
    structural_patterns: List[Dict[str, Any]]
    confidence_threshold: float = 0.7


class ASTAlgorithmDetector:
    """Detects algorithms using AST structural analysis"""
    
    def __init__(self):
        self.signatures = self._build_algorithm_signatures()
        
    def _build_algorithm_signatures(self) -> Dict[str, AlgorithmSignature]:
        """Define structural signatures for common algorithms"""
        return {
            "quicksort": AlgorithmSignature(
                name="quicksort",
                category="sorting",
                required_structures={"recursion", "partition", "comparison"},
                optional_structures={"array_slice", "array_concat", "pivot_selection"},
                structural_patterns=[
                    {
                        "type": "base_case",
                        "pattern": "early_return_on_length",
                        "details": {"length_check": "<=1"}
                    },
                    {
                        "type": "pivot",
                        "pattern": "element_selection",
                        "details": {"common_positions": ["first", "last", "middle", "random"]}
                    },
                    {
                        "type": "partition",
                        "pattern": "split_by_comparison",
                        "details": {"creates": ["less_than", "greater_than"]}
                    },
                    {
                        "type": "recursion",
                        "pattern": "self_call_on_partitions",
                        "details": {"calls": 2}
                    },
                    {
                        "type": "merge",
                        "pattern": "combine_results",
                        "details": {"order": ["left", "pivot", "right"]}
                    }
                ],
                confidence_threshold=0.7
            ),
            "bubblesort": AlgorithmSignature(
                name="bubblesort",
                category="sorting",
                required_structures={"nested_loops", "comparison", "swap"},
                optional_structures={"optimization_flag", "early_termination"},
                structural_patterns=[
                    {
                        "type": "outer_loop",
                        "pattern": "iterate_array_length",
                        "details": {"direction": "forward"}
                    },
                    {
                        "type": "inner_loop",
                        "pattern": "iterate_with_boundary",
                        "details": {"boundary": "length-i-1"}
                    },
                    {
                        "type": "comparison",
                        "pattern": "adjacent_elements",
                        "details": {"indices": ["j", "j+1"]}
                    },
                    {
                        "type": "swap",
                        "pattern": "exchange_elements",
                        "details": {"when": "out_of_order"}
                    }
                ],
                confidence_threshold=0.75
            ),
            "mergesort": AlgorithmSignature(
                name="mergesort",
                category="sorting",
                required_structures={"recursion", "divide", "merge"},
                optional_structures={"base_case", "array_slice"},
                structural_patterns=[
                    {
                        "type": "divide",
                        "pattern": "split_at_middle",
                        "details": {"method": "length/2"}
                    },
                    {
                        "type": "recursion",
                        "pattern": "recurse_on_halves",
                        "details": {"calls": 2}
                    },
                    {
                        "type": "merge",
                        "pattern": "combine_sorted",
                        "details": {"method": "two_pointer"}
                    }
                ],
                confidence_threshold=0.7
            ),
            "heapsort": AlgorithmSignature(
                name="heapsort",
                category="sorting",
                required_structures={"heapify", "swap", "loop"},
                optional_structures={"build_heap", "extract_max"},
                structural_patterns=[
                    {
                        "type": "heapify",
                        "pattern": "maintain_heap_property",
                        "details": {"uses": ["parent", "left_child", "right_child"]}
                    },
                    {
                        "type": "indexing",
                        "pattern": "heap_indices",
                        "details": {"left": "2*i+1", "right": "2*i+2"}
                    }
                ],
                confidence_threshold=0.7
            ),
            "binary_search": AlgorithmSignature(
                name="binary_search",
                category="searching",
                required_structures={"loop_or_recursion", "comparison", "boundary_update"},
                optional_structures={"sorted_check"},
                structural_patterns=[
                    {
                        "type": "middle",
                        "pattern": "calculate_midpoint",
                        "details": {"formula": "(low+high)/2"}
                    },
                    {
                        "type": "comparison",
                        "pattern": "compare_with_target",
                        "details": {"branches": 3}
                    },
                    {
                        "type": "boundary",
                        "pattern": "adjust_search_space",
                        "details": {"updates": ["low", "high"]}
                    }
                ],
                confidence_threshold=0.7
            ),
            "dfs": AlgorithmSignature(
                name="depth_first_search",
                category="graph_traversal",
                required_structures={"recursion_or_stack", "visited_tracking", "neighbor_iteration"},
                optional_structures={"path_tracking", "backtracking"},
                structural_patterns=[
                    {
                        "type": "visited",
                        "pattern": "track_visited_nodes",
                        "details": {"structure": ["set", "array", "map"]}
                    },
                    {
                        "type": "traversal",
                        "pattern": "explore_neighbors",
                        "details": {"order": "depth_first"}
                    }
                ],
                confidence_threshold=0.65
            ),
            "bfs": AlgorithmSignature(
                name="breadth_first_search",
                category="graph_traversal",
                required_structures={"queue", "visited_tracking", "neighbor_iteration"},
                optional_structures={"level_tracking", "path_tracking"},
                structural_patterns=[
                    {
                        "type": "queue",
                        "pattern": "use_queue_structure",
                        "details": {"operations": ["enqueue", "dequeue"]}
                    },
                    {
                        "type": "traversal",
                        "pattern": "explore_level_by_level",
                        "details": {"order": "breadth_first"}
                    }
                ],
                confidence_threshold=0.65
            )
        }
    
    def analyze_ast_node(self, node: Any, language: str = "python") -> Dict[str, Any]:
        """Analyze an AST node to extract structural features"""
        features = {
            "has_recursion": False,
            "has_loops": False,
            "has_nested_loops": False,
            "has_comparison": False,
            "has_swap": False,
            "has_partition": False,
            "has_merge": False,
            "has_divide": False,
            "has_array_ops": False,
            "has_queue_ops": False,
            "has_stack_ops": False,
            "loop_patterns": [],
            "comparison_patterns": [],
            "function_calls": [],
            "variable_patterns": [],
            "control_flow": []
        }
        
        # Language-specific analysis
        if language == "python":
            features.update(self._analyze_python_ast(node))
        elif language == "javascript":
            features.update(self._analyze_javascript_ast(node))
        else:
            features.update(self._analyze_generic_ast(node))
            
        return features
    
    def _analyze_python_ast(self, node: ast.AST) -> Dict[str, Any]:
        """Analyze Python AST for algorithm patterns"""
        features = defaultdict(lambda: False)
        features["loop_patterns"] = []
        features["comparison_patterns"] = []
        features["function_calls"] = []
        features["variable_patterns"] = []
        
        class AlgorithmVisitor(ast.NodeVisitor):
            def __init__(self, features):
                self.features = features
                self.loop_depth = 0
                self.function_name = None
                
            def visit_FunctionDef(self, node):
                old_name = self.function_name
                self.function_name = node.name
                self.generic_visit(node)
                self.function_name = old_name
                
            def visit_For(self, node):
                self.features["has_loops"] = True
                self.loop_depth += 1
                if self.loop_depth > 1:
                    self.features["has_nested_loops"] = True
                
                # Analyze loop pattern
                loop_info = {"type": "for", "depth": self.loop_depth}
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                    if node.iter.func.id == "range":
                        loop_info["pattern"] = "range_based"
                        if node.iter.args:
                            loop_info["range_args"] = len(node.iter.args)
                            
                self.features["loop_patterns"].append(loop_info)
                self.generic_visit(node)
                self.loop_depth -= 1
                
            def visit_While(self, node):
                self.features["has_loops"] = True
                self.loop_depth += 1
                if self.loop_depth > 1:
                    self.features["has_nested_loops"] = True
                    
                loop_info = {"type": "while", "depth": self.loop_depth}
                self.features["loop_patterns"].append(loop_info)
                self.generic_visit(node)
                self.loop_depth -= 1
                
            def visit_Compare(self, node):
                self.features["has_comparison"] = True
                comp_info = {"ops": [op.__class__.__name__ for op in node.ops]}
                self.features["comparison_patterns"].append(comp_info)
                self.generic_visit(node)
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                    self.features["function_calls"].append(call_name)
                    
                    # Check for recursion
                    if call_name == self.function_name:
                        self.features["has_recursion"] = True
                        
                    # Check for common operations
                    if call_name in ["append", "push"]:
                        self.features["has_array_ops"] = True
                    elif call_name in ["pop", "popleft", "get"]:
                        self.features["has_queue_ops"] = True
                        
                elif isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    self.features["function_calls"].append(attr_name)
                    
                    if attr_name in ["append", "extend", "insert"]:
                        self.features["has_array_ops"] = True
                    elif attr_name in ["pop", "popleft"]:
                        self.features["has_queue_ops"] = True
                        
                self.generic_visit(node)
                
            def visit_Assign(self, node):
                # Check for swap pattern: a, b = b, a
                if (isinstance(node.value, ast.Tuple) and 
                    isinstance(node.targets[0], ast.Tuple) and
                    len(node.value.elts) == 2 and len(node.targets[0].elts) == 2):
                    self.features["has_swap"] = True
                    
                # Check for divide pattern: mid = len(arr) // 2
                if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.FloorDiv):
                    if isinstance(node.value.left, ast.Call) and isinstance(node.value.left.func, ast.Name):
                        if node.value.left.func.id == "len":
                            self.features["has_divide"] = True
                            
                self.generic_visit(node)
                
            def visit_If(self, node):
                # Check for base case pattern
                if isinstance(node.test, ast.Compare):
                    left = node.test.left
                    if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == "len":
                        if any(isinstance(op, (ast.LtE, ast.Lt)) for op in node.test.ops):
                            if any(isinstance(comp, ast.Constant) and comp.value in [0, 1] for comp in node.test.comparators):
                                self.features["has_base_case"] = True
                                
                self.generic_visit(node)
                
        visitor = AlgorithmVisitor(features)
        visitor.visit(node)
        
        return dict(features)
    
    def _analyze_javascript_ast(self, node: Any) -> Dict[str, Any]:
        """Analyze JavaScript AST (tree-sitter) for algorithm patterns"""
        features = defaultdict(lambda: False)
        features["loop_patterns"] = []
        features["comparison_patterns"] = []
        features["function_calls"] = []
        features["variable_patterns"] = []
        
        # JavaScript AST analysis using tree-sitter node structure
        def walk_js_ast(node, depth=0):
            node_type = node.type if hasattr(node, 'type') else str(type(node))
            
            # Check for loops
            if node_type in ['for_statement', 'for_in_statement', 'for_of_statement']:
                features["has_loops"] = True
                if depth > 0:
                    features["has_nested_loops"] = True
                features["loop_patterns"].append({"type": "for", "depth": depth})
                
            elif node_type == 'while_statement':
                features["has_loops"] = True
                if depth > 0:
                    features["has_nested_loops"] = True
                features["loop_patterns"].append({"type": "while", "depth": depth})
                
            # Check for comparisons
            elif node_type == 'binary_expression':
                features["has_comparison"] = True
                features["comparison_patterns"].append({"type": "binary"})
                
            # Check for function calls
            elif node_type == 'call_expression':
                features["function_calls"].append("call")
                # Check for array operations
                if hasattr(node, 'children'):
                    for child in node.children:
                        if hasattr(child, 'text'):
                            text = child.text.decode('utf8') if isinstance(child.text, bytes) else str(child.text)
                            if text in ['push', 'pop', 'shift', 'unshift']:
                                features["has_array_ops"] = True
                            elif text == node.parent.text if hasattr(node, 'parent') else "":
                                features["has_recursion"] = True
                                
            # Check for array destructuring (spread operator)
            elif node_type == 'spread_element':
                features["has_array_ops"] = True
                features["has_merge"] = True
                
            # Recursively process children
            if hasattr(node, 'children'):
                for child in node.children:
                    walk_js_ast(child, depth + (1 if node_type in ['for_statement', 'while_statement'] else 0))
                    
        walk_js_ast(node)
        return dict(features)
    
    def _analyze_generic_ast(self, node: Any) -> Dict[str, Any]:
        """Generic AST analysis for unsupported languages"""
        features = defaultdict(lambda: False)
        
        # Convert node to string and use pattern matching
        node_str = str(node)
        
        # Loop detection
        if re.search(r'\b(for|while|loop)\b', node_str, re.I):
            features["has_loops"] = True
            
        # Recursion detection (function calling itself)
        func_match = re.search(r'function\s+(\w+)', node_str)
        if func_match:
            func_name = func_match.group(1)
            if re.search(rf'\b{func_name}\s*\(', node_str[func_match.end():]):
                features["has_recursion"] = True
                
        # Comparison detection
        if re.search(r'[<>]=?|==|!=', node_str):
            features["has_comparison"] = True
            
        # Array operations
        if re.search(r'\.(push|pop|shift|unshift|append|extend)\s*\(', node_str):
            features["has_array_ops"] = True
            
        return dict(features)
    
    def detect_algorithm(self, ast_node: Any, language: str = "python") -> List[Dict[str, Any]]:
        """Detect algorithms based on AST structure"""
        # Extract features from AST
        features = self.analyze_ast_node(ast_node, language)
        
        detected_algorithms = []
        
        # Check each algorithm signature
        for algo_name, signature in self.signatures.items():
            confidence = self._calculate_confidence(features, signature)
            
            if confidence >= signature.confidence_threshold:
                detected_algorithms.append({
                    "algorithm": algo_name,
                    "category": signature.category,
                    "confidence": confidence,
                    "matched_structures": self._get_matched_structures(features, signature),
                    "evidence": self._gather_evidence(features, signature)
                })
                
        # Sort by confidence
        detected_algorithms.sort(key=lambda x: x.get("confidence", 0) if x.get("confidence") is not None else 0, reverse=True)
        
        return detected_algorithms
    
    def _calculate_confidence(self, features: Dict[str, Any], signature: AlgorithmSignature) -> float:
        """Calculate confidence score for algorithm match"""
        score = 0.0
        max_score = 0.0
        
        # Check required structures (weighted heavily)
        for structure in signature.required_structures:
            max_score += 0.3
            if self._has_structure(features, structure):
                score += 0.3
                
        # Check optional structures (weighted less)
        for structure in signature.optional_structures:
            max_score += 0.1
            if self._has_structure(features, structure):
                score += 0.1
                
        # Check structural patterns
        for pattern in signature.structural_patterns:
            max_score += 0.2
            if self._matches_pattern(features, pattern):
                score += 0.2
                
        return score / max_score if max_score > 0 else 0.0
    
    def _has_structure(self, features: Dict[str, Any], structure: str) -> bool:
        """Check if features contain a specific structure"""
        structure_map = {
            "recursion": features.get("has_recursion", False),
            "loops": features.get("has_loops", False),
            "nested_loops": features.get("has_nested_loops", False),
            "comparison": features.get("has_comparison", False),
            "swap": features.get("has_swap", False),
            "partition": features.get("has_partition", False) or 
                         (features.get("has_comparison", False) and features.get("has_array_ops", False)),
            "merge": features.get("has_merge", False) or 
                     ("concat" in features.get("function_calls", [])),
            "divide": features.get("has_divide", False),
            "array_slice": features.get("has_array_ops", False),
            "array_concat": features.get("has_merge", False),
            "pivot_selection": features.get("has_array_ops", False),
            "queue": features.get("has_queue_ops", False),
            "stack": features.get("has_stack_ops", False),
            "visited_tracking": "visited" in str(features.get("variable_patterns", [])),
            "neighbor_iteration": features.get("has_loops", False),
            "loop_or_recursion": features.get("has_loops", False) or features.get("has_recursion", False),
            "recursion_or_stack": features.get("has_recursion", False) or features.get("has_stack_ops", False),
            "boundary_update": features.get("has_comparison", False),
            "heapify": "heapify" in features.get("function_calls", []),
            "optimization_flag": "swapped" in str(features.get("variable_patterns", [])),
            "early_termination": features.get("has_base_case", False),
            "base_case": features.get("has_base_case", False),
            "build_heap": "build" in features.get("function_calls", []),
            "extract_max": "extract" in features.get("function_calls", [])
        }
        
        return structure_map.get(structure, False)
    
    def _matches_pattern(self, features: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if features match a specific pattern"""
        pattern_type = pattern.get("type")
        pattern_name = pattern.get("pattern")
        
        # Pattern matching logic
        if pattern_type == "base_case" and pattern_name == "early_return_on_length":
            return features.get("has_base_case", False)
            
        elif pattern_type == "pivot" and pattern_name == "element_selection":
            return features.get("has_array_ops", False)
            
        elif pattern_type == "partition" and pattern_name == "split_by_comparison":
            return features.get("has_comparison", False) and features.get("has_array_ops", False)
            
        elif pattern_type == "recursion" and pattern_name == "self_call_on_partitions":
            return features.get("has_recursion", False)
            
        elif pattern_type == "merge" and pattern_name == "combine_results":
            return features.get("has_merge", False) or features.get("has_array_ops", False)
            
        elif pattern_type == "outer_loop" and pattern_name == "iterate_array_length":
            loops = features.get("loop_patterns", [])
            return any(loop.get("depth", 0) == 0 for loop in loops)
            
        elif pattern_type == "inner_loop" and pattern_name == "iterate_with_boundary":
            return features.get("has_nested_loops", False)
            
        elif pattern_type == "comparison" and pattern_name == "adjacent_elements":
            return features.get("has_comparison", False)
            
        elif pattern_type == "swap" and pattern_name == "exchange_elements":
            return features.get("has_swap", False)
            
        return False
    
    def _get_matched_structures(self, features: Dict[str, Any], signature: AlgorithmSignature) -> List[str]:
        """Get list of matched structures"""
        matched = []
        
        for structure in signature.required_structures:
            if self._has_structure(features, structure):
                matched.append(structure)
                
        for structure in signature.optional_structures:
            if self._has_structure(features, structure):
                matched.append(structure)
                
        return matched
    
    def _gather_evidence(self, features: Dict[str, Any], signature: AlgorithmSignature) -> Dict[str, Any]:
        """Gather evidence for algorithm detection"""
        evidence = {
            "features_found": {},
            "patterns_matched": []
        }
        
        # Add found features
        for key, value in features.items():
            if value and not key.endswith("_patterns") and not key == "function_calls":
                evidence["features_found"][key] = value
                
        # Add matched patterns
        for pattern in signature.structural_patterns:
            if self._matches_pattern(features, pattern):
                evidence["patterns_matched"].append(pattern["pattern"])
                
        return evidence


# Integration function for CopycatM
def detect_algorithms_from_ast(ast_node: Any, language: str = "python") -> List[Dict[str, Any]]:
    """
    Main entry point for AST-based algorithm detection.
    
    Args:
        ast_node: The AST node to analyze (Python ast.Node or tree-sitter Node)
        language: The programming language ("python", "javascript", etc.)
        
    Returns:
        List of detected algorithms with confidence scores
    """
    detector = ASTAlgorithmDetector()
    return detector.detect_algorithm(ast_node, language)