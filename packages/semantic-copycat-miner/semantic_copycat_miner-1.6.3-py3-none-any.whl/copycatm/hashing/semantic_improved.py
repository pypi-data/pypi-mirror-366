"""
Improved semantic hashing with better cross-language support and reduced collisions.
"""

import hashlib
import re
from typing import List, Any, Set, Dict, Tuple
import random
from collections import defaultdict
from .cross_language_normalizer import CrossLanguageNormalizer


class ImprovedSemanticHasher:
    """Enhanced semantic hasher with better cross-language MinHash and reduced collisions."""
    
    def __init__(self, num_perm: int = 256, lsh_bands: int = 32, shingle_size: int = 4):
        self.num_perm = num_perm  # Increased from 128 for better accuracy
        self.lsh_bands = lsh_bands
        self.shingle_size = shingle_size
        self.normalizer = CrossLanguageNormalizer()  # Add normalizer
        
        # Generate more hash functions for better MinHash
        random.seed(42)  # Reproducible
        self.hash_functions = []
        
        # Use larger prime numbers for better distribution
        large_prime = (1 << 61) - 1  # Mersenne prime
        
        for i in range(num_perm):
            a = random.randint(1, large_prime - 1)
            b = random.randint(0, large_prime - 1)
            self.hash_functions.append((a, b, large_prime))
    
    def generate_minhash(self, text: str, language: str = None) -> str:
        """Generate improved MinHash with language normalization."""
        # Apply cross-language normalization if language is specified
        if language and language in ['python', 'javascript', 'c', 'cpp', 'java']:
            normalized_text = self.normalizer.normalize(text, language)
        else:
            normalized_text = text
            
        # Extract both structural and semantic shingles from normalized text
        structural_shingles = self._extract_structural_shingles(normalized_text, language)
        semantic_shingles = self._extract_semantic_shingles(normalized_text, language)
        
        # Combine shingles with weights
        all_shingles = structural_shingles.union(semantic_shingles)
        
        if not all_shingles:
            # Generate hash based on file characteristics instead of static value
            content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            return content_hash[:32]
        
        # Initialize MinHash signature with 64-bit values
        signature = [float('inf')] * self.num_perm
        
        # Apply hash functions to each shingle
        for shingle in all_shingles:
            # Use SHA256 for better distribution
            shingle_bytes = shingle.encode('utf-8')
            shingle_hash = int(hashlib.sha256(shingle_bytes).hexdigest()[:16], 16)
            
            for i, (a, b, p) in enumerate(self.hash_functions):
                # Universal hash function with better distribution
                hash_value = (a * shingle_hash + b) % p
                signature[i] = min(signature[i], hash_value)
        
        # Convert to hex with better encoding (256-bit output)
        hex_parts = []
        for i in range(0, min(32, len(signature)), 2):
            # Combine pairs of values
            if i + 1 < len(signature):
                combined = signature[i] ^ signature[i + 1]
            else:
                combined = signature[i]
            
            # Convert to 8-char hex
            hex_part = format(int(combined) & 0xFFFFFFFF, '08x')
            hex_parts.append(hex_part)
        
        return ''.join(hex_parts)[:64]  # Return 64 hex chars (256 bits)
    
    def _extract_structural_shingles(self, text: str, language: str = None) -> Set[str]:
        """Extract structural shingles that are language-agnostic."""
        shingles = set()
        
        # Normalize code structure across languages
        normalized = self._normalize_code_structure(text, language)
        
        # Extract control flow shingles
        control_patterns = [
            r'IF \([^)]+\) BLOCK',
            r'FOR \([^)]+\) BLOCK',
            r'WHILE \([^)]+\) BLOCK',
            r'FUNC \w+ \([^)]*\) BLOCK',
            r'RETURN \w+',
            r'VAR = EXPR'
        ]
        
        for pattern in control_patterns:
            matches = re.findall(pattern, normalized)
            for match in matches:
                shingles.add(f"struct:{match}")
        
        # Extract operation sequences
        operations = re.findall(r'[+\-*/=<>!&|]+', normalized)
        for i in range(len(operations) - self.shingle_size + 1):
            op_sequence = ''.join(operations[i:i + self.shingle_size])
            shingles.add(f"ops:{op_sequence}")
        
        # Extract call patterns
        calls = re.findall(r'CALL_\w+', normalized)
        for i in range(len(calls) - 2):
            call_sequence = ' '.join(calls[i:i + 3])
            shingles.add(f"calls:{call_sequence}")
        
        return shingles
    
    def _extract_semantic_shingles(self, text: str, language: str = None) -> Set[str]:
        """Extract semantic shingles that capture algorithmic meaning."""
        shingles = set()
        
        # Language-agnostic tokenization
        tokens = self._semantic_tokenize(text, language)
        
        # Extract token n-grams
        for n in [3, 4, 5]:  # Multiple n-gram sizes
            for i in range(len(tokens) - n + 1):
                ngram = ' '.join(tokens[i:i + n])
                shingles.add(f"tok{n}:{ngram}")
        
        # Extract algorithmic patterns
        algo_patterns = self._detect_algorithmic_patterns(text)
        for pattern_type, pattern_value in algo_patterns:
            shingles.add(f"algo:{pattern_type}:{pattern_value}")
        
        # Extract data flow patterns
        data_flow = self._extract_data_flow_patterns(text)
        for flow in data_flow:
            shingles.add(f"flow:{flow}")
        
        return shingles
    
    def _normalize_code_structure(self, text: str, language: str = None) -> str:
        """Normalize code to language-agnostic structure."""
        # Remove comments
        text = self._remove_comments(text, language)
        
        # Normalize function definitions
        func_patterns = [
            (r'\bdef\s+(\w+)\s*\([^)]*\)\s*:', r'FUNC \1 () BLOCK'),  # Python
            (r'\bfunction\s+(\w+)\s*\([^)]*\)\s*{', r'FUNC \1 () BLOCK'),  # JavaScript
            (r'\b(void|int|float|double|char\*?)\s+(\w+)\s*\([^)]*\)\s*{', r'FUNC \2 () BLOCK'),  # C/C++
            (r'\bfunc\s+(\w+)\s*\([^)]*\).*{', r'FUNC \1 () BLOCK'),  # Go
        ]
        
        for pattern, replacement in func_patterns:
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        
        # Normalize control structures
        control_patterns = [
            (r'\bif\s*\([^)]+\)', 'IF (COND) BLOCK'),
            (r'\bwhile\s*\([^)]+\)', 'WHILE (COND) BLOCK'),
            (r'\bfor\s*\([^)]+\)', 'FOR (COND) BLOCK'),
            (r'\breturn\s+([^;]+)', r'RETURN \1'),
        ]
        
        for pattern, replacement in control_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Normalize variable declarations and assignments
        text = re.sub(r'\b(var|let|const|int|float|double|char\*?)\s+(\w+)\s*=\s*([^;]+)', 
                     r'VAR = EXPR', text)
        
        # Normalize function calls
        text = re.sub(r'\b(\w+)\s*\([^)]*\)', r'CALL_\1', text)
        
        # Normalize array access
        text = re.sub(r'\[\s*[^]]+\s*\]', '[IDX]', text)
        
        return text
    
    def _remove_comments(self, text: str, language: str = None) -> str:
        """Remove comments based on language."""
        # C-style comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Python comments
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        
        # Remove strings to avoid confusion
        text = re.sub(r'"[^"]*"', '""', text)
        text = re.sub(r"'[^']*'", "''", text)
        
        return text
    
    def _semantic_tokenize(self, text: str, language: str = None) -> List[str]:
        """Tokenize code into semantic units."""
        # First normalize
        text = self._remove_comments(text, language)
        
        # Extract meaningful tokens
        tokens = []
        
        # Keywords (language-agnostic)
        keywords = {
            'if', 'else', 'elif', 'while', 'for', 'do', 'switch', 'case',
            'return', 'break', 'continue', 'try', 'catch', 'finally',
            'class', 'struct', 'function', 'def', 'func', 'void',
            'true', 'false', 'null', 'nil', 'none'
        }
        
        # Operators
        operators = {
            '++', '--', '+=', '-=', '*=', '/=', '%=',
            '==', '!=', '<=', '>=', '&&', '||',
            '<<', '>>', '&', '|', '^', '~',
            '+', '-', '*', '/', '%', '=', '<', '>'
        }
        
        # Tokenize with pattern matching
        pattern = r'\b\w+\b|' + '|'.join(re.escape(op) for op in sorted(operators, key=len, reverse=True))
        raw_tokens = re.findall(pattern, text)
        
        for token in raw_tokens:
            if token.lower() in keywords:
                tokens.append(f"KW_{token.upper()}")
            elif token in operators:
                tokens.append(f"OP_{token}")
            elif token.isdigit():
                tokens.append("NUM")
            elif re.match(r'^[a-zA-Z_]\w*$', token):
                # Check for common patterns
                if re.match(r'^(i|j|k|n|x|y|z)$', token):
                    tokens.append("IDX")  # Index variable
                elif re.match(r'^(temp|tmp|result|res)$', token, re.IGNORECASE):
                    tokens.append("TMP")  # Temporary variable
                else:
                    tokens.append("ID")  # Generic identifier
        
        return tokens
    
    def _detect_algorithmic_patterns(self, text: str) -> List[Tuple[str, str]]:
        """Detect specific algorithmic patterns."""
        patterns = []
        
        # Sorting patterns
        if re.search(r'pivot|partition', text, re.IGNORECASE):
            patterns.append(('sort', 'quicksort'))
        if re.search(r'merge.*sort|merge.*left.*right', text, re.IGNORECASE):
            patterns.append(('sort', 'mergesort'))
        if re.search(r'bubble|swap.*adjacent', text, re.IGNORECASE):
            patterns.append(('sort', 'bubblesort'))
        
        # Search patterns
        if re.search(r'binary.*search|left.*right.*mid', text, re.IGNORECASE):
            patterns.append(('search', 'binary'))
        if re.search(r'linear.*search|for.*if.*return', text, re.IGNORECASE):
            patterns.append(('search', 'linear'))
        
        # Graph patterns
        if re.search(r'visited|adjacency|graph|vertex|edge', text, re.IGNORECASE):
            patterns.append(('graph', 'traversal'))
        if re.search(r'bfs|breadth.*first|queue', text, re.IGNORECASE):
            patterns.append(('graph', 'bfs'))
        if re.search(r'dfs|depth.*first|stack|recursive', text, re.IGNORECASE):
            patterns.append(('graph', 'dfs'))
        
        # Mathematical patterns
        if re.search(r'fibonacci|fib.*n-1.*n-2', text, re.IGNORECASE):
            patterns.append(('math', 'fibonacci'))
        if re.search(r'factorial|n\s*\*.*n-1', text, re.IGNORECASE):
            patterns.append(('math', 'factorial'))
        if re.search(r'gcd|greatest.*common|euclidean', text, re.IGNORECASE):
            patterns.append(('math', 'gcd'))
        
        # Cryptographic patterns
        if re.search(r'encrypt|decrypt|cipher|crypto', text, re.IGNORECASE):
            patterns.append(('crypto', 'encryption'))
        if re.search(r'hash|digest|sha|md5', text, re.IGNORECASE):
            patterns.append(('crypto', 'hashing'))
        if re.search(r'rsa|public.*key|private.*key|modular.*exp', text, re.IGNORECASE):
            patterns.append(('crypto', 'rsa'))
        
        return patterns
    
    def _extract_data_flow_patterns(self, text: str) -> List[str]:
        """Extract data flow patterns."""
        patterns = []
        
        # Loop patterns
        if re.search(r'for.*range|for.*in\s+\w+', text):
            patterns.append('iterate_collection')
        if re.search(r'while.*[<>]|for.*[<>]', text):
            patterns.append('conditional_loop')
        
        # Recursion patterns
        func_name = re.search(r'def\s+(\w+)|function\s+(\w+)', text)
        if func_name:
            name = func_name.group(1) or func_name.group(2)
            if re.search(rf'\b{name}\s*\(', text[func_name.end():]):
                patterns.append('recursive_call')
        
        # Assignment patterns
        if re.search(r'\w+\s*=\s*\w+\s*[+\-*/]\s*\w+', text):
            patterns.append('arithmetic_assignment')
        if re.search(r'\w+\s*=\s*\[.*\]|\w+\s*=\s*\{.*\}', text):
            patterns.append('collection_init')
        
        return patterns
    
    def generate_simhash(self, text: str, language: str = None) -> str:
        """Generate improved SimHash with language awareness."""
        # Extract weighted features
        features = self._extract_weighted_features(text, language)
        
        if not features:
            return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        
        # Use 128-bit SimHash for better discrimination
        hash_bits = 128
        vector = [0] * hash_bits
        
        # Process features with weights
        for feature, weight in features.items():
            # Use SHA256 for better distribution
            feature_hash = int(hashlib.sha256(feature.encode('utf-8')).hexdigest(), 16)
            
            # Update vector
            for i in range(hash_bits):
                if feature_hash & (1 << i):
                    vector[i] += weight
                else:
                    vector[i] -= weight
        
        # Generate final SimHash
        simhash_value = 0
        for i in range(hash_bits):
            if vector[i] > 0:
                simhash_value |= (1 << i)
        
        # Return as hex string
        return format(simhash_value, '032x').upper()
    
    def _extract_weighted_features(self, text: str, language: str = None) -> Dict[str, int]:
        """Extract features with weights for SimHash."""
        features = defaultdict(int)
        
        # Structural features
        struct_features = self._extract_structural_features(text, language)
        for feat, weight in struct_features.items():
            features[f"struct:{feat}"] += weight
        
        # Semantic features
        sem_features = self._extract_semantic_features(text, language)
        for feat, weight in sem_features.items():
            features[f"sem:{feat}"] += weight
        
        # Complexity features
        complex_features = self._extract_complexity_features(text)
        for feat, weight in complex_features.items():
            features[f"complex:{feat}"] += weight
        
        return dict(features)
    
    def _extract_structural_features(self, text: str, language: str = None) -> Dict[str, int]:
        """Extract structural code features."""
        features = {}
        
        # Control flow features
        features['if_count'] = len(re.findall(r'\bif\b', text, re.IGNORECASE)) * 5
        features['loop_count'] = len(re.findall(r'\b(for|while)\b', text, re.IGNORECASE)) * 7
        features['function_count'] = len(re.findall(r'\b(def|function|func)\b', text, re.IGNORECASE)) * 10
        
        # Nesting depth
        max_indent = 0
        for line in text.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        features[f'max_indent_{min(max_indent // 4, 10)}'] = 8
        
        return features
    
    def _extract_semantic_features(self, text: str, language: str = None) -> Dict[str, int]:
        """Extract semantic code features."""
        features = {}
        
        # Algorithm indicators
        algo_indicators = {
            'sort': ['sort', 'swap', 'pivot', 'partition', 'merge'],
            'search': ['search', 'find', 'lookup', 'binary', 'linear'],
            'graph': ['graph', 'node', 'edge', 'vertex', 'visited'],
            'crypto': ['encrypt', 'decrypt', 'hash', 'key', 'cipher'],
            'math': ['fibonacci', 'factorial', 'prime', 'gcd', 'lcm']
        }
        
        for category, keywords in algo_indicators.items():
            score = sum(len(re.findall(rf'\b{kw}\b', text, re.IGNORECASE)) for kw in keywords)
            if score > 0:
                features[f'algo_{category}'] = min(score * 10, 50)
        
        return features
    
    def _extract_complexity_features(self, text: str) -> Dict[str, int]:
        """Extract complexity-related features."""
        features = {}
        
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Size features
        features[f'size_{min(len(non_empty_lines) // 20, 10)}'] = 5
        
        # Cyclomatic complexity approximation
        decision_points = len(re.findall(r'\b(if|while|for|case|catch)\b', text, re.IGNORECASE))
        features[f'cyclomatic_{min(decision_points, 20)}'] = 7
        
        # Operation density
        operators = len(re.findall(r'[+\-*/=<>!&|]+', text))
        op_density = operators / max(len(non_empty_lines), 1)
        features[f'op_density_{min(int(op_density * 10), 10)}'] = 4
        
        return features
    
    def calculate_similarity(self, hash1: str, hash2: str, hash_type: str = "minhash") -> float:
        """Calculate similarity with better accuracy."""
        try:
            if not hash1 or not hash2:
                return 0.0
            
            if hash_type == "minhash":
                return self._calculate_minhash_similarity(hash1, hash2)
            elif hash_type == "simhash":
                return self._calculate_simhash_similarity(hash1, hash2)
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _calculate_minhash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate MinHash similarity with better estimation."""
        if hash1 == hash2:
            return 1.0
        
        # Compare 8-character chunks (32 bits each)
        chunk_size = 8
        chunks1 = [hash1[i:i+chunk_size] for i in range(0, len(hash1), chunk_size)]
        chunks2 = [hash2[i:i+chunk_size] for i in range(0, len(hash2), chunk_size)]
        
        if len(chunks1) != len(chunks2):
            # Different hash sizes
            return 0.0
        
        # Count exact matches and near matches
        exact_matches = 0
        near_matches = 0
        
        for c1, c2 in zip(chunks1, chunks2):
            if c1 == c2:
                exact_matches += 1
            else:
                # Check Hamming distance for near matches
                try:
                    val1 = int(c1, 16)
                    val2 = int(c2, 16)
                    hamming = bin(val1 ^ val2).count('1')
                    if hamming <= 8:  # Less than 25% bit difference
                        near_matches += 0.5
                except ValueError:
                    pass
        
        # Calculate weighted similarity
        total_matches = exact_matches + near_matches
        raw_similarity = total_matches / len(chunks1)
        
        # Apply non-linear scaling for better discrimination
        if raw_similarity < 0.2:
            return raw_similarity * 0.25  # Heavily reduce low similarities
        elif raw_similarity < 0.5:
            return 0.05 + (raw_similarity - 0.2) * 0.5  # Moderate scaling
        elif raw_similarity < 0.8:
            return 0.2 + (raw_similarity - 0.5) * 1.33  # Linear scaling
        else:
            return 0.6 + (raw_similarity - 0.8) * 2.0  # Amplify high similarities
    
    def _calculate_simhash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate SimHash similarity with better accuracy."""
        if len(hash1) != len(hash2):
            return 0.0
        
        try:
            # Convert to integers
            val1 = int(hash1, 16)
            val2 = int(hash2, 16)
            
            # Calculate Hamming distance
            xor = val1 ^ val2
            distance = bin(xor).count('1')
            
            # Normalize by hash length in bits
            max_distance = len(hash1) * 4  # 4 bits per hex char
            
            raw_similarity = 1.0 - (distance / max_distance)
            
            # Apply scaling for better discrimination
            if raw_similarity < 0.5:
                return raw_similarity * 0.2
            elif raw_similarity < 0.7:
                return 0.1 + (raw_similarity - 0.5) * 0.75
            elif raw_similarity < 0.85:
                return 0.25 + (raw_similarity - 0.7) * 2.33
            else:
                return 0.6 + (raw_similarity - 0.85) * 2.67
                
        except ValueError:
            return 0.0
    
    # Compatibility methods
    def minhash(self, ast_tree: Any) -> str:
        """Generate MinHash from AST."""
        return self.minhash_from_ast(ast_tree)
    
    def simhash(self, data: str) -> str:
        """Generate SimHash from text."""
        return self.generate_simhash(data)
    
    def minhash_from_ast(self, ast_tree: Any) -> str:
        """Generate MinHash from AST with language detection."""
        language = None
        if hasattr(ast_tree, 'language'):
            language = ast_tree.language
        
        # Extract code if available
        if hasattr(ast_tree, 'code'):
            return self.generate_minhash(ast_tree.code, language)
        
        # Try to extract features from AST
        features = []
        if hasattr(ast_tree, 'root'):
            self._extract_ast_features(ast_tree.root, features)
        
        if features:
            feature_text = ' '.join(features)
            return self.generate_minhash(feature_text, language)
        
        return hashlib.sha256(b"empty_ast").hexdigest()[:64]
    
    def _extract_ast_features(self, node: Any, features: List[str], depth: int = 0):
        """Extract features from AST nodes."""
        if not hasattr(node, 'type') or depth > 15:
            return
        
        # Add node type
        node_type = str(node.type)
        features.append(f"node:{node_type}")
        
        # Add structural patterns
        if hasattr(node, 'children') and node.children:
            child_types = [str(c.type) for c in node.children[:3] if hasattr(c, 'type')]
            if child_types:
                pattern = f"{node_type}->{','.join(child_types)}"
                features.append(f"pattern:{pattern}")
        
        # Recurse
        if hasattr(node, 'children'):
            for child in node.children:
                self._extract_ast_features(child, features, depth + 1)