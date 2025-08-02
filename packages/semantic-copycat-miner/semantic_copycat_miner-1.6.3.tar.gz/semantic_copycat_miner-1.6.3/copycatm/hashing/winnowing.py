"""
Winnowing algorithm implementation for code fingerprinting.

This module implements the Winnowing algorithm for generating robust
fingerprints from source code that can detect partial matches and
survive common code transformations.
"""

import re
import zlib
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WinnowingConfig:
    """Configuration for the Winnowing algorithm."""
    k_gram_size: int = 30      # Size of k-grams
    window_size: int = 64      # Window size for hash selection
    hash_function: str = "crc32"  # Hash function to use
    normalize_code: bool = True   # Whether to normalize code
    remove_comments: bool = True  # Remove comments during normalization
    case_sensitive: bool = False  # Case sensitivity for normalization


class RollingHash:
    """Efficient rolling hash implementation for k-gram hashing."""
    
    def __init__(self, k: int, base: int = 256, prime: int = 1000000007):
        """
        Initialize rolling hash.
        
        Args:
            k: Size of k-grams
            base: Base for polynomial hash
            prime: Large prime for modulo operation
        """
        self.k = k
        self.base = base
        self.prime = prime
        self.power = pow(base, k-1, prime)
        self.current_hash = 0
        
    def hash(self, text: str) -> int:
        """Calculate initial hash for first k-gram."""
        self.current_hash = 0
        for i in range(min(self.k, len(text))):
            self.current_hash = (self.current_hash * self.base + ord(text[i])) % self.prime
        return self.current_hash
    
    def roll(self, old_char: str, new_char: str) -> int:
        """Roll the hash by removing old character and adding new one."""
        self.current_hash = (self.current_hash - ord(old_char) * self.power) % self.prime
        self.current_hash = (self.current_hash * self.base + ord(new_char)) % self.prime
        if self.current_hash < 0:
            self.current_hash += self.prime
        return self.current_hash


class CodeNormalizer:
    """Language-aware code normalization for winnowing."""
    
    def __init__(self, config: WinnowingConfig):
        """Initialize normalizer with configuration."""
        self.config = config
        
    def normalize(self, code: str, language: Optional[str] = None) -> str:
        """
        Normalize code for fingerprinting.
        
        Args:
            code: Source code to normalize
            language: Programming language (for language-specific normalization)
            
        Returns:
            Normalized code string
        """
        if not self.config.normalize_code:
            return code
            
        normalized = code
        
        # Remove comments if configured
        if self.config.remove_comments and language:
            normalized = self._remove_comments(normalized, language)
        
        # Language-specific keyword normalization for better cross-language matching
        normalized = self._normalize_keywords(normalized, language)
        
        # Basic normalization
        # Replace multiple whitespace with single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove extra spaces around punctuation
        normalized = re.sub(r'\s*([,;()[\]])\s*', r'\1', normalized)
        
        # Normalize braces and colons to a common structure delimiter
        normalized = re.sub(r'\s*\{\s*', ' BLOCK_START ', normalized)
        normalized = re.sub(r'\s*\}\s*', ' BLOCK_END ', normalized)
        normalized = re.sub(r'\s*:\s*', ' BLOCK_START ', normalized)
        
        # Normalize function declarations across languages
        normalized = re.sub(r'\b(def|function|func|void|int|public|private|static)\s+', 'FUNC ', normalized)
        
        # Normalize control structures
        normalized = re.sub(r'\b(if|elif|else if|elsif)\b', 'IF', normalized)
        normalized = re.sub(r'\b(for|while|do)\b', 'LOOP', normalized)
        normalized = re.sub(r'\b(return|yield)\b', 'RETURN', normalized)
        
        # Remove type annotations and declarations
        normalized = re.sub(r'\bint\s+\w+\s*=', 'VAR =', normalized)
        normalized = re.sub(r'\b(int|float|double|char|void)\s+', '', normalized)
        normalized = re.sub(r'\[\s*\]', '', normalized)  # Remove empty array brackets
        
        # Remove semicolons - they're just statement terminators
        normalized = re.sub(r';', '', normalized)
        
        # Convert to lowercase unless case sensitive
        if not self.config.case_sensitive:
            normalized = normalized.lower()
            
        # Final cleanup - remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
            
        return normalized
    
    def _normalize_keywords(self, code: str, language: Optional[str] = None) -> str:
        """Normalize language-specific keywords for cross-language matching."""
        if not language:
            return code
            
        # Normalize data types across languages
        code = re.sub(r'\b(int|integer|Integer|long|Long|i32|i64)\b', 'INT', code)
        code = re.sub(r'\b(float|double|Float|Double|f32|f64)\b', 'FLOAT', code)
        code = re.sub(r'\b(str|string|String|char\s*\*|&str)\b', 'STRING', code)
        code = re.sub(r'\b(bool|boolean|Boolean)\b', 'BOOL', code)
        code = re.sub(r'\b(list|array|Array|ArrayList|vec|Vec|vector)\b', 'ARRAY', code)
        
        # Normalize common algorithm patterns
        code = re.sub(r'\b(pivot|mid|middle)\b', 'PIVOT', code, flags=re.IGNORECASE)
        code = re.sub(r'\b(left|low|start|lo)\b', 'LEFT', code, flags=re.IGNORECASE)
        code = re.sub(r'\b(right|high|end|hi)\b', 'RIGHT', code, flags=re.IGNORECASE)
        code = re.sub(r'\b(partition|split|divide)\b', 'PARTITION', code, flags=re.IGNORECASE)
        code = re.sub(r'\b(swap|exchange)\b', 'SWAP', code, flags=re.IGNORECASE)
        code = re.sub(r'\b(arr|array|list|lst|vec|data|items|nums)\b', 'ARR', code, flags=re.IGNORECASE)
        
        # Normalize variable declarations across languages
        code = re.sub(r'\b(let|const|var|int|void|auto)\s+(\w+)\s*=', r'VAR \2 =', code)
        code = re.sub(r'\b(let|const|var|int|void|auto)\s+(\w+)', r'VAR \2', code)
        
        # Normalize list comprehensions to loop-like structures
        if language in ['python', 'py']:
            # [x for x in arr if x < pivot] -> FILTER(ARR, LESS_THAN PIVOT)
            code = re.sub(r'\[(.*?)\s+for\s+.*?\s+in\s+(\w+)\s+if\s+(.*?)\]', 
                         r'FILTER(\2, \3)', code)
        
        # Normalize comparison operators for all languages
        code = re.sub(r'\s*<\s*', ' LESS_THAN ', code)
        code = re.sub(r'\s*>\s*', ' GREATER_THAN ', code)
        code = re.sub(r'\s*==\s*', ' EQUALS ', code)
        code = re.sub(r'\s*<=\s*', ' LESS_EQUAL ', code)
        code = re.sub(r'\s*>=\s*', ' GREATER_EQUAL ', code)
        
        # Normalize language-specific constructs
        if language in ['python', 'py']:
            code = re.sub(r'\blen\(', 'LENGTH(', code)
            code = re.sub(r'\brange\(', 'RANGE(', code)
            code = re.sub(r'\s+//\s+', ' DIV ', code)  # Floor division
        elif language in ['c', 'cpp', 'c++']:
            code = re.sub(r'->|\.', '.', code)  # Normalize pointer access
            code = re.sub(r'\bsizeof\(', 'LENGTH(', code)
            code = re.sub(r'\bmalloc\(', 'ALLOC(', code)
            code = re.sub(r'\bfree\(', 'FREE(', code)
        elif language in ['java']:
            code = re.sub(r'\.length\b', '.LENGTH', code)
            code = re.sub(r'\bnew\s+', 'NEW ', code)
        elif language in ['javascript', 'js', 'typescript', 'ts']:
            code = re.sub(r'\.length\b', '.LENGTH', code)
            code = re.sub(r'\bconst\s+|let\s+|var\s+', 'VAR ', code)
            code = re.sub(r'=>', 'ARROW', code)
            
        return code
    
    def _remove_comments(self, code: str, language: str) -> str:
        """Remove comments based on language."""
        if language in ['python', 'py']:
            # Remove Python comments
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'"""[\s\S]*?"""', '', code)
            code = re.sub(r"'''[\s\S]*?'''", '', code)
        elif language in ['javascript', 'js', 'typescript', 'ts']:
            # Remove JavaScript/TypeScript comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        elif language in ['c', 'cpp', 'c++', 'java']:
            # Remove C-style comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        elif language in ['go']:
            # Remove Go comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        elif language in ['rust', 'rs']:
            # Remove Rust comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            code = re.sub(r'/\*[\s\S]*?\*/', '', code)
            
        return code


class Winnowing:
    """Main Winnowing algorithm implementation."""
    
    def __init__(self, config: Optional[WinnowingConfig] = None):
        """
        Initialize Winnowing with configuration.
        
        Args:
            config: Winnowing configuration (uses defaults if not provided)
        """
        self.config = config or WinnowingConfig()
        self.normalizer = CodeNormalizer(self.config)
        
    def generate_fingerprint(self, text: str, language: Optional[str] = None) -> List[Tuple[int, int]]:
        """
        Generate winnowing fingerprints for the given text.
        
        Args:
            text: Input text to fingerprint
            language: Programming language for normalization
            
        Returns:
            List of (hash, position) tuples representing the fingerprint
        """
        # Step 1: Normalize
        normalized = self.normalizer.normalize(text, language)
        
        if not normalized:
            return []
        
        # Step 2: Generate k-grams
        kgrams = self._generate_kgrams(normalized)
        
        if not kgrams:
            return []
        
        # Step 3: Hash k-grams
        hashes = self._hash_kgrams(kgrams)
        
        # Step 4: Select from windows
        fingerprints = self._select_from_windows(hashes)
        
        # Remove duplicates while preserving order
        unique_fingerprints = self._remove_duplicates(fingerprints)
        
        return unique_fingerprints
    
    def _generate_kgrams(self, text: str) -> List[str]:
        """Generate k-grams from normalized text."""
        if len(text) < self.config.k_gram_size:
            return [text]  # Return whole text if shorter than k
            
        kgrams = []
        for i in range(len(text) - self.config.k_gram_size + 1):
            kgrams.append(text[i:i + self.config.k_gram_size])
        return kgrams
    
    def _hash_kgrams(self, kgrams: List[str]) -> List[int]:
        """Hash k-grams using configured hash function."""
        if self.config.hash_function == "crc32":
            return [zlib.crc32(kg.encode()) & 0xffffffff for kg in kgrams]
        elif self.config.hash_function == "rolling":
            # Use rolling hash for efficiency
            if not kgrams:
                return []
                
            hasher = RollingHash(self.config.k_gram_size)
            hashes = []
            
            # First hash
            first_hash = hasher.hash(kgrams[0])
            hashes.append(first_hash)
            
            # Roll through remaining k-grams
            for i in range(1, len(kgrams)):
                if i < len(kgrams):
                    old_char = kgrams[i-1][0]
                    new_char = kgrams[i][-1] if i < len(kgrams) else ''
                    rolled_hash = hasher.roll(old_char, new_char)
                    hashes.append(rolled_hash)
                    
            return hashes
        else:
            # Default to simple hash
            return [hash(kg) & 0xffffffff for kg in kgrams]
    
    def _select_from_windows(self, hashes: List[int]) -> List[Tuple[int, int]]:
        """Select minimum hash from each window."""
        if len(hashes) <= self.config.window_size:
            # If we have fewer hashes than window size, return min
            if hashes:
                min_hash = min(hashes)
                min_idx = hashes.index(min_hash)
                return [(min_hash, min_idx)]
            return []
            
        fingerprints = []
        
        for i in range(len(hashes) - self.config.window_size + 1):
            window = hashes[i:i + self.config.window_size]
            min_hash = min(window)
            min_index = i + window.index(min_hash)
            fingerprints.append((min_hash, min_index))
            
        return fingerprints
    
    def _remove_duplicates(self, fingerprints: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Remove duplicate hashes while preserving order and first occurrence."""
        seen = set()
        unique = []
        
        for hash_val, pos in fingerprints:
            if hash_val not in seen:
                seen.add(hash_val)
                unique.append((hash_val, pos))
                
        return unique
    
    def compare_fingerprints(self, fp1: List[Tuple[int, int]], 
                           fp2: List[Tuple[int, int]]) -> float:
        """
        Calculate Jaccard similarity between two fingerprints.
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Similarity score between 0 and 1
        """
        if not fp1 or not fp2:
            return 0.0
            
        set1 = set(h for h, _ in fp1)
        set2 = set(h for h, _ in fp2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def find_matching_regions(self, fp1: List[Tuple[int, int]], 
                            fp2: List[Tuple[int, int]]) -> List[Dict[str, int]]:
        """
        Find matching regions between two fingerprints.
        
        Args:
            fp1: First fingerprint with positions
            fp2: Second fingerprint with positions
            
        Returns:
            List of matching regions with positions
        """
        # Create hash to positions mapping
        hash_to_pos1 = {}
        for hash_val, pos in fp1:
            if hash_val not in hash_to_pos1:
                hash_to_pos1[hash_val] = []
            hash_to_pos1[hash_val].append(pos)
            
        hash_to_pos2 = {}
        for hash_val, pos in fp2:
            if hash_val not in hash_to_pos2:
                hash_to_pos2[hash_val] = []
            hash_to_pos2[hash_val].append(pos)
        
        # Find matching regions
        matches = []
        for hash_val in set(hash_to_pos1.keys()) & set(hash_to_pos2.keys()):
            for pos1 in hash_to_pos1[hash_val]:
                for pos2 in hash_to_pos2[hash_val]:
                    matches.append({
                        'hash': hash_val,
                        'pos1': pos1,
                        'pos2': pos2,
                        'length': self.config.k_gram_size
                    })
                    
        # Sort by position in first document
        matches.sort(key=lambda x: x['pos1'])
        
        return matches
    
    def generate_signature(self, text: str, language: Optional[str] = None) -> Dict[str, any]:
        """
        Generate a winnowing signature with metadata.
        
        Args:
            text: Input text
            language: Programming language
            
        Returns:
            Dictionary containing fingerprint and metadata
        """
        fingerprint = self.generate_fingerprint(text, language)
        normalized_text = self.normalizer.normalize(text, language)
        
        return {
            'fingerprint': fingerprint,
            'fingerprint_count': len(fingerprint),
            'config': {
                'k_gram_size': self.config.k_gram_size,
                'window_size': self.config.window_size,
                'hash_function': self.config.hash_function
            },
            'normalized_length': len(normalized_text) if normalized_text else 0,
            'original_length': len(text),
            'hash_values': [h for h, _ in fingerprint],
            'positions': [p for _, p in fingerprint]
        }