"""
Enhanced Semantic Analyzer for CopycatM
Implements all recommendations for improved semantic similarity detection.
"""

import re
import hashlib
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path

from ..hashing.winnowing import Winnowing, WinnowingConfig
from ..hashing.ast_winnowing import ASTWinnowing, ASTWinnowingConfig
from ..parsers.tree_sitter_parser import TreeSitterParser
from .algorithm_detector import AlgorithmDetector
from .pseudocode_normalizer import PseudocodeNormalizer

logger = logging.getLogger(__name__)


@dataclass
class ControlFlowNode:
    """Node in control flow graph."""
    node_type: str  # 'if', 'loop', 'call', 'return', etc.
    node_id: int
    children: List[int] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFlowEdge:
    """Edge in data flow graph."""
    source_var: str
    target_var: str
    operation: str
    location: int


@dataclass
class SemanticFingerprint:
    """Complete semantic fingerprint of code."""
    # Multi-granularity winnowing
    winnowing_fine: List[Tuple[int, int]]      # k=5
    winnowing_medium: List[Tuple[int, int]]     # k=15
    winnowing_coarse: List[Tuple[int, int]]     # k=30
    
    # Control and data flow
    cfg_hash: str
    dfg_hash: str
    cfg_nodes: List[ControlFlowNode]
    dfg_edges: List[DataFlowEdge]
    
    # Mathematical operations
    math_sequence: List[str]
    math_patterns: Dict[str, int]
    
    # Memory patterns
    memory_access_patterns: List[str]
    array_dimensions: Dict[str, int]
    
    # Domain-specific features
    transforms: List[str]
    quantization_ops: List[str]
    entropy_coding: List[str]
    crypto_ops: List[str]
    
    # Constants and literals
    numeric_constants: List[float]
    string_constants: List[str]
    hex_constants: List[int]
    
    # Structural features
    function_signatures: List[str]
    loop_nesting_depth: int
    cyclomatic_complexity: int
    
    # AST features
    ast_depth: int
    ast_node_types: Dict[str, int]
    unique_ast_patterns: List[str]


class SemanticAnalyzer:
    """Enhanced semantic analyzer with all recommended improvements."""
    
    def __init__(self, reference_db_path: Optional[str] = None):
        """Initialize semantic analyzer with optional reference database."""
        # Multi-granularity winnowing instances
        self.winnowing_configs = {
            'fine': WinnowingConfig(k_gram_size=5, window_size=10, normalize_code=True),
            'medium': WinnowingConfig(k_gram_size=15, window_size=30, normalize_code=True),
            'coarse': WinnowingConfig(k_gram_size=30, window_size=60, normalize_code=True)
        }
        self.winnowing_instances = {
            name: Winnowing(config) for name, config in self.winnowing_configs.items()
        }
        
        # AST-based winnowing for better cross-language matching
        # Smaller k-grams for better matching
        self.ast_winnowing_configs = {
            'fine': ASTWinnowingConfig(k_gram_size=2, window_size=4),
            'medium': ASTWinnowingConfig(k_gram_size=3, window_size=6),
            'coarse': ASTWinnowingConfig(k_gram_size=5, window_size=10)
        }
        self.ast_winnowing_instances = {
            name: ASTWinnowing(config) for name, config in self.ast_winnowing_configs.items()
        }
        
        # Initialize components
        self.parser = TreeSitterParser()
        self.algorithm_detector = AlgorithmDetector()
        self.pseudocode_normalizer = PseudocodeNormalizer()
        
        # Domain-specific patterns
        self._init_domain_patterns()
        
        # Reference database for known implementations
        # Initialize empty first to avoid recursion during loading
        self.reference_db = defaultdict(list)
        if reference_db_path:
            self.reference_db = self._load_reference_db(reference_db_path)
        
    def _load_reference_db(self, db_path: Optional[str]) -> Dict[str, List[SemanticFingerprint]]:
        """Load reference implementation database."""
        if not db_path or not Path(db_path).exists():
            return defaultdict(list)
            
        with open(db_path, 'r') as f:
            data = json.load(f)
            # Extract implementations and generate fingerprints
            db = defaultdict(list)
            for algo_name, algo_data in data.items():
                if 'implementations' in algo_data:
                    for impl in algo_data['implementations']:
                        try:
                            # Extract fingerprint from implementation code
                            code = impl.get('code', '')
                            language = impl.get('language', 'python')
                            if code:
                                # Temporarily clear reference_db to avoid recursion
                                temp_db = self.reference_db
                                self.reference_db = defaultdict(list)
                                
                                fp = self.extract_semantic_fingerprint(code, language)
                                db[algo_name].append(fp)
                                
                                # Restore reference_db
                                self.reference_db = temp_db
                        except Exception as e:
                            logger.debug(f"Failed to load reference {algo_name}: {e}")
            return db
    
    def _init_domain_patterns(self):
        """Initialize domain-specific pattern matchers."""
        # Codec/DSP patterns
        self.transform_patterns = {
            'dct': r'\b(dct|discrete.*cosine|cosine.*transform)\b',
            'fft': r'\b(fft|fast.*fourier|fourier.*transform)\b',
            'dwt': r'\b(dwt|discrete.*wavelet|wavelet.*transform)\b',
            'mdct': r'\b(mdct|modified.*dct)\b',
            'hadamard': r'\b(hadamard|walsh.*hadamard)\b',
            'butterfly': r'butterfly|twiddle.*factor',
            'convolution': r'convolv|filter.*kernel'
        }
        
        # Quantization patterns
        self.quantization_patterns = {
            'uniform': r'(quant|quantiz).*uniform',
            'nonuniform': r'(quant|quantiz).*(non.*uniform|adaptive)',
            'deadzone': r'dead.*zone|zero.*zone',
            'rounding': r'round|floor|ceil|trunc',
            'clipping': r'clip|clamp|saturate|bound'
        }
        
        # Crypto patterns
        self.crypto_patterns = {
            'aes_sbox': r's.*box|substitution.*box|aes.*table',
            'sha_constants': r'0x[0-9a-f]{8}.*0x[0-9a-f]{8}',  # SHA constants pattern
            'modular': r'mod.*prime|modular.*exp|montgomery',
            'permutation': r'permut|shuffle|mix.*column',
            'rotation': r'rot[lr]|rotate|circular.*shift'
        }
        
    def extract_semantic_fingerprint(self, code: str, language: str) -> SemanticFingerprint:
        """Extract comprehensive semantic fingerprint from code."""
        # Parse AST first (needed for pseudocode normalization)
        try:
            ast_tree = self.parser.parse(code, language)
        except:
            ast_tree = None
            
        # Multi-granularity winnowing
        winnowing_fingerprints = {}
        
        # If we have a valid AST, use AST-based winnowing for better cross-language matching
        if ast_tree and hasattr(ast_tree, 'root'):
            logger.debug("Using AST-based winnowing for better cross-language matching")
            for name, ast_winnowing in self.ast_winnowing_instances.items():
                try:
                    winnowing_fingerprints[name] = ast_winnowing.generate_ast_fingerprint(ast_tree)
                except Exception as e:
                    logger.debug(f"AST winnowing failed for {name}, falling back to text-based: {e}")
                    # Fallback to text-based winnowing
                    winnowing_fingerprints[name] = self.winnowing_instances[name].generate_fingerprint(code, language)
        else:
            # Fallback to text-based winnowing with language normalization
            logger.debug("Using text-based winnowing (no valid AST available)")
            for name, winnowing in self.winnowing_instances.items():
                winnowing_fingerprints[name] = winnowing.generate_fingerprint(code, language)
            
        # Extract control flow graph
        cfg_nodes, cfg_hash = self._extract_cfg(code, ast_tree, language)
        
        # Extract data flow graph
        dfg_edges, dfg_hash = self._extract_dfg(code, ast_tree, language)
        
        # Extract mathematical operations
        math_sequence = self._extract_math_sequence(code)
        math_patterns = self._analyze_math_patterns(math_sequence)
        
        # Extract memory patterns
        memory_patterns = self._extract_memory_patterns(code)
        array_dims = self._extract_array_dimensions(code)
        
        # Extract domain-specific features
        transforms = self._extract_transforms(code)
        quant_ops = self._extract_quantization(code)
        entropy_ops = self._extract_entropy_coding(code)
        crypto_ops = self._extract_crypto_ops(code)
        
        # Extract constants
        numeric_consts = self._extract_numeric_constants(code)
        string_consts = self._extract_string_constants(code)
        hex_consts = self._extract_hex_constants(code)
        
        # Extract structural features
        func_sigs = self._extract_function_signatures(code, language)
        loop_depth = self._calculate_loop_nesting(code, ast_tree)
        complexity = self._calculate_cyclomatic_complexity(cfg_nodes)
        
        # AST features
        ast_features = self._extract_ast_features(ast_tree) if ast_tree else {
            'depth': 0, 'node_types': {}, 'patterns': []
        }
        
        return SemanticFingerprint(
            winnowing_fine=winnowing_fingerprints['fine'],
            winnowing_medium=winnowing_fingerprints['medium'],
            winnowing_coarse=winnowing_fingerprints['coarse'],
            cfg_hash=cfg_hash,
            dfg_hash=dfg_hash,
            cfg_nodes=cfg_nodes,
            dfg_edges=dfg_edges,
            math_sequence=math_sequence,
            math_patterns=math_patterns,
            memory_access_patterns=memory_patterns,
            array_dimensions=array_dims,
            transforms=transforms,
            quantization_ops=quant_ops,
            entropy_coding=entropy_ops,
            crypto_ops=crypto_ops,
            numeric_constants=numeric_consts,
            string_constants=string_consts,
            hex_constants=hex_consts,
            function_signatures=func_sigs,
            loop_nesting_depth=loop_depth,
            cyclomatic_complexity=complexity,
            ast_depth=ast_features['depth'],
            ast_node_types=ast_features['node_types'],
            unique_ast_patterns=ast_features['patterns']
        )
    
    def _extract_cfg(self, code: str, ast_tree: Any, language: str) -> Tuple[List[ControlFlowNode], str]:
        """Extract control flow graph."""
        nodes = []
        node_id = 0
        
        # Simple regex-based extraction (fallback)
        # For production, use proper AST traversal
        
        # Extract if statements
        for match in re.finditer(r'\b(if|elif|else)\b', code):
            nodes.append(ControlFlowNode(
                node_type='conditional',
                node_id=node_id,
                attributes={'keyword': match.group(1), 'pos': match.start()}
            ))
            node_id += 1
            
        # Extract loops
        for match in re.finditer(r'\b(for|while|do)\b', code):
            nodes.append(ControlFlowNode(
                node_type='loop',
                node_id=node_id,
                attributes={'keyword': match.group(1), 'pos': match.start()}
            ))
            node_id += 1
            
        # Extract function calls
        for match in re.finditer(r'(\w+)\s*\(', code):
            nodes.append(ControlFlowNode(
                node_type='call',
                node_id=node_id,
                attributes={'function': match.group(1), 'pos': match.start()}
            ))
            node_id += 1
            
        # Generate CFG hash
        cfg_str = '|'.join([f"{n.node_type}:{n.attributes}" for n in nodes])
        cfg_hash = hashlib.sha256(cfg_str.encode()).hexdigest()[:16]
        
        return nodes, cfg_hash
    
    def _extract_dfg(self, code: str, ast_tree: Any, language: str) -> Tuple[List[DataFlowEdge], str]:
        """Extract data flow graph."""
        edges = []
        
        # Extract variable assignments and their dependencies
        # Simplified regex approach
        assignments = re.findall(r'(\w+)\s*=\s*([^;,\n]+)', code)
        
        for i, (target, expr) in enumerate(assignments):
            # Find variables used in expression
            used_vars = re.findall(r'\b([a-zA-Z_]\w*)\b', expr)
            for var in used_vars:
                if var != target:  # Avoid self-references
                    edges.append(DataFlowEdge(
                        source_var=var,
                        target_var=target,
                        operation='assign',
                        location=i
                    ))
        
        # Generate DFG hash
        dfg_str = '|'.join([f"{e.source_var}->{e.target_var}:{e.operation}" for e in edges])
        dfg_hash = hashlib.sha256(dfg_str.encode()).hexdigest()[:16]
        
        return edges, dfg_hash
    
    def _extract_math_sequence(self, code: str) -> List[str]:
        """Extract sequence of mathematical operations."""
        ops = []
        
        # Basic arithmetic
        arithmetic_ops = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
            '%': 'MOD', '**': 'POW', '<<': 'SHL', '>>': 'SHR',
            '&': 'AND', '|': 'OR', '^': 'XOR', '~': 'NOT'
        }
        
        # Extract operations in order
        pattern = r'(\+|\-|\*|\/|\%|\*\*|<<|>>|&|\||\^|~)'
        for match in re.finditer(pattern, code):
            op = match.group(1)
            ops.append(arithmetic_ops.get(op, op))
            
        # Math functions
        math_funcs = [
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
            'exp', 'log', 'log10', 'log2', 'sqrt', 'pow',
            'abs', 'floor', 'ceil', 'round', 'min', 'max'
        ]
        
        for func in math_funcs:
            for match in re.finditer(rf'\b{func}\b', code, re.IGNORECASE):
                ops.append(f"FUNC_{func.upper()}")
                
        return ops
    
    def _analyze_math_patterns(self, sequence: List[str]) -> Dict[str, int]:
        """Analyze mathematical operation patterns."""
        patterns = defaultdict(int)
        
        # Count operation frequencies
        for op in sequence:
            patterns[f"count_{op}"] += 1
            
        # Detect common patterns
        seq_str = ' '.join(sequence)
        
        # MAC (Multiply-Accumulate)
        if 'MUL ADD' in seq_str or 'ADD MUL' in seq_str:
            patterns['mac_operations'] = seq_str.count('MUL ADD') + seq_str.count('ADD MUL')
            
        # Butterfly operations (common in FFT)
        if 'ADD SUB' in seq_str and 'MUL' in seq_str:
            patterns['butterfly_ops'] = min(seq_str.count('ADD'), seq_str.count('SUB'))
            
        # Modular arithmetic (crypto)
        if 'MOD' in seq_str:
            patterns['modular_ops'] = seq_str.count('MOD')
            
        return dict(patterns)
    
    def _extract_memory_patterns(self, code: str) -> List[str]:
        """Extract memory access patterns."""
        patterns = []
        
        # Array access patterns
        array_accesses = re.findall(r'(\w+)\[([^\]]+)\]', code)
        
        for arr, idx in array_accesses:
            # Classify index complexity
            if re.search(r'[+\-*/]', idx):
                if '*' in idx or '/' in idx:
                    patterns.append(f"COMPLEX_INDEX_{arr}")
                else:
                    patterns.append(f"LINEAR_INDEX_{arr}")
            else:
                patterns.append(f"SIMPLE_INDEX_{arr}")
                
        # Multi-dimensional arrays
        if re.search(r'\w+\[[^\]]+\]\[[^\]]+\]', code):
            patterns.append("MULTI_DIM_ARRAY")
            
        # Stride patterns
        stride_pattern = r'(\w+)\[(\w+)\s*\*\s*(\d+)\s*\+\s*(\w+)\]'
        if re.search(stride_pattern, code):
            patterns.append("STRIDED_ACCESS")
            
        return patterns
    
    def _extract_array_dimensions(self, code: str) -> Dict[str, int]:
        """Extract array dimensions."""
        dims = {}
        
        # Look for array declarations
        # C/Java style
        c_arrays = re.findall(r'(\w+)\s*\[(\d+)\](?:\s*\[(\d+)\])?', code)
        for match in c_arrays:
            name = match[0]
            if match[2]:  # 2D array
                dims[name] = 2
            else:
                dims[name] = 1
                
        # Python style (less reliable)
        py_arrays = re.findall(r'(\w+)\s*=\s*\[\s*\[', code)
        for name in py_arrays:
            dims[name] = 2
            
        return dims
    
    def _extract_transforms(self, code: str) -> List[str]:
        """Extract transform operations."""
        found_transforms = []
        
        for transform, pattern in self.transform_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                found_transforms.append(transform.upper())
                
        # Look for transform-specific patterns
        if re.search(r'cos.*\(.*pi.*\/', code, re.IGNORECASE):
            found_transforms.append("COSINE_BASIS")
            
        if re.search(r'twiddle|W_N|omega', code):
            found_transforms.append("FFT_TWIDDLE")
            
        return list(set(found_transforms))
    
    def _extract_quantization(self, code: str) -> List[str]:
        """Extract quantization operations."""
        quant_ops = []
        
        for quant_type, pattern in self.quantization_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                quant_ops.append(quant_type.upper())
                
        # Specific quantization patterns
        if re.search(r'>\s*>\s*\d+.*<\s*<\s*\d+', code):
            quant_ops.append("SHIFT_QUANTIZE")
            
        if re.search(r'\/\s*quant.*\*\s*quant', code, re.IGNORECASE):
            quant_ops.append("DEQUANTIZE")
            
        return list(set(quant_ops))
    
    def _extract_entropy_coding(self, code: str) -> List[str]:
        """Extract entropy coding operations."""
        entropy_ops = []
        
        entropy_patterns = {
            'huffman': r'huffman|huff.*code|huff.*table',
            'arithmetic': r'arithmetic.*cod|range.*cod|cabac|cavlc',
            'rice': r'rice.*cod|golomb',
            'rle': r'run.*length|rle|zero.*run',
            'vlc': r'variable.*length|vlc|exp.*golomb'
        }
        
        for op_type, pattern in entropy_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                entropy_ops.append(op_type.upper())
                
        return list(set(entropy_ops))
    
    def _extract_crypto_ops(self, code: str) -> List[str]:
        """Extract cryptographic operations."""
        crypto_ops = []
        
        for op_type, pattern in self.crypto_patterns.items():
            if re.search(pattern, code, re.IGNORECASE):
                crypto_ops.append(op_type.upper())
                
        # Additional crypto indicators
        if re.search(r'xor.*key|key.*xor', code, re.IGNORECASE):
            crypto_ops.append("KEY_XOR")
            
        if re.search(r'iv|initialization.*vector', code, re.IGNORECASE):
            crypto_ops.append("IV_USAGE")
            
        return list(set(crypto_ops))
    
    def _extract_numeric_constants(self, code: str) -> List[float]:
        """Extract numeric constants."""
        constants = []
        
        # Floating point
        float_pattern = r'\b\d+\.\d+(?:[eE][+-]?\d+)?\b'
        for match in re.finditer(float_pattern, code):
            val = float(match.group())
            if val not in [0.0, 1.0, 2.0, 0.5]:  # Filter common values
                constants.append(val)
                
        # Important integers
        int_pattern = r'\b\d{3,}\b'  # 3+ digit integers
        for match in re.finditer(int_pattern, code):
            val = float(match.group())
            if val > 100:  # Likely important
                constants.append(val)
                
        # Mathematical constants
        if re.search(r'3\.14159|pi|PI', code):
            constants.append(3.141592653589793)
            
        if re.search(r'2\.71828|euler|e', code, re.IGNORECASE):
            constants.append(2.718281828459045)
            
        return list(set(constants))[:50]  # Limit to 50 unique constants
    
    def _extract_string_constants(self, code: str) -> List[str]:
        """Extract string constants."""
        strings = []
        
        # Extract quoted strings
        pattern = r'["\']([^"\']+)["\']'
        for match in re.finditer(pattern, code):
            s = match.group(1)
            if len(s) > 3 and not s.isspace():  # Non-trivial strings
                strings.append(s)
                
        return list(set(strings))[:20]  # Limit to 20 unique strings
    
    def _extract_hex_constants(self, code: str) -> List[int]:
        """Extract hexadecimal constants."""
        hex_values = []
        
        # Hex constants
        hex_pattern = r'0x[0-9a-fA-F]{4,}'  # At least 4 hex digits
        for match in re.finditer(hex_pattern, code):
            val = int(match.group(), 16)
            hex_values.append(val)
            
        return list(set(hex_values))[:30]  # Limit to 30 unique values
    
    def _extract_function_signatures(self, code: str, language: str) -> List[str]:
        """Extract function signatures."""
        signatures = []
        
        if language in ['python', 'py']:
            pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        elif language in ['java', 'c', 'cpp', 'c++']:
            pattern = r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)'
        elif language in ['javascript', 'js']:
            pattern = r'function\s+(\w+)\s*\(([^)]*)\)|(\w+)\s*=\s*\([^)]*\)\s*=>'
        else:
            return []
            
        for match in re.finditer(pattern, code):
            name = match.group(1)
            params = match.group(2) if len(match.groups()) >= 2 else ''
            # Normalize parameter types
            param_count = len([p for p in params.split(',') if p.strip()])
            signatures.append(f"{name}/{param_count}")
            
        return signatures
    
    def _calculate_loop_nesting(self, code: str, ast_tree: Any) -> int:
        """Calculate maximum loop nesting depth."""
        if ast_tree:
            # AST-based calculation would be more accurate
            pass
            
        # Fallback: regex-based
        max_depth = 0
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Count indentation level of loops
            if re.search(r'\b(for|while)\b', line):
                indent = len(line) - len(line.lstrip())
                depth = indent // 4 + 1  # Assuming 4-space indent
                max_depth = max(max_depth, depth)
                
        return max_depth
    
    def _calculate_cyclomatic_complexity(self, cfg_nodes: List[ControlFlowNode]) -> int:
        """Calculate cyclomatic complexity from CFG."""
        # Simplified: count decision points
        decision_nodes = [n for n in cfg_nodes if n.node_type in ['conditional', 'loop']]
        return len(decision_nodes) + 1
    
    def _extract_ast_features(self, ast_tree: Any) -> Dict[str, Any]:
        """Extract AST-based features."""
        if not ast_tree:
            return {'depth': 0, 'node_types': {}, 'patterns': []}
            
        # This would traverse the AST and extract features
        # Placeholder implementation
        return {
            'depth': 5,  # Example depth
            'node_types': {'FunctionDef': 3, 'For': 2, 'If': 4},
            'patterns': ['nested_loop', 'recursive_call']
        }
    
    def calculate_similarity(self, fp1: SemanticFingerprint, 
                           fp2: SemanticFingerprint) -> Dict[str, float]:
        """Calculate comprehensive similarity between two fingerprints."""
        similarities = {}
        
        # Multi-granularity winnowing similarities
        # Check if we have AST fingerprints (they'll have different structure)
        if fp1.winnowing_fine and fp2.winnowing_fine:
            # Check if it's AST winnowing (tuple format) or text winnowing
            if isinstance(fp1.winnowing_fine[0], tuple) and len(fp1.winnowing_fine[0]) == 2:
                # AST winnowing format
                ast_winnowing = ASTWinnowing(self.ast_winnowing_configs['medium'])
                similarities['winnowing_fine'] = ast_winnowing.compare_fingerprints(
                    fp1.winnowing_fine, fp2.winnowing_fine)
                similarities['winnowing_medium'] = ast_winnowing.compare_fingerprints(
                    fp1.winnowing_medium, fp2.winnowing_medium)
                similarities['winnowing_coarse'] = ast_winnowing.compare_fingerprints(
                    fp1.winnowing_coarse, fp2.winnowing_coarse)
            else:
                # Text winnowing format
                winnowing = Winnowing(self.winnowing_configs['medium'])
                similarities['winnowing_fine'] = winnowing.compare_fingerprints(
                    fp1.winnowing_fine, fp2.winnowing_fine)
                similarities['winnowing_medium'] = winnowing.compare_fingerprints(
                    fp1.winnowing_medium, fp2.winnowing_medium)
                similarities['winnowing_coarse'] = winnowing.compare_fingerprints(
                    fp1.winnowing_coarse, fp2.winnowing_coarse)
        else:
            similarities['winnowing_fine'] = 0.0
            similarities['winnowing_medium'] = 0.0
            similarities['winnowing_coarse'] = 0.0
        
        # Best winnowing score
        similarities['winnowing_best'] = max(
            similarities['winnowing_fine'],
            similarities['winnowing_medium'],
            similarities['winnowing_coarse']
        )
        
        # Control flow similarity
        similarities['cfg'] = 1.0 if fp1.cfg_hash == fp2.cfg_hash else 0.3
        
        # Data flow similarity
        similarities['dfg'] = 1.0 if fp1.dfg_hash == fp2.dfg_hash else 0.2
        
        # Math sequence similarity (using LCS)
        similarities['math_sequence'] = self._sequence_similarity(
            fp1.math_sequence, fp2.math_sequence)
        
        # Math pattern similarity
        similarities['math_patterns'] = self._dict_similarity(
            fp1.math_patterns, fp2.math_patterns)
        
        # Memory pattern similarity
        similarities['memory_patterns'] = self._list_similarity(
            fp1.memory_access_patterns, fp2.memory_access_patterns)
        
        # Domain-specific similarities
        similarities['transforms'] = self._list_similarity(
            fp1.transforms, fp2.transforms)
        similarities['quantization'] = self._list_similarity(
            fp1.quantization_ops, fp2.quantization_ops)
        similarities['crypto'] = self._list_similarity(
            fp1.crypto_ops, fp2.crypto_ops)
        
        # Constant similarity (with fuzzy matching)
        similarities['constants'] = self._fuzzy_constant_similarity(
            fp1.numeric_constants, fp2.numeric_constants)
        
        # Structural similarity
        similarities['structure'] = self._structural_similarity(fp1, fp2)
        
        # AST similarity
        similarities['ast'] = self._ast_similarity(fp1, fp2)
        
        # Calculate weighted overall similarity
        weights = {
            'winnowing_best': 0.20,
            'cfg': 0.15,
            'dfg': 0.10,
            'math_sequence': 0.15,
            'transforms': 0.10,
            'constants': 0.10,
            'structure': 0.10,
            'ast': 0.10
        }
        
        overall = sum(similarities.get(k, 0) * weights.get(k, 0) 
                     for k in weights)
        similarities['overall'] = overall
        
        return similarities
    
    def _sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate sequence similarity using longest common subsequence."""
        if not seq1 or not seq2:
            return 0.0
            
        m, n = len(seq1), len(seq2)
        lcs = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    lcs[i][j] = lcs[i-1][j-1] + 1
                else:
                    lcs[i][j] = max(lcs[i-1][j], lcs[i][j-1])
                    
        return 2.0 * lcs[m][n] / (m + n)
    
    def _dict_similarity(self, d1: Dict, d2: Dict) -> float:
        """Calculate similarity between two dictionaries."""
        if not d1 and not d2:
            return 1.0
        if not d1 or not d2:
            return 0.0
            
        keys = set(d1.keys()) | set(d2.keys())
        if not keys:
            return 0.0
            
        similarity = 0.0
        for key in keys:
            v1 = d1.get(key, 0)
            v2 = d2.get(key, 0)
            if v1 == v2:
                similarity += 1.0
            elif v1 and v2:
                similarity += min(v1, v2) / max(v1, v2)
                
        return similarity / len(keys)
    
    def _list_similarity(self, l1: List, l2: List) -> float:
        """Calculate Jaccard similarity between two lists."""
        if not l1 and not l2:
            return 1.0
        if not l1 or not l2:
            return 0.0
            
        set1, set2 = set(l1), set(l2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _fuzzy_constant_similarity(self, const1: List[float], 
                                  const2: List[float], 
                                  tolerance: float = 0.01) -> float:
        """Calculate similarity with fuzzy matching for constants."""
        if not const1 and not const2:
            return 1.0
        if not const1 or not const2:
            return 0.0
            
        matches = 0
        for c1 in const1:
            for c2 in const2:
                if abs(c1 - c2) / max(abs(c1), abs(c2), 1.0) <= tolerance:
                    matches += 1
                    break
                    
        return 2.0 * matches / (len(const1) + len(const2))
    
    def _structural_similarity(self, fp1: SemanticFingerprint, 
                              fp2: SemanticFingerprint) -> float:
        """Calculate structural similarity."""
        features = []
        
        # Loop nesting similarity
        if fp1.loop_nesting_depth == fp2.loop_nesting_depth:
            features.append(1.0)
        else:
            max_depth = max(fp1.loop_nesting_depth, fp2.loop_nesting_depth)
            if max_depth > 0:
                features.append(1.0 - abs(fp1.loop_nesting_depth - fp2.loop_nesting_depth) / max_depth)
            else:
                features.append(1.0)
                
        # Complexity similarity
        if fp1.cyclomatic_complexity == fp2.cyclomatic_complexity:
            features.append(1.0)
        else:
            max_complex = max(fp1.cyclomatic_complexity, fp2.cyclomatic_complexity)
            if max_complex > 0:
                features.append(1.0 - abs(fp1.cyclomatic_complexity - fp2.cyclomatic_complexity) / max_complex)
            else:
                features.append(1.0)
                
        # Function signature similarity
        features.append(self._list_similarity(fp1.function_signatures, fp2.function_signatures))
        
        return sum(features) / len(features) if features else 0.0
    
    def _ast_similarity(self, fp1: SemanticFingerprint, 
                       fp2: SemanticFingerprint) -> float:
        """Calculate AST-based similarity."""
        features = []
        
        # AST depth similarity
        if fp1.ast_depth == fp2.ast_depth:
            features.append(1.0)
        else:
            max_depth = max(fp1.ast_depth, fp2.ast_depth)
            if max_depth > 0:
                features.append(1.0 - abs(fp1.ast_depth - fp2.ast_depth) / max_depth)
            else:
                features.append(1.0)
                
        # Node type distribution similarity
        features.append(self._dict_similarity(fp1.ast_node_types, fp2.ast_node_types))
        
        # Unique pattern similarity
        features.append(self._list_similarity(fp1.unique_ast_patterns, fp2.unique_ast_patterns))
        
        return sum(features) / len(features) if features else 0.0
    
    def find_similar_in_reference_db(self, fingerprint: SemanticFingerprint, 
                                   threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Find similar implementations in reference database."""
        matches = []
        
        for algo_name, ref_fingerprints in self.reference_db.items():
            for ref_fp in ref_fingerprints:
                similarity = self.calculate_similarity(fingerprint, ref_fp)
                if similarity['overall'] >= threshold:
                    matches.append((algo_name, similarity['overall']))
                    
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def add_to_reference_db(self, algo_name: str, 
                          fingerprint: SemanticFingerprint,
                          save_path: Optional[str] = None):
        """Add new implementation to reference database."""
        self.reference_db[algo_name].append(fingerprint)
        
        if save_path:
            # Save updated database
            # (Simplified - would need proper serialization)
            pass