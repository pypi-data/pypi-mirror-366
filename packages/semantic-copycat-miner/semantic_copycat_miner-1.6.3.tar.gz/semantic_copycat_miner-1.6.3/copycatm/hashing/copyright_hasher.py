"""
Copyright and license information hashing for CopycatM.

This module generates various hashes from copyright, authorship, and license
information to enable similarity detection and tracking.
"""

import hashlib
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CopyrightHasher:
    """Generate hashes from copyright and license information."""
    
    def __init__(self):
        """Initialize copyright hasher."""
        self.hash_algorithms = {
            'sha256': hashlib.sha256,
            'sha1': hashlib.sha1,
            'md5': hashlib.md5,
        }
    
    def generate_hashes(self, copyright_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate comprehensive hashes from copyright information.
        
        Args:
            copyright_info: Dictionary from CopyrightExtractor.extract()
            
        Returns:
            Dictionary of various hashes
        """
        hashes = {}
        
        # Generate individual component hashes
        hashes['copyright_hash'] = self._hash_copyright_statements(
            copyright_info.get('copyright_statements', [])
        )
        
        hashes['license_hash'] = self._hash_license_info(
            copyright_info.get('license_spdx_ids', []),
            copyright_info.get('license_text', '')
        )
        
        hashes['authorship_hash'] = self._hash_authors(
            copyright_info.get('authors', [])
        )
        
        # Generate composite hashes
        hashes['composite_hash'] = self._generate_composite_hash(copyright_info)
        
        # Generate year-based hash
        hashes['year_hash'] = self._hash_years(
            copyright_info.get('copyright_years', [])
        )
        
        # Generate holder hash
        hashes['holder_hash'] = self._hash_holders(
            copyright_info.get('copyright_holders', [])
        )
        
        # Generate normalized copyright hash (order-independent)
        hashes['normalized_copyright_hash'] = self._hash_normalized_copyright(copyright_info)
        
        # Generate fuzzy hashes for similarity detection
        hashes['fuzzy_license_hash'] = self._generate_fuzzy_hash(
            copyright_info.get('license_text', '')
        )
        
        return hashes
    
    def _hash_copyright_statements(self, statements: List[Dict]) -> str:
        """Hash copyright statements."""
        if not statements:
            return self._compute_hash('')
        
        # Sort statements for consistency
        sorted_statements = sorted(
            [stmt.get('text', '') for stmt in statements]
        )
        
        combined = '\n'.join(sorted_statements)
        return self._compute_hash(combined)
    
    def _hash_license_info(self, spdx_ids: List[str], license_text: str) -> str:
        """Hash license information."""
        if spdx_ids:
            # Use SPDX IDs for consistent hashing
            sorted_ids = sorted(set(spdx_ids))
            return self._compute_hash('|'.join(sorted_ids))
        elif license_text:
            # Fallback to text hash
            normalized_text = self._normalize_text(license_text)
            return self._compute_hash(normalized_text)
        else:
            return self._compute_hash('')
    
    def _hash_authors(self, authors: List[Dict]) -> str:
        """Hash author information."""
        if not authors:
            return self._compute_hash('')
        
        # Create normalized author strings
        author_strings = []
        for author in authors:
            name = author.get('name', '').lower().strip()
            email = author.get('email') or ''
            email = email.lower().strip()
            if email:
                author_strings.append(f"{name} <{email}>")
            else:
                author_strings.append(name)
        
        # Sort for consistency
        sorted_authors = sorted(set(author_strings))
        return self._compute_hash('|'.join(sorted_authors))
    
    def _hash_years(self, years: List[int]) -> str:
        """Hash copyright years."""
        if not years:
            return self._compute_hash('')
        
        # Sort and deduplicate years
        sorted_years = sorted(set(years))
        year_string = ','.join(str(y) for y in sorted_years)
        return self._compute_hash(year_string)
    
    def _hash_holders(self, holders: List[str]) -> str:
        """Hash copyright holders."""
        if not holders:
            return self._compute_hash('')
        
        # Normalize and sort holders
        normalized_holders = sorted(set(
            h.lower().strip() for h in holders if h.strip()
        ))
        return self._compute_hash('|'.join(normalized_holders))
    
    def _generate_composite_hash(self, copyright_info: Dict[str, Any]) -> str:
        """Generate composite hash of all copyright information."""
        # Extract key components
        components = {
            'copyright_years': sorted(copyright_info.get('copyright_years', [])),
            'copyright_holders': sorted(copyright_info.get('copyright_holders', [])),
            'license_spdx_ids': sorted(copyright_info.get('license_spdx_ids', [])),
            'author_count': len(copyright_info.get('authors', [])),
            'has_copyright': copyright_info.get('has_copyright', False),
            'has_license': copyright_info.get('has_license', False),
        }
        
        # Convert to stable JSON representation
        json_str = json.dumps(components, sort_keys=True)
        return self._compute_hash(json_str)
    
    def _hash_normalized_copyright(self, copyright_info: Dict[str, Any]) -> str:
        """
        Generate normalized copyright hash that's order-independent.
        
        This hash will be the same for files with the same copyright
        information regardless of the order it appears in the file.
        """
        normalized_data = {
            'spdx_licenses': sorted(set(copyright_info.get('license_spdx_ids', []))),
            'years': sorted(set(copyright_info.get('copyright_years', []))),
            'holders': sorted(set(
                h.lower().strip() for h in copyright_info.get('copyright_holders', [])
            )),
            'author_names': sorted(set(
                a.get('name', '').lower().strip() 
                for a in copyright_info.get('authors', [])
                if a.get('name')
            )),
        }
        
        # Create canonical representation
        canonical = json.dumps(normalized_data, sort_keys=True)
        return self._compute_hash(canonical)
    
    def _generate_fuzzy_hash(self, text: str) -> str:
        """
        Generate fuzzy hash for similarity detection.
        
        Uses a simple approach - in production, could use TLSH or similar.
        """
        if not text:
            return self._compute_hash('')
        
        # Normalize text heavily
        normalized = self._normalize_text(text)
        
        # Extract key terms
        words = normalized.split()
        
        # Use only significant words (length > 3)
        significant_words = sorted(set(w for w in words if len(w) > 3))
        
        # Take first N significant words for fuzzy matching
        fuzzy_text = ' '.join(significant_words[:20])
        
        return self._compute_hash(fuzzy_text, algorithm='md5')
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent hashing."""
        if not text:
            return ''
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        import re
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _compute_hash(self, data: str, algorithm: str = 'sha256') -> str:
        """Compute hash of string data."""
        if algorithm not in self.hash_algorithms:
            algorithm = 'sha256'
        
        hasher = self.hash_algorithms[algorithm]()
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
    
    def generate_copyright_signature(self, copyright_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive copyright signature for comparison.
        
        This includes hashes and normalized data for similarity detection.
        """
        hashes = self.generate_hashes(copyright_info)
        
        signature = {
            'hashes': hashes,
            'license_spdx_ids': sorted(set(copyright_info.get('license_spdx_ids', []))),
            'copyright_years': sorted(set(copyright_info.get('copyright_years', []))),
            'copyright_holder_count': len(set(copyright_info.get('copyright_holders', []))),
            'author_count': len(copyright_info.get('authors', [])),
            'has_copyright': copyright_info.get('has_copyright', False),
            'has_license': copyright_info.get('has_license', False),
            'license_confidence': copyright_info.get('license_confidence', 0.0),
            'signature_version': '1.0',
            'generated_at': datetime.now().isoformat() + 'Z'
        }
        
        return signature
    
    def compare_signatures(self, sig1: Dict[str, Any], sig2: Dict[str, Any]) -> Dict[str, float]:
        """
        Compare two copyright signatures and return similarity scores.
        
        Returns dict with various similarity metrics.
        """
        scores = {}
        
        # Exact hash matches
        hashes1 = sig1.get('hashes', {})
        hashes2 = sig2.get('hashes', {})
        
        # Check exact matches
        scores['exact_match'] = float(
            hashes1.get('normalized_copyright_hash') == 
            hashes2.get('normalized_copyright_hash')
        )
        
        # License similarity
        licenses1 = set(sig1.get('license_spdx_ids', []))
        licenses2 = set(sig2.get('license_spdx_ids', []))
        
        if licenses1 or licenses2:
            if licenses1 and licenses2:
                scores['license_similarity'] = len(licenses1 & licenses2) / len(licenses1 | licenses2)
            else:
                scores['license_similarity'] = 0.0
        else:
            scores['license_similarity'] = 1.0  # Both have no license
        
        # Year overlap
        years1 = set(sig1.get('copyright_years', []))
        years2 = set(sig2.get('copyright_years', []))
        
        if years1 or years2:
            if years1 and years2:
                scores['year_overlap'] = len(years1 & years2) / len(years1 | years2)
            else:
                scores['year_overlap'] = 0.0
        else:
            scores['year_overlap'] = 1.0  # Both have no years
        
        # Fuzzy license similarity
        if hashes1.get('fuzzy_license_hash') == hashes2.get('fuzzy_license_hash'):
            scores['fuzzy_license_match'] = 1.0
        else:
            scores['fuzzy_license_match'] = 0.0
        
        # Overall similarity
        weights = {
            'exact_match': 0.4,
            'license_similarity': 0.3,
            'year_overlap': 0.1,
            'fuzzy_license_match': 0.2
        }
        
        scores['overall_similarity'] = sum(
            scores.get(key, 0) * weight 
            for key, weight in weights.items()
        )
        
        return scores