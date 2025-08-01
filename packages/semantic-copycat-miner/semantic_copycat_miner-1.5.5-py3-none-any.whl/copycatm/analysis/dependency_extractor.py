"""
Import and dependency extraction for code fingerprinting.
"""

import ast
import re
import hashlib
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict


class DependencyExtractor:
    """Extract and fingerprint imports and dependencies from source code."""
    
    def __init__(self):
        # Common standard library modules by language
        self.stdlib_modules = {
            'python': {
                'os', 'sys', 're', 'json', 'datetime', 'time', 'math', 'random',
                'collections', 'itertools', 'functools', 'pathlib', 'typing',
                'urllib', 'http', 'socket', 'subprocess', 'threading', 'multiprocessing',
                'logging', 'argparse', 'configparser', 'csv', 'sqlite3', 'hashlib'
            },
            'javascript': {
                'fs', 'path', 'http', 'https', 'crypto', 'util', 'stream', 'events',
                'child_process', 'cluster', 'os', 'process', 'buffer', 'url', 'querystring'
            },
            'java': {
                'java.lang', 'java.util', 'java.io', 'java.net', 'java.nio', 'java.math',
                'java.security', 'java.text', 'java.time', 'javax.swing', 'javax.xml'
            }
        }
        
        # Common third-party packages
        self.common_packages = {
            'python': {
                'numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn', 'sklearn',
                'tensorflow', 'torch', 'keras', 'flask', 'django', 'requests',
                'pytest', 'pillow', 'opencv-cv', 'sqlalchemy', 'pydantic'
            },
            'javascript': {
                'react', 'vue', 'angular', 'express', 'axios', 'lodash', 'moment',
                'jest', 'mocha', 'webpack', 'babel', 'eslint', 'prettier', 'redux'
            },
            'java': {
                'spring', 'hibernate', 'junit', 'mockito', 'slf4j', 'log4j',
                'apache', 'guava', 'jackson', 'gson', 'okhttp', 'retrofit'
            }
        }
    
    def extract_dependencies(self, code: str, language: str, ast_tree: Optional[Any] = None) -> Dict[str, Any]:
        """Extract all dependencies from code."""
        if language == 'python':
            return self._extract_python_dependencies(code, ast_tree)
        elif language in ['javascript', 'typescript']:
            return self._extract_javascript_dependencies(code)
        elif language in ['java']:
            return self._extract_java_dependencies(code)
        elif language in ['c', 'cpp']:
            return self._extract_c_dependencies(code)
        elif language == 'go':
            return self._extract_go_dependencies(code)
        elif language == 'rust':
            return self._extract_rust_dependencies(code)
        else:
            return self._extract_generic_dependencies(code)
    
    def _extract_python_dependencies(self, code: str, ast_tree: Optional[ast.AST]) -> Dict[str, Any]:
        """Extract Python imports and dependencies."""
        dependencies = {
            'imports': [],
            'from_imports': [],
            'dynamic_imports': [],
            'stdlib': set(),
            'third_party': set(),
            'local': set(),
            'import_patterns': defaultdict(int)
        }
        
        if ast_tree and hasattr(ast_tree, '__class__') and ast_tree.__class__.__module__ == 'ast':
            # Use AST for accurate extraction
            for node in ast.walk(ast_tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        as_name = alias.asname
                        dependencies['imports'].append({
                            'module': module,
                            'as': as_name,
                            'line': node.lineno if hasattr(node, 'lineno') else 0
                        })
                        self._categorize_module(module, 'python', dependencies)
                        
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    level = node.level  # Relative import level
                    
                    for alias in node.names:
                        name = alias.name
                        as_name = alias.asname
                        dependencies['from_imports'].append({
                            'module': module,
                            'name': name,
                            'as': as_name,
                            'level': level,
                            'line': node.lineno if hasattr(node, 'lineno') else 0
                        })
                    
                    if module:
                        self._categorize_module(module, 'python', dependencies)
                
                # Check for dynamic imports
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == '__import__':
                        if node.args and isinstance(node.args[0], ast.Str):
                            module = node.args[0].s
                            dependencies['dynamic_imports'].append(module)
                            self._categorize_module(module, 'python', dependencies)
        else:
            # Fallback to regex
            self._extract_python_imports_regex(code, dependencies)
        
        # Extract import patterns
        self._analyze_import_patterns(dependencies)
        
        return dependencies
    
    def _extract_python_imports_regex(self, code: str, dependencies: Dict):
        """Extract Python imports using regex as fallback."""
        # Standard imports
        import_pattern = r'^import\s+([a-zA-Z_][\w.]*(?:\s*,\s*[a-zA-Z_][\w.]*)*)'
        for match in re.finditer(import_pattern, code, re.MULTILINE):
            modules = match.group(1).split(',')
            for module in modules:
                module = module.strip()
                if ' as ' in module:
                    mod, alias = module.split(' as ')
                    dependencies['imports'].append({'module': mod.strip(), 'as': alias.strip()})
                    self._categorize_module(mod.strip(), 'python', dependencies)
                else:
                    dependencies['imports'].append({'module': module, 'as': None})
                    self._categorize_module(module, 'python', dependencies)
        
        # From imports
        from_pattern = r'^from\s+([a-zA-Z_][\w.]*)\s+import\s+(.+)'
        for match in re.finditer(from_pattern, code, re.MULTILINE):
            module = match.group(1)
            imports = match.group(2)
            
            # Handle multiple imports
            for imp in imports.split(','):
                imp = imp.strip()
                if ' as ' in imp:
                    name, alias = imp.split(' as ')
                    dependencies['from_imports'].append({
                        'module': module,
                        'name': name.strip(),
                        'as': alias.strip()
                    })
                else:
                    dependencies['from_imports'].append({
                        'module': module,
                        'name': imp,
                        'as': None
                    })
            
            self._categorize_module(module, 'python', dependencies)
    
    def _extract_javascript_dependencies(self, code: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript imports and requires."""
        dependencies = {
            'imports': [],
            'requires': [],
            'dynamic_imports': [],
            'stdlib': set(),
            'third_party': set(),
            'local': set(),
            'import_patterns': defaultdict(int)
        }
        
        # ES6 imports
        # Named imports: import { x } from 'module'
        named_import_pattern = r'import\s+{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(named_import_pattern, code):
            module = match.group(2)
            dependencies['imports'].append({'module': module, 'type': 'named'})
            self._categorize_js_module(module, dependencies)
        
        # Default imports: import x from 'module'
        default_import_pattern = r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(default_import_pattern, code):
            module = match.group(2)
            dependencies['imports'].append({'module': module, 'type': 'default'})
            self._categorize_js_module(module, dependencies)
        
        # Namespace imports: import * as x from 'module'
        namespace_import_pattern = r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(namespace_import_pattern, code):
            module = match.group(2)
            dependencies['imports'].append({'module': module, 'type': 'namespace'})
            self._categorize_js_module(module, dependencies)
        
        # Side effect imports: import 'module'
        side_effect_pattern = r'import\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(side_effect_pattern, code):
            module = match.group(1)
            dependencies['imports'].append({'module': module, 'type': 'side_effect'})
            self._categorize_js_module(module, dependencies)
        
        # CommonJS requires
        require_pattern = r'(?:const|let|var)\s+(?:(\w+)|{([^}]+)})\s*=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        for match in re.finditer(require_pattern, code):
            module = match.group(3)
            dependencies['requires'].append({'module': module})
            self._categorize_js_module(module, dependencies)
        
        # Dynamic imports
        dynamic_pattern = r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        for match in re.finditer(dynamic_pattern, code):
            module = match.group(1)
            dependencies['dynamic_imports'].append(module)
            self._categorize_js_module(module, dependencies)
        
        self._analyze_import_patterns(dependencies)
        return dependencies
    
    def _extract_java_dependencies(self, code: str) -> Dict[str, Any]:
        """Extract Java imports."""
        dependencies = {
            'imports': [],
            'static_imports': [],
            'package': None,
            'stdlib': set(),
            'third_party': set(),
            'import_patterns': defaultdict(int)
        }
        
        # Package declaration
        package_pattern = r'^package\s+([\w.]+);'
        package_match = re.search(package_pattern, code, re.MULTILINE)
        if package_match:
            dependencies['package'] = package_match.group(1)
        
        # Regular imports
        import_pattern = r'^import\s+([\w.]+(?:\.\*)?);'
        for match in re.finditer(import_pattern, code, re.MULTILINE):
            import_stmt = match.group(1)
            dependencies['imports'].append(import_stmt)
            self._categorize_java_import(import_stmt, dependencies)
        
        # Static imports
        static_pattern = r'^import\s+static\s+([\w.]+(?:\.\*)?);'
        for match in re.finditer(static_pattern, code, re.MULTILINE):
            import_stmt = match.group(1)
            dependencies['static_imports'].append(import_stmt)
            self._categorize_java_import(import_stmt, dependencies)
        
        self._analyze_import_patterns(dependencies)
        return dependencies
    
    def _extract_c_dependencies(self, code: str) -> Dict[str, Any]:
        """Extract C/C++ includes."""
        dependencies = {
            'system_includes': [],
            'local_includes': [],
            'stdlib': set(),
            'third_party': set(),
            'import_patterns': defaultdict(int)
        }
        
        # System includes
        system_pattern = r'#include\s*<([^>]+)>'
        for match in re.finditer(system_pattern, code):
            header = match.group(1)
            dependencies['system_includes'].append(header)
            
            # Categorize common headers
            if header in ['stdio.h', 'stdlib.h', 'string.h', 'math.h', 'time.h',
                         'iostream', 'vector', 'string', 'map', 'algorithm']:
                dependencies['stdlib'].add(header)
            else:
                dependencies['third_party'].add(header)
        
        # Local includes
        local_pattern = r'#include\s*"([^"]+)"'
        for match in re.finditer(local_pattern, code):
            header = match.group(1)
            dependencies['local_includes'].append(header)
        
        self._analyze_import_patterns(dependencies)
        return dependencies
    
    def _extract_go_dependencies(self, code: str) -> Dict[str, Any]:
        """Extract Go imports."""
        dependencies = {
            'imports': [],
            'stdlib': set(),
            'third_party': set(),
            'local': set(),
            'import_patterns': defaultdict(int)
        }
        
        # Single line imports
        import_pattern = r'import\s+"([^"]+)"'
        for match in re.finditer(import_pattern, code):
            pkg = match.group(1)
            dependencies['imports'].append(pkg)
            self._categorize_go_import(pkg, dependencies)
        
        # Multi-line imports
        multiline_pattern = r'import\s*\((.*?)\)'
        multiline_match = re.search(multiline_pattern, code, re.DOTALL)
        if multiline_match:
            imports_block = multiline_match.group(1)
            for line in imports_block.split('\n'):
                pkg_match = re.search(r'"([^"]+)"', line)
                if pkg_match:
                    pkg = pkg_match.group(1)
                    dependencies['imports'].append(pkg)
                    self._categorize_go_import(pkg, dependencies)
        
        self._analyze_import_patterns(dependencies)
        return dependencies
    
    def _extract_rust_dependencies(self, code: str) -> Dict[str, Any]:
        """Extract Rust use statements and external crates."""
        dependencies = {
            'use_statements': [],
            'extern_crates': [],
            'stdlib': set(),
            'third_party': set(),
            'import_patterns': defaultdict(int)
        }
        
        # Use statements
        use_pattern = r'use\s+([\w:]+(?:::\*)?);'
        for match in re.finditer(use_pattern, code):
            use_stmt = match.group(1)
            dependencies['use_statements'].append(use_stmt)
            
            # Check if stdlib
            if use_stmt.startswith('std::'):
                dependencies['stdlib'].add(use_stmt)
            else:
                dependencies['third_party'].add(use_stmt)
        
        # External crates
        extern_pattern = r'extern\s+crate\s+(\w+);'
        for match in re.finditer(extern_pattern, code):
            crate = match.group(1)
            dependencies['extern_crates'].append(crate)
            dependencies['third_party'].add(crate)
        
        self._analyze_import_patterns(dependencies)
        return dependencies
    
    def _extract_generic_dependencies(self, code: str) -> Dict[str, Any]:
        """Generic dependency extraction for unsupported languages."""
        dependencies = {
            'potential_imports': [],
            'import_patterns': defaultdict(int)
        }
        
        # Look for common import patterns
        patterns = [
            r'import\s+[\w.]+',
            r'require\s*\([\'"][^\'"]+[\'"]\)',
            r'include\s+[<"][\w./]+[>"]',
            r'using\s+[\w.]+;'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, code):
                dependencies['potential_imports'].append(match.group(0))
        
        return dependencies
    
    def _categorize_module(self, module: str, language: str, dependencies: Dict):
        """Categorize a module as stdlib, third-party, or local."""
        if not module:
            return
        
        # Get top-level module name
        top_level = module.split('.')[0]
        
        stdlib = self.stdlib_modules.get(language, set())
        common = self.common_packages.get(language, set())
        
        if top_level in stdlib:
            dependencies['stdlib'].add(module)
        elif top_level in common or not module.startswith('.'):
            dependencies['third_party'].add(module)
        else:
            dependencies['local'].add(module)
    
    def _categorize_js_module(self, module: str, dependencies: Dict):
        """Categorize JavaScript module."""
        if module.startswith('.') or module.startswith('/'):
            dependencies['local'].add(module)
        elif module in self.stdlib_modules.get('javascript', set()):
            dependencies['stdlib'].add(module)
        else:
            dependencies['third_party'].add(module)
    
    def _categorize_java_import(self, import_stmt: str, dependencies: Dict):
        """Categorize Java import."""
        if any(import_stmt.startswith(prefix) for prefix in self.stdlib_modules.get('java', set())):
            dependencies['stdlib'].add(import_stmt)
        else:
            dependencies['third_party'].add(import_stmt)
    
    def _categorize_go_import(self, pkg: str, dependencies: Dict):
        """Categorize Go import."""
        if '.' not in pkg:
            # Standard library packages don't have dots
            dependencies['stdlib'].add(pkg)
        elif pkg.startswith('./') or pkg.startswith('../'):
            dependencies['local'].add(pkg)
        else:
            dependencies['third_party'].add(pkg)
    
    def _analyze_import_patterns(self, dependencies: Dict):
        """Analyze import patterns and characteristics."""
        patterns = dependencies['import_patterns']
        
        # Count different import styles
        if 'imports' in dependencies:
            patterns['direct_imports'] = len(dependencies['imports'])
        
        if 'from_imports' in dependencies:
            patterns['from_imports'] = len(dependencies['from_imports'])
        
        if 'requires' in dependencies:
            patterns['commonjs_requires'] = len(dependencies['requires'])
        
        if 'dynamic_imports' in dependencies:
            patterns['dynamic_imports'] = len(dependencies['dynamic_imports'])
        
        # Calculate ratios
        patterns['stdlib_ratio'] = len(dependencies.get('stdlib', [])) / max(1, 
            len(dependencies.get('stdlib', [])) + len(dependencies.get('third_party', [])))
        
        patterns['third_party_count'] = len(dependencies.get('third_party', []))
        patterns['local_import_count'] = len(dependencies.get('local', []))
    
    def generate_dependency_fingerprint(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fingerprint from dependencies."""
        fingerprint = {}
        
        # Create sorted lists for consistent hashing
        stdlib_list = sorted(list(dependencies.get('stdlib', [])))
        third_party_list = sorted(list(dependencies.get('third_party', [])))
        local_list = sorted(list(dependencies.get('local', [])))
        
        # Generate hashes
        fingerprint['stdlib_hash'] = hashlib.sha256(
            '|'.join(stdlib_list).encode()
        ).hexdigest()[:16]
        
        fingerprint['third_party_hash'] = hashlib.sha256(
            '|'.join(third_party_list).encode()
        ).hexdigest()[:16]
        
        fingerprint['import_pattern_hash'] = hashlib.sha256(
            str(sorted(dependencies.get('import_patterns', {}).items())).encode()
        ).hexdigest()[:16]
        
        # Create dependency signature
        all_deps = stdlib_list + third_party_list
        fingerprint['dependency_signature'] = hashlib.sha256(
            '|'.join(sorted(all_deps)).encode()
        ).hexdigest()[:16]
        
        # Summary statistics
        fingerprint['dependency_stats'] = {
            'stdlib_count': len(stdlib_list),
            'third_party_count': len(third_party_list),
            'local_count': len(local_list),
            'total_unique': len(set(all_deps)),
            'import_complexity': len(dependencies.get('import_patterns', {}))
        }
        
        return fingerprint
    
    def compare_dependencies(self, deps1: Dict, deps2: Dict) -> Dict[str, float]:
        """Compare two dependency sets and calculate similarity."""
        similarities = {}
        
        # Compare standard library usage
        stdlib1 = set(deps1.get('stdlib', []))
        stdlib2 = set(deps2.get('stdlib', []))
        
        if stdlib1 or stdlib2:
            similarities['stdlib_similarity'] = len(stdlib1.intersection(stdlib2)) / len(stdlib1.union(stdlib2))
        else:
            similarities['stdlib_similarity'] = 1.0
        
        # Compare third-party dependencies
        third1 = set(deps1.get('third_party', []))
        third2 = set(deps2.get('third_party', []))
        
        if third1 or third2:
            similarities['third_party_similarity'] = len(third1.intersection(third2)) / len(third1.union(third2))
        else:
            similarities['third_party_similarity'] = 1.0
        
        # Compare import patterns
        patterns1 = deps1.get('import_patterns', {})
        patterns2 = deps2.get('import_patterns', {})
        
        pattern_sim = 0.0
        pattern_keys = set(patterns1.keys()).union(set(patterns2.keys()))
        
        for key in pattern_keys:
            val1 = patterns1.get(key, 0)
            val2 = patterns2.get(key, 0)
            
            if val1 > 0 or val2 > 0:
                pattern_sim += min(val1, val2) / max(val1, val2)
        
        similarities['pattern_similarity'] = pattern_sim / len(pattern_keys) if pattern_keys else 1.0
        
        # Overall similarity
        similarities['overall'] = sum(similarities.values()) / len(similarities)
        
        return similarities