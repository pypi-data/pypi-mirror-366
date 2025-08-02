"""
Three-tier analysis architecture for CopycatM.

This module implements the hybrid approach specified in COPYCATM_SPECS2.md:
- Tier 1: Common Baseline (applied to all files)
- Tier 2: Traditional approach (for smaller files)
- Tier 3: Semantic AI transformation approach (for larger, complex files)
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pathlib import Path

from ..analysis.metadata import MetadataExtractor
from ..analysis.complexity import ComplexityAnalyzer
from ..analysis.invariant_extractor_improved import ImprovedInvariantExtractor
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy import FuzzyHasher
from ..hashing.semantic import SemanticHasher
from ..parsers.tree_sitter_parser import TreeSitterParser
from ..data.language_configs import get_language_config
from .config import AnalysisConfig
from .exceptions import AnalysisError
from ..gnn import GNNSimilarityDetector
from ..analysis.mutation_detector import MutationDetector
from ..analysis.control_block_extractor import ControlBlockExtractor
from ..analysis.mathematical_property_detector import MathematicalPropertyDetector
from ..analysis.cross_language_normalizer import CrossLanguageNormalizer
from .signature_aggregator import SignatureAggregator, AggregationStrategy
from ..analysis.unknown_algorithm_clustering import UnknownAlgorithmClusterer
from .advanced_config import AdvancedConfigManager
from .. import __version__

logger = logging.getLogger(__name__)


class AnalysisTier(Enum):
    """Analysis tier levels."""
    BASELINE = "baseline"
    TRADITIONAL = "traditional"
    SEMANTIC = "semantic"


class ExtractionMethod(Enum):
    """Extraction method used."""
    BASELINE = "baseline"
    TRADITIONAL = "traditional"
    SEMANTIC = "semantic"


class SignatureType(Enum):
    """Signature generation method."""
    BASELINE = "baseline"
    WINNOWING = "winnowing"
    SLIDING_WINDOW = "sliding_window"
    SEMANTIC_BLOCK = "semantic_block"


class ThreeTierAnalyzer:
    """
    Implements the three-tier analysis architecture for code analysis.
    
    The analyzer applies different analysis methods based on file characteristics:
    - Small files: Baseline + Traditional approach
    - Large/complex files: Baseline + Semantic approach (with Traditional fallback)
    """
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize the three-tier analyzer."""
        self.config = config or AnalysisConfig.load_default()
        
        # Initialize components
        self.metadata_extractor = MetadataExtractor()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.invariant_extractor = ImprovedInvariantExtractor()
        
        # Initialize hashers
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = FuzzyHasher(self.config.tlsh_threshold)
        self.semantic_hasher = SemanticHasher(
            num_perm=128, 
            lsh_bands=self.config.lsh_bands
        )
        
        # Initialize parser
        self.parser = TreeSitterParser()
        
        # Initialize GNN detector
        self.gnn_detector = GNNSimilarityDetector(use_pytorch=False)  # Start with simple model
        
        # Initialize mutation detector
        self.mutation_detector = MutationDetector()
        
        # Initialize control block extractor
        self.control_block_extractor = ControlBlockExtractor()
        
        # Initialize mathematical property detector
        self.math_property_detector = MathematicalPropertyDetector()
        
        # Initialize cross-language normalizer
        self.cross_lang_normalizer = CrossLanguageNormalizer()
        
        # Initialize signature aggregator
        self.signature_aggregator = SignatureAggregator(AggregationStrategy.ENSEMBLE)
        
        # Initialize unknown algorithm clusterer
        self.unknown_clusterer = UnknownAlgorithmClusterer()
        
        # Initialize advanced configuration manager
        self.config_manager = AdvancedConfigManager()
        self._initialize_config_manager()
        
        # Track extraction methods used
        self.extraction_methods_used = []
        self.fallback_reasons = []
    
    def _initialize_config_manager(self):
        """Initialize advanced configuration manager."""
        # Load from environment variables
        self.config_manager.load_from_env()
        
        # Load from config files
        config_files = [
            Path.home() / '.copycatm' / 'config.json',
            Path.cwd() / 'copycatm.json',
            Path.cwd() / '.copycatm.json',
        ]
        
        for config_file in config_files:
            if config_file.exists():
                self.config_manager.load_from_file(config_file)
        
        # Override with existing config values
        config_dict = self.config.to_dict()
        self.config_manager.load_from_cli(config_dict)
    
    def analyze_file(self, file_path: str, force_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a file using the three-tier approach.
        
        Args:
            file_path: Path to the file to analyze
            force_language: Optional language override
            
        Returns:
            Analysis results with signatures and metadata
        """
        self.extraction_methods_used = []
        self.fallback_reasons = []
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tier 1: Common Baseline (always applied)
            baseline_results = self._tier1_baseline_analysis(file_path, content, force_language)
            
            # Get language configuration for thresholds
            language = baseline_results['file_metadata']['language']
            lang_config = get_language_config(language)
            
            # Determine which additional tier to apply based on file size
            line_count = baseline_results['file_metadata']['line_count']
            signatures = []
            
            # Get thresholds from language config
            traditional_threshold = lang_config.get('min_lines', 5)
            semantic_threshold = lang_config.get('semantic_threshold', 50)
            
            # Check if this might be minified code
            from ..analysis.minified_detector import MinifiedCodeDetector
            minified_detector = MinifiedCodeDetector()
            is_minified, minified_confidence = minified_detector.is_minified(content, language)
            
            # Apply tier based on file size and minified status
            if line_count < traditional_threshold and not is_minified:
                # Very small file - baseline only
                logger.info(f"File {file_path} has {line_count} lines, using baseline only")
                self.extraction_methods_used.append(ExtractionMethod.BASELINE)
            elif line_count < traditional_threshold and is_minified:
                # Minified file - force traditional analysis
                logger.info(f"File {file_path} detected as minified (confidence: {minified_confidence:.2f}), applying traditional approach")
                traditional_sigs = self._tier2_traditional_analysis(content, language, baseline_results)
                signatures.extend(traditional_sigs)
                
            elif line_count < semantic_threshold:
                # Small to medium file - apply traditional approach
                logger.info(f"File {file_path} has {line_count} lines, applying traditional approach")
                traditional_sigs = self._tier2_traditional_analysis(content, language, baseline_results)
                signatures.extend(traditional_sigs)
                
            else:
                # Large file - try semantic approach with fallback
                logger.info(f"File {file_path} has {line_count} lines, applying semantic approach")
                
                # Special handling for C language - prefer traditional analysis
                if language.lower() == 'c':
                    logger.info("C language detected, using traditional analysis for better accuracy")
                    try:
                        traditional_sigs = self._tier2_traditional_analysis(content, language, baseline_results)
                        signatures.extend(traditional_sigs)
                    except Exception as e:
                        logger.error(f"Traditional analysis failed for C file: {e}")
                        self.fallback_reasons.append(f"Traditional analysis failed: {str(e)}")
                        # Try semantic as last resort
                        try:
                            semantic_sigs = self._tier3_semantic_analysis(content, language, baseline_results)
                            if semantic_sigs:
                                signatures.extend(semantic_sigs)
                        except:
                            pass
                else:
                    # Non-C languages - use semantic with fallback
                    try:
                        semantic_sigs = self._tier3_semantic_analysis(content, language, baseline_results)
                        if semantic_sigs and len(semantic_sigs) > 0:
                            # Semantic analysis produced results
                            signatures.extend(semantic_sigs)
                        else:
                            # Semantic analysis produced no results, fallback to traditional
                            logger.warning(f"Semantic analysis produced no signatures, falling back to traditional")
                            self.fallback_reasons.append("Semantic analysis produced no signatures")
                        
                            try:
                                traditional_sigs = self._tier2_traditional_analysis(content, language, baseline_results)
                                signatures.extend(traditional_sigs)
                            except Exception as e2:
                                # Final fallback to baseline only
                                logger.error(f"Traditional analysis also failed: {e2}, using baseline only")
                                self.fallback_reasons.append(f"Traditional analysis failed: {str(e2)}")
                                self.extraction_methods_used.append(ExtractionMethod.BASELINE)
                    except Exception as e:
                        # Fallback to traditional
                        logger.warning(f"Semantic analysis failed: {e}, falling back to traditional")
                        self.fallback_reasons.append(f"Semantic analysis failed: {str(e)}")
                        
                        try:
                            traditional_sigs = self._tier2_traditional_analysis(content, language, baseline_results)
                            signatures.extend(traditional_sigs)
                        except Exception as e2:
                            # Final fallback to baseline only
                            logger.error(f"Traditional analysis also failed: {e2}, using baseline only")
                            self.fallback_reasons.append(f"Traditional analysis failed: {str(e2)}")
                            self.extraction_methods_used.append(ExtractionMethod.BASELINE)
            
            # Build final output
            return self._build_output(baseline_results, signatures)
            
        except Exception as e:
            raise AnalysisError(f"Failed to analyze {file_path}: {str(e)}") from e
    
    def _tier1_baseline_analysis(self, file_path: str, content: str, 
                                 force_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Tier 1: Common Baseline Analysis
        
        Applied to all files regardless of size:
        - File metadata extraction
        - Traditional hashes (SHA-1, SHA-256, MD5)
        - Fuzzy hashes (SSDEEP, TLSH)
        - Mathematical invariants
        - Basic metrics (cyclomatic complexity, imports, license tags)
        """
        logger.debug("Applying Tier 1: Common Baseline analysis")
        self.extraction_methods_used.append(ExtractionMethod.BASELINE)
        
        # Extract metadata
        metadata = self.metadata_extractor.extract(file_path)
        if force_language:
            metadata['language'] = force_language
        
        # Generate traditional hashes
        direct_hashes = {
            "sha1": self.direct_hasher.sha1(content),
            "sha256": self.direct_hasher.sha256(content),
            "md5": self.direct_hasher.md5(content),
            "blake2b": self.direct_hasher.blake2b(content)
        }
        
        # Generate fuzzy hashes
        fuzzy_hashes = {
            "tlsh": self.fuzzy_hasher.tlsh(content),
            "ssdeep": self.fuzzy_hasher.ssdeep(content)
        }
        
        # Generate semantic hashes
        semantic_hashes = {}
        if "minhash" in self.config.hash_algorithms:
            semantic_hashes["minhash"] = self.semantic_hasher.generate_minhash(content)
            semantic_hashes["lsh_bands"] = self.config.lsh_bands
        
        if "simhash" in self.config.hash_algorithms:
            semantic_hashes["simhash"] = self.semantic_hasher.generate_simhash(content)
        
        # Apply cross-language normalization
        normalized_code = self.cross_lang_normalizer.normalize_code(content, metadata['language'])
        normalized_patterns = self.cross_lang_normalizer.extract_normalized_patterns(content, metadata['language'])
        
        # Add normalized hash
        semantic_hashes["normalized_hash"] = self.direct_hasher.sha256(normalized_code)
        
        # Parse AST for invariant extraction
        try:
            ast_tree = self.parser.parse(content, metadata['language'])
            
            # Extract mathematical invariants
            invariants = self.invariant_extractor.extract(ast_tree, metadata['language'])
            
            # Extract complexity metrics
            complexity = self.complexity_analyzer.analyze(ast_tree, metadata['language'])
            
            # Extract control structure blocks
            control_blocks = self.control_block_extractor.extract_control_blocks(ast_tree, metadata['language'])
            logger.debug(f"Extracted {len(control_blocks)} control blocks")
            
            # Detect mathematical properties
            math_properties = self.math_property_detector.detect_properties(
                ast_tree, metadata['language'], invariants
            )
            logger.debug(f"Detected {len(math_properties)} mathematical properties")
            
            # Generate GNN similarity hash
            try:
                graph = self.gnn_detector.graph_builder.build_graph_from_ast(ast_tree, metadata['language'])
                gnn_hash = self.gnn_detector.get_similarity_hash(graph)
                semantic_hashes["gnn_hash"] = gnn_hash
                
                # Store graph features for later analysis
                graph_features = self.gnn_detector.graph_builder.get_graph_features(graph)
                semantic_hashes["gnn_features"] = {
                    "num_nodes": graph_features["num_nodes"],
                    "num_edges": graph_features["num_edges"],
                    "density": graph_features["density"],
                    "avg_degree": graph_features["avg_degree"]
                }
            except Exception as e:
                logger.debug(f"GNN hash generation failed: {e}")
                semantic_hashes["gnn_hash"] = None
                
        except Exception as e:
            logger.warning(f"Failed to parse AST for baseline analysis: {e}")
            invariants = []
            complexity = {"cyclomatic_complexity": 0, "average_complexity": 0}
            control_blocks = []
            math_properties = []
        
        # Generate mathematical properties composite hash
        if math_properties:
            semantic_hashes["math_properties_hash"] = self.math_property_detector.generate_composite_hash(math_properties)
            semantic_hashes["math_properties_count"] = len(math_properties)
        
        # Extract imports and license tags
        imports = self._extract_imports(content, metadata['language'])
        license_tags = self._extract_license_tags(content)
        
        return {
            'file_metadata': metadata,
            'hashes': {
                'direct': direct_hashes,
                'fuzzy': fuzzy_hashes,
                'semantic': semantic_hashes
            },
            'code_metrics': {
                'cyclomatic_complexity': complexity.get('cyclomatic_complexity', 0),
                'lines_of_code': metadata['line_count'],
                'comment_lines': self._count_comment_lines(content, metadata['language']),
                'imports': imports,
                'license_tags': license_tags,
                'source_headers': self._extract_source_headers(content)
            },
            'mathematical_invariants': invariants,
            'control_blocks': control_blocks,
            'mathematical_properties': math_properties,
            'cross_language_patterns': normalized_patterns
        }
    
    def _tier2_traditional_analysis(self, content: str, language: str, 
                                   baseline_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Tier 2: Traditional Approach
        
        For smaller files or as fallback:
        - Pattern-based algorithm detection
        - Keyword scanning
        - Standard algorithm recognition
        - Basic signature generation
        """
        logger.debug("Applying Tier 2: Traditional analysis")
        self.extraction_methods_used.append(ExtractionMethod.TRADITIONAL)
        
        signatures = []
        
        # Pattern-based algorithm detection
        from ..analysis.algorithm_detector import AlgorithmDetector
        detector = AlgorithmDetector(self.config)
        
        # Set content on detector for minified code detection
        detector.content = content
        
        try:
            # Parse code for pattern matching
            ast_tree = self.parser.parse(content, language)
            
            # Add file path to AST tree for domain detection
            if hasattr(ast_tree, '__dict__'):
                ast_tree.file_path = baseline_results.get('file_metadata', {}).get('absolute_path', '')
            
            # Detect algorithms using pattern matching
            algorithms = detector.detect(ast_tree, language, baseline_results['file_metadata']['line_count'])
            
            # Process unknown algorithms for clustering
            unknown_algorithms = [algo for algo in algorithms if algo.get('algorithm_type') == 'unknown_complex_algorithm']
            if unknown_algorithms:
                for algo in unknown_algorithms:
                    # Get normalized code from baseline results
                    normalized_code = baseline_results.get('cross_language_patterns', [])
                    
                    algo_data = {
                        'file_path': baseline_results['file_metadata']['absolute_path'],
                        'location': algo.get('location', {}),
                        'normalized_code': str(normalized_code),  # Convert patterns to string
                        'complexity_metrics': algo.get('evidence', {}).get('complexity_metrics', {}),
                        'confidence': algo.get('confidence', 0.0)
                    }
                    
                    # Add to clusterer
                    algo_id = self.unknown_clusterer.add_unknown_algorithm(algo_data)
                    
                    # Check if it matches any learned pattern
                    match = self.unknown_clusterer.match_algorithm(algo_data)
                    if match:
                        # Update algorithm with learned pattern info
                        algo['learned_pattern'] = match
                        algo['algorithm_type'] = 'learned_algorithm_pattern'
                        algo['algorithm_subtype'] = f"cluster_{match['cluster_id']}"
                        algo['confidence'] = max(algo.get('confidence', 0), match.get('confidence', 0))
            
            # Convert algorithms to signatures
            for algo in algorithms:
                # Calculate average transformation resistance
                trans_res = algo.get('transformation_resistance', {})
                if isinstance(trans_res, dict) and 'overall' in trans_res:
                    avg_trans_res = trans_res['overall']
                elif isinstance(trans_res, dict):
                    # Filter only numeric values
                    numeric_values = [v for k, v in trans_res.items() if isinstance(v, (int, float))]
                    avg_trans_res = sum(numeric_values) / len(numeric_values) if numeric_values else 0.0
                else:
                    avg_trans_res = float(trans_res) if trans_res else 0.0
                
                # Extract evidence properly - keep as dict if it's a dict
                evidence = algo.get('evidence', {})
                if isinstance(evidence, str):
                    # Convert string evidence to dict format
                    evidence = {'description': evidence}
                
                # Build proper algorithm classification
                algo_type = algo.get('algorithm_type', 'unknown')
                algo_subtype = algo.get('algorithm_subtype', '')
                if algo_subtype and algo_subtype != 'generic':
                    classification = f"{algo_type}/{algo_subtype}"
                else:
                    classification = algo_type
                
                # Create a block for mutation detection
                block_for_mutation = {
                    'normalized_code': evidence.get('normalized_representation', ''),
                    'location': algo.get('location', {}),
                    'function_name': algo.get('function_name', ''),
                    'classification': classification
                }
                
                # Check for mutations
                mutations = []
                mutation_hashes = {}
                if block_for_mutation['normalized_code']:
                    mutations = self.mutation_detector.detect_mutations(block_for_mutation, language)
                    if mutations:
                        mutation_hashes = self.mutation_detector.generate_mutation_hashes(mutations)
                        logger.info(f"Detected {len(mutations)} mutations for {algo.get('function_name', 'unknown')}")
                
                signature = {
                    'signature_hash': algo.get('hashes', {}).get('combined_hash', 
                                     hashlib.sha256(f"{algo_type}_{algo.get('function_name', '')}".encode()).hexdigest()),
                    'signature_type': SignatureType.BASELINE.value,
                    'extraction_method': ExtractionMethod.TRADITIONAL.value,
                    'source_location': {
                        'start_line': algo.get('location', {}).get('start', 1),
                        'end_line': algo.get('location', {}).get('end', 1),
                        'function_name': algo.get('function_name', ''),
                        'file_path': baseline_results['file_metadata']['absolute_path']
                    },
                    'confidence_score': algo.get('confidence', 0.0),
                    'transformation_resistance': avg_trans_res,
                    'algorithm_classification': classification,
                    'evidence': evidence,
                    'fuzzy_hashes': {
                        'tlsh': algo.get('hashes', {}).get('fuzzy', {}).get('tlsh', ''),
                        'ssdeep': None
                    },
                    'mutations': mutations,
                    'mutation_hashes': mutation_hashes,
                    'primary': True
                }
                signatures.append(signature)
                
        except Exception as e:
            logger.error(f"Traditional analysis error: {e}")
            self.fallback_reasons.append(f"Traditional pattern matching failed: {str(e)}")
        
        return signatures
    
    def _tier3_semantic_analysis(self, content: str, language: str,
                                baseline_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Tier 3: Semantic AI Transformation Approach
        
        For larger, complex files:
        - AST parsing and analysis
        - Pseudocode translation
        - Cross-language normalization
        - Algorithm block extraction
        - Unknown algorithm detection
        """
        logger.debug("Applying Tier 3: Semantic analysis")
        self.extraction_methods_used.append(ExtractionMethod.SEMANTIC)
        
        signatures = []
        
        # Import the pseudocode normalizer (to be implemented)
        from ..analysis.pseudocode_normalizer import PseudocodeNormalizer
        normalizer = PseudocodeNormalizer()
        
        try:
            # Parse AST
            ast_tree = self.parser.parse(content, language)
            
            # Extract and normalize code blocks
            normalized_blocks = normalizer.extract_and_normalize_blocks(ast_tree, language)
            
            # Analyze each normalized block
            for block in normalized_blocks:
                # Generate GNN hash for the block
                gnn_hash = None
                gnn_features = {}
                try:
                    if hasattr(block, 'ast_node') and block.get('ast_node'):
                        block_graph = self.gnn_detector.graph_builder.build_graph_from_ast(
                            block['ast_node'], language
                        )
                        gnn_hash = self.gnn_detector.get_similarity_hash(block_graph)
                        gnn_features = self.gnn_detector.graph_builder.get_graph_features(block_graph)
                except Exception as e:
                    logger.debug(f"GNN analysis failed for block: {e}")
                
                # Check for mutations
                mutations = self.mutation_detector.detect_mutations(block, language)
                mutation_hashes = {}
                if mutations:
                    mutation_hashes = self.mutation_detector.generate_mutation_hashes(mutations)
                    logger.info(f"Detected {len(mutations)} mutations in block")
                
                # Generate signature from normalized pseudocode
                signature = {
                    'signature_hash': self._generate_signature_hash(block['normalized_code']),
                    'signature_type': SignatureType.SEMANTIC_BLOCK.value,
                    'extraction_method': ExtractionMethod.SEMANTIC.value,
                    'source_location': {
                        'start_line': block['location']['start_line'],
                        'end_line': block['location']['end_line'],
                        'function_name': block.get('function_name', ''),
                        'file_path': baseline_results['file_metadata']['absolute_path']
                    },
                    'confidence_score': block.get('confidence', 0.9),
                    'transformation_resistance': 0.85,  # High for semantic analysis
                    'algorithm_classification': block.get('classification', 'unknown'),
                    'evidence': block['normalized_code'],  # Store normalized pseudocode as evidence
                    'fuzzy_hashes': {
                        'tlsh': self.fuzzy_hasher.tlsh(block['normalized_code']),
                        'ssdeep': None
                    },
                    'gnn_hash': gnn_hash,
                    'gnn_features': gnn_features,
                    'mutations': mutations,
                    'mutation_hashes': mutation_hashes,
                    'primary': block.get('is_primary', True)
                }
                signatures.append(signature)
                
        except Exception as e:
            logger.error(f"Semantic analysis error: {e}")
            raise  # Let the caller handle fallback
        
        return signatures
    
    def _build_output(self, baseline_results: Dict[str, Any], 
                     signatures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build the final output structure with signature aggregation."""
        
        # Group signatures by tier for aggregation
        tier_results = {}
        for sig in signatures:
            # Determine tier based on extraction method
            extraction_method = sig.get('extraction_method', 'baseline')
            if extraction_method == 'baseline':
                tier = 1
            elif extraction_method == 'traditional':
                tier = 2
            elif extraction_method == 'semantic':
                tier = 3
            else:
                tier = 1
            
            if tier not in tier_results:
                tier_results[tier] = []
            
            # Convert signature to format expected by aggregator
            aggregator_sig = {
                'signature_hash': sig.get('signature_hash', ''),
                'confidence_score': sig.get('confidence_score', 0.0),
                'algorithm_classification': {
                    'type': sig.get('algorithm_classification', '').split('/')[0] if '/' in str(sig.get('algorithm_classification', '')) else str(sig.get('algorithm_classification', '')),
                    'subtype': sig.get('algorithm_classification', '').split('/')[1] if '/' in str(sig.get('algorithm_classification', '')) and len(str(sig.get('algorithm_classification', '')).split('/')) > 1 else 'generic'
                },
                'source_location': sig.get('source_location', {}),
                'evidence': sig.get('evidence', {}),
                'transformation_resistance': sig.get('transformation_resistance', 0.0),
                'extraction_method': sig.get('extraction_method', 'unknown')  # Preserve extraction_method
            }
            tier_results[tier].append(aggregator_sig)
        
        # Apply signature aggregation if we have multiple tiers or multiple signatures
        aggregated_signatures = signatures  # Default to original signatures
        aggregation_results = None
        
        # Only aggregate if we have multiple tiers or need deduplication
        logger.info(f"Tier results count: {len(tier_results)}, Tiers: {list(tier_results.keys())}")
        if len(tier_results) > 1:
            try:
                logger.info("Applying signature aggregation and ranking")
                aggregation_results = self.signature_aggregator.aggregate_signatures(tier_results)
                aggregated_signatures = aggregation_results['aggregated_signatures']
                logger.info(f"Aggregation reduced {len(signatures)} to {len(aggregated_signatures)} signatures")
            except Exception as e:
                logger.warning(f"Signature aggregation failed: {e}, using original signatures")
                import traceback
                logger.debug(f"Aggregation error traceback: {traceback.format_exc()}")
                aggregated_signatures = signatures
        
        # Apply enhanced cross-language normalization to detected algorithms
        enhanced_signatures = []
        for sig in aggregated_signatures:
            try:
                # Extract algorithm info for normalization
                algo_classification = sig.get('algorithm_classification', {})
                algo_type = algo_classification.get('type', 'unknown') if isinstance(algo_classification, dict) else str(algo_classification)
                
                # Get the code content for this signature (if available)
                evidence = sig.get('evidence', {})
                code_content = None
                
                # Try to get code from various evidence fields
                if isinstance(evidence, dict):
                    if 'code_snippet' in evidence:
                        code_content = evidence['code_snippet']
                    elif 'normalized_representation' in evidence:
                        code_content = evidence['normalized_representation']
                
                # Also try to extract function from file using source location
                if not code_content and 'source_location' in sig:
                    try:
                        src_loc = sig['source_location']
                        file_path = src_loc.get('file_path')
                        start_line = src_loc.get('start_line', 1)
                        end_line = src_loc.get('end_line', start_line)
                        
                        if file_path:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                # Extract function lines (1-indexed to 0-indexed)
                                func_lines = lines[start_line-1:end_line]
                                code_content = ''.join(func_lines)
                    except Exception as e:
                        logger.debug(f"Failed to extract code from source location: {e}")
                
                if code_content:
                    language = baseline_results['file_metadata']['language']
                    
                    # Apply algorithm-specific normalization
                    normalized_signature = self.cross_lang_normalizer.normalize_algorithm_signature(
                        code_content, language, algo_type
                    )
                    
                    # Extract algorithmic features
                    algorithmic_features = self.cross_lang_normalizer.extract_algorithmic_features(
                        code_content, language
                    )
                    
                    # Add enhanced normalization data to signature
                    enhanced_sig = sig.copy()
                    enhanced_sig['cross_language_normalization'] = {
                        'normalized_signature': normalized_signature,
                        'algorithmic_features': algorithmic_features,
                        'language': language,
                        'algorithm_type': algo_type,
                        'original_code_length': len(code_content),
                        'normalized_code_length': len(normalized_signature)
                    }
                    enhanced_signatures.append(enhanced_sig)
                else:
                    enhanced_signatures.append(sig)
                    
            except Exception as e:
                logger.debug(f"Cross-language normalization failed for signature: {e}")
                enhanced_signatures.append(sig)
        
        # Build legacy algorithms field for backward compatibility
        algorithms = []
        for sig in enhanced_signatures:
            if sig.get('extraction_method') == 'traditional':
                # Parse classification back to type/subtype
                classification = sig.get('algorithm_classification', '')
                if isinstance(classification, dict):
                    algo_type = classification.get('type', 'unknown')
                    algo_subtype = classification.get('subtype', 'generic')
                elif '/' in str(classification):
                    algo_type, algo_subtype = str(classification).split('/', 1)
                else:
                    algo_type = str(classification)
                    algo_subtype = 'generic'
                
                algo = {
                    'algorithm_type': algo_type,
                    'algorithm_subtype': algo_subtype,
                    'confidence': sig.get('confidence_score', 0.0),
                    'location': {
                        'start': sig['source_location']['start_line'],
                        'end': sig['source_location']['end_line']
                    },
                    'function_name': sig['source_location'].get('function_name', ''),
                    'transformation_resistance': {
                        'average': sig.get('transformation_resistance', 0.0),
                        'variable_renaming': 0.9,
                        'language_translation': 0.7,
                        'style_changes': 0.8,
                        'framework_adaptation': 0.6
                    },
                    'evidence': sig.get('evidence', {}),
                    'hashes': {
                        'combined_hash': sig.get('signature_hash', ''),
                        'fuzzy': sig.get('fuzzy_hashes', {})
                    },
                    'complexity_metric': sig.get('complexity_metric', 0)
                }
                
                # Add cross-language normalization info if available
                if 'cross_language_normalization' in sig:
                    algo['cross_language_normalization'] = sig['cross_language_normalization']
                
                algorithms.append(algo)
        
        return {
            'file_metadata': baseline_results['file_metadata'],
            'extraction_metadata': {
                'tool_version': __version__,
                'extraction_methods_used': [m.value for m in self.extraction_methods_used],
                'extraction_timestamp': baseline_results['file_metadata']['analysis_timestamp'],
                'language_detected': baseline_results['file_metadata']['language'],
                'fallback_reasons': self.fallback_reasons,
                'configuration_version': '1.0'
            },
            'code_metrics': baseline_results['code_metrics'],
            'signatures': enhanced_signatures,  # Use enhanced signatures
            'aggregated_signatures': aggregated_signatures if aggregation_results else None,
            'signature_aggregation': aggregation_results,  # Full aggregation analysis
            'algorithms': algorithms,  # Legacy field for backward compatibility
            'conflicts': [],  # To be implemented with conflict resolution
            'hashes': baseline_results['hashes'],
            'mathematical_invariants': baseline_results['mathematical_invariants'],
            'control_blocks': baseline_results.get('control_blocks', []),
            'mathematical_properties': baseline_results.get('mathematical_properties', []),
            'cross_language_patterns': baseline_results.get('cross_language_patterns', [])
        }
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        
        if language == 'python':
            import_pattern = r'(?:from\s+[\w\.]+\s+)?import\s+[\w\.,\s]+(?:\s+as\s+\w+)?'
        elif language in ['javascript', 'typescript']:
            import_pattern = r'(?:import|require)\s*\([\'"][\w\./\-]+[\'"]\)|import\s+.*\s+from\s+[\'"][\w\./\-]+[\'"]'
        elif language == 'java':
            import_pattern = r'import\s+[\w\.]+;'
        else:
            return []
        
        import re
        matches = re.findall(import_pattern, content, re.MULTILINE)
        return matches[:50]  # Limit to first 50 imports
    
    def _extract_license_tags(self, content: str) -> List[str]:
        """Extract license information from file headers."""
        license_patterns = [
            r'(?i)license:\s*(\S+)',
            r'(?i)licensed under\s+the\s+(\S+\s+\S+)',
            r'(?i)spdx-license-identifier:\s*(\S+)'
        ]
        
        import re
        licenses = []
        for pattern in license_patterns:
            matches = re.findall(pattern, content[:2000])  # Check first 2000 chars
            licenses.extend(matches)
        
        return list(set(licenses))  # Unique licenses
    
    def _extract_source_headers(self, content: str) -> List[str]:
        """Extract source file headers/comments."""
        lines = content.split('\n')
        headers = []
        
        # Look for header comments in first 20 lines
        for i, line in enumerate(lines[:20]):
            if any(line.strip().startswith(c) for c in ['#', '//', '/*', '*']):
                headers.append(line.strip())
        
        return headers[:10]  # Limit to first 10 header lines
    
    def _count_comment_lines(self, content: str, language: str) -> int:
        """Count comment lines in code."""
        lines = content.split('\n')
        comment_count = 0
        
        if language == 'python':
            comment_chars = ['#']
        elif language in ['javascript', 'typescript', 'java', 'c', 'cpp']:
            comment_chars = ['//', '/*']
        else:
            comment_chars = ['#', '//']
        
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(c) for c in comment_chars):
                comment_count += 1
        
        return comment_count
    
    def _classify_algorithm(self, algo: Dict[str, Any]) -> str:
        """Classify algorithm as known/mutation/unknown/complex_code."""
        confidence = algo.get('confidence', 0.0)
        algo_type = algo.get('algorithm_type', '')
        
        if 'unknown' in algo_type.lower():
            return 'unknown'
        elif confidence > 0.85:
            return 'known'
        elif confidence > 0.7:
            return 'mutation'
        else:
            return 'complex_code'
    
    def _generate_signature_hash(self, normalized_code: str) -> str:
        """Generate a unique signature hash from normalized code."""
        import hashlib
        return hashlib.sha256(normalized_code.encode()).hexdigest()
    
    def cleanup(self):
        """Clean up resources and save state."""
        # Clean up configuration manager
        if hasattr(self, 'config_manager'):
            self.config_manager.cleanup()
        
        # Save unknown algorithm clustering database
        if hasattr(self, 'unknown_clusterer'):
            self.unknown_clusterer._save_database()
            logger.info(f"Saved {len(self.unknown_clusterer.algorithms)} unknown algorithms to database")