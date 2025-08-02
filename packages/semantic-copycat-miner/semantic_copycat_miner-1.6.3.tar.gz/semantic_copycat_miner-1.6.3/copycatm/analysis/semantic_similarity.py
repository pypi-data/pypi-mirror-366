"""
Semantic code similarity detection using multiple techniques.
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
try:
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .ast_normalizer import ASTNormalizer


class SemanticSimilarityDetector:
    """Detect semantic similarity between code fragments using advanced techniques."""
    
    def __init__(self):
        self.ast_normalizer = ASTNormalizer()
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                token_pattern=r'\b\w+\b',
                lowercase=False,
                ngram_range=(1, 3)
            )
        else:
            self.vectorizer = None
        
        # Semantic equivalence patterns
        self.equivalent_operations = {
            # Arithmetic equivalents
            'increment': {r'\+=1', r'\+\+', r'= .* \+ 1'},
            'decrement': {r'-=1', r'--', r'= .* - 1'},
            'multiply_by_2': {r'\*2', r'<<1', r'\+ .*'},  # x*2 == x<<1 == x+x
            'divide_by_2': {r'/2', r'>>1'},
            
            # Boolean equivalents
            'not_equal': {r'!=', r'<>', r'not .* =='},
            'greater_equal': {r'>=', r'not .* <'},
            'less_equal': {r'<=', r'not .* >'},
            
            # Control flow equivalents
            'early_return': {r'if .*: return', r'return .* if', r'&& return'},
            'guard_clause': {r'if not .*: return', r'unless .*', r'\|\| return'},
        }
        
        # Code idiom patterns across languages
        self.idiom_patterns = {
            'array_iteration': [
                r'for\s+\w+\s+in\s+range\(len\(',  # Python
                r'for\s*\(\s*int\s+\w+\s*=\s*0.*length',  # Java/C
                r'\.forEach\(',  # JavaScript
                r'for\s*\(\s*auto.*:',  # C++ range-based
            ],
            'null_check': [
                r'is\s+None',  # Python
                r'==\s*null',  # Java/C#
                r'==\s*NULL',  # C/C++
                r'===?\s*undefined',  # JavaScript
            ],
            'string_format': [
                r'f["\'].*{',  # Python f-string
                r'\.format\(',  # Python format
                r'String\.format\(',  # Java
                r'`.*\$\{',  # JavaScript template
                r'sprintf\(',  # C
            ],
        }
    
    def calculate_semantic_similarity(self, code1: str, code2: str, 
                                    language1: str, language2: str,
                                    ast1: Optional[Any] = None,
                                    ast2: Optional[Any] = None) -> Dict[str, Any]:
        """Calculate comprehensive semantic similarity between two code fragments."""
        
        # Parse ASTs if not provided
        if ast1 is None and language1 == "python":
            try:
                ast1 = ast.parse(code1)
            except:
                pass
        
        if ast2 is None and language2 == "python":
            try:
                ast2 = ast.parse(code2)
            except:
                pass
        
        # Calculate various similarity metrics
        similarities = {
            'token_similarity': self._token_similarity(code1, code2),
            'structure_similarity': self._structure_similarity(code1, code2, language1, language2, ast1, ast2),
            'semantic_operation_similarity': self._semantic_operation_similarity(code1, code2),
            'idiom_similarity': self._idiom_similarity(code1, code2),
            'variable_flow_similarity': self._variable_flow_similarity(code1, code2, language1, language2),
            'api_call_similarity': self._api_call_similarity(code1, code2),
        }
        
        # Calculate weighted overall similarity
        weights = {
            'token_similarity': 0.15,
            'structure_similarity': 0.25,
            'semantic_operation_similarity': 0.20,
            'idiom_similarity': 0.15,
            'variable_flow_similarity': 0.15,
            'api_call_similarity': 0.10,
        }
        
        overall_similarity = sum(
            similarities[metric] * weight 
            for metric, weight in weights.items()
        )
        
        return {
            'overall_similarity': overall_similarity,
            'metrics': similarities,
            'semantic_features': self._extract_semantic_features(code1, code2, language1, language2),
            'confidence': self._calculate_confidence(similarities)
        }
    
    def _token_similarity(self, code1: str, code2: str) -> float:
        """Calculate token-based similarity using TF-IDF."""
        try:
            # Tokenize and remove comments
            tokens1 = self._tokenize(code1)
            tokens2 = self._tokenize(code2)
            
            if not tokens1 or not tokens2:
                return 0.0
            
            if SKLEARN_AVAILABLE and self.vectorizer:
                # Create TF-IDF vectors
                corpus = [' '.join(tokens1), ' '.join(tokens2)]
                vectors = self.vectorizer.fit_transform(corpus)
                
                # Calculate cosine similarity
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                
                return float(similarity)
            else:
                # Fallback to Jaccard similarity
                set1 = set(tokens1)
                set2 = set(tokens2)
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                return intersection / union if union > 0 else 0.0
        except:
            return 0.0
    
    def _tokenize(self, code: str) -> List[str]:
        """Tokenize code into meaningful tokens."""
        # Remove comments and strings
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)  # Python comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)  # C-style comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Multi-line comments
        code = re.sub(r'["\'].*?["\']', 'STRING', code)  # Replace strings
        
        # Extract tokens
        tokens = re.findall(r'\b\w+\b', code)
        
        # Normalize common tokens
        normalized = []
        for token in tokens:
            if re.match(r'^\d+$', token):
                normalized.append('NUM')
            elif token in {'def', 'function', 'func', 'fn', 'void', 'int', 'public', 'private'}:
                normalized.append('FUNC_DECL')
            elif token in {'if', 'else', 'elif', 'switch', 'case'}:
                normalized.append('CONDITIONAL')
            elif token in {'for', 'while', 'do', 'foreach'}:
                normalized.append('LOOP')
            elif token in {'return', 'yield', 'break', 'continue'}:
                normalized.append('CONTROL')
            else:
                normalized.append(token)
        
        return normalized
    
    def _structure_similarity(self, code1: str, code2: str, 
                            language1: str, language2: str,
                            ast1: Any, ast2: Any) -> float:
        """Calculate structural similarity using AST normalization."""
        if ast1 and ast2:
            similarity = self.ast_normalizer.structural_similarity(
                ast1, ast2, language1, language2
            )
            return similarity['structure_similarity']
        
        # Fallback to control flow similarity
        return self._control_flow_similarity(code1, code2)
    
    def _control_flow_similarity(self, code1: str, code2: str) -> float:
        """Calculate control flow similarity."""
        # Extract control flow patterns
        cf_patterns = ['if', 'else', 'for', 'while', 'try', 'except', 'finally']
        
        flow1 = []
        flow2 = []
        
        for line in code1.split('\n'):
            for pattern in cf_patterns:
                if re.search(rf'\b{pattern}\b', line):
                    flow1.append(pattern)
        
        for line in code2.split('\n'):
            for pattern in cf_patterns:
                if re.search(rf'\b{pattern}\b', line):
                    flow2.append(pattern)
        
        if not flow1 or not flow2:
            return 0.0
        
        # Calculate sequence similarity
        common = set(zip(flow1, flow1[1:])).intersection(set(zip(flow2, flow2[1:])))
        return len(common) / max(len(flow1) - 1, len(flow2) - 1, 1)
    
    def _semantic_operation_similarity(self, code1: str, code2: str) -> float:
        """Detect semantically equivalent operations."""
        ops1 = self._extract_semantic_operations(code1)
        ops2 = self._extract_semantic_operations(code2)
        
        if not ops1 or not ops2:
            return 0.0
        
        # Count equivalent operations
        equivalent_count = 0
        total_ops = len(ops1) + len(ops2)
        
        for op_type1, patterns1 in ops1.items():
            if op_type1 in ops2:
                equivalent_count += min(len(patterns1), len(ops2[op_type1])) * 2
        
        return equivalent_count / total_ops if total_ops > 0 else 0.0
    
    def _extract_semantic_operations(self, code: str) -> Dict[str, List[str]]:
        """Extract semantic operations from code."""
        operations = defaultdict(list)
        
        for op_type, patterns in self.equivalent_operations.items():
            for pattern in patterns:
                matches = re.findall(pattern, code)
                if matches:
                    operations[op_type].extend(matches)
        
        return dict(operations)
    
    def _idiom_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity based on code idioms."""
        idioms1 = self._extract_idioms(code1)
        idioms2 = self._extract_idioms(code2)
        
        if not idioms1 or not idioms2:
            return 0.0
        
        # Jaccard similarity of idioms
        common = len(idioms1.intersection(idioms2))
        total = len(idioms1.union(idioms2))
        
        return common / total if total > 0 else 0.0
    
    def _extract_idioms(self, code: str) -> Set[str]:
        """Extract code idioms."""
        idioms = set()
        
        for idiom_type, patterns in self.idiom_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code):
                    idioms.add(idiom_type)
                    break
        
        return idioms
    
    def _variable_flow_similarity(self, code1: str, code2: str, 
                                language1: str, language2: str) -> float:
        """Calculate data flow similarity based on variable usage patterns."""
        flow1 = self._extract_variable_flow(code1, language1)
        flow2 = self._extract_variable_flow(code2, language2)
        
        if not flow1 or not flow2:
            return 0.0
        
        # Compare flow patterns
        pattern_similarity = 0.0
        total_patterns = 0
        
        for var_pattern1 in flow1:
            for var_pattern2 in flow2:
                if self._similar_flow_pattern(var_pattern1, var_pattern2):
                    pattern_similarity += 1
                total_patterns += 1
        
        return pattern_similarity / total_patterns if total_patterns > 0 else 0.0
    
    def _extract_variable_flow(self, code: str, language: str) -> List[Dict]:
        """Extract variable flow patterns."""
        flows = []
        
        # Simple pattern matching for variable assignments and usage
        var_pattern = r'(\w+)\s*=\s*([^;|\n]+)'
        assignments = re.findall(var_pattern, code)
        
        for var, value in assignments:
            # Look for usage after assignment
            usage_pattern = rf'{var}\s*[+\-*/\[\(]'
            usages = re.findall(usage_pattern, code)
            
            flows.append({
                'var': 'VAR',  # Normalize variable name
                'assign_type': self._classify_assignment(value),
                'usage_count': len(usages),
                'usage_types': self._classify_usages(usages)
            })
        
        return flows
    
    def _classify_assignment(self, value: str) -> str:
        """Classify assignment type."""
        if re.match(r'^\d+$', value.strip()):
            return 'literal_num'
        elif re.match(r'^["\'].*["\']$', value.strip()):
            return 'literal_str'
        elif re.search(r'[+\-*/]', value):
            return 'arithmetic'
        elif re.search(r'\(.*\)', value):
            return 'function_call'
        elif re.search(r'\[.*\]', value):
            return 'array_access'
        else:
            return 'other'
    
    def _classify_usages(self, usages: List[str]) -> List[str]:
        """Classify variable usage types."""
        types = []
        for usage in usages:
            if '+' in usage or '-' in usage:
                types.append('arithmetic')
            elif '[' in usage:
                types.append('indexing')
            elif '(' in usage:
                types.append('call_arg')
        return types
    
    def _similar_flow_pattern(self, pattern1: Dict, pattern2: Dict) -> bool:
        """Check if two flow patterns are similar."""
        return (
            pattern1['assign_type'] == pattern2['assign_type'] and
            abs(pattern1['usage_count'] - pattern2['usage_count']) <= 2 and
            set(pattern1['usage_types']).intersection(set(pattern2['usage_types']))
        )
    
    def _api_call_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity based on API/function calls."""
        calls1 = self._extract_api_calls(code1)
        calls2 = self._extract_api_calls(code2)
        
        if not calls1 or not calls2:
            return 0.0
        
        # Compare call sequences
        common_calls = set(calls1).intersection(set(calls2))
        total_calls = len(set(calls1).union(set(calls2)))
        
        return len(common_calls) / total_calls if total_calls > 0 else 0.0
    
    def _extract_api_calls(self, code: str) -> List[str]:
        """Extract API/function calls."""
        # Match function calls
        call_pattern = r'(\w+)\s*\('
        calls = re.findall(call_pattern, code)
        
        # Normalize common calls
        normalized = []
        for call in calls:
            if call in {'print', 'console', 'log', 'println', 'printf'}:
                normalized.append('OUTPUT')
            elif call in {'open', 'fopen', 'File', 'FileReader'}:
                normalized.append('FILE_OPEN')
            elif call in {'read', 'readline', 'readlines', 'fread'}:
                normalized.append('FILE_READ')
            elif call in {'write', 'writelines', 'fwrite', 'puts'}:
                normalized.append('FILE_WRITE')
            elif call in {'len', 'length', 'size', 'count'}:
                normalized.append('SIZE')
            elif call in {'append', 'push', 'add', 'insert'}:
                normalized.append('ADD_ELEMENT')
            elif call in {'remove', 'pop', 'delete', 'erase'}:
                normalized.append('REMOVE_ELEMENT')
            else:
                normalized.append(call)
        
        return normalized
    
    def _extract_semantic_features(self, code1: str, code2: str, 
                                 language1: str, language2: str) -> Dict[str, Any]:
        """Extract semantic features for comparison."""
        return {
            'common_operations': self._find_common_operations(code1, code2),
            'common_idioms': list(self._extract_idioms(code1).intersection(self._extract_idioms(code2))),
            'structural_patterns': self._find_common_patterns(code1, code2),
            'complexity_ratio': self._complexity_ratio(code1, code2),
        }
    
    def _find_common_operations(self, code1: str, code2: str) -> List[str]:
        """Find common semantic operations."""
        ops1 = self._extract_semantic_operations(code1)
        ops2 = self._extract_semantic_operations(code2)
        
        return list(set(ops1.keys()).intersection(set(ops2.keys())))
    
    def _find_common_patterns(self, code1: str, code2: str) -> List[str]:
        """Find common structural patterns."""
        patterns = []
        
        # Check for common loop patterns
        if 'for' in code1 and 'for' in code2:
            patterns.append('iteration')
        if 'while' in code1 and 'while' in code2:
            patterns.append('conditional_loop')
        
        # Check for common error handling
        if ('try' in code1 or 'catch' in code1) and ('try' in code2 or 'catch' in code2):
            patterns.append('error_handling')
        
        # Check for recursion
        if self._has_recursion(code1) and self._has_recursion(code2):
            patterns.append('recursion')
        
        return patterns
    
    def _has_recursion(self, code: str) -> bool:
        """Check if code likely contains recursion."""
        # Simple heuristic: function calls itself
        func_names = re.findall(r'def\s+(\w+)|function\s+(\w+)|func\s+(\w+)', code)
        for groups in func_names:
            for name in groups:
                if name and re.search(rf'\b{name}\s*\(', code):
                    return True
        return False
    
    def _complexity_ratio(self, code1: str, code2: str) -> float:
        """Calculate complexity ratio between codes."""
        lines1 = len([l for l in code1.split('\n') if l.strip()])
        lines2 = len([l for l in code2.split('\n') if l.strip()])
        
        if lines1 == 0 or lines2 == 0:
            return 0.0
        
        return min(lines1, lines2) / max(lines1, lines2)
    
    def _calculate_confidence(self, similarities: Dict[str, float]) -> float:
        """Calculate confidence score for similarity assessment."""
        # Higher confidence if multiple metrics agree
        high_similarity_count = sum(1 for score in similarities.values() if score > 0.7)
        medium_similarity_count = sum(1 for score in similarities.values() if 0.4 <= score <= 0.7)
        
        if high_similarity_count >= 3:
            return 0.9
        elif high_similarity_count >= 2:
            return 0.75
        elif medium_similarity_count >= 4:
            return 0.6
        else:
            return 0.4
    
    def detect_semantic_clones(self, code: str, candidates: List[Tuple[str, str]], 
                             source_language: str) -> List[Dict[str, Any]]:
        """Detect semantic clones from a list of candidates."""
        clones = []
        
        for candidate_code, candidate_language in candidates:
            similarity = self.calculate_semantic_similarity(
                code, candidate_code, source_language, candidate_language
            )
            
            if similarity['overall_similarity'] > 0.7:
                clones.append({
                    'code': candidate_code,
                    'language': candidate_language,
                    'similarity': similarity['overall_similarity'],
                    'confidence': similarity['confidence'],
                    'metrics': similarity['metrics'],
                    'semantic_features': similarity['semantic_features']
                })
        
        # Sort by similarity
        clones.sort(key=lambda x: x['similarity'], reverse=True)
        
        return clones