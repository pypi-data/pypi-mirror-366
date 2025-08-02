"""
Improved fuzzy hashing with better TLSH configuration and alternative methods.
"""

import hashlib
import logging
from typing import Optional, List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

try:
    import sys
    import os
    # Add user site-packages to path for macOS
    user_site = os.path.expanduser('~/Library/Python/3.9/lib/python/site-packages')
    if user_site not in sys.path:
        sys.path.insert(0, user_site)
    
    # Try py-tlsh first (newer version)
    try:
        import tlsh
        TLSH_AVAILABLE = True
        logger.debug("py-tlsh loaded successfully")
    except ImportError:
        # Fallback to original tlsh
        import tlsh
        TLSH_AVAILABLE = True
        logger.debug(f"TLSH loaded from: {tlsh.__file__}")
except ImportError as e:
    TLSH_AVAILABLE = False
    logger.warning(f"TLSH not available: {e}")

try:
    import ssdeep
    SSDEEP_AVAILABLE = True
except ImportError:
    SSDEEP_AVAILABLE = False


class ImprovedFuzzyHasher:
    """Enhanced fuzzy hasher with optimized TLSH and alternative methods."""
    
    def __init__(self, threshold: int = 100):
        self.threshold = threshold
        self.min_length = 256  # TLSH optimal minimum length
        self.optimal_length = 512  # Sweet spot for code similarity
        self.ssdeep_available = SSDEEP_AVAILABLE
    
    def hash_text(self, text: str) -> str:
        """Generate optimized fuzzy hash from text data."""
        return self.generate_fuzzy_hash(text)
    
    def generate_fuzzy_hash(self, data: str) -> str:
        """Generate best available fuzzy hash."""
        # Try TLSH with optimal configuration first
        if TLSH_AVAILABLE and len(data) >= 50:
            tlsh_hash = self._optimized_tlsh_hash(data)
            if tlsh_hash and not tlsh_hash.startswith('FALLBACK'):
                return tlsh_hash
        
        # Try ssdeep as backup (excellent for code similarity)
        if self.ssdeep_available:
            try:
                ssdeep_hash = ssdeep.hash(data)
                return f"SSDEEP:{ssdeep_hash}"
            except Exception:
                pass
        
        # Enhanced fallback method
        return self._enhanced_fallback_hash(data)
    
    def _optimized_tlsh_hash(self, data: str) -> str:
        """Generate TLSH hash with optimal preprocessing."""
        try:
            # Preprocess for better TLSH performance
            processed_data = self._preprocess_for_tlsh(data)
            
            # Smart padding if needed
            if len(processed_data) < self.min_length:
                if len(processed_data) < 50:
                    return "FALLBACK"
                processed_data = self._smart_pad_data(processed_data)
            
            # Generate TLSH hash
            tlsh_hash = tlsh.hash(processed_data.encode('utf-8'))
            return f"TLSH:{tlsh_hash}" if tlsh_hash else "FALLBACK"
            
        except Exception:
            return "FALLBACK"
    
    def _preprocess_for_tlsh(self, data: str) -> str:
        """Preprocess data to improve TLSH similarity detection."""
        import re
        
        # Normalize line endings
        data = data.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove comment noise while preserving algorithmic structure
        # Python comments
        data = re.sub(r'#[^\n]*', '', data)
        # C-style comments
        data = re.sub(r'//[^\n]*', '', data)
        data = re.sub(r'/\*.*?\*/', '', data, flags=re.DOTALL)
        
        # Normalize variable names to focus on algorithmic structure
        # Replace common variable patterns
        data = re.sub(r'\b[a-zA-Z_]\w*\d+\b', 'VAR', data)  # Variables with numbers
        data = re.sub(r'\b(temp|tmp|aux|temp\d+)\b', 'TEMP', data, re.IGNORECASE)
        data = re.sub(r'\b(index|idx|i|j|k|n|m)\b', 'IDX', data)  # Common indices
        
        # Normalize string literals and numbers to focus on structure
        data = re.sub(r'"[^"]*"', '"STR"', data)
        data = re.sub(r"'[^']*'", "'STR'", data)
        data = re.sub(r'\b\d+\.\d+\b', 'NUM', data)  # Floats
        data = re.sub(r'\b\d+\b', 'NUM', data)  # Integers
        
        # Normalize whitespace but preserve indentation structure
        lines = data.split('\n')
        processed_lines = []
        for line in lines:
            if line.strip():
                # Keep leading whitespace, normalize internal spaces
                leading_space = len(line) - len(line.lstrip())
                content = re.sub(r'\s+', ' ', line.strip())
                processed_lines.append(' ' * leading_space + content)
        
        return '\n'.join(processed_lines)
    
    def _smart_pad_data(self, data: str) -> str:
        """Smart padding that preserves algorithmic similarity."""
        if len(data) >= self.min_length:
            return data
        
        # Extract algorithmic patterns for padding
        lines = [line for line in data.split('\n') if line.strip()]
        if not lines:
            return data + ' ' * (self.min_length - len(data))
        
        # Use control flow and operation patterns for padding
        control_lines = [line for line in lines 
                        if any(keyword in line.lower() 
                              for keyword in ['if', 'for', 'while', 'return', '='])]
        
        padding_source = '\n'.join(control_lines[-3:]) if control_lines else '\n'.join(lines[-3:])
        
        # Calculate padding needed
        padding_needed = self.min_length - len(data)
        repetitions = (padding_needed // len(padding_source)) + 1
        padding = (padding_source * repetitions)[:padding_needed]
        
        return data + '\n' + padding
    
    def _enhanced_fallback_hash(self, data: str) -> str:
        """Enhanced fallback with multiple similarity-preserving components."""
        components = []
        
        # Algorithmic structure hash
        struct_hash = self._algorithmic_structure_hash(data)
        components.append(struct_hash)
        
        # Control flow pattern hash
        control_hash = self._control_flow_pattern_hash(data)
        components.append(control_hash)
        
        # Operation sequence hash
        op_hash = self._operation_sequence_hash(data)
        components.append(op_hash)
        
        # Semantic token hash
        semantic_hash = self._semantic_token_hash(data)
        components.append(semantic_hash)
        
        # Multi-scale n-gram hashes
        ngram2 = self._ngram_hash(data, 2)
        ngram3 = self._ngram_hash(data, 3)
        components.extend([ngram2, ngram3])
        
        # Combine with good distribution
        combined = '|'.join(components)
        final_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return f"ENHANCED:{final_hash[:20]}"
    
    def _algorithmic_structure_hash(self, data: str) -> str:
        """Hash based on algorithmic structure patterns."""
        import re
        
        # Count algorithmic constructs
        patterns = {
            'loops': len(re.findall(r'\b(for|while|do)\b', data, re.IGNORECASE)),
            'conditionals': len(re.findall(r'\b(if|else|elif|switch|case)\b', data, re.IGNORECASE)),
            'functions': len(re.findall(r'\b(def|function|func)\b', data, re.IGNORECASE)),
            'returns': len(re.findall(r'\breturn\b', data, re.IGNORECASE)),
            'assignments': len(re.findall(r'=(?!=)', data)),
            'comparisons': len(re.findall(r'[<>=!]=?', data)),
            'arithmetic': len(re.findall(r'[+\-*/%]', data))
        }
        
        # Normalize to hex digits
        signature = ""
        for key in ['loops', 'conditionals', 'functions', 'returns']:
            count = patterns[key]
            normalized = min(count, 15)  # Cap at 15 for hex digit
            signature += f"{normalized:X}"
        
        return signature
    
    def _control_flow_pattern_hash(self, data: str) -> str:
        """Hash based on control flow complexity."""
        lines = data.split('\n')
        
        # Analyze indentation patterns (proxy for nesting)
        indents = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indents.append(indent)
        
        if not indents:
            return "0000"
        
        # Control flow metrics
        max_indent = max(indents)
        indent_changes = sum(1 for i in range(1, len(indents)) 
                           if indents[i] != indents[i-1])
        unique_levels = len(set(indents))
        avg_indent = sum(indents) // len(indents)
        
        # Normalize to hex
        metrics = [
            min(max_indent // 4, 15),
            min(indent_changes // 3, 15),
            min(unique_levels, 15),
            min(avg_indent // 2, 15)
        ]
        
        return "".join(f"{m:X}" for m in metrics)
    
    def _operation_sequence_hash(self, data: str) -> str:
        """Hash based on sequence of operations."""
        import re
        
        # Extract operation sequence
        operations = []
        
        # Mathematical operations
        ops = re.findall(r'[+\-*/%=<>!&|^]', data)
        for op in ops[:20]:  # Limit to first 20 operations
            if op in '+-':
                operations.append('A')  # Arithmetic
            elif op in '*/':
                operations.append('M')  # Multiplication/Division
            elif op in '<>=!':
                operations.append('C')  # Comparison
            elif op in '&|^':
                operations.append('B')  # Bitwise
            else:
                operations.append('O')  # Other
        
        # Create sequence hash
        sequence = "".join(operations[:16])  # Limit length
        if not sequence:
            return "0000"
        
        # Hash the sequence
        seq_hash = hashlib.md5(sequence.encode()).hexdigest()
        return seq_hash[:4]
    
    def _semantic_token_hash(self, data: str) -> str:
        """Hash based on semantic programming tokens."""
        import re
        
        # Extract semantic tokens
        tokens = {
            'keywords': re.findall(r'\b(if|for|while|def|class|return|import)\b', data, re.IGNORECASE),
            'operators': re.findall(r'[+\-*/%=<>!]', data),
            'delimiters': re.findall(r'[(){}[\],;:]', data),
            'identifiers': re.findall(r'\b[a-zA-Z_]\w*\b', data)
        }
        
        # Create token frequency signature
        signature = ""
        for token_type in ['keywords', 'operators', 'delimiters']:
            count = len(tokens[token_type])
            normalized = min(count // 2, 15)
            signature += f"{normalized:X}"
        
        # Add identifier diversity metric
        unique_ids = len(set(tokens['identifiers']))
        total_ids = len(tokens['identifiers'])
        diversity = int((unique_ids / max(total_ids, 1)) * 15)
        signature += f"{diversity:X}"
        
        return signature
    
    def _ngram_hash(self, data: str, n: int) -> str:
        """Generate n-gram hash with better similarity preservation."""
        if len(data) < n:
            return "0000"
        
        # Normalize data for n-gram extraction
        normalized = data.lower()
        normalized = ''.join(c if c.isalnum() or c in '+-*/%=<>(){}[]' else ' ' 
                           for c in normalized)
        normalized = ' '.join(normalized.split())  # Normalize whitespace
        
        # Extract n-grams
        ngrams = []
        for i in range(len(normalized) - n + 1):
            ngram = normalized[i:i+n]
            if ngram.strip() and not ngram.isspace():
                ngrams.append(ngram)
        
        if not ngrams:
            return "0000"
        
        # Get most frequent n-grams for stability
        from collections import Counter
        common_ngrams = Counter(ngrams).most_common(10)
        
        # Create hash from common n-grams
        ngram_string = "".join([ng[0] for ng in common_ngrams])
        ngram_hash = hashlib.md5(ngram_string.encode()).hexdigest()
        
        return ngram_hash[:4]
    
    def calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two fuzzy hashes."""
        if hash1 == hash2:
            return 1.0
        
        # Handle different hash types
        if hash1.startswith('TLSH:') and hash2.startswith('TLSH:'):
            return self._tlsh_similarity(hash1[5:], hash2[5:])
        elif hash1.startswith('SSDEEP:') and hash2.startswith('SSDEEP:'):
            return self._ssdeep_similarity(hash1[7:], hash2[7:])
        elif hash1.startswith('ENHANCED:') and hash2.startswith('ENHANCED:'):
            return self._enhanced_similarity(hash1[9:], hash2[9:])
        else:
            # Different hash types - low similarity
            return 0.1
    
    def _tlsh_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate TLSH similarity score."""
        if not TLSH_AVAILABLE:
            return 0.0
        
        try:
            diff = tlsh.diff(hash1, hash2)
            # Convert TLSH diff (0=identical, higher=different) to similarity (0-1)
            return max(0.0, 1.0 - (diff / 999.0))
        except Exception:
            return 0.0
    
    def _ssdeep_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate ssdeep similarity score."""
        if not self.ssdeep_available:
            return 0.0
        
        try:
            import ssdeep
            similarity = ssdeep.compare(hash1, hash2)
            return similarity / 100.0  # Convert percentage to 0-1
        except Exception:
            return 0.0
    
    def _enhanced_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity for enhanced hashes."""
        if len(hash1) != len(hash2):
            return 0.0
        
        # Character-wise similarity
        matches = sum(1 for c1, c2 in zip(hash1, hash2) if c1 == c2)
        return matches / len(hash1)