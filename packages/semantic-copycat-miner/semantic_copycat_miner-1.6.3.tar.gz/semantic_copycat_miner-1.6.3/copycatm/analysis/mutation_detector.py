"""
Mutation detector for identifying code variations of known algorithms.

This module detects mutations of known algorithms where the similarity
is between 70-85%, indicating potential variations or adaptations.
"""

import logging
from typing import Dict, List, Any
import hashlib
from difflib import SequenceMatcher

from ..hashing import FuzzyHasher, SemanticHasher
from .pseudocode_normalizer import PseudocodeNormalizer

logger = logging.getLogger(__name__)


class MutationDetector:
    """
    Detects mutations of known algorithms with 70-85% similarity.
    
    Mutations include:
    - Variable renaming
    - Structure reorganization
    - Minor logic changes
    - Framework adaptations
    - Language translations
    """
    
    # Known algorithm patterns with their canonical representations
    KNOWN_PATTERNS = {
        'quicksort': {
            'canonical': 'FUNCTION VAR1\nCONDITION VAR LE VAR\nRETURN VAR\nASSIGN VAR ARRAY_ACCESS DIV\nASSIGN VAR FILTER LT VAR\nASSIGN VAR FILTER EQ VAR\nASSIGN VAR FILTER GT VAR\nRETURN CONCAT CALL CALL',
            'variants': [
                'pivot_selection', 'partition_scheme', 'recursion_style'
            ],
            'confidence_threshold': 0.7,
            'key_patterns': ['CONDITION VAR LE VAR', 'ARRAY_ACCESS DIV', 'CALL', 'RETURN']
        },
        'merge_sort': {
            'canonical': 'FUNCTION VAR1\nCONDITION VAR LE VAR\nRETURN VAR\nASSIGN VAR DIV\nASSIGN VAR SLICE\nASSIGN VAR SLICE\nRETURN CALL MERGE',
            'variants': [
                'split_method', 'merge_strategy', 'in_place'
            ],
            'confidence_threshold': 0.7
        },
        'binary_search': {
            'canonical': 'FUNCTION VAR1 VAR2\nLOOP CONDITION\nASSIGN VAR DIV ADD\nCONDITION EQ\nRETURN VAR\nCONDITION LT\nASSIGN VAR SUB\nASSIGN VAR ADD\nRETURN NEG',
            'variants': [
                'iterative', 'recursive', 'boundary_handling'
            ],
            'confidence_threshold': 0.75
        },
        'fibonacci': {
            'canonical': 'FUNCTION VAR1\nCONDITION VAR LE VAR\nRETURN VAR\nRETURN ADD CALL SUB CALL SUB',
            'variants': [
                'recursive', 'iterative', 'memoized', 'matrix'
            ],
            'confidence_threshold': 0.8
        },
        'dfs': {
            'canonical': 'FUNCTION VAR1 VAR2\nASSIGN VAR SET\nASSIGN VAR LIST\nLOOP CONDITION\nASSIGN VAR POP\nCONDITION IN\nCONTINUE\nADD VAR\nITERATE VAR\nAPPEND VAR',
            'variants': [
                'recursive', 'iterative', 'path_tracking'
            ],
            'confidence_threshold': 0.7
        },
        'bfs': {
            'canonical': 'FUNCTION VAR1 VAR2\nASSIGN VAR SET\nASSIGN VAR LIST\nLOOP CONDITION\nASSIGN VAR DEQUEUE\nCONDITION IN\nCONTINUE\nADD VAR\nITERATE VAR\nENQUEUE VAR',
            'variants': [
                'queue_type', 'visit_order', 'level_tracking'
            ],
            'confidence_threshold': 0.7
        }
    }
    
    def __init__(self):
        """Initialize mutation detector."""
        self.fuzzy_hasher = FuzzyHasher()
        self.semantic_hasher = SemanticHasher()
        self.normalizer = PseudocodeNormalizer()
    
    def detect_mutations(self, code_block: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """
        Detect if a code block is a mutation of a known algorithm.
        
        Args:
            code_block: Code block with normalized representation
            language: Programming language
            
        Returns:
            List of detected mutations with similarity scores
        """
        mutations = []
        
        # Get normalized representation
        normalized = code_block.get('normalized_code', '')
        if not normalized:
            logger.debug(f"No normalized code in block: {code_block.keys()}")
            return mutations
        
        logger.debug(f"Checking mutations for normalized code (first 100 chars): {normalized[:100]}")
        
        # Check against each known pattern
        for algo_name, pattern_info in self.KNOWN_PATTERNS.items():
            key_patterns = pattern_info.get('key_patterns', None)
            similarity = self._calculate_similarity(normalized, pattern_info['canonical'], key_patterns)
            logger.debug(f"Similarity with {algo_name}: {similarity:.3f}")
            
            # Check if it's in mutation range (70-85%)
            if 0.7 <= similarity <= 0.85:
                mutation_info = self._analyze_mutation(
                    code_block, pattern_info, algo_name, similarity
                )
                mutations.append(mutation_info)
                logger.info(f"Found mutation of {algo_name} with similarity {similarity:.3f}")
            
        return mutations
    
    def _calculate_similarity(self, code1: str, code2: str, key_patterns: List[str] = None) -> float:
        """Calculate similarity between two normalized code representations."""
        # Use sequence matcher for basic similarity
        seq_similarity = SequenceMatcher(None, code1, code2).ratio()
        
        # Calculate token-based similarity
        tokens1 = set(code1.split())
        tokens2 = set(code2.split())
        
        if not tokens1 or not tokens2:
            return seq_similarity
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard = len(intersection) / len(union) if union else 0
        
        # Check for key patterns if provided
        pattern_boost = 0.0
        if key_patterns:
            pattern_matches = sum(1 for pattern in key_patterns if pattern in code1)
            pattern_boost = min(0.3, pattern_matches * 0.1)  # Up to 0.3 boost
        
        # Weighted average with pattern boost
        base_similarity = 0.6 * seq_similarity + 0.4 * jaccard
        return min(1.0, base_similarity + pattern_boost)
    
    def _analyze_mutation(self, code_block: Dict[str, Any], 
                         pattern_info: Dict[str, Any], 
                         algo_name: str, 
                         similarity: float) -> Dict[str, Any]:
        """Analyze the specific type of mutation."""
        normalized = code_block.get('normalized_code', '')
        canonical = pattern_info['canonical']
        
        # Identify mutation type
        mutation_types = []
        
        # Check for structural changes
        if self._has_structural_changes(normalized, canonical):
            mutation_types.append('structural_reorganization')
        
        # Check for logic variations
        if self._has_logic_variations(normalized, canonical):
            mutation_types.append('logic_variation')
        
        # Check for additional operations
        if self._has_additional_operations(normalized, canonical):
            mutation_types.append('extended_functionality')
        
        # Generate mutation hash
        mutation_hash = self._generate_mutation_hash(code_block, algo_name, similarity)
        
        return {
            'algorithm_name': algo_name,
            'mutation_type': 'variant',
            'similarity_score': similarity,
            'mutation_types': mutation_types,
            'confidence': similarity * pattern_info['confidence_threshold'],
            'mutation_hash': mutation_hash,
            'evidence': {
                'normalized_diff': self._get_normalized_diff(normalized, canonical),
                'variant_indicators': self._detect_variant_indicators(normalized, pattern_info['variants']),
                'structural_similarity': self._calculate_structural_similarity(normalized, canonical)
            },
            'transformation_resistance': {
                'mutation_detection': 0.85,
                'variant_identification': 0.75,
                'pattern_matching': similarity
            }
        }
    
    def _has_structural_changes(self, code1: str, code2: str) -> bool:
        """Check if there are structural changes between code versions."""
        # Extract control structures
        structures1 = [line for line in code1.split('\n') if any(
            keyword in line for keyword in ['LOOP', 'CONDITION', 'FUNCTION']
        )]
        structures2 = [line for line in code2.split('\n') if any(
            keyword in line for keyword in ['LOOP', 'CONDITION', 'FUNCTION']
        )]
        
        return structures1 != structures2
    
    def _has_logic_variations(self, code1: str, code2: str) -> bool:
        """Check for logic variations."""
        # Extract operations
        ops1 = [line for line in code1.split('\n') if any(
            op in line for op in ['ASSIGN', 'RETURN', 'CALL']
        )]
        ops2 = [line for line in code2.split('\n') if any(
            op in line for op in ['ASSIGN', 'RETURN', 'CALL']
        )]
        
        # Check if operations are reordered or modified
        return len(ops1) != len(ops2) or ops1 != ops2
    
    def _has_additional_operations(self, code1: str, code2: str) -> bool:
        """Check if additional operations were added."""
        lines1 = len(code1.split('\n'))
        lines2 = len(code2.split('\n'))
        
        return abs(lines1 - lines2) > 2
    
    def _generate_mutation_hash(self, code_block: Dict[str, Any], 
                               algo_name: str, similarity: float) -> str:
        """Generate a unique hash for the mutation."""
        mutation_data = f"{algo_name}:{similarity:.3f}:{code_block.get('normalized_code', '')}"
        return hashlib.sha256(mutation_data.encode()).hexdigest()[:16]
    
    def _get_normalized_diff(self, code1: str, code2: str) -> Dict[str, Any]:
        """Get differences between normalized representations."""
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')
        
        matcher = SequenceMatcher(None, lines1, lines2)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                changes.append({
                    'type': tag,
                    'from_lines': lines1[i1:i2],
                    'to_lines': lines2[j1:j2]
                })
        
        return {
            'total_changes': len(changes),
            'change_ratio': len(changes) / max(len(lines1), len(lines2)),
            'changes': changes[:5]  # Limit to first 5 changes
        }
    
    def _detect_variant_indicators(self, normalized: str, variants: List[str]) -> List[str]:
        """Detect which variant indicators are present."""
        detected = []
        
        variant_patterns = {
            'pivot_selection': ['DIV', 'RANDOM', 'FIRST', 'LAST'],
            'partition_scheme': ['FILTER', 'SWAP', 'TWO_POINTER'],
            'recursion_style': ['CALL', 'LOOP', 'STACK'],
            'split_method': ['SLICE', 'COPY', 'INDEX'],
            'merge_strategy': ['MERGE', 'COMBINE', 'SORT'],
            'in_place': ['SWAP', 'NO_COPY', 'MODIFY'],
            'iterative': ['LOOP', 'WHILE'],
            'recursive': ['CALL', 'RETURN CALL'],
            'boundary_handling': ['CONDITION', 'CHECK', 'VALIDATE'],
            'memoized': ['CACHE', 'STORE', 'LOOKUP'],
            'matrix': ['MATRIX', 'MULTIPLY', 'POWER'],
            'path_tracking': ['PATH', 'TRACK', 'RECORD'],
            'queue_type': ['QUEUE', 'DEQUEUE', 'FIFO'],
            'visit_order': ['ORDER', 'VISIT', 'PROCESS'],
            'level_tracking': ['LEVEL', 'DEPTH', 'LAYER']
        }
        
        for variant in variants:
            if variant in variant_patterns:
                patterns = variant_patterns[variant]
                if any(pattern in normalized for pattern in patterns):
                    detected.append(variant)
        
        return detected
    
    def _calculate_structural_similarity(self, code1: str, code2: str) -> float:
        """Calculate structural similarity between code blocks."""
        # Extract structure tokens
        structure_keywords = ['FUNCTION', 'LOOP', 'CONDITION', 'RETURN', 'ASSIGN']
        
        struct1 = [line for line in code1.split('\n') 
                  if any(kw in line for kw in structure_keywords)]
        struct2 = [line for line in code2.split('\n') 
                  if any(kw in line for kw in structure_keywords)]
        
        if not struct1 or not struct2:
            return 0.0
        
        return SequenceMatcher(None, struct1, struct2).ratio()
    
    def generate_mutation_hashes(self, mutations: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate various hashes for detected mutations."""
        hashes = {}
        
        for i, mutation in enumerate(mutations):
            # Generate composite mutation hash
            mutation_str = f"{mutation['algorithm_name']}:{mutation['similarity_score']}"
            
            # Direct hash of mutation signature
            hashes[f'mutation_{i}_sha256'] = hashlib.sha256(mutation_str.encode()).hexdigest()
            
            # Fuzzy hash for similarity comparison
            hashes[f'mutation_{i}_tlsh'] = self.fuzzy_hasher.tlsh(mutation_str)
            
            # Semantic hash for structural similarity
            hashes[f'mutation_{i}_simhash'] = self.semantic_hasher.generate_simhash(mutation_str)
        
        return hashes