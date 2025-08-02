"""
Unknown algorithm clustering for pattern learning and similarity grouping.

This module clusters unknown algorithms to identify patterns and build
a database of learned algorithm signatures.
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime

from ..utils.optional_dependencies import sklearn_dep
# Try to import numpy (needed for clustering)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create minimal numpy fallback
    class np:
        @staticmethod
        def array(x):
            return x
        @staticmethod
        def full(shape, fill_value):
            return [fill_value] * shape
        @staticmethod
        def mean(x, axis=None):
            if axis is None:
                return sum(x) / len(x) if x else 0
            return x
        @staticmethod
        def std(x):
            return 0
        @staticmethod
        def min(x):
            return min(x) if x else 0
        @staticmethod
        def max(x):
            return max(x) if x else 0

# Try to import sklearn (optional for clustering)
try:
    from sklearn.cluster import DBSCAN, AgglomerativeClustering
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    # Warning is handled by optional_dependencies module
    
    # Create dummy classes
    class StandardScaler:
        def fit_transform(self, X):
            return X
        def transform(self, X):
            return X
    
    def cosine_similarity(X, Y):
        # Simple cosine similarity fallback
        return np.ones((X.shape[0], Y.shape[0]))

import pickle
import threading

from ..hashing import SemanticHasher

logger = logging.getLogger(__name__)


@dataclass
class UnknownAlgorithm:
    """Represents an unknown algorithm with its features."""
    id: str
    source_file: str
    location: Dict[str, int]
    complexity_metrics: Dict[str, float]
    structural_features: Dict[str, Any]
    semantic_hash: str
    control_flow_hash: str
    normalized_code: str
    timestamp: datetime = field(default_factory=datetime.now)
    cluster_id: Optional[int] = None
    confidence: float = 0.0
    
    def to_feature_vector(self) -> np.ndarray:
        """Convert algorithm to numerical feature vector."""
        features = []
        
        # Complexity metrics
        features.extend([
            self.complexity_metrics.get('cyclomatic_complexity', 0),
            self.complexity_metrics.get('lines_of_code', 0),
            self.complexity_metrics.get('nesting_depth', 0),
            self.complexity_metrics.get('parameter_count', 0),
            self.complexity_metrics.get('variable_count', 0)
        ])
        
        # Structural features
        features.extend([
            self.structural_features.get('has_loops', 0),
            self.structural_features.get('has_conditionals', 0),
            self.structural_features.get('has_recursion', 0),
            self.structural_features.get('has_try_catch', 0),
            self.structural_features.get('function_calls', 0),
            self.structural_features.get('return_statements', 0)
        ])
        
        # Hash-based features (convert to numeric)
        features.extend([
            int(self.semantic_hash[:8], 16) / (16**8),  # Normalize to [0,1]
            int(self.control_flow_hash[:8], 16) / (16**8)
        ])
        
        return np.array(features)


@dataclass
class AlgorithmCluster:
    """Represents a cluster of similar unknown algorithms."""
    id: int
    algorithms: List[UnknownAlgorithm] = field(default_factory=list)
    centroid: Optional[np.ndarray] = None
    pattern_signature: Optional[str] = None
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_signature(self) -> None:
        """Update cluster signature based on member algorithms."""
        if not self.algorithms:
            return
        
        # Combine normalized codes to create pattern
        combined_patterns = []
        for algo in self.algorithms[:5]:  # Use top 5 for signature
            combined_patterns.append(algo.normalized_code)
        
        # Create signature hash
        pattern_text = '\n'.join(combined_patterns)
        self.pattern_signature = hashlib.sha256(pattern_text.encode()).hexdigest()[:16]
        
        # Update confidence based on cluster size and similarity
        self.confidence = min(0.9, 0.5 + (len(self.algorithms) / 100))
        self.last_updated = datetime.now()


class UnknownAlgorithmClusterer:
    """
    Clusters unknown algorithms to identify patterns and learn new algorithm types.
    
    Features:
    - DBSCAN and hierarchical clustering
    - Pattern learning from clusters
    - Persistent storage of learned patterns
    - Confidence scoring
    - Incremental learning
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize clusterer with optional database path."""
        self.db_path = db_path or Path.home() / '.copycatm' / 'unknown_algorithms.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.algorithms: Dict[str, UnknownAlgorithm] = {}
        self.clusters: Dict[int, AlgorithmCluster] = {}
        self.feature_scaler = StandardScaler()
        self.semantic_hasher = SemanticHasher()
        self._lock = threading.RLock()
        
        # Clustering parameters
        self.min_cluster_size = 3
        self.similarity_threshold = 0.75
        
        # Load existing database
        self._load_database()
    
    def add_unknown_algorithm(self, algorithm_data: Dict[str, Any]) -> str:
        """
        Add an unknown algorithm for clustering.
        
        Args:
            algorithm_data: Algorithm information including metrics and code
            
        Returns:
            Algorithm ID
        """
        with self._lock:
            # Create UnknownAlgorithm instance
            algo_id = self._generate_algorithm_id(algorithm_data)
            
            # Extract features
            complexity_metrics = self._extract_complexity_metrics(algorithm_data)
            structural_features = self._extract_structural_features(algorithm_data)
            
            # Generate hashes
            normalized_code = algorithm_data.get('normalized_code', '')
            semantic_hash = self.semantic_hasher.generate_simhash(normalized_code)
            control_flow_hash = self._generate_control_flow_hash(algorithm_data)
            
            # Create algorithm object
            algorithm = UnknownAlgorithm(
                id=algo_id,
                source_file=algorithm_data.get('file_path', ''),
                location=algorithm_data.get('location', {}),
                complexity_metrics=complexity_metrics,
                structural_features=structural_features,
                semantic_hash=semantic_hash,
                control_flow_hash=control_flow_hash,
                normalized_code=normalized_code,
                confidence=algorithm_data.get('confidence', 0.0)
            )
            
            self.algorithms[algo_id] = algorithm
            
            # Trigger incremental clustering if enough new algorithms
            if len(self.algorithms) % 10 == 0:
                self._incremental_cluster()
            
            return algo_id
    
    def cluster_algorithms(self, method: str = 'dbscan') -> Dict[int, List[str]]:
        """
        Cluster all unknown algorithms.
        
        Args:
            method: Clustering method ('dbscan' or 'hierarchical')
            
        Returns:
            Mapping of cluster IDs to algorithm IDs
        """
        with self._lock:
            if len(self.algorithms) < self.min_cluster_size:
                logger.info(f"Not enough algorithms for clustering: {len(self.algorithms)}")
                return {}
            
            # Prepare feature matrix
            algo_ids = list(self.algorithms.keys())
            features = np.array([
                self.algorithms[aid].to_feature_vector() for aid in algo_ids
            ])
            
            # Scale features
            features_scaled = self.feature_scaler.fit_transform(features)
            
            # Perform clustering
            if method == 'dbscan':
                clusters = self._cluster_dbscan(features_scaled)
            else:
                clusters = self._cluster_hierarchical(features_scaled)
            
            # Update algorithm cluster assignments
            cluster_map = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id != -1:  # -1 is noise in DBSCAN
                    algo_id = algo_ids[i]
                    self.algorithms[algo_id].cluster_id = cluster_id
                    
                    if cluster_id not in cluster_map:
                        cluster_map[cluster_id] = []
                    cluster_map[cluster_id].append(algo_id)
            
            # Create or update cluster objects
            self._update_clusters(cluster_map, features_scaled, algo_ids, clusters)
            
            # Save to database
            self._save_database()
            
            return cluster_map
    
    def _cluster_dbscan(self, features: np.ndarray) -> np.ndarray:
        """Perform DBSCAN clustering."""
        if not sklearn_dep.available:
            # Return all as noise (-1) if sklearn not available
            return np.full(features.shape[0], -1)
            
        # Calculate pairwise similarities
        similarities = cosine_similarity(features)
        
        # Convert to distances
        distances = 1 - similarities
        
        # DBSCAN with precomputed distances
        clusterer = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=self.min_cluster_size,
            metric='precomputed'
        )
        
        return clusterer.fit_predict(distances)
    
    def _cluster_hierarchical(self, features: np.ndarray) -> np.ndarray:
        """Perform hierarchical clustering."""
        if not sklearn_dep.available:
            # Return all as noise (-1) if sklearn not available
            return np.full(features.shape[0], -1)
            
        # Agglomerative clustering
        clusterer = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1 - self.similarity_threshold,
            linkage='average'
        )
        
        return clusterer.fit_predict(features)
    
    def _update_clusters(self, cluster_map: Dict[int, List[str]], 
                        features: np.ndarray, algo_ids: List[str], 
                        cluster_labels: np.ndarray) -> None:
        """Update cluster objects with new assignments."""
        for cluster_id, algorithm_ids in cluster_map.items():
            if cluster_id not in self.clusters:
                self.clusters[cluster_id] = AlgorithmCluster(id=cluster_id)
            
            cluster = self.clusters[cluster_id]
            cluster.algorithms = [self.algorithms[aid] for aid in algorithm_ids]
            
            # Calculate centroid
            cluster_indices = [algo_ids.index(aid) for aid in algorithm_ids]
            cluster.centroid = np.mean(features[cluster_indices], axis=0)
            
            # Update signature
            cluster.update_signature()
    
    def _incremental_cluster(self) -> None:
        """Perform incremental clustering for new algorithms."""
        # Get unclustered algorithms
        unclustered = [
            algo for algo in self.algorithms.values() 
            if algo.cluster_id is None
        ]
        
        if len(unclustered) < self.min_cluster_size:
            return
        
        # Try to assign to existing clusters first
        for algo in unclustered:
            best_cluster = self._find_best_cluster(algo)
            if best_cluster is not None:
                algo.cluster_id = best_cluster
                self.clusters[best_cluster].algorithms.append(algo)
                self.clusters[best_cluster].update_signature()
        
        # Cluster remaining unclustered algorithms
        still_unclustered = [
            algo.id for algo in self.algorithms.values() 
            if algo.cluster_id is None
        ]
        
        if len(still_unclustered) >= self.min_cluster_size:
            self.cluster_algorithms()
    
    def _find_best_cluster(self, algorithm: UnknownAlgorithm) -> Optional[int]:
        """Find best existing cluster for an algorithm."""
        if not self.clusters:
            return None
        
        algo_features = algorithm.to_feature_vector().reshape(1, -1)
        algo_features_scaled = self.feature_scaler.transform(algo_features)
        
        best_cluster = None
        best_similarity = 0.0
        
        for cluster_id, cluster in self.clusters.items():
            if cluster.centroid is not None:
                similarity = cosine_similarity(
                    algo_features_scaled, 
                    cluster.centroid.reshape(1, -1)
                )[0, 0]
                
                if similarity > self.similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_cluster = cluster_id
        
        return best_cluster
    
    def get_cluster_patterns(self, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """
        Get learned patterns from clusters.
        
        Returns:
            List of pattern dictionaries with signature and examples
        """
        patterns = []
        
        with self._lock:
            for cluster in self.clusters.values():
                if cluster.confidence >= min_confidence:
                    # Extract common patterns
                    common_patterns = self._extract_common_patterns(cluster)
                    
                    patterns.append({
                        'cluster_id': cluster.id,
                        'signature': cluster.pattern_signature,
                        'confidence': cluster.confidence,
                        'algorithm_count': len(cluster.algorithms),
                        'common_patterns': common_patterns,
                        'example_files': [
                            algo.source_file for algo in cluster.algorithms[:3]
                        ],
                        'complexity_range': self._get_complexity_range(cluster),
                        'created_at': cluster.created_at.isoformat(),
                        'last_updated': cluster.last_updated.isoformat()
                    })
        
        return patterns
    
    def _extract_common_patterns(self, cluster: AlgorithmCluster) -> Dict[str, Any]:
        """Extract common patterns from cluster algorithms."""
        patterns = {
            'structural': {},
            'complexity': {},
            'normalized_patterns': []
        }
        
        # Analyze structural features
        structural_counts = {}
        for algo in cluster.algorithms:
            for feature, value in algo.structural_features.items():
                if value:
                    structural_counts[feature] = structural_counts.get(feature, 0) + 1
        
        # Features present in >70% of algorithms
        threshold = len(cluster.algorithms) * 0.7
        patterns['structural'] = {
            feature: count / len(cluster.algorithms)
            for feature, count in structural_counts.items()
            if count >= threshold
        }
        
        # Complexity statistics
        complexity_values = {
            metric: [algo.complexity_metrics.get(metric, 0) for algo in cluster.algorithms]
            for metric in ['cyclomatic_complexity', 'lines_of_code', 'nesting_depth']
        }
        
        patterns['complexity'] = {
            metric: {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
            for metric, values in complexity_values.items()
        }
        
        # Common normalized code patterns
        normalized_codes = [algo.normalized_code for algo in cluster.algorithms]
        patterns['normalized_patterns'] = self._find_common_subsequences(normalized_codes)
        
        return patterns
    
    def _find_common_subsequences(self, codes: List[str], min_length: int = 3) -> List[str]:
        """Find common subsequences in normalized codes."""
        if not codes:
            return []
        
        # Split codes into tokens
        tokenized = [code.split('\n') for code in codes]
        
        # Find common sequences
        common_sequences = []
        reference = tokenized[0]
        
        for i in range(len(reference)):
            for j in range(i + min_length, len(reference) + 1):
                sequence = reference[i:j]
                
                # Check if sequence appears in all codes
                if all(self._contains_sequence(tokens, sequence) for tokens in tokenized[1:]):
                    common_sequences.append('\n'.join(sequence))
        
        # Remove redundant sequences
        unique_sequences = []
        for seq in sorted(common_sequences, key=len, reverse=True):
            if not any(seq in existing for existing in unique_sequences):
                unique_sequences.append(seq)
        
        return unique_sequences[:5]  # Top 5 patterns
    
    def _contains_sequence(self, tokens: List[str], sequence: List[str]) -> bool:
        """Check if token list contains sequence."""
        seq_len = len(sequence)
        for i in range(len(tokens) - seq_len + 1):
            if tokens[i:i + seq_len] == sequence:
                return True
        return False
    
    def _get_complexity_range(self, cluster: AlgorithmCluster) -> Dict[str, Tuple[float, float]]:
        """Get complexity metric ranges for cluster."""
        ranges = {}
        
        for metric in ['cyclomatic_complexity', 'lines_of_code', 'nesting_depth']:
            values = [algo.complexity_metrics.get(metric, 0) for algo in cluster.algorithms]
            if values:
                ranges[metric] = (min(values), max(values))
        
        return ranges
    
    def match_algorithm(self, algorithm_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Match an algorithm against learned patterns.
        
        Returns:
            Best matching pattern or None
        """
        # Create temporary algorithm object
        temp_algo = UnknownAlgorithm(
            id='temp',
            source_file='temp',
            location={},
            complexity_metrics=self._extract_complexity_metrics(algorithm_data),
            structural_features=self._extract_structural_features(algorithm_data),
            semantic_hash=self.semantic_hasher.generate_simhash(
                algorithm_data.get('normalized_code', '')
            ),
            control_flow_hash=self._generate_control_flow_hash(algorithm_data),
            normalized_code=algorithm_data.get('normalized_code', '')
        )
        
        # Find best matching cluster
        best_cluster_id = self._find_best_cluster(temp_algo)
        
        if best_cluster_id is not None:
            cluster = self.clusters[best_cluster_id]
            return {
                'cluster_id': best_cluster_id,
                'signature': cluster.pattern_signature,
                'confidence': cluster.confidence,
                'algorithm_count': len(cluster.algorithms),
                'match_type': 'learned_pattern'
            }
        
        return None
    
    def _extract_complexity_metrics(self, algorithm_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract complexity metrics from algorithm data."""
        metrics = algorithm_data.get('complexity_metrics', {})
        
        return {
            'cyclomatic_complexity': metrics.get('cyclomatic_complexity', 0),
            'lines_of_code': algorithm_data.get('lines', {}).get('total', 0),
            'nesting_depth': metrics.get('nesting_depth', 0),
            'parameter_count': metrics.get('parameter_count', 0),
            'variable_count': metrics.get('variable_count', 0)
        }
    
    def _extract_structural_features(self, algorithm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structural features from algorithm data."""
        features = {}
        
        # Check for control structures
        normalized = algorithm_data.get('normalized_code', '')
        features['has_loops'] = int('LOOP' in normalized or 'FOR' in normalized)
        features['has_conditionals'] = int('IF' in normalized or 'CONDITION' in normalized)
        features['has_recursion'] = int('RECURSIVE_CALL' in normalized)
        features['has_try_catch'] = int('TRY' in normalized)
        
        # Count operations
        features['function_calls'] = normalized.count('CALL')
        features['return_statements'] = normalized.count('RETURN')
        
        return features
    
    def _generate_control_flow_hash(self, algorithm_data: Dict[str, Any]) -> str:
        """Generate hash based on control flow structure."""
        control_flow = algorithm_data.get('control_flow_graph', '')
        return hashlib.md5(control_flow.encode()).hexdigest()[:16]
    
    def _generate_algorithm_id(self, algorithm_data: Dict[str, Any]) -> str:
        """Generate unique ID for algorithm."""
        unique_str = f"{algorithm_data.get('file_path', '')}:{algorithm_data.get('location', {})}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]
    
    def _load_database(self) -> None:
        """Load algorithms and clusters from database."""
        if not self.db_path.exists():
            return
        
        try:
            with open(self.db_path, 'rb') as f:
                data = pickle.load(f)
                self.algorithms = data.get('algorithms', {})
                self.clusters = data.get('clusters', {})
                
                # Restore feature scaler if available
                if 'scaler' in data:
                    self.feature_scaler = data['scaler']
                
            logger.info(f"Loaded {len(self.algorithms)} algorithms and {len(self.clusters)} clusters")
            
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
    
    def _save_database(self) -> None:
        """Save algorithms and clusters to database."""
        try:
            data = {
                'algorithms': self.algorithms,
                'clusters': self.clusters,
                'scaler': self.feature_scaler,
                'metadata': {
                    'version': '1.0',
                    'last_updated': datetime.now().isoformat(),
                    'algorithm_count': len(self.algorithms),
                    'cluster_count': len(self.clusters)
                }
            }
            
            with open(self.db_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"Saved {len(self.algorithms)} algorithms to database")
            
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
    
    def export_patterns(self, output_path: Any) -> None:
        """Export learned patterns to JSON file."""
        patterns = self.get_cluster_patterns()
        
        with open(output_path, 'w') as f:
            json.dump({
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'pattern_count': len(patterns),
                'patterns': patterns
            }, f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get clustering statistics."""
        with self._lock:
            clustered_count = sum(
                1 for algo in self.algorithms.values() 
                if algo.cluster_id is not None
            )
            
            cluster_sizes = [
                len(cluster.algorithms) for cluster in self.clusters.values()
            ]
            
            return {
                'total_algorithms': len(self.algorithms),
                'clustered_algorithms': clustered_count,
                'unclustered_algorithms': len(self.algorithms) - clustered_count,
                'total_clusters': len(self.clusters),
                'average_cluster_size': np.mean(cluster_sizes) if cluster_sizes else 0,
                'largest_cluster_size': max(cluster_sizes) if cluster_sizes else 0,
                'smallest_cluster_size': min(cluster_sizes) if cluster_sizes else 0,
                'high_confidence_clusters': sum(
                    1 for cluster in self.clusters.values() 
                    if cluster.confidence >= 0.8
                )
            }