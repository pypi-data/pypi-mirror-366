"""
Function-level TLSH hashing for enhanced code similarity detection.
"""

import ast
import re
import hashlib
from typing import Dict, List, Any

from .fuzzy import FuzzyHasher


class FunctionLevelHasher:
    """Generate TLSH hashes at function granularity for better similarity detection."""
    
    def __init__(self):
        self.fuzzy_hasher = FuzzyHasher()
        self.min_function_length = 20  # Minimum characters for meaningful TLSH
    
    def extract_functions_from_ast(self, tree: ast.AST, source: str) -> List[Dict[str, Any]]:
        """Extract function definitions from AST with their source code."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    # Get function bounds
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                    
                    # Extract source lines
                    lines = source.split('\n')
                    func_lines = lines[start_line:end_line]
                    func_source = '\n'.join(func_lines)
                    
                    # Get function metadata
                    func_info = {
                        'name': node.name,
                        'start_line': start_line + 1,
                        'end_line': end_line,
                        'source': func_source,
                        'parameters': self._extract_parameters(node),
                        'parameter_signature': self.extract_parameter_signatures(node),
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'decorators': [d.id if isinstance(d, ast.Name) else str(d) 
                                     for d in node.decorator_list]
                    }
                    
                    functions.append(func_info)
                except Exception:
                    # Skip functions we can't extract properly
                    continue
        
        return functions
    
    def extract_functions_from_text(self, source: str, language: str) -> List[Dict[str, Any]]:
        """Extract functions from source code using regex patterns."""
        functions = []
        
        if language == 'python':
            pattern = r'^(async\s+)?def\s+(\w+)\s*\((.*?)\):\s*\n((?:\s{4,}.*\n?)*)'
            for match in re.finditer(pattern, source, re.MULTILINE):
                is_async = bool(match.group(1))
                name = match.group(2)
                params = match.group(3)
                body = match.group(4)
                
                func_info = {
                    'name': name,
                    'start_line': source[:match.start()].count('\n') + 1,
                    'end_line': source[:match.end()].count('\n') + 1,
                    'source': match.group(0),
                    'parameters': params.split(',') if params else [],
                    'is_async': is_async,
                    'decorators': []
                }
                functions.append(func_info)
        
        elif language in ['javascript', 'typescript']:
            # Match various JS function patterns
            patterns = [
                # Traditional function
                r'function\s+(\w+)\s*\((.*?)\)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}',
                # Arrow function with name
                r'const\s+(\w+)\s*=\s*(?:async\s+)?\((.*?)\)\s*=>\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}',
                # Method in class/object
                r'(\w+)\s*\((.*?)\)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}',
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, source, re.MULTILINE | re.DOTALL):
                    name = match.group(1)
                    params = match.group(2)
                    body = match.group(3) if len(match.groups()) > 2 else ''
                    
                    func_info = {
                        'name': name,
                        'start_line': source[:match.start()].count('\n') + 1,
                        'end_line': source[:match.end()].count('\n') + 1,
                        'source': match.group(0),
                        'parameters': [p.strip() for p in params.split(',') if p.strip()],
                        'is_async': 'async' in match.group(0),
                        'decorators': []
                    }
                    functions.append(func_info)
        
        elif language in ['c', 'cpp', 'java']:
            # Match C/C++/Java function patterns
            pattern = r'(?:(?:public|private|protected|static|virtual|inline|extern)\s+)*(?:\w+\s+)+(\w+)\s*\((.*?)\)\s*(?:const\s*)?{([^{}]*(?:{[^{}]*}[^{}]*)*)'
            
            for match in re.finditer(pattern, source, re.MULTILINE | re.DOTALL):
                name = match.group(1)
                params = match.group(2)
                body = match.group(3)
                
                func_info = {
                    'name': name,
                    'start_line': source[:match.start()].count('\n') + 1,
                    'end_line': source[:match.end()].count('\n') + 1,
                    'source': match.group(0),
                    'parameters': [p.strip() for p in params.split(',') if p.strip()],
                    'is_async': False,
                    'decorators': []
                }
                functions.append(func_info)
        
        return functions
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[str]:
        """Extract parameter names from function definition."""
        params = []
        
        # Regular arguments
        for arg in node.args.args:
            params.append(arg.arg)
        
        # *args
        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")
        
        # **kwargs
        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")
        
        return params
    
    def extract_parameter_signatures(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract detailed parameter signatures including types and defaults."""
        signature = {
            'positional': [],
            'keyword_only': [],
            'has_varargs': False,
            'has_kwargs': False,
            'defaults': [],
            'type_annotations': {}
        }
        
        # Extract positional arguments with type annotations
        for i, arg in enumerate(node.args.args):
            param_info = {'name': arg.arg}
            
            # Check for type annotation
            if arg.annotation:
                param_info['type'] = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)
                signature['type_annotations'][arg.arg] = param_info['type']
            
            signature['positional'].append(param_info)
        
        # Extract default values
        defaults_start = len(node.args.args) - len(node.args.defaults)
        for i, default in enumerate(node.args.defaults):
            param_idx = defaults_start + i
            if param_idx < len(signature['positional']):
                default_val = ast.unparse(default) if hasattr(ast, 'unparse') else str(default)
                signature['positional'][param_idx]['default'] = default_val
                signature['defaults'].append({
                    'param': signature['positional'][param_idx]['name'],
                    'value': default_val
                })
        
        # Extract keyword-only arguments
        for arg in node.args.kwonlyargs:
            kw_param = {'name': arg.arg}
            if arg.annotation:
                kw_param['type'] = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)
                signature['type_annotations'][arg.arg] = kw_param['type']
            signature['keyword_only'].append(kw_param)
        
        # Check for *args and **kwargs
        if node.args.vararg:
            signature['has_varargs'] = True
            signature['varargs_name'] = node.args.vararg.arg
            if node.args.vararg.annotation:
                signature['varargs_type'] = ast.unparse(node.args.vararg.annotation) if hasattr(ast, 'unparse') else str(node.args.vararg.annotation)
        
        if node.args.kwarg:
            signature['has_kwargs'] = True
            signature['kwargs_name'] = node.args.kwarg.arg
            if node.args.kwarg.annotation:
                signature['kwargs_type'] = ast.unparse(node.args.kwarg.annotation) if hasattr(ast, 'unparse') else str(node.args.kwarg.annotation)
        
        # Extract return type
        if node.returns:
            signature['return_type'] = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        # Create signature hash
        sig_components = []
        sig_components.append(f"pos:{len(signature['positional'])}")
        sig_components.append(f"kw:{len(signature['keyword_only'])}")
        sig_components.append(f"varargs:{signature['has_varargs']}")
        sig_components.append(f"kwargs:{signature['has_kwargs']}")
        sig_components.append(f"types:{len(signature['type_annotations'])}")
        
        signature['signature_hash'] = hashlib.md5('|'.join(sig_components).encode()).hexdigest()[:8]
        
        return signature
    
    def hash_functions(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate TLSH hashes for each function."""
        hashed_functions = []
        
        for func in functions:
            source = func['source']
            
            # Skip very short functions
            if len(source) < self.min_function_length:
                continue
            
            # Generate TLSH hash
            tlsh_hash = self.fuzzy_hasher.tlsh(source)
            
            # Also generate normalized hash (without variable names)
            normalized_source = self._normalize_function(source, func['name'])
            normalized_hash = self.fuzzy_hasher.tlsh(normalized_source)
            
            hashed_func = {
                **func,
                'tlsh': tlsh_hash,
                'normalized_tlsh': normalized_hash,
                'size': len(source),
                'line_count': func['end_line'] - func['start_line'] + 1,
                'parameter_signature': func.get('parameter_signature', {})
            }
            
            hashed_functions.append(hashed_func)
        
        return hashed_functions
    
    def _normalize_function(self, source: str, func_name: str) -> str:
        """Normalize function source for similarity comparison."""
        normalized = source
        
        # Replace function name with generic placeholder
        normalized = re.sub(rf'\b{re.escape(func_name)}\b', 'FUNC', normalized)
        
        # Replace variable names with generic placeholders
        # This is a simple approach - could be more sophisticated with AST
        var_pattern = r'\b([a-zA-Z_]\w*)\b'
        var_counter = 0
        var_map = {}
        
        def replace_var(match):
            nonlocal var_counter
            var_name = match.group(1)
            
            # Skip keywords and common functions
            keywords = {'def', 'if', 'else', 'elif', 'for', 'while', 'return', 
                       'import', 'from', 'class', 'try', 'except', 'finally',
                       'with', 'as', 'lambda', 'yield', 'await', 'async',
                       'function', 'const', 'let', 'var', 'new', 'this',
                       'int', 'float', 'str', 'bool', 'list', 'dict', 'set',
                       'print', 'len', 'range', 'open', 'True', 'False', 'None'}
            
            if var_name in keywords or var_name == 'FUNC':
                return var_name
            
            if var_name not in var_map:
                var_map[var_name] = f'VAR{var_counter}'
                var_counter += 1
            
            return var_map[var_name]
        
        normalized = re.sub(var_pattern, replace_var, normalized)
        
        # Remove comments
        normalized = re.sub(r'#.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'//.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def compare_function_sets(self, functions1: List[Dict[str, Any]], 
                            functions2: List[Dict[str, Any]], 
                            threshold: int = 100) -> List[Dict[str, Any]]:
        """Compare two sets of functions and find similarities."""
        similarities = []
        
        for f1 in functions1:
            if 'tlsh' not in f1:
                continue
                
            for f2 in functions2:
                if 'tlsh' not in f2:
                    continue
                
                # Compare original TLSH
                orig_score = self.fuzzy_hasher.tlsh_similarity(f1['tlsh'], f2['tlsh'])
                
                # Compare normalized TLSH
                norm_score = self.fuzzy_hasher.tlsh_similarity(
                    f1['normalized_tlsh'], f2['normalized_tlsh']
                )
                
                # Use the better score
                best_score = min(orig_score, norm_score)
                
                if best_score <= threshold:
                    similarities.append({
                        'function1': f1['name'],
                        'function2': f2['name'],
                        'file1_line': f1['start_line'],
                        'file2_line': f2['start_line'],
                        'original_score': orig_score,
                        'normalized_score': norm_score,
                        'best_score': best_score,
                        'size_ratio': min(f1['size'], f2['size']) / max(f1['size'], f2['size'])
                    })
        
        # Sort by best score (lower is more similar)
        similarities.sort(key=lambda x: x['best_score'])
        
        return similarities
    
    def cluster_similar_functions(self, functions: List[Dict[str, Any]], 
                                threshold: int = 50) -> List[List[Dict[str, Any]]]:
        """Cluster functions by similarity."""
        if not functions:
            return []
        
        # Filter functions with TLSH hashes
        hashable_functions = [f for f in functions if 'normalized_tlsh' in f]
        
        clusters = []
        remaining = hashable_functions.copy()
        
        while remaining:
            # Start new cluster
            seed = remaining.pop(0)
            cluster = [seed]
            
            # Find similar functions
            i = 0
            while i < len(remaining):
                score = self.fuzzy_hasher.tlsh_similarity(
                    seed['normalized_tlsh'], 
                    remaining[i]['normalized_tlsh']
                )
                
                if score <= threshold:
                    cluster.append(remaining.pop(i))
                else:
                    i += 1
            
            clusters.append(cluster)
        
        # Sort clusters by size
        clusters.sort(key=len, reverse=True)
        
        return clusters
    
    def generate_function_signatures(self, functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate various signatures for a set of functions."""
        signatures = {
            'function_count': len(functions),
            'total_size': sum(f.get('size', 0) for f in functions),
            'total_lines': sum(f.get('line_count', 0) for f in functions),
            'function_hashes': {},
            'parameter_patterns': {},
            'parameter_signatures': {},
            'size_distribution': {}
        }
        
        # Collect function hashes and signatures
        for func in functions:
            if 'tlsh' in func:
                signatures['function_hashes'][func['name']] = {
                    'tlsh': func['tlsh'],
                    'normalized_tlsh': func['normalized_tlsh'],
                    'size': func['size'],
                    'parameters': func['parameters']
                }
            
            # Add parameter signature if available
            if 'parameter_signature' in func:
                signatures['parameter_signatures'][func['name']] = func['parameter_signature']
        
        # Analyze parameter patterns
        param_counts = {}
        type_annotation_counts = {}
        for func in functions:
            param_count = len(func.get('parameters', []))
            param_counts[param_count] = param_counts.get(param_count, 0) + 1
            
            # Count type annotations
            if 'parameter_signature' in func:
                type_count = len(func['parameter_signature'].get('type_annotations', {}))
                type_annotation_counts[type_count] = type_annotation_counts.get(type_count, 0) + 1
        
        signatures['parameter_patterns'] = param_counts
        signatures['type_annotation_patterns'] = type_annotation_counts
        
        # Size distribution
        size_bins = {'small': 0, 'medium': 0, 'large': 0}
        for func in functions:
            size = func.get('size', 0)
            if size < 100:
                size_bins['small'] += 1
            elif size < 500:
                size_bins['medium'] += 1
            else:
                size_bins['large'] += 1
        signatures['size_distribution'] = size_bins
        
        return signatures