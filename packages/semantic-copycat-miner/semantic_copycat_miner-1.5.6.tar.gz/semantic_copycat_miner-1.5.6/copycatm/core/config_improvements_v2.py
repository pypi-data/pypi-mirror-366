"""
Configuration for improved algorithm detection v2.
Includes fixes for merge sort, RLE addition, and false positive reduction.
"""

from typing import Optional
from .config import AnalysisConfig
from ..analysis.algorithm_detector_improvements import ImprovedAlgorithmDetector


def create_improved_analyzer_v2(base_analyzer_class, config: Optional[AnalysisConfig] = None):
    """
    Create analyzer with all improvements including:
    - Multimedia patterns (from FFmpeg analysis)
    - Fixed merge sort detection
    - RLE compression pattern
    - Reduced false positives
    - Improved confidence thresholds
    
    Args:
        base_analyzer_class: The base CopycatAnalyzer class
        config: Optional analysis configuration
        
    Returns:
        Enhanced analyzer instance
    """
    if config is None:
        config = AnalysisConfig()
    
    # Create base analyzer
    analyzer = base_analyzer_class(config=config)
    
    # Replace algorithm detector with improved version
    improved_detector = ImprovedAlgorithmDetector(config)
    
    # Store original methods
    original_analyze = analyzer.analyze_file
    original_analyze_code = analyzer.analyze_code
    
    def analyze_with_improvements(file_path, force_language=None):
        """Analyze file with improved algorithm detection."""
        # Temporarily replace the detector
        old_detector = analyzer.algorithm_detector
        analyzer.algorithm_detector = improved_detector
        
        try:
            # Store file path for context
            analyzer._current_file_path = file_path
            result = original_analyze(file_path, force_language)
            
            # Post-process to ensure no duplicate algorithms
            if 'algorithms' in result:
                result['algorithms'] = _deduplicate_algorithms(result['algorithms'])
            
            return result
        finally:
            # Restore original detector
            analyzer.algorithm_detector = old_detector
            analyzer._current_file_path = None
    
    def analyze_code_with_improvements(code, language, file_path=None):
        """Analyze code with improved algorithm detection."""
        # Temporarily replace the detector
        old_detector = analyzer.algorithm_detector
        analyzer.algorithm_detector = improved_detector
        
        try:
            result = original_analyze_code(code, language, file_path)
            
            # Post-process to ensure no duplicate algorithms
            if 'algorithms' in result:
                result['algorithms'] = _deduplicate_algorithms(result['algorithms'])
            
            return result
        finally:
            # Restore original detector
            analyzer.algorithm_detector = old_detector
    
    # Replace methods
    analyzer.analyze_file = analyze_with_improvements
    analyzer.analyze_code = analyze_code_with_improvements
    
    return analyzer


def _deduplicate_algorithms(algorithms):
    """
    Remove duplicate algorithm detections and merge helper functions.
    """
    seen = {}
    filtered = []
    
    for algo in algorithms:
        key = (
            algo.get('algorithm_subtype', ''),
            algo.get('lines', {}).get('start', 0),
            algo.get('lines', {}).get('end', 0)
        )
        
        # Special handling for merge sort and its helper
        if algo.get('algorithm_subtype') == 'merge_helper':
            # Don't include merge helper as separate algorithm
            continue
        elif algo.get('algorithm_subtype') == 'merge_sort':
            # Boost confidence if we also detected merge helper
            if any(a.get('algorithm_subtype') == 'merge_helper' for a in algorithms):
                algo['confidence'] = min(1.0, algo.get('confidence', 0) + 0.1)
                algo['evidence']['has_merge_helper'] = True
        
        if key not in seen:
            seen[key] = algo
            filtered.append(algo)
        else:
            # Keep the one with higher confidence
            if algo.get('confidence', 0) > seen[key].get('confidence', 0):
                filtered.remove(seen[key])
                seen[key] = algo
                filtered.append(algo)
    
    return filtered


# Convenience function
def create_best_analyzer(base_analyzer_class):
    """
    Create the best available analyzer with all improvements.
    
    This includes:
    - Enhanced algorithm detection (V2)
    - Improved MinHash
    - Improved invariant extraction
    - FFmpeg patterns
    - Fixed merge sort detection
    - RLE compression pattern
    - Reduced false positives
    - Better confidence thresholds
    """
    config = AnalysisConfig(
        complexity_threshold=3,
        min_lines=20,
        hash_algorithms=["sha256", "tlsh", "minhash", "simhash"]
    )
    
    return create_improved_analyzer_v2(base_analyzer_class, config)