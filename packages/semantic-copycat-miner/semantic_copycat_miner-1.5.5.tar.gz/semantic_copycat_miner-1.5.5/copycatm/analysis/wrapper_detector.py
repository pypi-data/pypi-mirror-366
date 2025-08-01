"""
Wrapper and integration pattern detection for identifying code that wraps or integrates existing libraries.
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
import networkx as nx


class WrapperDetector:
    """Detect wrapper and integration patterns in code."""
    
    def __init__(self):
        # Common wrapper patterns
        self.wrapper_patterns = {
            'delegation': {
                'description': 'Methods that simply delegate to another object',
                'indicators': ['single_call', 'return_call', 'minimal_logic']
            },
            'adapter': {
                'description': 'Adapts one interface to another',
                'indicators': ['interface_mapping', 'parameter_transformation', 'return_transformation']
            },
            'facade': {
                'description': 'Simplifies complex API into simpler interface',
                'indicators': ['multiple_internal_calls', 'simplified_parameters', 'aggregated_results']
            },
            'proxy': {
                'description': 'Controls access to another object',
                'indicators': ['access_control', 'lazy_initialization', 'caching']
            },
            'decorator': {
                'description': 'Adds functionality to existing objects',
                'indicators': ['before_after_logic', 'call_wrapped', 'enhanced_return']
            },
            'factory_wrapper': {
                'description': 'Wraps object creation logic',
                'indicators': ['create_methods', 'configuration', 'instance_management']
            }
        }
        
        # Library integration patterns
        self.integration_patterns = {
            'api_client': ['request', 'response', 'endpoint', 'auth'],
            'database_wrapper': ['query', 'execute', 'connection', 'transaction'],
            'file_handler': ['open', 'read', 'write', 'close'],
            'network_wrapper': ['socket', 'connect', 'send', 'receive'],
            'ui_wrapper': ['window', 'button', 'event', 'render'],
            'ml_wrapper': ['model', 'predict', 'train', 'transform']
        }
        
    def detect_wrapper_patterns(self, code: str, language: str, 
                              ast_tree: Optional[Any] = None) -> Dict[str, Any]:
        """Detect wrapper and integration patterns in code."""
        results = {
            'is_wrapper': False,
            'wrapper_types': [],
            'confidence': 0.0,
            'wrapped_libraries': [],
            'integration_patterns': [],
            'evidence': {},
            'metrics': {}
        }
        
        if language == "python" and ast_tree is None:
            try:
                ast_tree = ast.parse(code)
            except:
                pass
        
        # Analyze imports to identify potential wrapped libraries
        imports = self._extract_imports(code, language, ast_tree)
        results['wrapped_libraries'] = self._identify_wrapped_libraries(imports)
        
        # Analyze functions/methods for wrapper patterns
        if ast_tree and hasattr(ast_tree, '__class__') and ast_tree.__class__.__module__ == 'ast':
            wrapper_analysis = self._analyze_python_wrappers(ast_tree, code)
        else:
            wrapper_analysis = self._analyze_generic_wrappers(code, language)
        
        results.update(wrapper_analysis)
        
        # Detect integration patterns
        integration_results = self._detect_integration_patterns(code, imports)
        results['integration_patterns'] = integration_results['patterns']
        
        # Calculate overall confidence
        results['confidence'] = self._calculate_confidence(results)
        results['is_wrapper'] = results['confidence'] > 0.5
        
        return results
    
    def _extract_imports(self, code: str, language: str, ast_tree: Any) -> List[Dict[str, str]]:
        """Extract import statements."""
        imports = []
        
        if ast_tree and hasattr(ast_tree, '__class__') and ast_tree.__class__.__module__ == 'ast':
            # Python AST
            class ImportVisitor(ast.NodeVisitor):
                def visit_Import(self, node):
                    for alias in node.names:
                        imports.append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'type': 'import'
                        })
                
                def visit_ImportFrom(self, node):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'type': 'from_import'
                        })
            
            ImportVisitor().visit(ast_tree)
        else:
            # Pattern-based extraction
            if language == "python":
                # import module
                for match in re.finditer(r'import\s+([\w.]+)(?:\s+as\s+(\w+))?', code):
                    imports.append({
                        'module': match.group(1),
                        'alias': match.group(2),
                        'type': 'import'
                    })
                
                # from module import name
                for match in re.finditer(r'from\s+([\w.]+)\s+import\s+([\w*,\s]+)', code):
                    module = match.group(1)
                    names = match.group(2).split(',')
                    for name in names:
                        name = name.strip()
                        if ' as ' in name:
                            name, alias = name.split(' as ')
                            imports.append({
                                'module': module,
                                'name': name.strip(),
                                'alias': alias.strip(),
                                'type': 'from_import'
                            })
                        else:
                            imports.append({
                                'module': module,
                                'name': name,
                                'type': 'from_import'
                            })
            
            elif language in ["javascript", "typescript"]:
                # ES6 imports
                for match in re.finditer(r'import\s+(?:{([^}]+)}|(\w+))\s+from\s+["\']([^"\']+)["\']', code):
                    module = match.group(3)
                    if match.group(1):  # Named imports
                        names = match.group(1).split(',')
                        for name in names:
                            imports.append({
                                'module': module,
                                'name': name.strip(),
                                'type': 'named_import'
                            })
                    else:  # Default import
                        imports.append({
                            'module': module,
                            'name': match.group(2),
                            'type': 'default_import'
                        })
        
        return imports
    
    def _identify_wrapped_libraries(self, imports: List[Dict]) -> List[str]:
        """Identify which libraries are being wrapped."""
        wrapped = []
        
        # Common libraries that are often wrapped
        common_wrapped = {
            'requests', 'urllib', 'http.client',  # HTTP
            'sqlite3', 'mysql', 'psycopg2', 'pymongo',  # Databases
            'pandas', 'numpy', 'scipy',  # Data processing
            'tensorflow', 'torch', 'sklearn',  # ML
            'boto3', 'google-cloud',  # Cloud services
            'flask', 'django', 'fastapi',  # Web frameworks
            'asyncio', 'threading', 'multiprocessing',  # Concurrency
            'logging', 'datetime', 'os', 'sys'  # System
        }
        
        for imp in imports:
            module = imp['module']
            # Check if it's a common wrapped library
            for lib in common_wrapped:
                if lib in module:
                    wrapped.append(lib)
                    break
        
        return list(set(wrapped))
    
    def _analyze_python_wrappers(self, tree: ast.AST, code: str) -> Dict[str, Any]:
        """Analyze Python AST for wrapper patterns."""
        results = {
            'wrapper_types': [],
            'evidence': {},
            'metrics': {}
        }
        
        class WrapperAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.classes = {}
                self.functions = {}
                self.current_class = None
                
            def visit_ClassDef(self, node):
                self.current_class = node.name
                self.classes[node.name] = {
                    'methods': {},
                    'attributes': [],
                    'base_classes': [base.id if isinstance(base, ast.Name) else str(base) 
                                   for base in node.bases]
                }
                self.generic_visit(node)
                self.current_class = None
            
            def visit_FunctionDef(self, node):
                func_info = self._analyze_function(node)
                
                if self.current_class:
                    self.classes[self.current_class]['methods'][node.name] = func_info
                else:
                    self.functions[node.name] = func_info
                
                self.generic_visit(node)
            
            def _analyze_function(self, node):
                """Analyze a function for wrapper patterns."""
                info = {
                    'name': node.name,
                    'params': len(node.args.args),
                    'calls': [],
                    'returns': [],
                    'has_single_call': False,
                    'has_delegation': False,
                    'complexity': 0
                }
                
                # Count statements and analyze patterns
                call_count = 0
                return_count = 0
                assignment_count = 0
                
                for stmt in node.body:
                    if isinstance(stmt, ast.Return):
                        return_count += 1
                        if isinstance(stmt.value, ast.Call):
                            info['returns'].append('call')
                            info['has_delegation'] = True
                    elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        call_count += 1
                        if isinstance(stmt.value.func, ast.Attribute):
                            info['calls'].append(stmt.value.func.attr)
                        elif isinstance(stmt.value.func, ast.Name):
                            info['calls'].append(stmt.value.func.id)
                    elif isinstance(stmt, ast.Assign):
                        assignment_count += 1
                
                info['has_single_call'] = call_count == 1 and return_count <= 1
                info['complexity'] = len(node.body)
                
                return info
        
        analyzer = WrapperAnalyzer()
        analyzer.visit(tree)
        
        # Detect wrapper patterns
        wrapper_types = set()
        evidence = defaultdict(list)
        
        # Check for delegation pattern
        delegation_count = 0
        for func_info in list(analyzer.functions.values()) + \
                        [m for c in analyzer.classes.values() for m in c['methods'].values()]:
            if func_info['has_delegation'] and func_info['complexity'] <= 3:
                delegation_count += 1
                evidence['delegation'].append(func_info['name'])
        
        if delegation_count >= 2:
            wrapper_types.add('delegation')
        
        # Check for adapter pattern
        if analyzer.classes:
            for class_name, class_info in analyzer.classes.items():
                # Check if class has init that stores wrapped object
                if '__init__' in class_info['methods']:
                    init_method = class_info['methods']['__init__']
                    if init_method['params'] >= 2:  # self + wrapped object
                        # Check if methods delegate to stored object
                        delegating_methods = sum(
                            1 for m in class_info['methods'].values()
                            if m['has_delegation'] and m['name'] != '__init__'
                        )
                        
                        if delegating_methods >= len(class_info['methods']) * 0.5:
                            wrapper_types.add('adapter')
                            evidence['adapter'].append(class_name)
        
        # Check for facade pattern
        complex_methods = sum(
            1 for func_info in analyzer.functions.values()
            if len(func_info['calls']) >= 3
        )
        
        if complex_methods >= 2:
            wrapper_types.add('facade')
            evidence['facade'].append(f"{complex_methods} methods with multiple internal calls")
        
        # Calculate metrics
        total_functions = len(analyzer.functions) + sum(
            len(c['methods']) for c in analyzer.classes.values()
        )
        
        if total_functions > 0:
            results['metrics'] = {
                'delegation_ratio': delegation_count / total_functions,
                'average_complexity': sum(
                    f['complexity'] for f in list(analyzer.functions.values()) +
                    [m for c in analyzer.classes.values() for m in c['methods'].values()]
                ) / total_functions,
                'class_count': len(analyzer.classes),
                'function_count': len(analyzer.functions)
            }
        
        results['wrapper_types'] = list(wrapper_types)
        results['evidence'] = dict(evidence)
        
        return results
    
    def _analyze_generic_wrappers(self, code: str, language: str) -> Dict[str, Any]:
        """Generic wrapper analysis using patterns."""
        results = {
            'wrapper_types': [],
            'evidence': {},
            'metrics': {}
        }
        
        # Count function definitions and calls
        if language in ["javascript", "typescript"]:
            func_pattern = r'(?:function\s+\w+|const\s+\w+\s*=.*?function|\w+\s*:\s*function)\s*\([^)]*\)\s*{'
            call_pattern = r'(\w+)\s*\('
        elif language in ["java", "c", "cpp"]:
            func_pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*{'
            call_pattern = r'(\w+)\s*\('
        else:
            func_pattern = r'def\s+\w+\s*\([^)]*\):'
            call_pattern = r'(\w+)\s*\('
        
        functions = list(re.finditer(func_pattern, code))
        
        # Analyze each function
        wrapper_indicators = defaultdict(int)
        
        for i, func_match in enumerate(functions):
            # Extract function body (simplified)
            start = func_match.end()
            # Find next function or end of file
            end = functions[i + 1].start() if i + 1 < len(functions) else len(code)
            
            func_body = code[start:end]
            
            # Count patterns
            calls = re.findall(call_pattern, func_body)
            returns = len(re.findall(r'return\b', func_body))
            
            # Check for delegation
            if len(calls) == 1 and returns == 1:
                wrapper_indicators['delegation'] += 1
            
            # Check for multiple calls (facade)
            if len(calls) >= 3:
                wrapper_indicators['facade'] += 1
        
        # Determine wrapper types based on indicators
        if functions:
            func_count = len(functions)
            
            if wrapper_indicators['delegation'] >= func_count * 0.3:
                results['wrapper_types'].append('delegation')
                results['evidence']['delegation'] = f"{wrapper_indicators['delegation']} delegating functions"
            
            if wrapper_indicators['facade'] >= 2:
                results['wrapper_types'].append('facade')
                results['evidence']['facade'] = f"{wrapper_indicators['facade']} facade-like functions"
        
        return results
    
    def _detect_integration_patterns(self, code: str, imports: List[Dict]) -> Dict[str, List[str]]:
        """Detect library integration patterns."""
        patterns_found = defaultdict(list)
        
        # Check for API client patterns
        api_keywords = ['request', 'response', 'endpoint', 'api', 'client', 'auth', 'token']
        api_score = sum(1 for keyword in api_keywords if keyword in code.lower())
        if api_score >= 3:
            patterns_found['integration_patterns'].append('api_client')
        
        # Check for database wrapper patterns
        db_keywords = ['query', 'execute', 'select', 'insert', 'update', 'delete', 'connection', 'cursor']
        db_score = sum(1 for keyword in db_keywords if keyword in code.lower())
        if db_score >= 3:
            patterns_found['integration_patterns'].append('database_wrapper')
        
        # Check for file handler patterns
        file_keywords = ['open', 'read', 'write', 'close', 'file', 'path', 'stream']
        file_score = sum(1 for keyword in file_keywords if re.search(rf'\b{keyword}\b', code.lower()))
        if file_score >= 3:
            patterns_found['integration_patterns'].append('file_handler')
        
        # Check for ML wrapper patterns
        ml_keywords = ['model', 'predict', 'train', 'fit', 'transform', 'feature', 'label']
        ml_score = sum(1 for keyword in ml_keywords if keyword in code.lower())
        if ml_score >= 3:
            patterns_found['integration_patterns'].append('ml_wrapper')
        
        # Check imports for specific patterns
        for imp in imports:
            module = imp['module'].lower()
            
            if any(api in module for api in ['requests', 'urllib', 'httpx', 'aiohttp']):
                patterns_found['integration_patterns'].append('http_client_wrapper')
            
            if any(db in module for db in ['sqlite', 'mysql', 'postgres', 'mongo', 'redis']):
                patterns_found['integration_patterns'].append('database_integration')
            
            if any(ml in module for ml in ['tensorflow', 'torch', 'sklearn', 'keras']):
                patterns_found['integration_patterns'].append('ml_framework_wrapper')
        
        return {
            'patterns': list(set(patterns_found['integration_patterns']))
        }
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calculate confidence score for wrapper detection."""
        confidence = 0.0
        
        # Base confidence from wrapper types
        if results['wrapper_types']:
            confidence += 0.3 * len(results['wrapper_types'])
        
        # Boost for wrapped libraries
        if results['wrapped_libraries']:
            confidence += 0.2 * min(len(results['wrapped_libraries']) / 3, 1.0)
        
        # Boost for integration patterns
        if results['integration_patterns']:
            confidence += 0.2 * min(len(results['integration_patterns']) / 2, 1.0)
        
        # Boost from metrics
        metrics = results.get('metrics', {})
        if metrics.get('delegation_ratio', 0) > 0.3:
            confidence += 0.2
        
        if metrics.get('average_complexity', 10) < 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def analyze_wrapper_quality(self, wrapper_results: Dict) -> Dict[str, Any]:
        """Analyze the quality and characteristics of detected wrappers."""
        quality_assessment = {
            'abstraction_level': 'unknown',
            'value_added': [],
            'potential_issues': [],
            'recommendations': []
        }
        
        # Assess abstraction level
        if 'facade' in wrapper_results['wrapper_types']:
            quality_assessment['abstraction_level'] = 'high'
            quality_assessment['value_added'].append('Simplifies complex API')
        elif 'adapter' in wrapper_results['wrapper_types']:
            quality_assessment['abstraction_level'] = 'medium'
            quality_assessment['value_added'].append('Provides interface compatibility')
        elif 'delegation' in wrapper_results['wrapper_types']:
            quality_assessment['abstraction_level'] = 'low'
            quality_assessment['potential_issues'].append('Minimal value addition')
        
        # Check for potential issues
        metrics = wrapper_results.get('metrics', {})
        
        if metrics.get('delegation_ratio', 0) > 0.8:
            quality_assessment['potential_issues'].append('Excessive delegation - consider direct library usage')
        
        if metrics.get('average_complexity', 0) < 2:
            quality_assessment['potential_issues'].append('Thin wrapper - minimal logic added')
        
        # Provide recommendations
        if wrapper_results['confidence'] < 0.5:
            quality_assessment['recommendations'].append('Consider implementing more substantial logic')
        
        if not wrapper_results['integration_patterns']:
            quality_assessment['recommendations'].append('Add integration patterns for better library utilization')
        
        if len(wrapper_results['wrapped_libraries']) > 3:
            quality_assessment['recommendations'].append('Consider splitting into multiple specialized wrappers')
        
        return quality_assessment