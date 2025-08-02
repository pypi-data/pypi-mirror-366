"""
Comment stripping for various programming languages.
"""

import re
from typing import Dict, Tuple


class CommentStripper:
    """Strip comments from source code while preserving structure."""
    
    def __init__(self):
        # Define comment patterns for different languages
        self.comment_patterns = {
            'python': {
                'single': r'#.*$',
                'multi_start': r'"""',
                'multi_end': r'"""',
                'alt_multi_start': r"'''",
                'alt_multi_end': r"'''"
            },
            'javascript': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/'
            },
            'typescript': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/'
            },
            'java': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/'
            },
            'c': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/'
            },
            'cpp': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/'
            },
            'go': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/'
            },
            'rust': {
                'single': r'//.*$',
                'multi_start': r'/\*',
                'multi_end': r'\*/',
                'doc_single': r'///',
                'doc_multi_start': r'/\*\*',
                'doc_multi_end': r'\*/'
            }
        }
    
    def strip_comments(self, code: str, language: str) -> Tuple[str, Dict[str, int]]:
        """
        Strip comments from code and return statistics.
        
        Returns:
            Tuple of (stripped_code, statistics)
        """
        if language not in self.comment_patterns:
            # Unknown language, return as-is
            return code, {'comments_removed': 0, 'lines_affected': 0}
        
        patterns = self.comment_patterns[language]
        original_lines = code.split('\n')
        lines_affected = set()
        comments_removed = 0
        
        # Handle language-specific stripping
        if language == 'python':
            stripped_code, stats = self._strip_python_comments(code)
        else:
            stripped_code, stats = self._strip_c_style_comments(code, patterns)
        
        return stripped_code, stats
    
    def _remove_python_docstrings(self, code: str) -> str:
        """Remove Python docstrings from code."""
        # Remove triple-quoted strings that are docstrings
        # This is a simplified approach - proper would use AST
        
        # Pattern for triple-quoted strings at the beginning of a line (likely docstrings)
        docstring_pattern = r'^\s*"""[\s\S]*?"""|^\s*\'\'\'[\s\S]*?\'\'\''
        code = re.sub(docstring_pattern, '', code, flags=re.MULTILINE)
        
        return code
    
    def _strip_python_comments(self, code: str) -> Tuple[str, Dict[str, int]]:
        """Strip Python comments while preserving strings."""
        # First, remove docstrings
        code = self._remove_python_docstrings(code)
        
        lines = code.split('\n')
        result_lines = []
        in_string = False
        string_char = None
        comments_removed = 0
        lines_affected = set()
        
        for line_num, line in enumerate(lines):
            result_chars = []
            i = 0
            
            while i < len(line):
                # Check for string literals
                if line[i] in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = line[i]
                    elif string_char == line[i]:
                        in_string = False
                        string_char = None
                    result_chars.append(line[i])
                    i += 1
                    continue
                
                # Check for comments
                if not in_string and line[i] == '#':
                    # Found comment, skip rest of line
                    comments_removed += 1
                    lines_affected.add(line_num)
                    break
                
                result_chars.append(line[i])
                i += 1
            
            result_lines.append(''.join(result_chars))
        
        return '\n'.join(result_lines), {
            'comments_removed': comments_removed,
            'lines_affected': len(lines_affected)
        }
    
    def _strip_c_style_comments(self, code: str, patterns: Dict[str, str]) -> Tuple[str, Dict[str, int]]:
        """Strip C-style comments (// and /* */)."""
        # Remove single-line comments
        single_pattern = patterns.get('single')
        comments_removed = 0
        lines_affected = set()
        
        if single_pattern:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if re.search(single_pattern, line):
                    lines[i] = re.sub(single_pattern, '', line, flags=re.MULTILINE)
                    comments_removed += 1
                    lines_affected.add(i)
            code = '\n'.join(lines)
        
        # Remove multi-line comments
        multi_start = patterns.get('multi_start')
        multi_end = patterns.get('multi_end')
        
        if multi_start and multi_end:
            # Count multi-line comments
            multi_pattern = re.escape(multi_start) + r'.*?' + re.escape(multi_end)
            multi_matches = list(re.finditer(multi_pattern, code, re.DOTALL))
            comments_removed += len(multi_matches)
            
            # Track affected lines
            for match in multi_matches:
                start_line = code[:match.start()].count('\n')
                end_line = code[:match.end()].count('\n')
                for line_num in range(start_line, end_line + 1):
                    lines_affected.add(line_num)
            
            # Remove the comments
            code = re.sub(multi_pattern, '', code, flags=re.DOTALL)
        
        return code, {
            'comments_removed': comments_removed,
            'lines_affected': len(lines_affected)
        }
    
    def strip_and_normalize_whitespace(self, code: str, language: str) -> str:
        """Strip comments and normalize whitespace."""
        stripped_code, _ = self.strip_comments(code, language)
        
        # Normalize whitespace
        # Remove trailing whitespace
        lines = stripped_code.split('\n')
        lines = [line.rstrip() for line in lines]
        
        # Remove multiple blank lines
        result_lines = []
        prev_blank = False
        for line in lines:
            if line.strip() == '':
                if not prev_blank:
                    result_lines.append('')
                prev_blank = True
            else:
                result_lines.append(line)
                prev_blank = False
        
        # Remove leading and trailing blank lines
        while result_lines and result_lines[0] == '':
            result_lines.pop(0)
        while result_lines and result_lines[-1] == '':
            result_lines.pop()
        
        return '\n'.join(result_lines)
    
    def generate_comment_free_hash(self, code: str, language: str, hasher) -> str:
        """Generate hash of comment-free code."""
        stripped_code = self.strip_and_normalize_whitespace(code, language)
        return hasher.tlsh(stripped_code)