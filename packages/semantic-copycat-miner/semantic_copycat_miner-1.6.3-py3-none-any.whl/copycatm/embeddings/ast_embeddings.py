"""
Semantic embeddings for AST nodes using pre-computed vectors.

This module provides semantic embeddings for common programming constructs
to enable better cross-language similarity detection.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import hashlib
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SemanticEmbedding:
    """Semantic embedding for an AST pattern."""
    pattern: str
    vector: np.ndarray
    semantic_group: str
    
    
class ASTEmbeddings:
    """Pre-computed semantic embeddings for AST patterns."""
    
    def __init__(self):
        """Initialize with pre-computed embeddings for common patterns."""
        self.embedding_dim = 64
        self.embeddings = self._initialize_embeddings()
        self.pattern_cache = {}
        
    def _initialize_embeddings(self) -> Dict[str, SemanticEmbedding]:
        """Initialize semantic embeddings for common programming patterns."""
        embeddings = {}
        
        # Core control flow patterns
        control_flow_base = np.random.RandomState(42).randn(self.embedding_dim)
        embeddings['IF_LT'] = SemanticEmbedding(
            'IF_LT',
            control_flow_base + 0.1 * np.random.RandomState(1).randn(self.embedding_dim),
            'control_flow'
        )
        embeddings['IF_GT'] = SemanticEmbedding(
            'IF_GT',
            control_flow_base + 0.1 * np.random.RandomState(2).randn(self.embedding_dim),
            'control_flow'
        )
        embeddings['IF_EQ'] = SemanticEmbedding(
            'IF_EQ',
            control_flow_base + 0.1 * np.random.RandomState(3).randn(self.embedding_dim),
            'control_flow'
        )
        embeddings['IF_NEQ'] = SemanticEmbedding(
            'IF_NEQ',
            control_flow_base + 0.1 * np.random.RandomState(15).randn(self.embedding_dim),
            'control_flow'
        )
        
        # Loop patterns
        loop_base = np.random.RandomState(43).randn(self.embedding_dim)
        embeddings['FOR_RANGE'] = SemanticEmbedding(
            'FOR_RANGE',
            loop_base + 0.1 * np.random.RandomState(4).randn(self.embedding_dim),
            'iteration'
        )
        embeddings['WHILE_CONDITION'] = SemanticEmbedding(
            'WHILE_CONDITION',
            loop_base + 0.1 * np.random.RandomState(5).randn(self.embedding_dim),
            'iteration'
        )
        
        # Recursion patterns
        recursion_base = np.random.RandomState(44).randn(self.embedding_dim)
        embeddings['RECURSIVE_CALL'] = SemanticEmbedding(
            'RECURSIVE_CALL',
            recursion_base + 0.1 * np.random.RandomState(6).randn(self.embedding_dim),
            'recursion'
        )
        embeddings['BASE_CASE'] = SemanticEmbedding(
            'BASE_CASE',
            recursion_base + 0.15 * np.random.RandomState(7).randn(self.embedding_dim),
            'recursion'
        )
        
        # Algorithm-specific patterns
        # Quicksort patterns
        quicksort_base = np.random.RandomState(45).randn(self.embedding_dim)
        embeddings['PARTITION_CALL'] = SemanticEmbedding(
            'PARTITION_CALL',
            quicksort_base + 0.05 * np.random.RandomState(8).randn(self.embedding_dim),
            'quicksort'
        )
        embeddings['PIVOT_COMPARE'] = SemanticEmbedding(
            'PIVOT_COMPARE',
            quicksort_base + 0.05 * np.random.RandomState(9).randn(self.embedding_dim),
            'quicksort'
        )
        embeddings['RECURSIVE_SORT'] = SemanticEmbedding(
            'RECURSIVE_SORT',
            quicksort_base + 0.05 * np.random.RandomState(10).randn(self.embedding_dim),
            'quicksort'
        )
        
        # Array operations
        array_base = np.random.RandomState(46).randn(self.embedding_dim)
        embeddings['ARRAY_SWAP'] = SemanticEmbedding(
            'ARRAY_SWAP',
            array_base + 0.1 * np.random.RandomState(11).randn(self.embedding_dim),
            'array_ops'
        )
        embeddings['ARRAY_ACCESS'] = SemanticEmbedding(
            'ARRAY_ACCESS',
            array_base + 0.1 * np.random.RandomState(12).randn(self.embedding_dim),
            'array_ops'
        )
        
        # Math operations
        math_base = np.random.RandomState(47).randn(self.embedding_dim)
        embeddings['INCREMENT'] = SemanticEmbedding(
            'INCREMENT',
            math_base + 0.1 * np.random.RandomState(13).randn(self.embedding_dim),
            'math_ops'
        )
        embeddings['DECREMENT'] = SemanticEmbedding(
            'DECREMENT',
            math_base + 0.1 * np.random.RandomState(14).randn(self.embedding_dim),
            'math_ops'
        )
        embeddings['MODULO'] = SemanticEmbedding(
            'MODULO',
            math_base + 0.1 * np.random.RandomState(16).randn(self.embedding_dim),
            'math_ops'
        )
        
        # General patterns
        general_base = np.random.RandomState(48).randn(self.embedding_dim)
        embeddings['WHILE_NEQ'] = SemanticEmbedding(
            'WHILE_NEQ',
            general_base + 0.1 * np.random.RandomState(17).randn(self.embedding_dim),
            'iteration'
        )
        embeddings['TEMP_SWAP'] = SemanticEmbedding(
            'TEMP_SWAP',
            general_base + 0.1 * np.random.RandomState(18).randn(self.embedding_dim),
            'general'
        )
        embeddings['SIMPLE_LOOP'] = SemanticEmbedding(
            'SIMPLE_LOOP',
            general_base + 0.1 * np.random.RandomState(19).randn(self.embedding_dim),
            'iteration'
        )
        
        return embeddings
    
    def get_pattern_embedding(self, ast_sequence: List[str]) -> np.ndarray:
        """Convert AST sequence to semantic embedding."""
        # Extract semantic patterns from sequence
        patterns = self._extract_patterns(ast_sequence)
        
        if not patterns:
            # Return zero vector if no patterns found
            return np.zeros(self.embedding_dim)
        
        # Group patterns by semantic group
        group_embeddings = defaultdict(list)
        for pattern in patterns:
            if pattern in self.embeddings:
                emb = self.embeddings[pattern]
                group_embeddings[emb.semantic_group].append(emb.vector)
        
        # Combine embeddings with group weighting
        final_embedding = np.zeros(self.embedding_dim)
        
        # Dynamic weights based on what patterns we found
        has_algorithm_specific = any(g in group_embeddings for g in ['quicksort', 'mergesort'])
        
        if has_algorithm_specific:
            # If we have algorithm-specific patterns, weight them heavily
            group_weights = {
                'quicksort': 0.4,
                'mergesort': 0.4,
                'recursion': 0.2,
                'control_flow': 0.15,
                'array_ops': 0.15,
                'iteration': 0.05,
                'math_ops': 0.05,
                'general': 0.05
            }
        else:
            # For general algorithms, use balanced weights
            group_weights = {
                'control_flow': 0.25,
                'iteration': 0.25,
                'math_ops': 0.20,
                'array_ops': 0.15,
                'general': 0.15,
                'recursion': 0.10,
                'quicksort': 0.05,
                'mergesort': 0.05
            }
        
        for group, embeddings_list in group_embeddings.items():
            if embeddings_list:
                # Average within group
                group_avg = np.mean(embeddings_list, axis=0)
                weight = group_weights.get(group, 0.1)
                final_embedding += weight * group_avg
        
        # Normalize
        norm = np.linalg.norm(final_embedding)
        if norm > 0:
            final_embedding = final_embedding / norm
            
        return final_embedding
    
    def _extract_patterns(self, sequence: List[str]) -> List[str]:
        """Extract semantic patterns from AST sequence."""
        patterns = []
        
        # Always add a simple loop pattern if we see a loop
        if any('LOOP' in s or 'WHILE' in s for s in sequence):
            patterns.append('SIMPLE_LOOP')
        
        # Sliding window pattern detection
        for i in range(len(sequence)):
            # Single node patterns
            node = sequence[i]
            
            # Look for modulo operations
            if 'BINARY_OP:MOD' in node or node == '%':
                patterns.append('MODULO')
            
            # Two-node patterns
            if i < len(sequence) - 1:
                next_node = sequence[i + 1]
                
                # Control flow patterns
                if node == 'CONDITIONAL' and 'BINARY_OP:LT' in sequence[max(0, i-3):i+3]:
                    patterns.append('IF_LT')
                elif node == 'CONDITIONAL' and 'BINARY_OP:GT' in sequence[max(0, i-3):i+3]:
                    patterns.append('IF_GT')
                elif node == 'CONDITIONAL' and 'BINARY_OP:EQ' in sequence[max(0, i-3):i+3]:
                    patterns.append('IF_EQ')
                elif node == 'CONDITIONAL' and ('BINARY_OP:NEQ' in sequence[max(0, i-3):i+3] or 'COMPARISON:NEQ' in sequence[max(0, i-3):i+3]):
                    patterns.append('IF_NEQ')
                
                # Loop patterns
                if node == 'LOOP' and 'VAR:INDEX' in sequence[i:i+5]:
                    patterns.append('FOR_RANGE')
                elif node == 'LOOP' and 'CONDITIONAL' in sequence[i:i+5]:
                    patterns.append('WHILE_CONDITION')
                elif ('WHILE' in node or 'LOOP' in node) and ('NEQ' in str(sequence[max(0, i-3):i+5]) or '!=' in str(sequence[max(0, i-3):i+5])):
                    patterns.append('WHILE_NEQ')
                
                # Temp swap pattern
                if 'ASSIGN' in node and 'temp' in str(sequence[max(0, i-5):i+5]).lower():
                    patterns.append('TEMP_SWAP')
            
            # Three-node patterns
            if i < len(sequence) - 2:
                third_node = sequence[i + 2]
                
                # Recursion patterns - only if we see multiple calls
                call_count = sum(1 for s in sequence if 'CALL' in s)
                if call_count >= 2:  # Need at least 2 calls for recursion
                    if 'CALL' in node and 'CONDITIONAL' in sequence[max(0, i-5):i]:
                        patterns.append('BASE_CASE')
                    elif 'CALL' in node and any('CALL' in s for s in sequence[i+1:min(i+10, len(sequence))]):
                        patterns.append('RECURSIVE_CALL')
                
                # Algorithm-specific patterns
                if 'CALL:PARTITION' in node:
                    patterns.append('PARTITION_CALL')
                    patterns.append('RECURSIVE_SORT')  # Quicksort always has partition
                if 'VAR:PIVOT' in node and 'BINARY_OP' in str(sequence[max(0, i-2):i+3]):
                    patterns.append('PIVOT_COMPARE')
                    patterns.append('PARTITION_CALL')  # Pivot compare implies partition
                if 'CALL' in node and 'quicksort' in node.lower():
                    patterns.append('RECURSIVE_SORT')
                if 'CALL' in node and 'CALL' in str(sequence[i+1:i+5]):
                    # Two recursive calls in sequence = divide and conquer
                    patterns.append('RECURSIVE_SORT')
                if 'VAR:PIVOT' in str(sequence[max(0,i-5):i+5]):
                    patterns.append('PARTITION_CALL')  # Pivot usage implies partition
                    
                # Additional quicksort patterns - only if we have partition context
                if 'VAR:PIVOT' in str(sequence[max(0,i-10):i+10]) or 'CALL:PARTITION' in str(sequence):
                    if 'ASSIGN' in node and any(x in str(sequence[max(0,i-3):i+3]) for x in ['VAR:LEFT', 'VAR:RIGHT', 'VAR:INDEX']):
                        patterns.append('PARTITION_CALL')
                    if 'BINOP' in node and 'VAR:PIVOT' in str(sequence[max(0,i-5):i+5]):
                        patterns.append('PIVOT_COMPARE')
                    if 'LOOP' in node and 'VAR:INDEX' in str(sequence[i:i+10]) and 'VAR:PIVOT' in str(sequence):
                        patterns.append('PARTITION_CALL')
                
                # Array operations
                if 'VAR:ARRAY' in node and 'ASSIGN' in str(sequence[i:i+5]):
                    patterns.append('ARRAY_SWAP')
                elif 'VAR:ARRAY' in node or 'INDEX' in node:
                    patterns.append('ARRAY_ACCESS')
                
                # Math operations
                if 'ADD' in node and 'VAR' in str(sequence[max(0, i-2):i+2]):
                    patterns.append('INCREMENT')
                elif 'SUB' in node and 'VAR' in str(sequence[max(0, i-2):i+2]):
                    patterns.append('DECREMENT')
        
        return patterns
    
    def _hash_based_embedding(self, patterns: List[str]) -> np.ndarray:
        """Create embedding from hash of patterns."""
        # Combine patterns into string
        pattern_str = '|'.join(sorted(patterns))
        
        # Use hash to seed random generator
        hash_val = int(hashlib.md5(pattern_str.encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(hash_val)
        
        # Generate consistent embedding
        return rng.randn(self.embedding_dim)
    
    def sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate semantic similarity between two AST sequences."""
        # Get embeddings
        emb1 = self.get_pattern_embedding(seq1)
        emb2 = self.get_pattern_embedding(seq2)
        
        # Cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to [0, 1]
        return (similarity + 1) / 2
    
    def get_semantic_fingerprint(self, ast_sequence: List[str]) -> Dict[str, Any]:
        """Generate semantic fingerprint from AST sequence."""
        # Extract patterns
        patterns = self._extract_patterns(ast_sequence)
        pattern_counts = {}
        for p in patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
        
        # Get embedding
        embedding = self.get_pattern_embedding(ast_sequence)
        
        # Generate hash of embedding for quick comparison
        embedding_hash = hashlib.sha256(embedding.tobytes()).hexdigest()[:16]
        
        return {
            'patterns': pattern_counts,
            'embedding': embedding,
            'embedding_hash': embedding_hash,
            'sequence_length': len(ast_sequence)
        }