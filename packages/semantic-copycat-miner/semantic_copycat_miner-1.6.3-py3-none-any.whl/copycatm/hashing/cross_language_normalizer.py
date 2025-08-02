"""
Cross-language code normalizer for improved similarity detection.
Converts code from different languages to a common representation.
"""

import re


class CrossLanguageNormalizer:
    """Normalizes code across languages for better similarity comparison."""
    
    def __init__(self):
        # Common control flow normalizations
        self.control_flow_patterns = {
            'python': {
                r'for\s+(\w+)\s+in\s+range\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)': 'FOR \\1 FROM \\2 TO \\3',
                r'for\s+(\w+)\s+in\s+range\s*\(\s*(\w+)\s*\)': 'FOR \\1 FROM 0 TO \\2',
                r'if\s+(.+?):': 'IF \\1 THEN',
                r'elif\s+(.+?):': 'ELSEIF \\1 THEN',
                r'else\s*:': 'ELSE',
                r'while\s+(.+?):': 'WHILE \\1 DO',
                r'def\s+(\w+)\s*\((.+?)\)\s*:': 'FUNCTION \\1(\\2)',
                r'return\s+': 'RETURN ',
            },
            'javascript': {
                r'for\s*\(\s*let\s+(\w+)\s*=\s*(\w+)\s*;\s*\1\s*<\s*(\w+)\s*;\s*\1\+\+\s*\)': 'FOR \\1 FROM \\2 TO \\3',
                r'for\s*\(\s*var\s+(\w+)\s*=\s*(\w+)\s*;\s*\1\s*<\s*(\w+)\s*;\s*\1\+\+\s*\)': 'FOR \\1 FROM \\2 TO \\3',
                r'if\s*\((.+?)\)\s*\{': 'IF \\1 THEN',
                r'else\s+if\s*\((.+?)\)\s*\{': 'ELSEIF \\1 THEN',
                r'else\s*\{': 'ELSE',
                r'while\s*\((.+?)\)\s*\{': 'WHILE \\1 DO',
                r'function\s+(\w+)\s*\((.+?)\)\s*\{': 'FUNCTION \\1(\\2)',
                r'const\s+(\w+)\s*=\s*function\s*\((.+?)\)\s*\{': 'FUNCTION \\1(\\2)',
                r'return\s+': 'RETURN ',
            },
            'c': {
                r'for\s*\(\s*int\s+(\w+)\s*=\s*(\w+)\s*;\s*\1\s*<\s*(\w+)\s*;\s*\1\+\+\s*\)': 'FOR \\1 FROM \\2 TO \\3',
                r'if\s*\((.+?)\)\s*\{': 'IF \\1 THEN',
                r'else\s+if\s*\((.+?)\)\s*\{': 'ELSEIF \\1 THEN',
                r'else\s*\{': 'ELSE',
                r'while\s*\((.+?)\)\s*\{': 'WHILE \\1 DO',
                r'(void|int|float|double)\s+(\w+)\s*\((.+?)\)\s*\{': 'FUNCTION \\2(\\3)',
                r'return\s+': 'RETURN ',
            }
        }
        
        # Operator normalizations (applied to all languages)
        self.operator_normalizations = [
            # Increment/decrement
            (r'\+\+', '+=1'),
            (r'--', '-=1'),
            # Comparison operators
            (r'===', '=='),
            (r'!==', '!='),
            # Assignment operators
            (r'\+=', ' = $ + '),
            (r'-=', ' = $ - '),
            (r'\*=', ' = $ * '),
            (r'/=', ' = $ / '),
            # Logical operators
            (r'&&', ' AND '),
            (r'\|\|', ' OR '),
            (r'!', ' NOT '),
        ]
        
        # Type declaration removals
        self.type_removals = [
            # C/Java types
            r'\b(int|float|double|char|void|long|short|unsigned|signed)\s+',
            # JavaScript
            r'\b(let|const|var)\s+',
            # Python (in function signatures)
            r':\s*(int|float|str|bool|List|Dict|Set|Tuple|Any)',
        ]
    
    def normalize(self, code: str, language: str) -> str:
        """
        Normalize code to a common representation.
        
        Args:
            code: Source code to normalize
            language: Source language (python, javascript, c, etc.)
            
        Returns:
            Normalized code string
        """
        # Step 1: Remove comments
        code = self._remove_comments(code, language)
        
        # Step 2: Normalize whitespace
        code = self._normalize_whitespace(code)
        
        # Step 3: Apply language-specific control flow normalizations
        if language in self.control_flow_patterns:
            for pattern, replacement in self.control_flow_patterns[language].items():
                code = re.sub(pattern, replacement, code, flags=re.MULTILINE)
        
        # Step 4: Normalize operators
        for pattern, replacement in self.operator_normalizations:
            code = re.sub(pattern, replacement, code)
        
        # Step 5: Remove type declarations
        for pattern in self.type_removals:
            code = re.sub(pattern, '', code)
        
        # Step 6: Normalize array/list access
        code = self._normalize_array_access(code, language)
        
        # Step 7: Abstract variable names
        code = self._abstract_variable_names(code)
        
        # Step 8: Normalize function calls
        code = self._normalize_function_calls(code)
        
        # Step 9: Final cleanup
        code = ' '.join(code.split())
        
        return code
    
    def _remove_comments(self, code: str, language: str) -> str:
        """Remove comments based on language."""
        if language == 'python':
            # Remove Python comments
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            # Remove docstrings
            code = re.sub(r'"""[\s\S]*?"""', '', code)
            code = re.sub(r"'''[\s\S]*?'''", '', code)
        elif language in ['c', 'cpp', 'java', 'javascript']:
            # Remove single-line comments
            code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            # Remove multi-line comments
            code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        
        return code
    
    def _normalize_whitespace(self, code: str) -> str:
        """Normalize whitespace while preserving structure."""
        # Replace multiple spaces with single space
        code = re.sub(r' +', ' ', code)
        # Remove trailing whitespace
        code = re.sub(r' +$', '', code, flags=re.MULTILINE)
        # Normalize newlines
        code = re.sub(r'\n+', '\n', code)
        return code
    
    def _normalize_array_access(self, code: str, language: str) -> str:
        """Normalize array/list access patterns."""
        # Convert all array access to common format
        code = re.sub(r'\[([^\]]+)\]', '[\\1]', code)
        return code
    
    def _abstract_variable_names(self, code: str) -> str:
        """Replace variable names with abstract tokens."""
        # Find all variable names (simplified)
        var_pattern = r'\b([a-z_][a-zA-Z0-9_]*)\b'
        
        # Skip keywords
        keywords = {
            'IF', 'THEN', 'ELSE', 'ELSEIF', 'FOR', 'FROM', 'TO', 'WHILE', 'DO',
            'FUNCTION', 'RETURN', 'AND', 'OR', 'NOT', 'true', 'false', 'null'
        }
        
        # Extract variables
        variables = re.findall(var_pattern, code)
        unique_vars = []
        for var in variables:
            if var not in keywords and var not in unique_vars:
                unique_vars.append(var)
        
        # Replace with generic names
        for i, var in enumerate(unique_vars):
            code = re.sub(r'\b' + var + r'\b', f'VAR{i}', code)
        
        return code
    
    def _normalize_function_calls(self, code: str) -> str:
        """Normalize function call patterns."""
        # Already partially handled by variable abstraction
        # Additional normalization can be added here
        return code


def demonstrate_normalizer():
    """Demonstrate the cross-language normalizer."""
    normalizer = CrossLanguageNormalizer()
    
    # Test with quicksort implementations
    quicksort_examples = {
        'python': '''
def quicksort(arr, low, high):
    # QuickSort implementation
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)
''',
        'javascript': '''
function quickSort(arr, low, high) {
    // QuickSort implementation
    if (low < high) {
        const pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}
''',
        'c': '''
void quicksort(int arr[], int low, int high) {
    // QuickSort implementation
    if (low < high) {
        int pi = partition(arr, low, high);
        quicksort(arr, low, pi - 1);
        quicksort(arr, pi + 1, high);
    }
}
'''
    }
    
    print("Cross-Language Normalization Demo")
    print("=" * 60)
    
    normalized_versions = {}
    
    for language, code in quicksort_examples.items():
        normalized = normalizer.normalize(code, language)
        normalized_versions[language] = normalized
        
        print(f"\n{language.upper()} normalized:")
        print("-" * 40)
        print(normalized)
    
    # Compare normalized versions
    print("\n" + "=" * 60)
    print("SIMILARITY COMPARISON")
    print("=" * 60)
    
    # Simple similarity check
    for lang1 in normalized_versions:
        for lang2 in normalized_versions:
            if lang1 < lang2:  # Avoid duplicates
                norm1 = normalized_versions[lang1]
                norm2 = normalized_versions[lang2]
                
                # Calculate simple similarity
                words1 = set(norm1.split())
                words2 = set(norm2.split())
                
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                
                similarity = intersection / union if union > 0 else 0
                
                print(f"{lang1} vs {lang2}: {similarity*100:.1f}% word similarity")


if __name__ == "__main__":
    demonstrate_normalizer()