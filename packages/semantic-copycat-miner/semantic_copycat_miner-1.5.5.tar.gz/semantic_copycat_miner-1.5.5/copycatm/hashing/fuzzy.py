"""
Fuzzy hashing (TLSH) for CopycatM.
"""

import hashlib
from typing import Optional, List, Tuple, Dict, Any

try:
    import tlsh
    TLSH_AVAILABLE = True
except ImportError:
    TLSH_AVAILABLE = False


class FuzzyHasher:
    """Generate fuzzy hashes for similarity detection."""
    
    def __init__(self, threshold: int = 100):
        self.threshold = threshold
        self.min_length = 50  # TLSH requires minimum length
    
    def hash_text(self, text: str) -> str:
        """Generate TLSH hash from text data."""
        return self.tlsh(text)
    
    def hash_file(self, file_path: str) -> str:
        """Generate TLSH hash from file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.tlsh(content)
        except Exception:
            return "T1A2B3C4error_reading_file"
    
    def tlsh(self, data: str) -> str:
        """Generate TLSH fuzzy hash of data."""
        if not TLSH_AVAILABLE:
            # Fallback to a similarity-preserving hash
            return self._fallback_hash(data)
        
        try:
            # TLSH requires minimum length
            if len(data) < self.min_length:
                # Pad short data or use fallback
                if len(data) < 10:
                    return self._fallback_hash(data)
                # Pad with repeated content to meet minimum length
                padded_data = (data * ((self.min_length // len(data)) + 1))[:self.min_length]
                hash_result = tlsh.hash(padded_data.encode('utf-8'))
                if hash_result is None or hash_result == "TNULL":
                    return self._fallback_hash(data)
                return hash_result
            
            hash_result = tlsh.hash(data.encode('utf-8'))
            # TLSH returns None for some inputs, handle this case
            if hash_result is None or hash_result == "TNULL":
                return self._fallback_hash(data)
            return hash_result
        except Exception as e:
            # Fallback if TLSH fails
            return self._fallback_hash(data)
    
    def _fallback_hash(self, data: str) -> str:
        """Generate fallback fuzzy hash when TLSH unavailable."""
        # Create a hash that preserves some similarity characteristics
        
        # Normalize the data for similarity
        normalized = self._normalize_for_similarity(data)
        
        # Create multiple hash components for similarity detection
        components = []
        
        # 1. Character frequency hash
        char_freq = self._character_frequency_hash(normalized)
        components.append(char_freq)
        
        # 2. N-gram hash
        ngram_hash = self._ngram_hash(normalized, n=3)
        components.append(ngram_hash)
        
        # 3. Structure hash (line lengths, indentation)
        struct_hash = self._structure_hash(data)
        components.append(struct_hash)
        
        # 4. Word pattern hash
        word_hash = self._word_pattern_hash(normalized)
        components.append(word_hash)
        
        # Combine components
        combined = "".join(components)
        final_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # Format like TLSH (prefix with T)
        return f"T{final_hash[:15]}"
    
    def _normalize_for_similarity(self, text: str) -> str:
        """Normalize text to preserve similarity while removing noise."""
        # Convert to lowercase
        normalized = text.lower()
        
        # Remove extra whitespace but preserve structure
        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove comments but preserve code structure
        normalized = re.sub(r'#.*$', '', normalized, flags=re.MULTILINE)  # Python comments
        normalized = re.sub(r'//.*$', '', normalized, flags=re.MULTILINE)  # C-style comments
        
        return normalized.strip()
    
    def _character_frequency_hash(self, text: str) -> str:
        """Create hash based on character frequency distribution."""
        if not text:
            return "0000"
        
        # Count character frequencies
        char_freq = {}
        for char in text:
            if char.isalnum():  # Only alphanumeric characters
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Create frequency signature
        total_chars = sum(char_freq.values())
        if total_chars == 0:
            return "0000"
        
        # Get most common characters and their relative frequencies
        sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)
        top_chars = sorted_chars[:10]  # Top 10 characters
        
        # Create signature from relative frequencies
        freq_sig = ""
        for char, count in top_chars:
            relative_freq = int((count / total_chars) * 16)  # Scale to 0-15
            freq_sig += f"{relative_freq:X}"
        
        return freq_sig[:4].ljust(4, '0')
    
    def _ngram_hash(self, text: str, n: int = 3) -> str:
        """Create hash based on n-gram frequency."""
        if len(text) < n:
            return "0000"
        
        # Extract n-grams
        ngrams = {}
        for i in range(len(text) - n + 1):
            ngram = text[i:i+n]
            if ngram.strip():  # Skip whitespace-only n-grams
                ngrams[ngram] = ngrams.get(ngram, 0) + 1
        
        if not ngrams:
            return "0000"
        
        # Get most common n-grams
        sorted_ngrams = sorted(ngrams.items(), key=lambda x: x[1], reverse=True)
        top_ngrams = sorted_ngrams[:8]  # Top 8 n-grams
        
        # Create hash from n-gram pattern
        ngram_hash = hashlib.md5("".join([ng[0] for ng in top_ngrams]).encode()).hexdigest()
        return ngram_hash[:4]
    
    def _structure_hash(self, text: str) -> str:
        """Create hash based on structural features."""
        lines = text.split('\n')
        
        # Structural features
        features = []
        
        # Line count (binned)
        line_count_bin = min(len(lines) // 10, 15)
        features.append(f"{line_count_bin:X}")
        
        # Average line length (binned)
        if lines:
            avg_line_length = sum(len(line) for line in lines) // len(lines)
            avg_length_bin = min(avg_line_length // 10, 15)
            features.append(f"{avg_length_bin:X}")
        else:
            features.append("0")
        
        # Indentation pattern (for code)
        indentation_levels = set()
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indentation_levels.add(indent // 4)  # Assume 4-space indentation
        
        max_indent = max(indentation_levels) if indentation_levels else 0
        indent_bin = min(max_indent, 15)
        features.append(f"{indent_bin:X}")
        
        # Punctuation density
        punct_count = sum(1 for char in text if not char.isalnum() and not char.isspace())
        punct_density = int((punct_count / len(text)) * 15) if text else 0
        features.append(f"{punct_density:X}")
        
        return "".join(features)
    
    def _word_pattern_hash(self, text: str) -> str:
        """Create hash based on word patterns."""
        import re
        words = re.findall(r'\b\w+\b', text)
        
        if not words:
            return "0000"
        
        # Word length distribution
        length_counts = {}
        for word in words:
            length = min(len(word), 10)  # Cap at 10
            length_counts[length] = length_counts.get(length, 0) + 1
        
        # Create pattern signature
        pattern = ""
        for length in range(1, 6):  # Lengths 1-5
            count = length_counts.get(length, 0)
            relative_count = int((count / len(words)) * 15) if words else 0
            pattern += f"{relative_count:X}"
        
        return pattern[:4].ljust(4, '0')
    
    def tlsh_similarity(self, hash1: str, hash2: str) -> int:
        """Calculate TLSH similarity between two hashes."""
        if not TLSH_AVAILABLE:
            return self._fallback_similarity(hash1, hash2)
        
        try:
            # Handle our fallback hashes
            if hash1.startswith('T') and len(hash1) == 16 and not hash1.startswith('TLSH'):
                return self._fallback_similarity(hash1, hash2)
            
            return tlsh.diff(hash1, hash2)
        except Exception:
            return self._fallback_similarity(hash1, hash2)
    
    def _fallback_similarity(self, hash1: str, hash2: str) -> int:
        """Calculate similarity for fallback hashes."""
        if hash1 == hash2:
            return 0
        
        # Remove 'T' prefix if present
        h1 = hash1[1:] if hash1.startswith('T') else hash1
        h2 = hash2[1:] if hash2.startswith('T') else hash2
        
        # Calculate character-wise differences
        min_len = min(len(h1), len(h2))
        max_len = max(len(h1), len(h2))
        
        if min_len == 0:
            return 999
        
        # Hamming distance for common length
        differences = sum(c1 != c2 for c1, c2 in zip(h1[:min_len], h2[:min_len]))
        
        # Add penalty for length differences
        length_diff = max_len - min_len
        
        # Scale to TLSH-like range (0-999)
        similarity_score = int((differences + length_diff) * (999 / max_len))
        
        return min(similarity_score, 999)
    
    def is_similar(self, hash1: str, hash2: str) -> bool:
        """Check if two TLSH hashes are similar within threshold."""
        similarity = self.tlsh_similarity(hash1, hash2)
        return similarity <= self.threshold
    
    def batch_similarity(self, target_hash: str, hash_list: List[str]) -> List[Tuple[str, int]]:
        """Calculate similarity between target hash and a list of hashes."""
        similarities = []
        for hash_val in hash_list:
            similarity = self.tlsh_similarity(target_hash, hash_val)
            similarities.append((hash_val, similarity))
        
        return sorted(similarities, key=lambda x: x[1])
    
    def find_similar(self, target_hash: str, hash_list: List[str]) -> List[str]:
        """Find all hashes similar to target within threshold."""
        similar_hashes = []
        for hash_val in hash_list:
            if self.is_similar(target_hash, hash_val):
                similar_hashes.append(hash_val)
        
        return similar_hashes
    
    def similarity_percentage(self, hash1: str, hash2: str) -> float:
        """Convert TLSH similarity score to percentage (0-100)."""
        similarity_score = self.tlsh_similarity(hash1, hash2)
        
        # TLSH scores: 0 = identical, higher = more different
        # Convert to percentage: 0 = 100% similar, 999 = 0% similar
        percentage = max(0.0, 100.0 - (similarity_score / 999.0 * 100.0))
        return round(percentage, 2)
    
    def analyze_similarity_distribution(self, hash_list: List[str]) -> Dict[str, Any]:
        """Analyze similarity distribution in a list of hashes."""
        if len(hash_list) < 2:
            return {"error": "Need at least 2 hashes for analysis"}
        
        similarities = []
        comparisons = 0
        
        # Compare all pairs
        for i in range(len(hash_list)):
            for j in range(i + 1, len(hash_list)):
                similarity = self.tlsh_similarity(hash_list[i], hash_list[j])
                similarities.append(similarity)
                comparisons += 1
        
        if not similarities:
            return {"error": "No valid comparisons"}
        
        # Calculate statistics
        avg_similarity = sum(similarities) / len(similarities)
        min_similarity = min(similarities)
        max_similarity = max(similarities)
        
        # Count similar pairs (within threshold)
        similar_pairs = sum(1 for s in similarities if s <= self.threshold)
        
        return {
            "total_hashes": len(hash_list),
            "total_comparisons": comparisons,
            "average_similarity": round(avg_similarity, 2),
            "min_similarity": min_similarity,
            "max_similarity": max_similarity,
            "similar_pairs": similar_pairs,
            "similarity_rate": round((similar_pairs / comparisons) * 100, 2),
            "threshold": self.threshold
        }
    
    def cluster_similar_hashes(self, hash_list: List[str]) -> List[List[str]]:
        """Group similar hashes into clusters."""
        if not hash_list:
            return []
        
        clusters = []
        remaining_hashes = hash_list.copy()
        
        while remaining_hashes:
            # Start new cluster with first remaining hash
            current_hash = remaining_hashes.pop(0)
            current_cluster = [current_hash]
            
            # Find all hashes similar to current hash
            i = 0
            while i < len(remaining_hashes):
                if self.is_similar(current_hash, remaining_hashes[i]):
                    current_cluster.append(remaining_hashes.pop(i))
                else:
                    i += 1
            
            clusters.append(current_cluster)
        
        # Sort clusters by size (largest first)
        clusters.sort(key=len, reverse=True)
        return clusters