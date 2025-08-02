"""
Transformation resistance validation for CopycatM.
Tests how well signatures resist common code transformations.
"""

import os
import re
import random
from typing import Dict, List, Tuple, Any
from ..core.analyzer import CopycatAnalyzer


class TransformationValidator:
    """Validates transformation resistance of algorithm detection."""
    
    def __init__(self, analyzer: CopycatAnalyzer):
        self.analyzer = analyzer
    
    def validate_transformation_resistance(self, original_code: str, language: str) -> Dict[str, float]:
        """
        Test resistance to various code transformations.
        
        Returns:
            Dictionary of transformation types to similarity scores (0-1)
        """
        results = {}
        
        # Get original analysis
        original_result = self.analyzer.analyze_code(original_code, language)
        original_hashes = self._extract_all_hashes(original_result)
        original_algorithms = self._extract_algorithm_signatures(original_result)
        
        # Test each transformation
        transformations = {
            'variable_renaming': self._transform_variable_names,
            'whitespace_changes': self._transform_whitespace,
            'comment_modification': self._transform_comments,
            'function_reordering': self._transform_function_order,
            'code_formatting': self._transform_formatting,
            'constant_changes': self._transform_constants,
            'loop_unrolling': self._transform_loop_unrolling,
            'language_idioms': self._transform_to_language_idioms
        }
        
        for transform_name, transform_func in transformations.items():
            try:
                transformed_code = transform_func(original_code, language)
                transformed_result = self.analyzer.analyze_code(transformed_code, language)
                
                # Calculate similarity
                similarity = self._calculate_similarity(
                    original_result, transformed_result,
                    original_hashes, self._extract_all_hashes(transformed_result),
                    original_algorithms, self._extract_algorithm_signatures(transformed_result)
                )
                
                results[transform_name] = similarity
                
            except Exception:
                results[transform_name] = 0.0  # Transformation failed
        
        return results
    
    def _transform_variable_names(self, code: str, language: str) -> str:
        """Rename all variables to generic names."""
        # Language-specific variable patterns
        if language == 'python':
            # Find all variable names (simplified)
            var_pattern = r'\b([a-z_][a-z0-9_]*)\b(?!\s*\()'
            
            # Get all variables
            variables = set(re.findall(var_pattern, code))
            
            # Filter out keywords
            keywords = {'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'import', 
                       'from', 'return', 'in', 'and', 'or', 'not', 'True', 'False', 'None'}
            variables = variables - keywords
            
            # Create mapping
            var_mapping = {var: f'var_{i}' for i, var in enumerate(sorted(variables))}
            
            # Replace variables
            transformed = code
            for old_var, new_var in var_mapping.items():
                transformed = re.sub(r'\b' + old_var + r'\b', new_var, transformed)
            
            return transformed
            
        elif language in ['c', 'cpp', 'java', 'javascript']:
            # Simplified C-style variable renaming
            var_pattern = r'\b([a-z_][a-zA-Z0-9_]*)\b(?!\s*\()'
            variables = set(re.findall(var_pattern, code))
            
            # Filter out common keywords
            keywords = {'int', 'char', 'void', 'float', 'double', 'if', 'else', 'for',
                       'while', 'return', 'const', 'static', 'public', 'private'}
            variables = variables - keywords
            
            var_mapping = {var: f'v{i}' for i, var in enumerate(sorted(variables))}
            
            transformed = code
            for old_var, new_var in var_mapping.items():
                transformed = re.sub(r'\b' + old_var + r'\b', new_var, transformed)
            
            return transformed
        
        return code
    
    def _transform_whitespace(self, code: str, language: str) -> str:
        """Modify whitespace while preserving syntax."""
        # Remove extra spaces
        transformed = re.sub(r' +', ' ', code)
        
        # Remove blank lines
        lines = [line for line in transformed.split('\n') if line.strip()]
        transformed = '\n'.join(lines)
        
        # Add random indentation (language-aware)
        if language == 'python':
            # Python requires proper indentation
            return transformed
        else:
            # C-style languages are flexible with whitespace
            lines = transformed.split('\n')
            transformed_lines = []
            for line in lines:
                if line.strip():
                    indent = ' ' * random.randint(0, 4)
                    transformed_lines.append(indent + line.strip())
            return '\n'.join(transformed_lines)
    
    def _transform_comments(self, code: str, language: str) -> str:
        """Remove or modify comments."""
        if language == 'python':
            # Remove Python comments
            transformed = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            # Remove docstrings
            transformed = re.sub(r'"""[\s\S]*?"""', '', transformed)
            transformed = re.sub(r"'''[\s\S]*?'''", '', transformed)
        else:
            # Remove C-style comments
            transformed = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
            transformed = re.sub(r'/\*[\s\S]*?\*/', '', transformed)
        
        return transformed
    
    def _transform_function_order(self, code: str, language: str) -> str:
        """Reorder functions in the file."""
        if language == 'python':
            # Extract functions
            func_pattern = r'(^def\s+\w+.*?(?=^def|\Z))'
            functions = re.findall(func_pattern, code, re.MULTILINE | re.DOTALL)
            
            if len(functions) > 1:
                # Shuffle functions
                import random
                random.shuffle(functions)
                
                # Find imports and class definitions
                import_section = re.findall(r'^(import.*?$|from.*?$)', code, re.MULTILINE)
                
                # Reconstruct code
                transformed = '\n'.join(import_section) + '\n\n' + '\n\n'.join(functions)
                return transformed
        
        return code
    
    def _transform_formatting(self, code: str, language: str) -> str:
        """Change code formatting style."""
        # Change bracket style for C-like languages
        if language in ['c', 'cpp', 'java', 'javascript']:
            # Convert K&R to Allman style
            transformed = re.sub(r'\s*{', '\n{', code)
            # Add spaces around operators
            transformed = re.sub(r'([+\-*/=<>!]+)', r' \1 ', transformed)
            # Remove duplicate spaces
            transformed = re.sub(r' +', ' ', transformed)
            return transformed
        
        return code
    
    def _transform_constants(self, code: str, language: str) -> str:
        """Change constant values slightly."""
        # Change numeric constants
        def replace_number(match):
            num = float(match.group())
            if num.is_integer() and num > 1:
                # Change by ±1
                return str(int(num) + random.choice([-1, 1]))
            return match.group()
        
        transformed = re.sub(r'\b\d+\b', replace_number, code)
        return transformed
    
    def _transform_loop_unrolling(self, code: str, language: str) -> str:
        """Simulate simple loop unrolling."""
        # This is a complex transformation - simplified version
        # In practice, this would require full AST transformation
        return code
    
    def _transform_to_language_idioms(self, code: str, language: str) -> str:
        """Transform to language-specific idioms."""
        if language == 'python':
            # Convert simple loops to list comprehensions (simplified)
            # for i in range(n): arr.append(i) -> arr = [i for i in range(n)]
            pass
        
        return code
    
    def _extract_all_hashes(self, result: Dict[str, Any]) -> Dict[str, str]:
        """Extract all hashes from analysis result."""
        hashes = {}
        
        # Direct hashes
        if 'hashes' in result:
            for hash_type in ['direct', 'fuzzy', 'semantic']:
                if hash_type in result['hashes']:
                    for name, value in result['hashes'][hash_type].items():
                        if isinstance(value, str):
                            hashes[f"{hash_type}_{name}"] = value
        
        # Algorithm hashes
        for algo in result.get('algorithms', []):
            if 'hashes' in algo:
                algo_name = algo.get('function_info', {}).get('name', 'unknown')
                for hash_type in ['direct', 'fuzzy', 'semantic']:
                    if hash_type in algo['hashes']:
                        if isinstance(algo['hashes'][hash_type], str):
                            hashes[f"algo_{algo_name}_{hash_type}"] = algo['hashes'][hash_type]
                        elif isinstance(algo['hashes'][hash_type], dict):
                            for name, value in algo['hashes'][hash_type].items():
                                if isinstance(value, str):
                                    hashes[f"algo_{algo_name}_{hash_type}_{name}"] = value
        
        return hashes
    
    def _extract_algorithm_signatures(self, result: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Extract algorithm type and subtype pairs."""
        signatures = []
        
        for algo in result.get('algorithms', []):
            algo_type = algo.get('algorithm_type', 'unknown')
            algo_subtype = algo.get('algorithm_subtype', 'unknown')
            signatures.append((algo_type, algo_subtype))
        
        return signatures
    
    def _calculate_similarity(self, original_result: Dict, transformed_result: Dict,
                            original_hashes: Dict, transformed_hashes: Dict,
                            original_algos: List, transformed_algos: List) -> float:
        """Calculate overall similarity score."""
        scores = []
        
        # 1. Algorithm detection similarity
        if original_algos and transformed_algos:
            # Check if same algorithms detected
            algo_matches = sum(1 for algo in original_algos if algo in transformed_algos)
            algo_score = algo_matches / max(len(original_algos), len(transformed_algos))
            scores.append(algo_score)
        
        # 2. Hash similarity
        hash_scores = []
        
        # Semantic hashes (should be most resistant)
        semantic_hashes_orig = {k: v for k, v in original_hashes.items() if 'semantic' in k}
        semantic_hashes_trans = {k: v for k, v in transformed_hashes.items() if 'semantic' in k}
        
        if semantic_hashes_orig and semantic_hashes_trans:
            semantic_matches = sum(1 for k, v in semantic_hashes_orig.items() 
                                 if k in semantic_hashes_trans and v == semantic_hashes_trans[k])
            semantic_score = semantic_matches / len(semantic_hashes_orig)
            hash_scores.append(semantic_score * 1.5)  # Weight semantic hashes higher
        
        # Fuzzy hashes
        fuzzy_hashes_orig = {k: v for k, v in original_hashes.items() if 'fuzzy' in k}
        fuzzy_hashes_trans = {k: v for k, v in transformed_hashes.items() if 'fuzzy' in k}
        
        if fuzzy_hashes_orig and fuzzy_hashes_trans:
            # TLSH allows similarity calculation
            fuzzy_score = self._calculate_tlsh_similarity(fuzzy_hashes_orig, fuzzy_hashes_trans)
            hash_scores.append(fuzzy_score)
        
        # Direct hashes (should change with any modification)
        direct_hashes_orig = {k: v for k, v in original_hashes.items() if 'direct' in k}
        direct_hashes_trans = {k: v for k, v in transformed_hashes.items() if 'direct' in k}
        
        if direct_hashes_orig and direct_hashes_trans:
            direct_matches = sum(1 for k, v in direct_hashes_orig.items() 
                               if k in direct_hashes_trans and v == direct_hashes_trans[k])
            direct_score = direct_matches / len(direct_hashes_orig)
            hash_scores.append(direct_score * 0.5)  # Weight direct hashes lower
        
        if hash_scores:
            scores.append(sum(hash_scores) / len(hash_scores))
        
        # 3. Invariant preservation
        orig_invariants = len(original_result.get('mathematical_invariants', []))
        trans_invariants = len(transformed_result.get('mathematical_invariants', []))
        
        if orig_invariants > 0:
            invariant_score = min(trans_invariants / orig_invariants, 1.0)
            scores.append(invariant_score)
        
        # Calculate final score
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_tlsh_similarity(self, orig_hashes: Dict, trans_hashes: Dict) -> float:
        """Calculate TLSH similarity score."""
        # Simplified - in practice would use TLSH library
        # For now, check if hashes are somewhat similar
        similarities = []
        
        for key in orig_hashes:
            if key in trans_hashes:
                orig = orig_hashes[key]
                trans = trans_hashes[key]
                
                if orig.startswith('TLSH:') and trans.startswith('TLSH:'):
                    # Compare TLSH hashes (simplified)
                    # Real implementation would use tlsh.diff()
                    if orig == trans:
                        similarities.append(1.0)
                    else:
                        # Estimate based on common prefix
                        common_len = len(os.path.commonprefix([orig, trans]))
                        similarities.append(common_len / len(orig))
        
        return sum(similarities) / len(similarities) if similarities else 0.0


def validate_transformation_resistance(code_samples: List[Tuple[str, str]]) -> Dict[str, Dict[str, float]]:
    """
    Validate transformation resistance for multiple code samples.
    
    Args:
        code_samples: List of (code, language) tuples
        
    Returns:
        Dictionary mapping sample names to transformation scores
    """
    from ..core.config_improvements import create_improved_analyzer
    
    analyzer = create_improved_analyzer(CopycatAnalyzer())
    validator = TransformationValidator(analyzer)
    
    results = {}
    
    for i, (code, language) in enumerate(code_samples):
        sample_name = f"sample_{i}_{language}"
        scores = validator.validate_transformation_resistance(code, language)
        results[sample_name] = scores
        
        # Calculate average resistance
        avg_resistance = sum(scores.values()) / len(scores) if scores else 0.0
        results[sample_name]['average_resistance'] = avg_resistance
    
    return results