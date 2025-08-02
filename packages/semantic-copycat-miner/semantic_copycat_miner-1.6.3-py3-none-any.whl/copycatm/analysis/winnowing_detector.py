"""
Winnowing-enhanced algorithm detection for CopycatM.

This module uses the Winnowing algorithm to detect algorithms through
fingerprint matching, providing robust detection against code transformations.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from ..hashing.winnowing import Winnowing, WinnowingConfig

logger = logging.getLogger(__name__)


@dataclass
class AlgorithmFingerprint:
    """Stored fingerprint for a known algorithm."""
    algorithm_type: str
    algorithm_subtype: str
    fingerprint: List[Tuple[int, int]]
    language: str
    source: str  # Original source for reference
    metadata: Dict[str, Any]


@dataclass
class WinnowingMatch:
    """Result of winnowing-based algorithm detection."""
    algorithm_type: str
    algorithm_subtype: str
    confidence: float
    similarity_score: float
    matching_regions: List[Dict[str, int]]
    fingerprint_overlap: int
    total_fingerprints: int


class WinnowingDetector:
    """Algorithm detection using Winnowing fingerprints."""
    
    def __init__(self, config: Optional[WinnowingConfig] = None,
                 fingerprint_db_path: Optional[str] = None):
        """
        Initialize Winnowing detector.
        
        Args:
            config: Winnowing configuration
            fingerprint_db_path: Path to fingerprint database
        """
        self.config = config or WinnowingConfig()
        self.winnowing = Winnowing(self.config)
        self.fingerprint_db: Dict[str, List[AlgorithmFingerprint]] = {}
        
        # Load fingerprint database
        if fingerprint_db_path:
            self.load_fingerprint_database(fingerprint_db_path)
        else:
            # Initialize with built-in fingerprints
            self._initialize_builtin_fingerprints()
    
    def _initialize_builtin_fingerprints(self):
        """Initialize with common algorithm fingerprints."""
        # This would be populated with pre-computed fingerprints
        # For now, we'll compute them on-the-fly from known implementations
        
        known_algorithms = {
            'sorting_algorithm': {
                'quicksort': {
                    'python': '''def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)''',
                    'javascript': '''function quickSort(arr) {
    if (arr.length <= 1) return arr;
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    return [...quickSort(left), ...middle, ...quickSort(right)];
}''',
                    'c': '''void quicksort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = (low - 1);
    for (int j = low; j <= high - 1; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}'''
                },
                'mergesort': {
                    'python': '''def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result'''
                }
            },
            'search_algorithm': {
                'binary_search': {
                    'python': '''def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
                    'javascript': '''function binarySearch(arr, target) {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (arr[mid] === target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}'''
                }
            }
        }
        
        # Generate fingerprints for known algorithms
        for algo_type, subtypes in known_algorithms.items():
            if algo_type not in self.fingerprint_db:
                self.fingerprint_db[algo_type] = []
                
            for subtype, implementations in subtypes.items():
                for language, code in implementations.items():
                    signature = self.winnowing.generate_signature(code, language)
                    
                    algo_fp = AlgorithmFingerprint(
                        algorithm_type=algo_type,
                        algorithm_subtype=subtype,
                        fingerprint=signature['fingerprint'],
                        language=language,
                        source=code,
                        metadata=signature
                    )
                    
                    self.fingerprint_db[algo_type].append(algo_fp)
                    
        logger.info(f"Initialized {sum(len(fps) for fps in self.fingerprint_db.values())} algorithm fingerprints")
    
    def detect_algorithm(self, code: str, language: Optional[str] = None,
                        threshold: float = 0.7) -> Optional[WinnowingMatch]:
        """
        Detect algorithm using winnowing fingerprints.
        
        Args:
            code: Source code to analyze
            language: Programming language
            threshold: Minimum similarity threshold
            
        Returns:
            Best matching algorithm or None
        """
        # Generate fingerprint for input code
        code_fingerprint = self.winnowing.generate_fingerprint(code, language)
        
        if not code_fingerprint:
            return None
        
        best_match = None
        best_score = 0.0
        
        # Compare against all known fingerprints
        for algo_type, fingerprints in self.fingerprint_db.items():
            for algo_fp in fingerprints:
                # For cross-language detection, we still want to compare
                # but may apply a small penalty for different languages
                language_penalty = 0.0
                if language and algo_fp.language != language:
                    language_penalty = 0.1  # 10% penalty for cross-language
                    
                # Calculate similarity
                similarity = self.winnowing.compare_fingerprints(
                    code_fingerprint, 
                    algo_fp.fingerprint
                )
                
                logger.debug(f"Comparing with {algo_fp.algorithm_type}/{algo_fp.algorithm_subtype} "
                           f"({algo_fp.language}): similarity={similarity:.3f}")
                
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    
                    # Find matching regions
                    matching_regions = self.winnowing.find_matching_regions(
                        code_fingerprint,
                        algo_fp.fingerprint
                    )
                    
                    # Calculate confidence based on similarity and coverage
                    coverage = len(matching_regions) / max(
                        len(code_fingerprint), 
                        len(algo_fp.fingerprint)
                    )
                    confidence = (similarity + coverage) / 2
                    
                    # Apply language penalty
                    confidence = confidence * (1 - language_penalty)
                    
                    best_match = WinnowingMatch(
                        algorithm_type=algo_fp.algorithm_type,
                        algorithm_subtype=algo_fp.algorithm_subtype,
                        confidence=confidence,
                        similarity_score=similarity,
                        matching_regions=matching_regions,
                        fingerprint_overlap=len(matching_regions),
                        total_fingerprints=len(code_fingerprint)
                    )
        
        return best_match
    
    def detect_multiple_algorithms(self, code: str, language: Optional[str] = None,
                                 threshold: float = 0.5) -> List[WinnowingMatch]:
        """
        Detect multiple algorithms in code.
        
        Args:
            code: Source code to analyze
            language: Programming language
            threshold: Minimum similarity threshold
            
        Returns:
            List of matching algorithms sorted by confidence
        """
        matches = []
        
        # Generate fingerprint for input code
        code_fingerprint = self.winnowing.generate_fingerprint(code, language)
        
        if not code_fingerprint:
            return matches
        
        # Compare against all known fingerprints
        for algo_type, fingerprints in self.fingerprint_db.items():
            for algo_fp in fingerprints:
                # Skip if language doesn't match
                if language and algo_fp.language != language:
                    continue
                    
                # Calculate similarity
                similarity = self.winnowing.compare_fingerprints(
                    code_fingerprint,
                    algo_fp.fingerprint
                )
                
                if similarity >= threshold:
                    # Find matching regions
                    matching_regions = self.winnowing.find_matching_regions(
                        code_fingerprint,
                        algo_fp.fingerprint
                    )
                    
                    # Calculate confidence
                    coverage = len(matching_regions) / max(
                        len(code_fingerprint),
                        len(algo_fp.fingerprint)
                    )
                    confidence = (similarity + coverage) / 2
                    
                    match = WinnowingMatch(
                        algorithm_type=algo_fp.algorithm_type,
                        algorithm_subtype=algo_fp.algorithm_subtype,
                        confidence=confidence,
                        similarity_score=similarity,
                        matching_regions=matching_regions,
                        fingerprint_overlap=len(matching_regions),
                        total_fingerprints=len(code_fingerprint)
                    )
                    
                    matches.append(match)
        
        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        
        # Remove duplicates (same algorithm detected multiple times)
        unique_matches = []
        seen = set()
        
        for match in matches:
            key = (match.algorithm_type, match.algorithm_subtype)
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def add_algorithm_fingerprint(self, code: str, algorithm_type: str,
                                algorithm_subtype: str, language: str) -> AlgorithmFingerprint:
        """
        Add a new algorithm fingerprint to the database.
        
        Args:
            code: Algorithm implementation
            algorithm_type: Type of algorithm
            algorithm_subtype: Specific algorithm name
            language: Programming language
            
        Returns:
            Generated algorithm fingerprint
        """
        signature = self.winnowing.generate_signature(code, language)
        
        algo_fp = AlgorithmFingerprint(
            algorithm_type=algorithm_type,
            algorithm_subtype=algorithm_subtype,
            fingerprint=signature['fingerprint'],
            language=language,
            source=code,
            metadata=signature
        )
        
        if algorithm_type not in self.fingerprint_db:
            self.fingerprint_db[algorithm_type] = []
            
        self.fingerprint_db[algorithm_type].append(algo_fp)
        
        return algo_fp
    
    def save_fingerprint_database(self, path: str):
        """Save fingerprint database to file."""
        data = {}
        
        for algo_type, fingerprints in self.fingerprint_db.items():
            data[algo_type] = []
            for fp in fingerprints:
                data[algo_type].append({
                    'algorithm_subtype': fp.algorithm_subtype,
                    'fingerprint': fp.fingerprint,
                    'language': fp.language,
                    'source': fp.source,
                    'metadata': fp.metadata
                })
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved {sum(len(fps) for fps in data.values())} fingerprints to {path}")
    
    def load_fingerprint_database(self, path: str):
        """Load fingerprint database from file."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
            self.fingerprint_db = {}
            
            for algo_type, fingerprints in data.items():
                self.fingerprint_db[algo_type] = []
                
                for fp_data in fingerprints:
                    algo_fp = AlgorithmFingerprint(
                        algorithm_type=algo_type,
                        algorithm_subtype=fp_data['algorithm_subtype'],
                        fingerprint=[(h, p) for h, p in fp_data['fingerprint']],
                        language=fp_data['language'],
                        source=fp_data['source'],
                        metadata=fp_data['metadata']
                    )
                    
                    self.fingerprint_db[algo_type].append(algo_fp)
                    
            logger.info(f"Loaded {sum(len(fps) for fps in self.fingerprint_db.values())} fingerprints from {path}")
            
        except Exception as e:
            logger.error(f"Failed to load fingerprint database: {e}")
            self._initialize_builtin_fingerprints()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the fingerprint database."""
        total_fingerprints = sum(len(fps) for fps in self.fingerprint_db.values())
        
        stats = {
            'total_algorithms': len(self.fingerprint_db),
            'total_fingerprints': total_fingerprints,
            'algorithms_by_type': {
                algo_type: len(fps) 
                for algo_type, fps in self.fingerprint_db.items()
            },
            'languages': set(),
            'average_fingerprint_size': 0
        }
        
        total_fp_size = 0
        for fps in self.fingerprint_db.values():
            for fp in fps:
                stats['languages'].add(fp.language)
                total_fp_size += len(fp.fingerprint)
                
        stats['languages'] = list(stats['languages'])
        stats['average_fingerprint_size'] = (
            total_fp_size / total_fingerprints if total_fingerprints > 0 else 0
        )
        
        return stats