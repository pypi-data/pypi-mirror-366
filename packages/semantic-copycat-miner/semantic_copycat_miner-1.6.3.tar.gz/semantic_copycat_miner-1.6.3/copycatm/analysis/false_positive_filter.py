"""
False Positive Filter for Algorithm Detection.

This module provides comprehensive filtering to reduce false positives
in algorithm detection by analyzing context, complexity, and patterns.
"""

from typing import Dict, List, Any
import re
from ..analysis.algorithm_types import AlgorithmType


class FalsePositiveFilter:
    """Filter to reduce false positives in algorithm detection."""
    
    def __init__(self):
        """Initialize the false positive filter."""
        # Common utility functions that should not be detected as algorithms
        self.utility_functions = {
            'main', 'init', '__init__', 'setup', 'teardown', 'cleanup',
            'test', 'assert', 'validate', 'check', 'verify',
            'get', 'set', 'update', 'delete', 'create', 'read', 'write',
            'open', 'close', 'connect', 'disconnect',
            'start', 'stop', 'run', 'execute',
            'parse', 'format', 'convert', 'transform',
            'log', 'debug', 'info', 'warn', 'error',
            'handle', 'process', 'dispatch', 'route',
            'configure', 'initialize', 'finalize',
            'toString', 'valueOf', 'equals', 'hashCode',
            'render', 'draw', 'paint', 'display',
            'save', 'load', 'export', 'import'
        }
        
        # Keywords that indicate simple control flow, not algorithms
        self.simple_control_keywords = {
            'for', 'while', 'if', 'else', 'elif', 'switch', 'case',
            'try', 'catch', 'finally', 'throw', 'raise',
            'return', 'break', 'continue', 'pass', 'yield'
        }
        
        # Minimum complexity thresholds by algorithm type
        self.min_complexity = {
            AlgorithmType.SORTING_ALGORITHM: 3,
            AlgorithmType.SEARCH_ALGORITHM: 2,
            AlgorithmType.GRAPH_TRAVERSAL: 4,
            AlgorithmType.DYNAMIC_PROGRAMMING: 4,
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM: 3,
            AlgorithmType.NUMERICAL_ALGORITHM: 3,
            AlgorithmType.COMPRESSION_ALGORITHM: 4,
            AlgorithmType.AUDIO_CODEC: 1,  # Lower threshold for audio codecs
            AlgorithmType.VIDEO_CODEC: 1,  # Lower threshold for video codecs
            AlgorithmType.SIGNAL_PROCESSING: 3,
            AlgorithmType.IMAGE_PROCESSING: 3,
        }
        
        # Pattern-specific filters
        self.pattern_filters = {
            'fft_transform': self._filter_fft_false_positive,
            'linear_search': self._filter_linear_search_false_positive,
            'bubble_sort': self._filter_bubble_sort_false_positive,
        }
    
    def should_filter(self, 
                     func_name: str,
                     func_text: str,
                     algo_type: AlgorithmType,
                     subtype: str,
                     confidence: float,
                     complexity: int = None) -> bool:
        """
        Determine if a detection should be filtered as false positive.
        
        Returns True if the detection should be filtered out.
        """
        
        # Handle None confidence values
        if confidence is None:
            confidence = 0.0
        
        # High confidence detections are likely real algorithms
        if confidence >= 0.7:
            return False
        
        # Special handling for audio/video codecs - lower threshold
        if algo_type in [AlgorithmType.AUDIO_CODEC, AlgorithmType.VIDEO_CODEC]:
            # For codec functions, use a lower confidence threshold
            if confidence >= 0.6:
                return False
            # Also check if function name strongly indicates codec
            if any(indicator in func_name.lower() for indicator in ['encode', 'decode', 'codec']):
                if confidence >= 0.5:
                    return False
        
        # Check utility function names
        if self._is_utility_function(func_name):
            return True
        
        # Check simple control flow only if we have function text
        if func_text and self._is_simple_control_flow(func_name, func_text):
            return True
        
        # Check minimum complexity only if available
        if complexity is not None and not self._meets_complexity_threshold(algo_type, complexity):
            return True
        
        # Apply pattern-specific filters only if we have function text
        if func_text and subtype in self.pattern_filters:
            if self.pattern_filters[subtype](func_name, func_text):
                    return True
        
        # Filter low confidence detections for certain types
        if self._should_filter_by_confidence(algo_type, subtype, confidence):
            return True
        
        # Check context clues only if we have function text
        if func_text and self._has_disqualifying_context(func_text, algo_type, subtype):
            return True
        
        return False
    
    def _is_utility_function(self, func_name: str) -> bool:
        """Check if function name indicates a utility function."""
        func_lower = func_name.lower()
        
        # Direct match
        if func_lower in self.utility_functions:
            return True
        
        # Check prefixes/suffixes
        utility_prefixes = ['get_', 'set_', 'is_', 'has_', 'check_', 'validate_']
        utility_suffixes = ['_handler', '_callback', '_listener', '_helper']
        
        for prefix in utility_prefixes:
            if func_lower.startswith(prefix):
                return True
        
        for suffix in utility_suffixes:
            if func_lower.endswith(suffix):
                return True
        
        return False
    
    def _is_simple_control_flow(self, func_name: str, func_text: str) -> bool:
        """Check if this is just simple control flow, not an algorithm."""
        # If function name is a control keyword
        if func_name.lower() in self.simple_control_keywords:
            return True
        
        # If func_text is empty, we can't determine - don't filter
        if not func_text:
            return False
        
        # Count lines of actual logic (excluding comments and blank lines)
        lines = func_text.split('\n')
        logic_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(('#', '//', '/*', '*')):
                logic_lines += 1
        
        # Too short to be a meaningful algorithm
        # Note: Some algorithms like list comprehension quicksort can be very short
        if logic_lines < 3:  # Reduced from 5
            return True
        
        return False
    
    def _meets_complexity_threshold(self, algo_type: AlgorithmType, complexity: int) -> bool:
        """Check if complexity meets minimum threshold for algorithm type."""
        min_complexity = self.min_complexity.get(algo_type, 2)
        return complexity >= min_complexity
    
    def _should_filter_by_confidence(self, algo_type: AlgorithmType, subtype: str, confidence: float) -> bool:
        """Filter low confidence detections for certain algorithm types."""
        # High threshold for generic detections
        if subtype == 'generic' and confidence < 0.7:
            return True
        
        # Medium threshold for complex algorithms
        complex_types = {
            AlgorithmType.DYNAMIC_PROGRAMMING,
            AlgorithmType.GRAPH_TRAVERSAL,
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM
        }
        if algo_type in complex_types and confidence < 0.5:
            return True
        
        return False
    
    def _has_disqualifying_context(self, func_text: str, algo_type: AlgorithmType, subtype: str) -> bool:
        """Check for context that disqualifies the detection."""
        # Check for test/example code indicators
        test_indicators = [
            r'test_', r'example', r'demo', r'sample',
            r'TODO', r'FIXME', r'NOT IMPLEMENTED'
        ]
        for indicator in test_indicators:
            if re.search(indicator, func_text, re.IGNORECASE):
                # Test code can contain algorithms, but be more strict
                return False  # Don't filter test code algorithms
        
        # Check for framework-specific patterns that look like algorithms
        framework_patterns = [
            r'@app\.route',  # Flask routes
            r'def get\(self, request\)',  # Django views
            r'async def on_',  # Discord bot handlers
        ]
        for pattern in framework_patterns:
            if re.search(pattern, func_text):
                return True
        
        return False
    
    def _filter_fft_false_positive(self, func_name: str, func_text: str) -> bool:
        """Filter false positives for FFT detection."""
        # Simple for loops should not be detected as FFT
        if 'fft' not in func_name.lower() and 'fourier' not in func_name.lower():
            # Check if it's actually doing FFT-like operations
            fft_indicators = [
                r'np\.fft', r'scipy\.fft', r'fftw',
                r'real.*imag', r'complex', r'frequency',
                r'spectrum', r'dft', r'idft'
            ]
            
            has_fft_indicator = any(
                re.search(pattern, func_text, re.IGNORECASE) 
                for pattern in fft_indicators
            )
            
            if not has_fft_indicator:
                # Check if it's just a simple loop
                if re.search(r'for\s+\w+\s+in\s+range', func_text):
                    # Count nested loops
                    for_count = len(re.findall(r'for\s+\w+\s+in', func_text))
                    if for_count < 2:  # FFT typically has nested loops
                        return True
        
        return False
    
    def _filter_linear_search_false_positive(self, func_name: str, func_text: str) -> bool:
        """Filter false positives for linear search detection."""
        # Check if it's actually searching for something
        search_indicators = [
            r'target', r'search', r'find', r'locate',
            r'==\s*\w+.*return', r'if.*==.*:\s*return'
        ]
        
        has_search_indicator = any(
            re.search(pattern, func_text, re.IGNORECASE) 
            for pattern in search_indicators
        )
        
        if not has_search_indicator:
            # It's probably just iterating, not searching
            return True
        
        # Check for graph traversal patterns that might be misclassified
        graph_indicators = ['graph', 'node', 'vertex', 'edge', 'neighbor', 'visited']
        if any(indicator in func_text.lower() for indicator in graph_indicators):
            return True
        
        return False
    
    def _filter_bubble_sort_false_positive(self, func_name: str, func_text: str) -> bool:
        """Filter false positives for bubble sort detection."""
        # Bubble sort needs nested loops and swapping
        nested_loops = len(re.findall(r'for\s+\w+\s+in', func_text)) >= 2
        has_swap = re.search(r'\w+\s*,\s*\w+\s*=\s*\w+\s*,\s*\w+', func_text) is not None
        
        if not (nested_loops and has_swap):
            return True
        
        return False
    
    def enhance_detection_results(self, 
                                results: List[Dict[str, Any]], 
                                file_content: str = None) -> List[Dict[str, Any]]:
        """
        Post-process detection results to filter false positives.
        
        Returns filtered list of algorithm detections.
        """
        filtered_results = []
        
        for result in results:
            
            func_name = result.get('function_name', 'unknown')
            algo_type = result.get('algorithm_type')
            subtype = result.get('algorithm_subtype', 'generic')
            confidence = result.get('confidence', 0.0)
            
            # Handle string algorithm type
            if isinstance(algo_type, str):
                # Convert string to AlgorithmType enum if needed
                try:
                    from ..analysis.algorithm_types import AlgorithmType
                    algo_type = AlgorithmType[algo_type.upper()]
                except:
                    # Don't filter if we can't determine type
                    filtered_results.append(result)
                    continue
            
            # Extract function text if possible
            func_text = result.get('function_code', '')
            if not func_text and file_content and 'location' in result:
                start = result['location'].get('start_line', 0)
                end = result['location'].get('end_line', len(file_content.split('\n')))
                lines = file_content.split('\n')[start-1:end]
                func_text = '\n'.join(lines)
            
            # If still no function text, try ast_representation
            if not func_text and 'ast_representation' in result:
                ast_repr = result['ast_representation']
                # If it's a dict, convert to string
                if isinstance(ast_repr, dict):
                    func_text = str(ast_repr)
                else:
                    func_text = ast_repr
            
            
            # Get complexity if available
            complexity = None
            if 'complexity' in result:
                complexity = result['complexity'].get('cyclomatic', 0)
            
            
            # Apply filtering
            if not self.should_filter(func_name, func_text, algo_type, subtype, confidence, complexity):
                filtered_results.append(result)
        
        return filtered_results