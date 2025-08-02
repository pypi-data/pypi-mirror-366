"""
Main analyzer class for CopycatM.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import threading

from .config import AnalysisConfig
from .advanced_config import AdvancedConfigManager
from .exceptions import AnalysisError, UnsupportedLanguageError
from .swhid import SWHIDGenerator
from .three_tier_analyzer import ThreeTierAnalyzer

logger = logging.getLogger(__name__)
from ..analysis.metadata import MetadataExtractor
from ..analysis.complexity import ComplexityAnalyzer
from .. import __version__
from ..analysis.algorithm_detector_enhanced_final import EnhancedAlgorithmDetectorFinal
from ..analysis import ImprovedInvariantExtractor
from ..analysis.directory_structure import DirectoryStructureAnalyzer
from ..analysis.dependency_extractor import DependencyExtractor
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy import FuzzyHasher
from ..hashing.semantic import SemanticHasher
from ..hashing.function_level import FunctionLevelHasher
from ..hashing.comment_stripper import CommentStripper
from ..parsers.tree_sitter_parser_improved import ImprovedTreeSitterParser
from ..utils.file_utils import is_supported_language, is_supported_file
from ..utils.json_utils import format_output
from ..utils.error_handler import (
    handle_file_errors, ErrorRecovery
)
from ..gnn.similarity_detector import GNNSimilarityDetector
from ..analysis.cross_language_normalizer import CrossLanguageNormalizer
from ..analysis.unknown_algorithm_clustering import UnknownAlgorithmClusterer


class CopycatAnalyzer:
    """Main analyzer for detecting AI-generated code derived from copyrighted sources."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize the analyzer with configuration."""
        self.config = config or AnalysisConfig.load_default()
        
        # Initialize advanced configuration manager
        self.config_manager = AdvancedConfigManager()
        self._initialize_config_manager()
        
        # Initialize components
        self.metadata_extractor = MetadataExtractor()
        self.complexity_analyzer = ComplexityAnalyzer()
        # Use enhanced algorithm detector for better accuracy and reduced false positives
        self.algorithm_detector = EnhancedAlgorithmDetectorFinal(self.config)
        self.invariant_extractor = ImprovedInvariantExtractor()
        
        # Initialize hashers
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = FuzzyHasher(self.config.tlsh_threshold)
        # Use semantic hasher for better algorithm differentiation
        self.semantic_hasher = SemanticHasher(num_perm=128, lsh_bands=self.config.lsh_bands)
        # Initialize function-level hasher
        self.function_hasher = FunctionLevelHasher()
        # Initialize comment stripper
        self.comment_stripper = CommentStripper()
        
        # Initialize parser - use improved version with better fallback
        self.parser = ImprovedTreeSitterParser()
        
        # Initialize GNN similarity detector
        self.gnn_detector = GNNSimilarityDetector(use_pytorch=self.config.use_gnn_pytorch)
        
        # Initialize directory structure analyzer
        self.dir_analyzer = DirectoryStructureAnalyzer()
        self._directory_structure = None  # Cache for directory analysis
        
        # Initialize dependency extractor
        self.dependency_extractor = DependencyExtractor()
        
        # Initialize cross-language normalizer
        self.cross_lang_normalizer = CrossLanguageNormalizer()
        
        # Initialize unknown algorithm clusterer
        self.unknown_clusterer = UnknownAlgorithmClusterer()
        
        # Initialize enhanced three-tier analyzer for enhanced features
        self.three_tier_analyzer = ThreeTierAnalyzer(self.config)
        
        # Performance tracking
        self.analysis_times: Dict[str, float] = {}
        self._lock = threading.Lock()  # For thread-safe operations
    
    def _initialize_config_manager(self):
        """Initialize advanced configuration manager with multiple sources."""
        # Load from environment variables
        self.config_manager.load_from_env()
        
        # Load from config files
        config_files = [
            Path.home() / '.copycatm' / 'config.json',  # User config
            Path.cwd() / 'copycatm.json',  # Project config
            Path.cwd() / '.copycatm.json',  # Hidden project config
        ]
        
        for config_file in config_files:
            if config_file.exists():
                self.config_manager.load_from_file(config_file)
        
        # Override with existing config values
        config_dict = self.config.to_dict()
        self.config_manager.load_from_cli(config_dict)
        
        # Register callback for dynamic config updates
        self.config_manager.register_change_callback(self._on_config_change)
    
    def _on_config_change(self, key: str, value: Any):
        """Handle configuration changes dynamically."""
        logger.info(f"Configuration changed: {key} = {value}")
        
        # Update relevant components
        if key.startswith('hashing.'):
            self._update_hashing_config(key, value)
        elif key.startswith('analysis.'):
            self._update_analysis_config(key, value)
    
    def _update_hashing_config(self, key: str, value: Any):
        """Update hashing configuration."""
        if key == 'hashing.tlsh_threshold':
            self.fuzzy_hasher = FuzzyHasher(value)
        elif key == 'hashing.lsh_bands':
            self.semantic_hasher = SemanticHasher(num_perm=128, lsh_bands=value)
    
    def _update_analysis_config(self, key: str, value: Any):
        """Update analysis configuration."""
        if key == 'analysis.complexity_threshold':
            self.config.complexity_threshold = value
        elif key == 'analysis.min_lines':
            self.config.min_lines = value
    
    @handle_file_errors
    def analyze_file_enhanced(self, file_path: str, force_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze file using enhanced three-tier analyzer with cross-language normalization
        and signature aggregation.
        
        Args:
            file_path: Path to the file to analyze
            force_language: Optional language override
            
        Returns:
            Enhanced analysis results with cross-language normalization and signature aggregation
        """
        logger.info("Using enhanced three-tier analyzer")
        return self.three_tier_analyzer.analyze_file(file_path, force_language)
    
    @handle_file_errors
    def analyze_file(self, file_path: str, force_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze single file and return results.
        
        Args:
            file_path: Path to the file to analyze
            force_language: Optional language override. If provided, this language will be used
                          instead of auto-detecting from file extension. Useful for files with
                          non-standard extensions or when you want to analyze code as a 
                          different language.
                          
        Returns:
            Dictionary containing analysis results including metadata, algorithms, 
            invariants, and hashes
            
        Raises:
            AnalysisError: If analysis fails
            UnsupportedLanguageError: If the language is not supported
            
        Examples:
            # Auto-detect language from extension
            result = analyzer.analyze_file("script.py")
            
            # Force specific language
            result = analyzer.analyze_file("script.txt", force_language="python")
        """
        start_time = time.time()
        
        try:
            # Stage 0: Metadata extraction
            metadata = self.metadata_extractor.extract(file_path)
            
            # Override language if forced
            if force_language:
                metadata["language"] = force_language
                # Update MIME type to match forced language
                metadata["mime_type"] = f"text/x-{force_language}"
            
            # Check if file is supported
            if not is_supported_language(metadata["language"]):
                raise UnsupportedLanguageError(f"Language {metadata['language']} not supported")
            
            # Stage 1: Parse code
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ast_tree = self.parser.parse(code, metadata["language"])
            
            # Stage 1.5: Cross-language normalization
            normalized_code = self.cross_lang_normalizer.normalize_code(code, metadata["language"])
            normalized_patterns = self.cross_lang_normalizer.extract_normalized_patterns(code, metadata["language"])
            
            # Stage 2: Complexity analysis
            complexity_results = self.complexity_analyzer.analyze(ast_tree, metadata["language"])
            
            # Stage 3: Algorithm detection
            # Note: We check function size in the detector, not file size
            # Pass line count for unknown algorithm detection (50+ line files)
            # Set content on detector for function body extraction
            self.algorithm_detector.content = code
            algorithms = self.algorithm_detector.detect(ast_tree, metadata["language"], 
                                                       metadata.get("line_count", 0))
            
            # Stage 3.5: Unknown algorithm clustering
            unknown_algorithms = [algo for algo in algorithms if algo.get('algorithm_type') == 'unknown_complex_algorithm']
            clustered_patterns = []
            
            if unknown_algorithms:
                # Add to clusterer and check for patterns
                for algo in unknown_algorithms:
                    algo_data = {
                        'file_path': file_path,
                        'location': {'start': algo.get('start_line', 0), 'end': algo.get('end_line', 0)},
                        'normalized_code': normalized_code,
                        'complexity_metrics': algo.get('evidence', {}).get('complexity_metrics', {}),
                        'confidence': algo.get('confidence', 0.0)
                    }
                    
                    # Add to clusterer
                    self.unknown_clusterer.add_unknown_algorithm(algo_data)
                    
                    # Check if it matches any learned pattern
                    match = self.unknown_clusterer.match_algorithm(algo_data)
                    if match:
                        # Update algorithm with learned pattern info
                        algo['learned_pattern'] = match
                        algo['algorithm_type'] = 'learned_algorithm_pattern'
                        algo['subtype'] = f"cluster_{match['cluster_id']}"
                
                # Trigger clustering if enough algorithms
                if len(self.unknown_clusterer.algorithms) >= 10:
                    self.unknown_clusterer.cluster_algorithms()
                    clustered_patterns = self.unknown_clusterer.get_cluster_patterns()
            
            # Stage 4: Invariant extraction (always extract invariants)
            invariants = self.invariant_extractor.extract(ast_tree, metadata["language"])
            
            # Stage 5: Dependency extraction
            dependencies = self.dependency_extractor.extract_dependencies(code, metadata["language"], ast_tree)
            dependency_fingerprint = self.dependency_extractor.generate_dependency_fingerprint(dependencies)
            
            # Stage 6: Hash generation (use normalized code for better cross-language matching)
            hashes = self._generate_hashes(code, ast_tree, metadata["language"], normalized_code)
            
            # Stage 7: GNN analysis
            gnn_analysis = self._perform_gnn_analysis(ast_tree, metadata["language"])
            
            # Stage 8: Build output
            result = self._build_output(
                metadata, complexity_results, algorithms, invariants, hashes, gnn_analysis,
                dependencies, dependency_fingerprint, normalized_patterns, clustered_patterns
            )
            
            # Add directory context if available
            if self._directory_structure:
                result["directory_context"] = {
                    "project_type": self._directory_structure.get("signatures", {}).get("project_type"),
                    "language_confidence": self._directory_structure.get("signatures", {}).get("language_confidence", {})
                }
            
            self.analysis_times[file_path] = time.time() - start_time
            return result
            
        except Exception as e:
            raise AnalysisError(f"Failed to analyze {file_path}: {str(e)}") from e
    
    def analyze_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Analyze all supported files in directory and directory structure."""
        directory = Path(directory_path)
        
        # Analyze directory structure first
        try:
            self._directory_structure = self.dir_analyzer.analyze_directory(str(directory))
        except Exception as e:
            logger.warning(f"Failed to analyze directory structure: {e}")
            self._directory_structure = None
        
        if recursive:
            files = directory.rglob("*")
        else:
            files = directory.glob("*")
        
        supported_files = [
            f for f in files 
            if f.is_file() and is_supported_file(f.name)
        ]
        
        # Analyze files
        if hasattr(self.config, 'parallel_workers') and self.config.parallel_workers and len(supported_files) > 1:
            file_results = self._analyze_files_parallel(supported_files)
        else:
            file_results = self._analyze_files_sequential(supported_files)
        
        # Return combined results
        return {
            "directory_path": str(directory),
            "directory_structure": self._directory_structure,
            "file_results": file_results,
            "summary": {
                "total_files_analyzed": len(file_results),
                "total_files_found": len(supported_files),
                "has_directory_structure": self._directory_structure is not None
            }
        }
    
    def _analyze_files_sequential(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Analyze files sequentially with error recovery."""
        def analyze_single(file_path):
            return self.analyze_file(str(file_path))
        
        # Use partial results to continue on error
        results, errors = ErrorRecovery.partial_results(
            analyze_single, 
            file_paths,
            continue_on_error=True
        )
        
        if errors:
            logger.warning(f"Failed to analyze {len(errors)} files out of {len(file_paths)}")
            for error in errors[:5]:  # Log first 5 errors
                logger.error(f"Error analyzing {error['item']}: {error['error']}")
        
        return results
    
    def _analyze_files_parallel(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Analyze files in parallel using thread or process pools."""
        results = []
        max_workers = min(self.config.parallel_workers or cpu_count(), len(file_paths))
        
        # Use ThreadPoolExecutor for I/O bound operations
        # ProcessPoolExecutor would be better for CPU-bound work but requires more setup
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file analysis tasks
            future_to_file = {
                executor.submit(self._analyze_single_file_safe, str(file_path)): file_path 
                for file_path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:  # Only add successful results
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _analyze_single_file_safe(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Thread-safe wrapper for analyze_file."""
        try:
            return self.analyze_file(file_path)
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_batch(self, file_paths: List[str], chunk_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze a batch of files with optional chunking for memory management."""
        if not file_paths:
            return []
        
        chunk_size = chunk_size or getattr(self.config, 'chunk_size', 100)
        all_results = []
        
        # Process files in chunks to manage memory
        for i in range(0, len(file_paths), chunk_size):
            chunk = file_paths[i:i + chunk_size]
            logger.info(f"Processing chunk {i//chunk_size + 1}/{(len(file_paths) + chunk_size - 1)//chunk_size} ({len(chunk)} files)")
            
            # Convert strings to Path objects
            chunk_paths = [Path(fp) for fp in chunk]
            
            # Analyze chunk
            if hasattr(self.config, 'parallel_workers') and self.config.parallel_workers and len(chunk) > 1:
                chunk_results = self._analyze_files_parallel(chunk_paths)
            else:
                chunk_results = self._analyze_files_sequential(chunk_paths)
            
            all_results.extend(chunk_results)
            
            # Optional: Force garbage collection between chunks
            if i + chunk_size < len(file_paths):  # Not the last chunk
                import gc
                gc.collect()
        
        return all_results
    
    def analyze_code(self, code: str, language: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze code string directly."""
        # Create temporary metadata
        metadata = {
            "file_name": file_path or "input_code",
            "relative_path": file_path or "input_code",
            "absolute_path": file_path or "input_code",
            "file_size": len(code.encode('utf-8')),
            "content_checksum": self.direct_hasher.sha256(code),
            "file_hash": self.direct_hasher.md5(code),
            "mime_type": f"text/x-{language}",
            "language": language,
            "encoding": "utf-8",
            "line_count": len(code.splitlines()),
            "is_source_code": True,
            "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        # Parse code
        ast_tree = self.parser.parse(code, language)
        
        # Cross-language normalization
        normalized_code = self.cross_lang_normalizer.normalize_code(code, language)
        normalized_patterns = self.cross_lang_normalizer.extract_normalized_patterns(code, language)
        
        # Analyze
        complexity_results = self.complexity_analyzer.analyze(ast_tree, language)
        
        # Algorithm detection (check function size in detector, not file size)
        # Pass line count for unknown algorithm detection (50+ line files)
        # Set content on detector for function body extraction
        self.algorithm_detector.content = code
        algorithms = self.algorithm_detector.detect(ast_tree, language, 
                                                   metadata.get("line_count", 0))
        
        # Process unknown algorithms
        unknown_algorithms = [algo for algo in algorithms if algo.get('algorithm_type') == 'unknown_complex_algorithm']
        clustered_patterns = []
        
        if unknown_algorithms:
            for algo in unknown_algorithms:
                algo_data = {
                    'file_path': file_path or "input_code",
                    'location': {'start': algo.get('start_line', 0), 'end': algo.get('end_line', 0)},
                    'normalized_code': normalized_code,
                    'complexity_metrics': algo.get('evidence', {}).get('complexity_metrics', {}),
                    'confidence': algo.get('confidence', 0.0)
                }
                
                # Add to clusterer
                self.unknown_clusterer.add_unknown_algorithm(algo_data)
                
                # Check if it matches any learned pattern
                match = self.unknown_clusterer.match_algorithm(algo_data)
                if match:
                    algo['learned_pattern'] = match
                    algo['algorithm_type'] = 'learned_algorithm_pattern'
                    algo['subtype'] = f"cluster_{match['cluster_id']}"
        
        # Always extract invariants
        invariants = self.invariant_extractor.extract(ast_tree, language)
        
        # Extract dependencies
        dependencies = self.dependency_extractor.extract_dependencies(code, language, ast_tree)
        dependency_fingerprint = self.dependency_extractor.generate_dependency_fingerprint(dependencies)
        
        hashes = self._generate_hashes(code, ast_tree, language, normalized_code)
        
        # GNN analysis
        gnn_analysis = self._perform_gnn_analysis(ast_tree, language)
        
        return self._build_output(metadata, complexity_results, algorithms, invariants, hashes, gnn_analysis,
                                dependencies, dependency_fingerprint, normalized_patterns, clustered_patterns)
    
    def _generate_hashes(self, code: str, ast_tree: Any, language: str, normalized_code: str = None) -> Dict[str, Any]:
        """Generate all types of hashes for the code."""
        hashes = {
            "direct": {},
            "fuzzy": {},
            "semantic": {},
            "function_level": {},
            "normalized": {}
        }
        
        # Direct hashes
        if "sha256" in self.config.hash_algorithms:
            hashes["direct"]["sha256"] = self.direct_hasher.sha256(code)
        if "md5" in self.config.hash_algorithms:
            hashes["direct"]["md5"] = self.direct_hasher.md5(code)
        
        # Fuzzy hashes
        if "tlsh" in self.config.hash_algorithms:
            tlsh_hash = self.fuzzy_hasher.tlsh(code)
            hashes["fuzzy"]["tlsh"] = tlsh_hash
            hashes["fuzzy"]["tlsh_threshold"] = self.config.tlsh_threshold
        
        # Semantic hashes
        if "minhash" in self.config.hash_algorithms:
            minhash = self.semantic_hasher.minhash(ast_tree)
            hashes["semantic"]["minhash"] = minhash
            hashes["semantic"]["lsh_bands"] = self.config.lsh_bands
        
        if "simhash" in self.config.hash_algorithms:
            simhash = self.semantic_hasher.simhash(code)
            hashes["semantic"]["simhash"] = simhash
        
        # Comment-stripped hash
        if "tlsh" in self.config.hash_algorithms:
            comment_free_hash = self.comment_stripper.generate_comment_free_hash(
                code, language, self.fuzzy_hasher
            )
            hashes["fuzzy"]["comment_free_tlsh"] = comment_free_hash
            
            # Also generate comment statistics
            _, comment_stats = self.comment_stripper.strip_comments(code, language)
            hashes["fuzzy"]["comment_stats"] = comment_stats
        
        # Normalized hashes (if normalized code provided)
        if normalized_code:
            hashes["normalized"]["sha256"] = self.direct_hasher.sha256(normalized_code)
            hashes["normalized"]["tlsh"] = self.fuzzy_hasher.tlsh(normalized_code)
            hashes["normalized"]["simhash"] = self.semantic_hasher.simhash(normalized_code)
        
        # Function-level hashes
        try:
            # Extract functions based on language
            if language == "python":
                # Parse Python code with ast module for accurate extraction
                try:
                    import ast
                    python_ast = ast.parse(code)
                    functions = self.function_hasher.extract_functions_from_ast(python_ast, code)
                except:
                    # Fallback to text extraction
                    functions = self.function_hasher.extract_functions_from_text(code, language)
            else:
                # Use text extraction for other languages
                functions = self.function_hasher.extract_functions_from_text(code, language)
            
            # Generate hashes for functions
            hashed_functions = self.function_hasher.hash_functions(functions)
            
            # Generate function signatures
            function_signatures = self.function_hasher.generate_function_signatures(hashed_functions)
            
            hashes["function_level"] = {
                "functions": [
                    {
                        "name": f["name"],
                        "tlsh": f["tlsh"],
                        "normalized_tlsh": f["normalized_tlsh"],
                        "size": f["size"],
                        "lines": f["line_count"],
                        "start_line": f["start_line"]
                    }
                    for f in hashed_functions
                ],
                "signatures": function_signatures,
                "total_functions": len(hashed_functions)
            }
        except Exception as e:
            # Log error but don't fail the analysis
            logger.debug(f"Function-level hashing failed: {e}")
            hashes["function_level"] = {
                "functions": [],
                "signatures": {},
                "total_functions": 0,
                "error": str(e)
            }
        
        return hashes
    
    def _generate_swhids(self, metadata: Dict, algorithms: List[Dict]) -> List[Dict[str, Any]]:
        """Generate Software Heritage IDs for the analyzed content."""
        swhids = []
        
        # Check if SWHID generation is enabled
        if not self.config.enable_swhid:
            return swhids
        
        try:
            file_path = metadata.get("absolute_path")
            if not file_path or not os.path.exists(file_path):
                return swhids
            
            # Create analysis result structure for SWHID generation
            analysis_result = {
                "file_path": file_path,
                "metadata": metadata,
                "algorithms": algorithms
            }
            
            # Generate SWHIDs with configuration options
            generated_swhids = SWHIDGenerator.from_analysis_result(
                analysis_result,
                enable_swhid=self.config.enable_swhid,
                include_directory=self.config.swhid_include_directory
            )
            
            for swhid in generated_swhids:
                swhid_info = {
                    "swhid": str(swhid),
                    "core_swhid": swhid.core_swhid,
                    "object_type": swhid.object_type,
                    "object_id": swhid.object_id,
                    "qualifiers": swhid.qualifiers,
                    "resolver_url": f"https://archive.softwareheritage.org/{swhid}",
                    "api_url": f"https://archive.softwareheritage.org/api/1/resolve/{swhid}/"
                }
                swhids.append(swhid_info)
                
        except Exception as e:
            logger.warning(f"Failed to generate SWHIDs: {e}")
            
        return swhids

    def _build_output(self, metadata: Dict, complexity_results: Dict, 
                     algorithms: List[Dict], invariants: List[Dict], 
                     hashes: Dict, gnn_analysis: Dict,
                     dependencies: Dict = None, dependency_fingerprint: Dict = None,
                     normalized_patterns: List[Dict] = None, clustered_patterns: List[Dict] = None) -> Dict[str, Any]:
        """Build the complete output structure."""
        
        # Generate SWHIDs if enabled
        swhids = self._generate_swhids(metadata, algorithms)
        
        output = {
            "copycatm_version": __version__,
            "analysis_config": self.config.to_dict(),
            "file_metadata": metadata,
            "file_properties": {
                "has_invariants": len(invariants) > 0,
                "has_signatures": len(algorithms) > 0,
                "transformation_resistant": self._calculate_transformation_resistance(algorithms, invariants),
                "mathematical_complexity": complexity_results.get("average_complexity", 0),
                "has_property_distribution": len(algorithms) > 1,
                "algorithm_count": len(algorithms)
            },
            "algorithms": algorithms,
            "mathematical_invariants": invariants,
            "hashes": hashes,
            "dependencies": dependencies or {},
            "dependency_fingerprint": dependency_fingerprint or {},
            "gnn_analysis": gnn_analysis,
            "cross_language_patterns": normalized_patterns or [],
            "learned_patterns": clustered_patterns or [],
            "analysis_summary": {
                "total_algorithms": len(algorithms),
                "total_invariants": len(invariants),
                "total_normalized_patterns": len(normalized_patterns) if normalized_patterns else 0,
                "total_learned_patterns": len(clustered_patterns) if clustered_patterns else 0,
                "highest_complexity": complexity_results.get("max_complexity", 0),
                "average_confidence": self._calculate_average_confidence(algorithms, invariants),
                "processing_time_ms": int(self.analysis_times.get(metadata["absolute_path"], 0) * 1000)
            }
        }
        
        # Add SWHIDs if enabled
        if swhids:
            output["software_heritage_ids"] = swhids
        
        return format_output(output)
    
    def _calculate_transformation_resistance(self, algorithms: List[Dict], 
                                          invariants: List[Dict]) -> float:
        """Calculate overall transformation resistance score."""
        if not algorithms and not invariants:
            return 0.0
        
        total_resistance = 0.0
        count = 0
        
        for algo in algorithms:
            resistance = algo.get("transformation_resistance", {})
            if isinstance(resistance, dict):
                # Use the overall score if available, otherwise calculate average
                if 'overall' in resistance:
                    avg_resistance = resistance['overall']
                else:
                    # Calculate average of numeric values only (skip 'metrics' dict)
                    numeric_values = [v for k, v in resistance.items() 
                                    if isinstance(v, (int, float)) and k != 'overall']
                    avg_resistance = sum(numeric_values) / len(numeric_values) if numeric_values else 0.0
            else:
                avg_resistance = 0.0
            total_resistance += avg_resistance
            count += 1
        
        for inv in invariants:
            resistance = inv.get("transformation_resistance", {})
            if isinstance(resistance, dict):
                # Calculate average of numeric values only
                numeric_values = [v for k, v in resistance.items() if isinstance(v, (int, float))]
                avg_resistance = sum(numeric_values) / len(numeric_values) if numeric_values else 0.0
            else:
                avg_resistance = 0.0
            total_resistance += avg_resistance
            count += 1
        
        return total_resistance / count if count > 0 else 0.0
    
    def _perform_gnn_analysis(self, ast_tree: Any, language: str) -> Dict[str, Any]:
        """Perform GNN-based analysis on the AST."""
        try:
            # Build graph from AST
            graph = self.gnn_detector.graph_builder.build_graph_from_ast(ast_tree, language)
            
            # Extract graph features
            graph_features = self.gnn_detector.graph_builder.get_graph_features(graph)
            
            # Generate similarity hash
            similarity_hash = self.gnn_detector.get_similarity_hash(graph)
            
            return {
                "graph_features": graph_features,
                "similarity_hash": similarity_hash,
                "num_nodes": graph.number_of_nodes(),
                "num_edges": graph.number_of_edges(),
                "model_type": self.gnn_detector.gnn_model.__class__.__name__
            }
        except Exception as e:
            return {
                "error": f"GNN analysis failed: {str(e)}",
                "graph_features": {},
                "similarity_hash": "",
                "num_nodes": 0,
                "num_edges": 0,
                "model_type": "error"
            }
    
    def _calculate_average_confidence(self, algorithms: List[Dict], 
                                    invariants: List[Dict]) -> float:
        """Calculate average confidence score."""
        confidences = []
        
        for algo in algorithms:
            confidences.append(algo.get("confidence", 0.0))
        
        for inv in invariants:
            confidences.append(inv.get("confidence", 0.0))
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def cleanup(self):
        """Clean up resources and save state."""
        # Clean up configuration manager
        if hasattr(self, 'config_manager'):
            self.config_manager.cleanup()
        
        # Save unknown algorithm clustering database
        if hasattr(self, 'unknown_clusterer'):
            self.unknown_clusterer._save_database()
            logger.info(f"Saved {len(self.unknown_clusterer.algorithms)} unknown algorithms to database") 