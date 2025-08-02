"""
Advanced code clone detection supporting Type 1-4 clones.
"""

import ast
import re
import hashlib
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import difflib
from dataclasses import dataclass
try:
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from .ast_normalizer import ASTNormalizer
from .semantic_similarity import SemanticSimilarityDetector
from .call_graph import CallGraphAnalyzer


@dataclass
class CodeClone:
    """Represents a detected code clone."""
    clone_type: int  # 1-4
    source_file: str
    source_lines: Tuple[int, int]
    target_file: str
    target_lines: Tuple[int, int]
    similarity_score: float
    confidence: float
    evidence: Dict[str, Any]


class CodeCloneDetector:
    """
    Detect various types of code clones:
    - Type 1: Exact clones (identical except whitespace/comments)
    - Type 2: Renamed clones (identical except variable/function names)
    - Type 3: Modified clones (statements added/removed/modified)
    - Type 4: Semantic clones (functionally equivalent, different syntax)
    """
    
    def __init__(self):
        self.ast_normalizer = ASTNormalizer()
        self.semantic_detector = SemanticSimilarityDetector()
        self.call_graph_analyzer = CallGraphAnalyzer()
        
        # Clone detection thresholds
        self.thresholds = {
            'type1': 0.95,  # Near exact match
            'type2': 0.85,  # High similarity after normalization
            'type3': 0.70,  # Moderate similarity with modifications
            'type4': 0.60   # Semantic similarity
        }
    
    def detect_clones(self, source_code: str, target_code: str,
                     source_file: str = "source", target_file: str = "target",
                     source_language: str = "python", target_language: str = "python") -> List[CodeClone]:
        """Detect all types of clones between source and target code."""
        clones = []
        
        # Parse code into functions/blocks
        source_blocks = self._extract_code_blocks(source_code, source_language)
        target_blocks = self._extract_code_blocks(target_code, target_language)
        
        # Compare each source block with each target block
        for source_block in source_blocks:
            for target_block in target_blocks:
                detected_clones = self._compare_blocks(
                    source_block, target_block,
                    source_file, target_file,
                    source_language, target_language
                )
                clones.extend(detected_clones)
        
        # Merge overlapping clones and sort by confidence
        clones = self._merge_overlapping_clones(clones)
        clones.sort(key=lambda x: (x.confidence, x.similarity_score), reverse=True)
        
        return clones
    
    def _extract_code_blocks(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract code blocks (functions, classes, methods) from code."""
        blocks = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                blocks.extend(self._extract_python_blocks(tree, code))
            except:
                # Fallback to line-based extraction
                blocks.extend(self._extract_blocks_by_pattern(code, language))
        else:
            blocks.extend(self._extract_blocks_by_pattern(code, language))
        
        return blocks
    
    def _extract_python_blocks(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Extract blocks from Python AST."""
        blocks = []
        lines = code.split('\n')
        
        class BlockExtractor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                
                block_code = '\n'.join(lines[start_line:end_line])
                blocks.append({
                    'type': 'function',
                    'name': node.name,
                    'code': block_code,
                    'lines': (start_line + 1, end_line),
                    'ast': node
                })
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                
                block_code = '\n'.join(lines[start_line:end_line])
                blocks.append({
                    'type': 'class',
                    'name': node.name,
                    'code': block_code,
                    'lines': (start_line + 1, end_line),
                    'ast': node
                })
                
                # Don't visit methods inside classes (they're already included)
        
        BlockExtractor().visit(tree)
        
        # Also add the entire module as a block for file-level comparison
        blocks.append({
            'type': 'module',
            'name': 'module',
            'code': code,
            'lines': (1, len(lines)),
            'ast': tree
        })
        
        return blocks
    
    def _extract_blocks_by_pattern(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract blocks using regex patterns."""
        blocks = []
        lines = code.split('\n')
        
        # Language-specific patterns
        if language in ["javascript", "typescript"]:
            patterns = [
                (r'function\s+(\w+)\s*\([^)]*\)\s*{', 'function'),
                (r'const\s+(\w+)\s*=.*?function\s*\([^)]*\)\s*{', 'function'),
                (r'class\s+(\w+)\s*{', 'class'),
            ]
        elif language in ["java", "c", "cpp"]:
            patterns = [
                (r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*{', 'function'),
                (r'class\s+(\w+)\s*{', 'class'),
            ]
        else:
            patterns = [
                (r'def\s+(\w+)\s*\([^)]*\):', 'function'),
                (r'class\s+(\w+).*:', 'class'),
            ]
        
        for pattern, block_type in patterns:
            for match in re.finditer(pattern, code, re.MULTILINE):
                start_pos = match.start()
                start_line = code[:start_pos].count('\n') + 1
                
                # Find end of block
                end_line = self._find_block_end(lines, start_line - 1, language)
                
                block_code = '\n'.join(lines[start_line - 1:end_line])
                blocks.append({
                    'type': block_type,
                    'name': match.group(1),
                    'code': block_code,
                    'lines': (start_line, end_line),
                    'ast': None
                })
        
        # Add entire file as a block
        blocks.append({
            'type': 'module',
            'name': 'module',
            'code': code,
            'lines': (1, len(lines)),
            'ast': None
        })
        
        return blocks
    
    def _find_block_end(self, lines: List[str], start_idx: int, language: str) -> int:
        """Find the end of a code block."""
        if language == "python":
            # Find by indentation
            if start_idx >= len(lines):
                return len(lines)
            
            base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
            
            for i in range(start_idx + 1, len(lines)):
                line = lines[i]
                if line.strip():  # Non-empty line
                    indent = len(line) - len(line.lstrip())
                    if indent <= base_indent:
                        return i
            
            return len(lines)
        else:
            # Find by brace matching
            brace_count = 0
            in_string = False
            escape = False
            
            for i in range(start_idx, len(lines)):
                line = lines[i]
                for char in line:
                    if escape:
                        escape = False
                        continue
                    
                    if char == '\\':
                        escape = True
                    elif char in ['"', "'"]:
                        in_string = not in_string
                    elif not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                return i + 1
            
            return len(lines)
    
    def _compare_blocks(self, source_block: Dict, target_block: Dict,
                       source_file: str, target_file: str,
                       source_language: str, target_language: str) -> List[CodeClone]:
        """Compare two code blocks for various types of clones."""
        clones = []
        
        # Skip if blocks are too different in size (optimization)
        size_ratio = min(len(source_block['code']), len(target_block['code'])) / max(len(source_block['code']), len(target_block['code']), 1)
        if size_ratio < 0.5:
            return clones
        
        # Type 1: Exact clones
        type1_result = self._detect_type1_clone(source_block, target_block)
        if type1_result['is_clone']:
            clones.append(CodeClone(
                clone_type=1,
                source_file=source_file,
                source_lines=source_block['lines'],
                target_file=target_file,
                target_lines=target_block['lines'],
                similarity_score=type1_result['similarity'],
                confidence=type1_result['confidence'],
                evidence=type1_result['evidence']
            ))
            return clones  # No need to check other types if Type 1 found
        
        # Type 2: Renamed clones
        type2_result = self._detect_type2_clone(source_block, target_block, source_language, target_language)
        if type2_result['is_clone']:
            clones.append(CodeClone(
                clone_type=2,
                source_file=source_file,
                source_lines=source_block['lines'],
                target_file=target_file,
                target_lines=target_block['lines'],
                similarity_score=type2_result['similarity'],
                confidence=type2_result['confidence'],
                evidence=type2_result['evidence']
            ))
        
        # Type 3: Modified clones
        type3_result = self._detect_type3_clone(source_block, target_block, source_language, target_language)
        if type3_result['is_clone']:
            clones.append(CodeClone(
                clone_type=3,
                source_file=source_file,
                source_lines=source_block['lines'],
                target_file=target_file,
                target_lines=target_block['lines'],
                similarity_score=type3_result['similarity'],
                confidence=type3_result['confidence'],
                evidence=type3_result['evidence']
            ))
        
        # Type 4: Semantic clones
        type4_result = self._detect_type4_clone(source_block, target_block, source_language, target_language)
        if type4_result['is_clone']:
            clones.append(CodeClone(
                clone_type=4,
                source_file=source_file,
                source_lines=source_block['lines'],
                target_file=target_file,
                target_lines=target_block['lines'],
                similarity_score=type4_result['similarity'],
                confidence=type4_result['confidence'],
                evidence=type4_result['evidence']
            ))
        
        return clones
    
    def _detect_type1_clone(self, source_block: Dict, target_block: Dict) -> Dict[str, Any]:
        """Detect Type 1 (exact) clones."""
        # Normalize whitespace and comments
        source_normalized = self._normalize_whitespace(source_block['code'])
        target_normalized = self._normalize_whitespace(target_block['code'])
        
        # Calculate similarity
        similarity = self._text_similarity(source_normalized, target_normalized)
        
        is_clone = similarity >= self.thresholds['type1']
        
        return {
            'is_clone': is_clone,
            'similarity': similarity,
            'confidence': similarity if is_clone else 0,
            'evidence': {
                'normalized_match': source_normalized == target_normalized,
                'length_ratio': len(source_normalized) / max(len(target_normalized), 1),
                'hash_match': hashlib.md5(source_normalized.encode()).hexdigest() == 
                             hashlib.md5(target_normalized.encode()).hexdigest()
            }
        }
    
    def _normalize_whitespace(self, code: str) -> str:
        """Normalize whitespace and remove comments."""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)  # Python
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)  # C-style
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Multi-line
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'\s*([{}()\[\];,])\s*', r'\1', code)
        
        return code.strip()
    
    def _detect_type2_clone(self, source_block: Dict, target_block: Dict,
                           source_language: str, target_language: str) -> Dict[str, Any]:
        """Detect Type 2 (renamed) clones."""
        # Normalize identifiers
        source_normalized = self._normalize_identifiers(source_block['code'], source_language)
        target_normalized = self._normalize_identifiers(target_block['code'], target_language)
        
        # Also normalize whitespace
        source_normalized = self._normalize_whitespace(source_normalized)
        target_normalized = self._normalize_whitespace(target_normalized)
        
        # Calculate similarity
        similarity = self._text_similarity(source_normalized, target_normalized)
        
        # Check structural similarity if AST available
        structural_similarity = 0
        if source_block.get('ast') and target_block.get('ast'):
            ast_similarity = self.ast_normalizer.structural_similarity(
                source_block['ast'], target_block['ast'],
                source_language, target_language
            )
            structural_similarity = ast_similarity['structure_similarity']
        
        # Combined similarity
        combined_similarity = 0.7 * similarity + 0.3 * structural_similarity
        
        is_clone = combined_similarity >= self.thresholds['type2']
        
        return {
            'is_clone': is_clone,
            'similarity': combined_similarity,
            'confidence': combined_similarity if is_clone else 0,
            'evidence': {
                'text_similarity': similarity,
                'structural_similarity': structural_similarity,
                'identifier_patterns_match': self._check_identifier_patterns(
                    source_block['code'], target_block['code']
                )
            }
        }
    
    def _normalize_identifiers(self, code: str, language: str) -> str:
        """Normalize all identifiers to generic names."""
        # First, collect all identifiers
        if language == "python":
            identifier_pattern = r'\b(?!(?:def|class|if|else|elif|for|while|import|from|return|yield|break|continue|pass|try|except|finally|with|as|lambda|and|or|not|in|is|None|True|False)\b)[a-zA-Z_]\w*\b'
        else:
            identifier_pattern = r'\b(?!(?:function|const|let|var|if|else|for|while|do|switch|case|return|break|continue|class|public|private|protected|static|void|int|float|double|string|boolean)\b)[a-zA-Z_]\w*\b'
        
        identifiers = list(set(re.findall(identifier_pattern, code)))
        
        # Sort by length (longest first) to avoid partial replacements
        identifiers.sort(key=len, reverse=True)
        
        # Replace with generic names
        normalized = code
        for i, identifier in enumerate(identifiers):
            normalized = re.sub(rf'\b{re.escape(identifier)}\b', f'ID{i}', normalized)
        
        return normalized
    
    def _check_identifier_patterns(self, code1: str, code2: str) -> bool:
        """Check if identifier usage patterns are similar."""
        # Extract identifier usage patterns
        pattern1 = re.findall(r'(\w+)\s*=\s*(\w+)', code1)
        pattern2 = re.findall(r'(\w+)\s*=\s*(\w+)', code2)
        
        # Check if pattern counts are similar
        return abs(len(pattern1) - len(pattern2)) <= 2
    
    def _detect_type3_clone(self, source_block: Dict, target_block: Dict,
                           source_language: str, target_language: str) -> Dict[str, Any]:
        """Detect Type 3 (modified) clones."""
        # Use diff-based analysis
        source_lines = source_block['code'].split('\n')
        target_lines = target_block['code'].split('\n')
        
        # Calculate line-level similarity
        matcher = difflib.SequenceMatcher(None, source_lines, target_lines)
        line_similarity = matcher.ratio()
        
        # Token-based similarity
        source_tokens = self._tokenize_code(source_block['code'])
        target_tokens = self._tokenize_code(target_block['code'])
        
        token_matcher = difflib.SequenceMatcher(None, source_tokens, target_tokens)
        token_similarity = token_matcher.ratio()
        
        # Statement-level analysis
        statement_similarity = self._statement_similarity(
            source_block['code'], target_block['code'], 
            source_language, target_language
        )
        
        # Combined similarity
        combined_similarity = (
            0.3 * line_similarity +
            0.4 * token_similarity +
            0.3 * statement_similarity
        )
        
        is_clone = combined_similarity >= self.thresholds['type3']
        
        # Extract modifications
        modifications = self._extract_modifications(matcher)
        
        return {
            'is_clone': is_clone,
            'similarity': combined_similarity,
            'confidence': combined_similarity * 0.9 if is_clone else 0,  # Slightly lower confidence
            'evidence': {
                'line_similarity': line_similarity,
                'token_similarity': token_similarity,
                'statement_similarity': statement_similarity,
                'modifications': modifications,
                'modification_ratio': len(modifications) / max(len(source_lines), len(target_lines), 1)
            }
        }
    
    def _tokenize_code(self, code: str) -> List[str]:
        """Tokenize code into meaningful tokens."""
        # Remove comments and strings
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'["\'].*?["\']', 'STRING', code)
        
        # Extract tokens
        tokens = re.findall(r'\b\w+\b|[{}()\[\];,=<>!+\-*/]', code)
        
        return tokens
    
    def _statement_similarity(self, code1: str, code2: str, lang1: str, lang2: str) -> float:
        """Calculate statement-level similarity."""
        # Extract statements
        statements1 = self._extract_statements(code1, lang1)
        statements2 = self._extract_statements(code2, lang2)
        
        if not statements1 or not statements2:
            return 0.0
        
        # Compare statement types
        stmt_types1 = [s['type'] for s in statements1]
        stmt_types2 = [s['type'] for s in statements2]
        
        # Sequence matching
        matcher = difflib.SequenceMatcher(None, stmt_types1, stmt_types2)
        
        return matcher.ratio()
    
    def _extract_statements(self, code: str, language: str) -> List[Dict[str, str]]:
        """Extract statements from code."""
        statements = []
        
        # Simple pattern-based extraction
        patterns = {
            'assignment': r'^\s*\w+\s*=(?!=)',
            'call': r'^\s*\w+\s*\(',
            'return': r'^\s*return\b',
            'if': r'^\s*if\b',
            'for': r'^\s*for\b',
            'while': r'^\s*while\b',
            'import': r'^\s*(import|from)\b',
        }
        
        for line in code.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            for stmt_type, pattern in patterns.items():
                if re.match(pattern, line):
                    statements.append({
                        'type': stmt_type,
                        'content': line
                    })
                    break
            else:
                # Default to 'other'
                statements.append({
                    'type': 'other',
                    'content': line
                })
        
        return statements
    
    def _extract_modifications(self, matcher: difflib.SequenceMatcher) -> List[Dict[str, Any]]:
        """Extract modification operations from diff."""
        modifications = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                modifications.append({
                    'type': 'replace',
                    'source_lines': (i1 + 1, i2),
                    'target_lines': (j1 + 1, j2)
                })
            elif tag == 'delete':
                modifications.append({
                    'type': 'delete',
                    'source_lines': (i1 + 1, i2)
                })
            elif tag == 'insert':
                modifications.append({
                    'type': 'insert',
                    'target_lines': (j1 + 1, j2)
                })
        
        return modifications
    
    def _detect_type4_clone(self, source_block: Dict, target_block: Dict,
                           source_language: str, target_language: str) -> Dict[str, Any]:
        """Detect Type 4 (semantic) clones."""
        # Use semantic similarity detection
        semantic_result = self.semantic_detector.calculate_semantic_similarity(
            source_block['code'], target_block['code'],
            source_language, target_language,
            source_block.get('ast'), target_block.get('ast')
        )
        
        # Analyze call graphs
        call_graph_similarity = 0
        try:
            source_cg = self.call_graph_analyzer.analyze_code(
                source_block['code'], source_language, source_block.get('ast')
            )
            target_cg = self.call_graph_analyzer.analyze_code(
                target_block['code'], target_language, target_block.get('ast')
            )
            
            if source_cg['call_graph']['node_count'] > 0 and target_cg['call_graph']['node_count'] > 0:
                cg_comparison = self.call_graph_analyzer.compare_call_graphs(
                    source_cg['call_graph'], target_cg['call_graph']
                )
                call_graph_similarity = cg_comparison['similarity']
        except:
            pass
        
        # Combined semantic similarity
        combined_similarity = (
            0.7 * semantic_result['overall_similarity'] +
            0.3 * call_graph_similarity
        )
        
        is_clone = combined_similarity >= self.thresholds['type4']
        
        return {
            'is_clone': is_clone,
            'similarity': combined_similarity,
            'confidence': semantic_result['confidence'] if is_clone else 0,
            'evidence': {
                'semantic_similarity': semantic_result['overall_similarity'],
                'semantic_metrics': semantic_result['metrics'],
                'semantic_features': semantic_result['semantic_features'],
                'call_graph_similarity': call_graph_similarity
            }
        }
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using sequence matching."""
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def _merge_overlapping_clones(self, clones: List[CodeClone]) -> List[CodeClone]:
        """Merge overlapping clone detections."""
        if not clones:
            return clones
        
        # Group by source and target files
        grouped = defaultdict(list)
        for clone in clones:
            key = (clone.source_file, clone.target_file)
            grouped[key].append(clone)
        
        merged = []
        for key, group in grouped.items():
            # Sort by line numbers
            group.sort(key=lambda c: (c.source_lines[0], c.target_lines[0]))
            
            # Merge overlapping
            current = group[0]
            for clone in group[1:]:
                # Check for overlap
                if (current.source_lines[1] >= clone.source_lines[0] and
                    current.target_lines[1] >= clone.target_lines[0]):
                    # Merge: keep higher type and extend range
                    current = CodeClone(
                        clone_type=min(current.clone_type, clone.clone_type),  # Lower number = higher type
                        source_file=current.source_file,
                        source_lines=(current.source_lines[0], max(current.source_lines[1], clone.source_lines[1])),
                        target_file=current.target_file,
                        target_lines=(current.target_lines[0], max(current.target_lines[1], clone.target_lines[1])),
                        similarity_score=max(current.similarity_score, clone.similarity_score),
                        confidence=max(current.confidence, clone.confidence),
                        evidence={**current.evidence, **clone.evidence}
                    )
                else:
                    merged.append(current)
                    current = clone
            
            merged.append(current)
        
        return merged
    
    def generate_clone_report(self, clones: List[CodeClone]) -> Dict[str, Any]:
        """Generate a summary report of detected clones."""
        if not clones:
            return {
                'total_clones': 0,
                'by_type': {},
                'summary': 'No clones detected'
            }
        
        # Count by type
        by_type = defaultdict(int)
        for clone in clones:
            by_type[f'type{clone.clone_type}'] = by_type.get(f'type{clone.clone_type}', 0) + 1
        
        # Calculate coverage
        total_lines = sum(c.source_lines[1] - c.source_lines[0] + 1 for c in clones)
        
        return {
            'total_clones': len(clones),
            'by_type': dict(by_type),
            'average_similarity': sum([c.similarity_score for c in clones]) / len(clones) if clones else 0.0,
            'average_confidence': sum([c.confidence for c in clones]) / len(clones) if clones else 0.0,
            'total_cloned_lines': total_lines,
            'clone_types_found': sorted(list(set(c.clone_type for c in clones))),
            'highest_confidence_clone': max(clones, key=lambda c: c.confidence) if clones else None,
            'summary': self._generate_summary(clones, by_type)
        }
    
    def _generate_summary(self, clones: List[CodeClone], by_type: Dict[str, int]) -> str:
        """Generate human-readable summary."""
        total = len(clones)
        
        if total == 0:
            return "No clones detected"
        
        summary = f"Found {total} clone(s): "
        
        type_descriptions = []
        for clone_type in range(1, 5):
            count = by_type.get(f'type{clone_type}', 0)
            if count > 0:
                type_descriptions.append(f"{count} Type-{clone_type}")
        
        summary += ", ".join(type_descriptions)
        
        # Add confidence note
        avg_confidence = sum([c.confidence for c in clones]) / len(clones) if clones else 0.0
        if avg_confidence >= 0.8:
            summary += " (high confidence)"
        elif avg_confidence >= 0.6:
            summary += " (moderate confidence)"
        else:
            summary += " (low confidence)"
        
        return summary