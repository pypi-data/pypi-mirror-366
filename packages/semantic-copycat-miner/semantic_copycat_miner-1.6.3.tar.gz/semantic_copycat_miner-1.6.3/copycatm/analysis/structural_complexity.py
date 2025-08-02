"""
Structural complexity analyzer for unknown algorithm detection.
"""

import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class StructuralComplexityAnalyzer:
    """Analyzes structural complexity of code to detect unknown algorithms."""
    
    def __init__(self):
        """Initialize the structural complexity analyzer."""
        self.computational_primitives = {
            'arithmetic': ['+', '-', '*', '/', '%', '**', '//', '<<', '>>', '&', '|', '^', '~'],
            'comparison': ['<', '>', '<=', '>=', '==', '!=', 'is', 'in'],
            'logical': ['and', 'or', 'not', '&&', '||', '!'],
            'assignment': ['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='],
            'memory': ['new', 'delete', 'malloc', 'free', 'alloc', 'dealloc'],
            'array': ['[]', 'push', 'pop', 'shift', 'unshift', 'slice', 'splice'],
            'bitwise': ['&', '|', '^', '~', '<<', '>>'],
        }
        
    def analyze_complexity(self, ast_tree: Any, language: str) -> Dict[str, Any]:
        """
        Analyze structural complexity of code.
        
        Returns:
            Dictionary containing complexity metrics and patterns
        """
        try:
            # Extract functions
            functions = self._extract_functions(ast_tree, language)
            
            if not functions:
                return self._empty_analysis()
            
            # Analyze each function
            complex_functions = []
            for func in functions:
                analysis = self._analyze_function_complexity(func, language)
                if analysis['is_complex']:
                    complex_functions.append(analysis)
            
            # Generate algorithmic fingerprint
            fingerprint = self._generate_algorithmic_fingerprint(complex_functions)
            
            return {
                'total_functions': len(functions),
                'complex_functions': len(complex_functions),
                'algorithmic_fingerprint': fingerprint,
                'complexity_metrics': self._aggregate_metrics(complex_functions),
                'unique_patterns': self._extract_unique_patterns(complex_functions),
                'functions': complex_functions[:10]  # Limit output
            }
            
        except Exception as e:
            logger.debug(f"Structural complexity analysis failed: {e}")
            return self._empty_analysis()
    
    def _extract_functions(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Extract functions from AST."""
        functions = []
        
        try:
            if hasattr(ast_tree, 'root'):
                # TreeSitterAST - traverse the tree manually
                functions = self._extract_functions_from_tree_sitter(ast_tree.root, ast_tree.code, language)
                        
            elif hasattr(ast_tree, 'functions'):
                # FallbackAST
                functions = ast_tree.functions
                
        except Exception as e:
            logger.debug(f"Function extraction failed: {e}")
            
        return functions
    
    def _extract_functions_from_tree_sitter(self, node: Any, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract functions from tree-sitter node."""
        functions = []
        
        # Define function node types per language
        function_types = {
            'javascript': ['function_declaration', 'function_expression', 'arrow_function', 'method_definition'],
            'typescript': ['function_declaration', 'function_expression', 'arrow_function', 'method_definition'],
            'python': ['function_definition'],
            'c': ['function_definition'],
            'cpp': ['function_definition'],
            'java': ['method_declaration'],
        }
        
        target_types = function_types.get(language, [])
        
        # Recursive traversal
        if hasattr(node, 'type') and node.type in target_types:
            func_info = self._extract_function_info(node, code, language)
            if func_info['lines'] > 0:  # Only add if we got valid info
                functions.append(func_info)
        
        # Traverse children
        if hasattr(node, 'children'):
            for child in node.children:
                functions.extend(self._extract_functions_from_tree_sitter(child, code, language))
        
        return functions
    
    def _extract_function_info(self, node: Any, code: str, language: str) -> Dict[str, Any]:
        """Extract function information from AST node."""
        try:
            # Get function name
            name = 'anonymous'
            if hasattr(node, 'child_by_field_name'):
                name_node = node.child_by_field_name('name')
                if name_node and hasattr(name_node, 'text'):
                    name = name_node.text.decode('utf-8')
            elif hasattr(node, 'children'):
                # Try to find identifier in children
                for child in node.children:
                    if hasattr(child, 'type') and child.type == 'identifier':
                        if hasattr(child, 'text'):
                            name = child.text.decode('utf-8')
                            break
            
            # Get function body using byte offsets
            body = ''
            if hasattr(node, 'start_byte') and hasattr(node, 'end_byte'):
                try:
                    start_byte = node.start_byte
                    end_byte = node.end_byte
                    body = code[start_byte:end_byte]
                except:
                    # Fallback to text attribute
                    if hasattr(node, 'text'):
                        body = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            elif hasattr(node, 'text'):
                body = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Get line numbers
            start_line = 0
            end_line = 0
            if hasattr(node, 'start_point') and hasattr(node, 'end_point'):
                start_line = node.start_point[0]
                end_line = node.end_point[0]
            
            return {
                'name': name,
                'body': body,
                'lines': end_line - start_line + 1,
                'start_line': start_line,
                'end_line': end_line,
                'ast_node': node
            }
            
        except Exception as e:
            logger.debug(f"Function info extraction failed: {e}")
            return {
                'name': 'unknown',
                'body': '',
                'lines': 0,
                'start_line': 0,
                'end_line': 0,
                'ast_node': None
            }
    
    def _analyze_function_complexity(self, func: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Analyze complexity of a single function."""
        body = func.get('body', '')
        
        # Calculate various complexity metrics
        metrics = {
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(body),
            'nesting_depth': self._calculate_nesting_depth(body),
            'loop_complexity': self._analyze_loop_patterns(body),
            'conditional_complexity': self._analyze_conditional_patterns(body),
            'operation_density': self._calculate_operation_density(body),
            'unique_operations': self._extract_unique_operations(body),
            'data_flow_complexity': self._analyze_data_flow(body),
            'computational_primitives': self._extract_computational_primitives(body),
        }
        
        # Calculate overall complexity score
        complexity_score = self._calculate_overall_complexity(metrics)
        
        # Determine if function is complex enough to be an unknown algorithm
        is_complex = (
            complexity_score > 0.5 and
            func['lines'] > 5 and
            len(metrics['unique_operations']) > 10
        )
        
        # Generate operation n-grams for pattern detection
        operation_ngrams = self._generate_operation_ngrams(body, n=3)
        
        return {
            'name': func['name'],
            'lines': func['lines'],
            'complexity_score': complexity_score,
            'is_complex': is_complex,
            'metrics': metrics,
            'operation_ngrams': operation_ngrams[:10],  # Top 10 patterns
            'structural_hash': self._generate_structural_hash(metrics, operation_ngrams)
        }
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        # Count decision points
        decision_keywords = [
            r'\bif\b', r'\belif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b',
            r'\bcase\b', r'\bcatch\b', r'\b\?\s*:', r'\&\&', r'\|\|'
        ]
        
        complexity = 1  # Base complexity
        for keyword in decision_keywords:
            complexity += len(re.findall(keyword, code))
        
        return complexity
    
    def _calculate_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char in '{[(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '}])':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _analyze_loop_patterns(self, code: str) -> Dict[str, int]:
        """Analyze loop patterns in code."""
        patterns = {
            'for_loops': len(re.findall(r'\bfor\s*\(', code)),
            'while_loops': len(re.findall(r'\bwhile\s*\(', code)),
            'do_while_loops': len(re.findall(r'\bdo\s*\{', code)),
            'nested_loops': len(re.findall(r'for.*for|while.*while', code, re.DOTALL)),
            'infinite_loops': len(re.findall(r'while\s*\(\s*(?:true|1)\s*\)', code)),
        }
        return patterns
    
    def _analyze_conditional_patterns(self, code: str) -> Dict[str, int]:
        """Analyze conditional patterns."""
        patterns = {
            'if_statements': len(re.findall(r'\bif\s*\(', code)),
            'else_statements': len(re.findall(r'\belse\b', code)),
            'switch_statements': len(re.findall(r'\bswitch\s*\(', code)),
            'ternary_operators': len(re.findall(r'\?.*:', code)),
            'complex_conditions': len(re.findall(r'(?:\&\&|\|\|).*(?:\&\&|\|\|)', code)),
        }
        return patterns
    
    def _calculate_operation_density(self, code: str) -> float:
        """Calculate operation density (operations per line)."""
        lines = code.count('\n') + 1
        operations = sum(code.count(op) for ops in self.computational_primitives.values() 
                        for op in ops if isinstance(op, str) and len(op) <= 2)
        return operations / lines if lines > 0 else 0
    
    def _extract_unique_operations(self, code: str) -> List[str]:
        """Extract unique operations used in code."""
        operations = set()
        
        # Extract all operators
        operator_pattern = r'(?:[\+\-\*/%&\|^~<>=!]+|<<|>>|&&|\|\||==|!=|<=|>=)'
        for match in re.finditer(operator_pattern, code):
            operations.add(match.group())
        
        # Extract function calls
        func_pattern = r'\b(\w+)\s*\('
        for match in re.finditer(func_pattern, code):
            operations.add(f"call:{match.group(1)}")
        
        return sorted(list(operations))
    
    def _analyze_data_flow(self, code: str) -> Dict[str, int]:
        """Analyze data flow patterns."""
        patterns = {
            'assignments': len(re.findall(r'[^=<>!]=(?!=)', code)),
            'array_accesses': len(re.findall(r'\[[\w\s\+\-\*\/]+\]', code)),
            'function_calls': len(re.findall(r'\b\w+\s*\(', code)),
            'returns': len(re.findall(r'\breturn\b', code)),
            'variable_refs': len(re.findall(r'\b[a-zA-Z_]\w*\b', code)),
        }
        return patterns
    
    def _extract_computational_primitives(self, code: str) -> Dict[str, int]:
        """Extract computational primitives used."""
        primitive_counts = defaultdict(int)
        
        for category, primitives in self.computational_primitives.items():
            for primitive in primitives:
                if isinstance(primitive, str):
                    if len(primitive) <= 2:
                        # For operators, use word boundaries where appropriate
                        count = code.count(primitive)
                    else:
                        # For keywords, use word boundaries
                        count = len(re.findall(rf'\b{re.escape(primitive)}\b', code))
                    if count > 0:
                        primitive_counts[category] += count
        
        return dict(primitive_counts)
    
    def _calculate_overall_complexity(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall complexity score (0-1)."""
        score = 0.0
        
        # Cyclomatic complexity contribution
        score += min(metrics['cyclomatic_complexity'] / 20, 1.0) * 0.25
        
        # Nesting depth contribution
        score += min(metrics['nesting_depth'] / 10, 1.0) * 0.15
        
        # Loop complexity contribution
        loop_score = sum(metrics['loop_complexity'].values())
        score += min(loop_score / 10, 1.0) * 0.20
        
        # Operation density contribution
        score += min(metrics['operation_density'] / 5, 1.0) * 0.15
        
        # Unique operations contribution
        score += min(len(metrics['unique_operations']) / 20, 1.0) * 0.15
        
        # Data flow complexity contribution
        data_flow_score = metrics['data_flow_complexity']['assignments'] + \
                         metrics['data_flow_complexity']['array_accesses']
        score += min(data_flow_score / 20, 1.0) * 0.10
        
        return score
    
    def _generate_operation_ngrams(self, code: str, n: int = 3) -> List[Tuple[str, int]]:
        """Generate n-grams of operations for pattern detection."""
        # Extract sequence of operations
        operations = []
        
        # Simple tokenization for operations
        tokens = re.findall(r'[\+\-\*/%&\|^~<>=!]+|<<|>>|&&|\|\||==|!=|<=|>=|\w+', code)
        
        for token in tokens:
            if re.match(r'[+\-*/%&|^~<>=!]+|<<|>>|&&|\|\||==|!=|<=|>=', token):
                operations.append(token)
            elif token in ['if', 'for', 'while', 'return', 'break', 'continue']:
                operations.append(f"@{token}")
        
        # Generate n-grams
        ngrams = []
        for i in range(len(operations) - n + 1):
            ngram = tuple(operations[i:i+n])
            ngrams.append(ngram)
        
        # Count occurrences
        ngram_counts = Counter(ngrams)
        
        # Return top patterns
        return ngram_counts.most_common(20)
    
    def _generate_structural_hash(self, metrics: Dict[str, Any], 
                                 ngrams: List[Tuple[str, int]]) -> str:
        """Generate a hash representing the structural complexity."""
        # Create a canonical representation
        data = {
            'cyclomatic': metrics['cyclomatic_complexity'],
            'nesting': metrics['nesting_depth'],
            'loops': sum(metrics['loop_complexity'].values()),
            'density': round(metrics['operation_density'], 2),
            'unique_ops': len(metrics['unique_operations']),
            'top_patterns': [str(ng[0]) for ng in ngrams[:5]]
        }
        
        # Generate hash
        canonical = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    def _generate_algorithmic_fingerprint(self, complex_functions: List[Dict]) -> str:
        """Generate an algorithmic fingerprint for the file."""
        if not complex_functions:
            return ""
        
        # Aggregate key metrics
        fingerprint_data = {
            'num_complex': len(complex_functions),
            'avg_complexity': sum(f['complexity_score'] for f in complex_functions) / len(complex_functions),
            'total_lines': sum(f['lines'] for f in complex_functions),
            'unique_patterns': len(set(
                pattern for f in complex_functions 
                for pattern, _ in f.get('operation_ngrams', [])
            )),
            'structural_hashes': [f['structural_hash'] for f in complex_functions[:5]]
        }
        
        # Generate fingerprint
        canonical = json.dumps(fingerprint_data, sort_keys=True)
        return "ALG-" + hashlib.sha256(canonical.encode()).hexdigest()[:12].upper()
    
    def _aggregate_metrics(self, complex_functions: List[Dict]) -> Dict[str, Any]:
        """Aggregate metrics from all complex functions."""
        if not complex_functions:
            return {}
        
        return {
            'avg_cyclomatic_complexity': sum(f['metrics']['cyclomatic_complexity'] 
                                           for f in complex_functions) / len(complex_functions),
            'max_nesting_depth': max(f['metrics']['nesting_depth'] 
                                   for f in complex_functions),
            'total_loops': sum(sum(f['metrics']['loop_complexity'].values()) 
                             for f in complex_functions),
            'avg_operation_density': sum(f['metrics']['operation_density'] 
                                       for f in complex_functions) / len(complex_functions),
        }
    
    def _extract_unique_patterns(self, complex_functions: List[Dict]) -> List[str]:
        """Extract unique patterns across all complex functions."""
        all_patterns = []
        
        for func in complex_functions:
            for pattern, count in func.get('operation_ngrams', []):
                if count > 1:  # Only include repeated patterns
                    all_patterns.append(' '.join(pattern))
        
        # Return unique patterns
        return list(set(all_patterns))[:20]  # Limit to 20
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            'total_functions': 0,
            'complex_functions': 0,
            'algorithmic_fingerprint': '',
            'complexity_metrics': {},
            'unique_patterns': [],
            'functions': []
        }