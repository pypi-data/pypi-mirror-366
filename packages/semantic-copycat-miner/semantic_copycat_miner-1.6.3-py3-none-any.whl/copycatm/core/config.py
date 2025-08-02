"""
Configuration management for CopycatM.
"""

import json
import os
from typing import Dict, List, Optional, Any


class AnalysisConfig:
    """Configuration for code analysis."""
    
    def __init__(
        self,
        complexity_threshold: int = 3,
        min_lines: int = 20,
        include_intermediates: bool = False,
        hash_algorithms: Optional[List[str]] = None,
        confidence_threshold: float = 0.0,
        parallel_workers: Optional[int] = None,
        languages: Optional[List[str]] = None,
        tlsh_threshold: int = 100,
        lsh_bands: int = 20,
        chunk_size: int = 100,
        memory_limit_mb: Optional[int] = None,
        use_gnn_pytorch: bool = False,
        enable_swhid: bool = False,
        swhid_include_directory: bool = False,
    ):
        self.complexity_threshold = complexity_threshold
        self.min_lines = min_lines
        self.include_intermediates = include_intermediates
        self.hash_algorithms = hash_algorithms or ["sha256", "tlsh", "minhash", "simhash"]
        self.confidence_threshold = confidence_threshold
        self.parallel_workers = parallel_workers
        self.languages = languages or [
            "python", "javascript", "java", "c", "cpp", "go", "rust"
        ]
        self.tlsh_threshold = tlsh_threshold
        self.lsh_bands = lsh_bands
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.use_gnn_pytorch = use_gnn_pytorch
        self.enable_swhid = enable_swhid
        self.swhid_include_directory = swhid_include_directory
    
    @classmethod
    def from_file(cls, config_path: str) -> "AnalysisConfig":
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return cls(
            complexity_threshold=config_data.get("analysis", {}).get("complexity_threshold", 3),
            min_lines=config_data.get("analysis", {}).get("min_lines", 20),
            include_intermediates=config_data.get("output", {}).get("include_intermediates", False),
            hash_algorithms=config_data.get("hashing", {}).get("algorithms", ["sha256", "tlsh", "minhash", "simhash"]),
            confidence_threshold=config_data.get("analysis", {}).get("confidence_threshold", 0.0),
            parallel_workers=config_data.get("performance", {}).get("parallel_workers"),
            languages=config_data.get("languages", {}).get("enabled", [
                "python", "javascript", "java", "c", "cpp", "go", "rust"
            ]),
            tlsh_threshold=config_data.get("hashing", {}).get("tlsh_threshold", 100),
            lsh_bands=config_data.get("hashing", {}).get("lsh_bands", 20),
            chunk_size=config_data.get("performance", {}).get("chunk_size", 100),
            memory_limit_mb=config_data.get("performance", {}).get("memory_limit_mb"),
            use_gnn_pytorch=config_data.get("gnn", {}).get("use_pytorch", False),
            enable_swhid=config_data.get("swhid", {}).get("enabled", False),
            swhid_include_directory=config_data.get("swhid", {}).get("include_directory", False),
        )
    
    @classmethod
    def load_default(cls) -> "AnalysisConfig":
        """Load configuration from default locations."""
        config_paths = [
            "./copycatm.json",
            os.path.expanduser("~/.copycatm/config.json"),
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                return cls.from_file(config_path)
        
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "analysis": {
                "complexity_threshold": self.complexity_threshold,
                "min_lines": self.min_lines,
                "confidence_threshold": self.confidence_threshold,
            },
            "languages": {
                "enabled": self.languages,
            },
            "hashing": {
                "algorithms": self.hash_algorithms,
                "tlsh_threshold": self.tlsh_threshold,
                "lsh_bands": self.lsh_bands,
            },
            "performance": {
                "parallel_workers": self.parallel_workers,
                "chunk_size": self.chunk_size,
                "memory_limit_mb": self.memory_limit_mb,
            },
            "output": {
                "include_intermediates": self.include_intermediates,
            },
            "gnn": {
                "use_pytorch": self.use_gnn_pytorch,
            },
            "swhid": {
                "enabled": self.enable_swhid,
                "include_directory": self.swhid_include_directory,
            },
        }
    
    def save(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2) 