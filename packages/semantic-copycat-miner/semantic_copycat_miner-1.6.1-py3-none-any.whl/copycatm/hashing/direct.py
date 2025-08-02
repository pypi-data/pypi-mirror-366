"""
Direct hashing (SHA256, MD5) for CopycatM.
"""

import hashlib
from typing import Optional


class DirectHasher:
    """Generate direct cryptographic hashes."""
    
    def sha256(self, data: str) -> str:
        """Generate SHA256 hash of data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def md5(self, data: str) -> str:
        """Generate MD5 hash of data."""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def sha1(self, data: str) -> str:
        """Generate SHA1 hash of data."""
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    def blake2b(self, data: str, digest_size: int = 64) -> str:
        """Generate BLAKE2b hash of data."""
        return hashlib.blake2b(data.encode('utf-8'), digest_size=digest_size).hexdigest()
    
    def hash_file(self, file_path: str, algorithm: str = "sha256") -> str:
        """Hash a file using the specified algorithm."""
        hash_func = getattr(hashlib, algorithm)
        with open(file_path, 'rb') as f:
            return hash_func(f.read()).hexdigest()
    
    def hash_text(self, text: str, algorithm: str = "sha256") -> str:
        """Hash text using the specified algorithm."""
        if algorithm == "sha256":
            return self.sha256(text)
        elif algorithm == "md5":
            return self.md5(text)
        elif algorithm == "sha1":
            return self.sha1(text)
        elif algorithm == "blake2b":
            return self.blake2b(text)
        else:
            return self.sha256(text) 