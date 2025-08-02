"""
Minified code detection and analysis for CopycatM.

This module detects minified code and applies special analysis techniques
to extract algorithms and patterns from single-line, compressed code.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MinifiedCodeDetector:
    """
    Detects and analyzes minified code.
    
    Minified code characteristics:
    - Single or very few lines
    - No/minimal whitespace
    - Short variable names (often single letters)
    - No comments
    - High character density
    """
    
    def __init__(self):
        """Initialize minified code detector."""
        self.min_char_per_line_threshold = 200  # Characters per line to consider minified
        self.max_lines_threshold = 5  # Max lines to consider as potentially minified
        self.short_var_pattern = re.compile(r'\b[a-zA-Z]\b')  # Single letter variables
        self.function_pattern = re.compile(r'function\s*\w*\s*\(|=>\s*{|function\s*\(')
        
    def is_minified(self, content: str, language: str) -> Tuple[bool, float]:
        """
        Determine if code is minified.
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            Tuple of (is_minified, confidence_score)
        """
        lines = content.split('\n')
        line_count = len(lines)
        
        # Quick check for obvious cases
        if line_count > self.max_lines_threshold:
            return False, 0.0
            
        # Calculate metrics
        metrics = self._calculate_minification_metrics(content, lines, language)
        
        # Score based on multiple factors
        score = 0.0
        
        # Line-based scoring
        if line_count == 1:
            score += 0.3
        elif line_count <= 3:
            score += 0.2
            
        # Character density
        if metrics['avg_chars_per_line'] > self.min_char_per_line_threshold:
            score += 0.3
            
        # Variable naming
        if metrics['short_var_ratio'] > 0.7:
            score += 0.2
            
        # Whitespace ratio
        if metrics['whitespace_ratio'] < 0.1:
            score += 0.1
            
        # Function density (many functions in little space)
        if metrics['function_density'] > 0.01:  # More than 1 function per 100 chars
            score += 0.1
            
        is_minified = score >= 0.5
        return is_minified, min(score, 1.0)
        
    def _calculate_minification_metrics(self, content: str, lines: List[str], 
                                       language: str) -> Dict[str, float]:
        """Calculate metrics for minification detection."""
        total_chars = len(content)
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Average characters per line
        avg_chars_per_line = total_chars / max(len(non_empty_lines), 1)
        
        # Short variable ratio
        all_vars = self.short_var_pattern.findall(content)
        short_var_ratio = len(all_vars) / max(total_chars / 100, 1)  # Per 100 chars
        
        # Whitespace ratio
        whitespace_count = content.count(' ') + content.count('\t') + content.count('\n')
        whitespace_ratio = whitespace_count / max(total_chars, 1)
        
        # Function density
        function_matches = self.function_pattern.findall(content)
        function_density = len(function_matches) / max(total_chars, 1)
        
        return {
            'avg_chars_per_line': avg_chars_per_line,
            'short_var_ratio': short_var_ratio,
            'whitespace_ratio': whitespace_ratio,
            'function_density': function_density,
            'line_count': len(non_empty_lines),
            'total_chars': total_chars
        }
        
    def expand_minified_code(self, content: str, language: str) -> str:
        """
        Attempt to expand minified code for better analysis.
        
        This doesn't fully unminify but adds strategic newlines and spaces
        to help pattern matching.
        
        Args:
            content: Minified code content
            language: Programming language
            
        Returns:
            Partially expanded code
        """
        if language not in ['javascript', 'typescript']:
            return content  # Only handle JS/TS for now
            
        expanded = content
        
        # Add newlines after semicolons and braces
        expanded = re.sub(r';(?![\s}])', ';\n', expanded)
        expanded = re.sub(r'{', '{\n', expanded)
        expanded = re.sub(r'}', '\n}\n', expanded)
        
        # Add spaces around operators
        expanded = re.sub(r'([<>=!]+)', r' \1 ', expanded)
        expanded = re.sub(r'([+\-*/])', r' \1 ', expanded)
        
        # Add newlines for function definitions
        expanded = re.sub(r'function\s+(\w+)', r'\nfunction \1', expanded)
        
        # Clean up multiple newlines
        expanded = re.sub(r'\n\s*\n+', '\n', expanded)
        
        return expanded.strip()
        
    def extract_patterns_from_minified(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Extract algorithm patterns from minified code.
        
        Uses specialized techniques for compressed code.
        
        Args:
            content: Minified code content
            language: Programming language
            
        Returns:
            List of detected patterns
        """
        patterns = []
        logger.debug(f"Extracting patterns from minified {language} code ({len(content)} chars)")
        
        # Look for common algorithm signatures in minified form
        minified_patterns = {
            # Quicksort patterns - look for recursive function with partition-like behavior
            r'function\s+[qQ]\b.*?[qQ]\(.*?[qQ]\(': {
                'type': 'sorting_algorithm',
                'subtype': 'quicksort',
                'confidence': 0.7
            },
            # Partition function pattern (function r with pivot behavior)
            r'function\s+[rR]\b.*?\[\w+\].*?for.*?if.*?\[\w+\]<=': {
                'type': 'sorting_algorithm',
                'subtype': 'quicksort',
                'confidence': 0.6
            },
            # Recursive patterns - any function calling itself
            r'function\s+(\w)\b[^{]*\{[^}]*\1\([^)]*\)[^}]*\1\(': {
                'type': 'recursive_algorithm',
                'subtype': 'generic_recursion',
                'confidence': 0.5
            },
            # Loop patterns
            r'for\s*\([^)]*\).*?for\s*\([^)]*\)': {
                'type': 'nested_loop_algorithm',
                'subtype': 'nested_iteration',
                'confidence': 0.4
            },
            # Binary search pattern
            r'while.*?[<>].*?Math\.floor.*?/\s*2': {
                'type': 'search_algorithm',
                'subtype': 'binary_search',
                'confidence': 0.5
            }
        }
        
        for pattern, info in minified_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                logger.debug(f"Minified pattern matched: {info['type']}/{info['subtype']}")
                patterns.append({
                    'algorithm_type': info['type'],
                    'algorithm_subtype': info['subtype'],
                    'confidence': info['confidence'],
                    'evidence': {
                        'detection_method': 'minified_pattern_matching',
                        'pattern': pattern,
                        'matched_text': match.group(0)[:50]  # First 50 chars of match
                    }
                })
            else:
                logger.debug(f"Pattern not matched: {pattern[:30]}...")
                
        # Try to expand and re-analyze
        if not patterns and language in ['javascript', 'typescript']:
            expanded = self.expand_minified_code(content, language)
            # Could recurse here with regular algorithm detector on expanded code
            logger.debug(f"Expanded minified code from {len(content)} to {len(expanded)} chars")
            
        return patterns