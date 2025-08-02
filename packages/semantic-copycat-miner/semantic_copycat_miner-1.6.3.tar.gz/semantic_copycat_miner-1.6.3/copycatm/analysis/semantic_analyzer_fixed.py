"""
Semantic analyzer with fixes for better cross-language feature performance.

This module enhances the semantic analyzer to properly calculate MinHash/SimHash
similarities and improve CFG/DFG normalization.
"""

from .semantic_analyzer import SemanticAnalyzer, SemanticFingerprint
from ..hashing.semantic import SemanticHasher
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FixedSemanticAnalyzer(SemanticAnalyzer):
    """Fixed semantic analyzer with improved cross-language features."""
    
    def __init__(self, reference_db_path=None):
        """Initialize with semantic hasher for MinHash/SimHash."""
        super().__init__(reference_db_path)
        self.semantic_hasher = SemanticHasher()
    
    def extract_semantic_fingerprint(self, code: str, language: str) -> SemanticFingerprint:
        """Extract fingerprint with fixed MinHash/SimHash generation."""
        # Get base fingerprint
        fp = super().extract_semantic_fingerprint(code, language)
        
        # Parse AST for semantic hashing
        try:
            ast_tree = self.parser.parse(code, language)
            if ast_tree and hasattr(ast_tree, 'root'):
                # Generate semantic MinHash and SimHash from AST
                fp.minhash_semantic = self.semantic_hasher.minhash_from_ast(ast_tree.root)
                # SimHash needs features extracted from AST
                ast_features = []
                self._extract_semantic_ast_features(ast_tree.root, ast_features)
                feature_text = ' '.join(ast_features) if ast_features else 'empty'
                fp.simhash_semantic = self.semantic_hasher.simhash(feature_text)
                logger.debug(f"Generated semantic hashes - MinHash: {fp.minhash_semantic[:8]}..., SimHash: {fp.simhash_semantic[:8]}...")
            else:
                # Fallback to text-based but with normalization
                normalized_code = self._normalize_for_semantic_hash(code, language)
                fp.minhash_semantic = self.semantic_hasher.generate_minhash(normalized_code)
                fp.simhash_semantic = self.semantic_hasher.simhash_from_features(
                    self._extract_semantic_features(code, language)
                )
        except Exception as e:
            logger.debug(f"Failed to generate semantic hashes: {e}")
            fp.minhash_semantic = None
            fp.simhash_semantic = None
        
        return fp
    
    def calculate_similarity(self, fp1: SemanticFingerprint, 
                           fp2: SemanticFingerprint) -> Dict[str, float]:
        """Calculate similarity with MinHash/SimHash support."""
        # Get base similarities
        similarities = super().calculate_similarity(fp1, fp2)
        
        # Add MinHash similarity
        if hasattr(fp1, 'minhash_semantic') and hasattr(fp2, 'minhash_semantic'):
            if fp1.minhash_semantic and fp2.minhash_semantic:
                minhash_sim = self.semantic_hasher.estimate_similarity(
                    fp1.minhash_semantic, fp2.minhash_semantic, 'minhash'
                )
                similarities['minhash'] = minhash_sim
            else:
                similarities['minhash'] = 0.0
        else:
            similarities['minhash'] = 0.0
            
        # Add SimHash similarity  
        if hasattr(fp1, 'simhash_semantic') and hasattr(fp2, 'simhash_semantic'):
            if fp1.simhash_semantic and fp2.simhash_semantic:
                simhash_sim = self.semantic_hasher.estimate_similarity(
                    fp1.simhash_semantic, fp2.simhash_semantic, 'simhash'
                )
                similarities['simhash'] = simhash_sim
            else:
                similarities['simhash'] = 0.0
        else:
            similarities['simhash'] = 0.0
        
        # Fix CFG similarity to ignore positions
        if fp1.cfg_nodes and fp2.cfg_nodes:
            # Compare node types and functions only, not positions
            cfg1_normalized = self._normalize_cfg_nodes(fp1.cfg_nodes)
            cfg2_normalized = self._normalize_cfg_nodes(fp2.cfg_nodes)
            
            # Calculate Jaccard similarity of normalized nodes
            if cfg1_normalized or cfg2_normalized:
                intersection = len(cfg1_normalized & cfg2_normalized)
                union = len(cfg1_normalized | cfg2_normalized)
                similarities['cfg'] = intersection / union if union > 0 else 0.0
            else:
                similarities['cfg'] = 0.0
        
        return similarities
    
    def _normalize_cfg_nodes(self, nodes):
        """Normalize CFG nodes to ignore position information."""
        normalized = set()
        for node in nodes:
            # Extract just the semantic information
            node_sig = f"{node.node_type}"
            if hasattr(node, 'attributes'):
                if 'function' in node.attributes:
                    node_sig += f":{node.attributes['function']}"
                if 'keyword' in node.attributes:
                    node_sig += f":{node.attributes['keyword']}"
            normalized.add(node_sig)
        return normalized
    
    def _normalize_for_semantic_hash(self, code: str, language: str) -> str:
        """Normalize code for semantic hashing."""
        # Language-specific normalizations
        if language == 'python':
            code = code.replace('def ', 'function ')
            code = code.replace('elif ', 'else if ')
        elif language == 'javascript':
            code = code.replace('function ', 'function ')
            code = code.replace('let ', 'var ')
            code = code.replace('const ', 'var ')
        elif language in ['c', 'cpp']:
            code = code.replace('void ', 'function ')
            code = code.replace('int ', 'var ')
            
        # Common normalizations
        code = code.replace('(', ' ')
        code = code.replace(')', ' ')
        code = code.replace('{', ' ')
        code = code.replace('}', ' ')
        code = code.replace(';', ' ')
        
        return code
    
    def _extract_semantic_features(self, code: str, language: str) -> list:
        """Extract semantic features for SimHash."""
        features = []
        
        # Extract keywords and patterns
        import re
        
        # Control flow
        for pattern in ['if', 'for', 'while', 'return']:
            count = len(re.findall(rf'\b{pattern}\b', code))
            if count > 0:
                features.extend([f"CF:{pattern}"] * count)
        
        # Function calls
        for match in re.finditer(r'\b(\w+)\s*\(', code):
            func_name = match.group(1)
            if func_name not in ['if', 'for', 'while']:
                features.append(f"CALL:{func_name}")
        
        # Operators
        for op in ['<', '>', '==', '!=', '<=', '>=', '+', '-', '*', '/', '%']:
            count = code.count(op)
            if count > 0:
                features.extend([f"OP:{op}"] * count)
        
        return features
    
    def _extract_semantic_ast_features(self, node, features, depth=0, max_depth=10):
        """Extract semantic features from AST nodes."""
        if not node or depth > max_depth:
            return
            
        # Get node type
        node_type = 'unknown'
        if hasattr(node, 'type'):
            node_type = str(node.type)
        elif hasattr(node, 'kind'):
            node_type = str(node.kind)
            
        # Add normalized node type
        if node_type in ['if_statement', 'conditional_expression']:
            features.append('COND')
        elif node_type in ['for_statement', 'while_statement', 'do_statement']:
            features.append('LOOP')
        elif node_type in ['function_definition', 'function_declaration']:
            features.append('FUNC')
        elif node_type in ['call', 'call_expression']:
            features.append('CALL')
            # Try to get function name
            if hasattr(node, 'child_by_field_name'):
                func_node = node.child_by_field_name('function')
                if func_node and hasattr(func_node, 'text'):
                    func_name = func_node.text
                    if isinstance(func_name, bytes):
                        func_name = func_name.decode('utf-8', errors='ignore')
                    features.append(f'CALL:{func_name}')
        elif node_type in ['binary_expression', 'binary_operator']:
            features.append('BINOP')
            # Try to get operator
            for i in range(node.child_count if hasattr(node, 'child_count') else 0):
                child = node.child(i)
                if child and hasattr(child, 'type'):
                    if str(child.type) in ['<', '>', '==', '!=', '<=', '>=']:
                        features.append(f'OP:{child.type}')
        elif node_type == 'return_statement':
            features.append('RETURN')
        elif node_type in ['identifier', 'variable_name']:
            if hasattr(node, 'text'):
                text = node.text
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='ignore')
                # Normalize common variable names
                if text.lower() in ['arr', 'array', 'list']:
                    features.append('VAR:ARRAY')
                elif text.lower() in ['i', 'j', 'k', 'idx', 'index']:
                    features.append('VAR:INDEX')
                elif text.lower() in ['pivot', 'mid']:
                    features.append('VAR:PIVOT')
        
        # Recurse through children
        if hasattr(node, 'child_count'):
            for i in range(node.child_count):
                child = node.child(i)
                if child:
                    self._extract_semantic_ast_features(child, features, depth + 1, max_depth)
        elif hasattr(node, 'children'):
            for child in node.children:
                if child:
                    self._extract_semantic_ast_features(child, features, depth + 1, max_depth)