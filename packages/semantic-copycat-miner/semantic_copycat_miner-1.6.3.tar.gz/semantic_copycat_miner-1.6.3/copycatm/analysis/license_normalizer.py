"""
License normalization and SPDX identifier mapping for CopycatM.

This module provides comprehensive license detection and normalization
to SPDX identifiers for standardized license tracking.
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Set, Any
from pathlib import Path
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class LicenseNormalizer:
    """Normalize license text to SPDX identifiers with confidence scoring."""
    
    def __init__(self, spdx_data_path: Optional[str] = None):
        """
        Initialize license normalizer with SPDX data.
        
        Args:
            spdx_data_path: Path to SPDX license data JSON file
        """
        self.spdx_licenses = {}
        self.license_keywords = {}
        self.license_patterns = {}
        
        # Load SPDX data
        if spdx_data_path:
            self.load_spdx_data(spdx_data_path)
        else:
            # Use built-in minimal set
            self._initialize_builtin_licenses()
    
    def _initialize_builtin_licenses(self):
        """Initialize with built-in common licenses."""
        self.spdx_licenses = {
            'MIT': {
                'name': 'MIT License',
                'keywords': ['mit', 'permission', 'hereby', 'granted', 'free', 'charge'],
                'required_text': ['permission is hereby granted', 'without restriction'],
                'confidence_threshold': 0.85
            },
            'Apache-2.0': {
                'name': 'Apache License 2.0',
                'keywords': ['apache', 'license', 'version', '2.0', 'conditions'],
                'required_text': ['apache license', 'version 2.0'],
                'confidence_threshold': 0.85
            },
            'GPL-2.0': {
                'name': 'GNU General Public License v2.0',
                'keywords': ['gpl', 'gnu', 'general', 'public', 'version', '2'],
                'required_text': ['gnu general public license', 'version 2'],
                'confidence_threshold': 0.85
            },
            'GPL-3.0': {
                'name': 'GNU General Public License v3.0',
                'keywords': ['gpl', 'gnu', 'general', 'public', 'version', '3'],
                'required_text': ['gnu general public license', 'version 3'],
                'confidence_threshold': 0.85
            },
            'BSD-2-Clause': {
                'name': 'BSD 2-Clause License',
                'keywords': ['bsd', 'redistribution', 'binary', 'source', '2-clause', 'simplified'],
                'required_text': ['redistribution', 'source and binary forms'],
                'confidence_threshold': 0.80
            },
            'BSD-3-Clause': {
                'name': 'BSD 3-Clause License',
                'keywords': ['bsd', 'redistribution', 'binary', 'source', '3-clause', 'new', 'revised'],
                'required_text': ['redistribution', 'source and binary forms', 'neither the name'],
                'confidence_threshold': 0.80
            },
            'ISC': {
                'name': 'ISC License',
                'keywords': ['isc', 'permission', 'use', 'copy', 'modify'],
                'required_text': ['permission to use, copy, modify'],
                'confidence_threshold': 0.85
            },
            'LGPL-2.1': {
                'name': 'GNU Lesser General Public License v2.1',
                'keywords': ['lgpl', 'lesser', 'gnu', 'general', 'public', 'library', '2.1'],
                'required_text': ['gnu lesser general public license', 'version 2.1'],
                'confidence_threshold': 0.85
            },
            'LGPL-3.0': {
                'name': 'GNU Lesser General Public License v3.0',
                'keywords': ['lgpl', 'lesser', 'gnu', 'general', 'public', '3.0'],
                'required_text': ['gnu lesser general public license', 'version 3'],
                'confidence_threshold': 0.85
            },
            'MPL-2.0': {
                'name': 'Mozilla Public License 2.0',
                'keywords': ['mozilla', 'public', 'license', '2.0', 'mpl'],
                'required_text': ['mozilla public license', 'version 2.0'],
                'confidence_threshold': 0.85
            },
            'CC0-1.0': {
                'name': 'Creative Commons Zero v1.0 Universal',
                'keywords': ['cc0', 'creative', 'commons', 'zero', 'public', 'domain', 'dedication'],
                'required_text': ['cc0', 'public domain'],
                'confidence_threshold': 0.85
            },
            'Unlicense': {
                'name': 'The Unlicense',
                'keywords': ['unlicense', 'public', 'domain', 'no', 'conditions'],
                'required_text': ['this is free and unencumbered software', 'public domain'],
                'confidence_threshold': 0.85
            },
            'AGPL-3.0': {
                'name': 'GNU Affero General Public License v3.0',
                'keywords': ['agpl', 'affero', 'gnu', 'general', 'public', 'network', '3.0'],
                'required_text': ['gnu affero general public license', 'version 3'],
                'confidence_threshold': 0.85
            },
            'BSL-1.0': {
                'name': 'Boost Software License 1.0',
                'keywords': ['boost', 'software', 'license', '1.0'],
                'required_text': ['boost software license', 'version 1.0'],
                'confidence_threshold': 0.85
            },
            'EPL-2.0': {
                'name': 'Eclipse Public License 2.0',
                'keywords': ['eclipse', 'public', 'license', '2.0', 'epl'],
                'required_text': ['eclipse public license', 'version 2.0'],
                'confidence_threshold': 0.85
            },
            'Zlib': {
                'name': 'zlib License',
                'keywords': ['zlib', 'acknowledgment', 'appreciated', 'not', 'required'],
                'required_text': ['acknowledgment', 'would be appreciated but is not required'],
                'confidence_threshold': 0.85
            }
        }
        
        # Build keyword index
        self._build_keyword_index()
    
    def load_spdx_data(self, data_path: str):
        """Load SPDX license data from JSON file."""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.spdx_licenses = data.get('licenses', {})
                self._build_keyword_index()
                logger.info(f"Loaded {len(self.spdx_licenses)} SPDX licenses")
        except Exception as e:
            logger.warning(f"Failed to load SPDX data: {e}. Using built-in licenses.")
            self._initialize_builtin_licenses()
    
    def _build_keyword_index(self):
        """Build keyword index for fast license lookup."""
        self.license_keywords = {}
        for spdx_id, license_data in self.spdx_licenses.items():
            keywords = license_data.get('keywords', [])
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self.license_keywords:
                    self.license_keywords[keyword_lower] = []
                self.license_keywords[keyword_lower].append(spdx_id)
    
    def normalize(self, license_text: str, context: Optional[Dict] = None) -> Tuple[Optional[str], float, Dict]:
        """
        Normalize license text to SPDX identifier.
        
        Args:
            license_text: Raw license text or reference
            context: Optional context (e.g., filename, other metadata)
            
        Returns:
            Tuple of (SPDX ID, confidence, metadata)
        """
        if not license_text:
            return None, 0.0, {}
        
        # Clean the license text
        cleaned_text = self._clean_text(license_text)
        
        # First, check if it's already an SPDX ID
        if self._is_spdx_id(license_text):
            return license_text, 1.0, {'method': 'exact_spdx_id'}
        
        # Try exact matching on common patterns
        exact_match = self._exact_match(cleaned_text)
        if exact_match:
            return exact_match[0], exact_match[1], {'method': 'exact_match'}
        
        # Try keyword-based matching
        keyword_matches = self._keyword_match(cleaned_text)
        if keyword_matches:
            best_match = max(keyword_matches, key=lambda x: x[1])
            if best_match[1] >= 0.7:
                return best_match[0], best_match[1], {'method': 'keyword_match', 'matches': len(keyword_matches)}
        
        # Try fuzzy matching
        fuzzy_match = self._fuzzy_match(cleaned_text)
        if fuzzy_match and fuzzy_match[1] >= 0.6:
            return fuzzy_match[0], fuzzy_match[1], {'method': 'fuzzy_match'}
        
        # Try to extract from URL
        url_match = self._extract_from_url(license_text)
        if url_match:
            return url_match[0], url_match[1], {'method': 'url_extraction'}
        
        # Check for dual/multiple licensing
        multi_license = self._check_multi_license(license_text)
        if multi_license:
            return multi_license[0], multi_license[1], {'method': 'multi_license', 'components': multi_license[2]}
        
        return None, 0.0, {}
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for matching."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://[^\s]+', ' ', text)
        
        # Remove special characters but keep hyphens and dots
        text = re.sub(r'[^\w\s.-]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _is_spdx_id(self, text: str) -> bool:
        """Check if text is already an SPDX identifier."""
        # SPDX ID pattern: Letter + (Letter|Number|.|-)*
        pattern = r'^[A-Z][A-Za-z0-9.-]+(?:-\d+\.\d+)?(?:\+)?$'
        return bool(re.match(pattern, text.strip()))
    
    def _exact_match(self, text: str) -> Optional[Tuple[str, float]]:
        """Try exact matching against common patterns."""
        exact_patterns = {
            'mit license': ('MIT', 0.95),
            'mit': ('MIT', 0.90),
            'apache license 2.0': ('Apache-2.0', 0.95),
            'apache 2.0': ('Apache-2.0', 0.90),
            'apache 2': ('Apache-2.0', 0.85),
            'gpl v2': ('GPL-2.0', 0.90),
            'gplv2': ('GPL-2.0', 0.95),
            'gpl v3': ('GPL-3.0', 0.90),
            'gplv3': ('GPL-3.0', 0.95),
            'bsd 3-clause': ('BSD-3-Clause', 0.95),
            'new bsd': ('BSD-3-Clause', 0.90),
            'bsd 2-clause': ('BSD-2-Clause', 0.95),
            'simplified bsd': ('BSD-2-Clause', 0.90),
            'isc license': ('ISC', 0.95),
            'isc': ('ISC', 0.90),
            'lgpl v2.1': ('LGPL-2.1', 0.95),
            'lgplv2.1': ('LGPL-2.1', 0.95),
            'lgpl v3': ('LGPL-3.0', 0.90),
            'lgplv3': ('LGPL-3.0', 0.95),
            'mozilla public license 2.0': ('MPL-2.0', 0.95),
            'mpl 2.0': ('MPL-2.0', 0.90),
            'cc0': ('CC0-1.0', 0.95),
            'public domain': ('Unlicense', 0.80),
            'unlicense': ('Unlicense', 0.95),
        }
        
        text_normalized = text.strip()
        if text_normalized in exact_patterns:
            return exact_patterns[text_normalized]
        
        return None
    
    def _keyword_match(self, text: str) -> List[Tuple[str, float]]:
        """Match based on keywords and required text."""
        matches = []
        text_words = set(text.split())
        
        # Score each license
        for spdx_id, license_data in self.spdx_licenses.items():
            score = 0.0
            keyword_matches = 0
            required_matches = 0
            
            # Check keywords
            keywords = license_data.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in text:
                    keyword_matches += 1
            
            if keywords:
                keyword_score = keyword_matches / len(keywords)
                score += keyword_score * 0.4
            
            # Check required text
            required_texts = license_data.get('required_text', [])
            for required in required_texts:
                if required.lower() in text:
                    required_matches += 1
            
            if required_texts:
                required_score = required_matches / len(required_texts)
                score += required_score * 0.6
            else:
                # If no required text, give more weight to keywords
                score = keyword_score * 0.8 if keywords else 0
            
            if score > 0:
                matches.append((spdx_id, score))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def _fuzzy_match(self, text: str) -> Optional[Tuple[str, float]]:
        """Fuzzy matching using sequence matching."""
        best_match = None
        best_score = 0.0
        
        # Compare against license names
        for spdx_id, license_data in self.spdx_licenses.items():
            name = license_data.get('name', '').lower()
            
            # Compare with full name
            score = SequenceMatcher(None, text, name).ratio()
            
            # Also try with SPDX ID
            id_score = SequenceMatcher(None, text, spdx_id.lower()).ratio()
            score = max(score, id_score)
            
            if score > best_score:
                best_score = score
                best_match = spdx_id
        
        if best_score >= 0.6:
            return best_match, best_score
        
        return None
    
    def _extract_from_url(self, text: str) -> Optional[Tuple[str, float]]:
        """Extract license from common license URLs."""
        url_patterns = {
            r'opensource\.org/licenses/MIT': ('MIT', 0.95),
            r'opensource\.org/licenses/Apache-2\.0': ('Apache-2.0', 0.95),
            r'opensource\.org/licenses/BSD-3-Clause': ('BSD-3-Clause', 0.95),
            r'opensource\.org/licenses/BSD-2-Clause': ('BSD-2-Clause', 0.95),
            r'gnu\.org/licenses/gpl-2\.0': ('GPL-2.0', 0.95),
            r'gnu\.org/licenses/gpl-3\.0': ('GPL-3.0', 0.95),
            r'gnu\.org/licenses/lgpl-2\.1': ('LGPL-2.1', 0.95),
            r'gnu\.org/licenses/lgpl-3\.0': ('LGPL-3.0', 0.95),
            r'mozilla\.org/MPL/2\.0': ('MPL-2.0', 0.95),
            r'creativecommons\.org/publicdomain/zero': ('CC0-1.0', 0.95),
            r'spdx\.org/licenses/([A-Z][A-Za-z0-9.-]+)': (r'\1', 0.95),
        }
        
        for pattern, (license_id, confidence) in url_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if r'\1' in license_id:
                    # Extract from regex group
                    license_id = match.group(1)
                return license_id, confidence
        
        return None
    
    def _check_multi_license(self, text: str) -> Optional[Tuple[str, float, List[str]]]:
        """Check for dual or multiple licensing."""
        # Common dual licensing patterns
        dual_patterns = [
            r'dual[\s-]licen[cs]ed?\s+under\s+(?:the\s+)?([^,\n]+?)\s+(?:and|or)\s+([^,\n]+)',
            r'licen[cs]ed?\s+under\s+(?:either\s+)?(?:the\s+)?([^,\n]+?)\s+or\s+(?:the\s+)?([^,\n]+)',
            r'([^,\n]+?)\s+or\s+([^,\n]+?)\s+licen[cs]e',
        ]
        
        for pattern in dual_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                license1 = match.group(1).strip()
                license2 = match.group(2).strip()
                
                # Normalize each license
                spdx1, conf1, _ = self.normalize(license1)
                spdx2, conf2, _ = self.normalize(license2)
                
                if spdx1 and spdx2:
                    combined = f"{spdx1} OR {spdx2}"
                    confidence = min(conf1, conf2) * 0.9  # Slightly lower confidence for combined
                    return combined, confidence, [spdx1, spdx2]
        
        return None
    
    def detect_license_compatibility(self, spdx_id: str) -> Dict[str, Any]:
        """
        Detect license compatibility characteristics.
        
        Returns dict with compatibility info like:
        - is_permissive
        - is_copyleft
        - is_weak_copyleft
        - commercial_use_allowed
        - modification_allowed
        - distribution_allowed
        - patent_grant
        """
        compatibility = {
            'is_permissive': False,
            'is_copyleft': False,
            'is_weak_copyleft': False,
            'commercial_use_allowed': True,
            'modification_allowed': True,
            'distribution_allowed': True,
            'patent_grant': False,
            'private_use_allowed': True,
            'compatibility_notes': []
        }
        
        # Permissive licenses
        permissive = ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 
                     'ISC', 'CC0-1.0', 'Unlicense', 'BSL-1.0', 'Zlib']
        
        # Copyleft licenses
        copyleft = ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0']
        
        # Weak copyleft
        weak_copyleft = ['LGPL-2.1', 'LGPL-3.0', 'MPL-2.0', 'EPL-2.0']
        
        # Patent grant licenses
        patent_grant = ['Apache-2.0', 'GPL-3.0', 'AGPL-3.0', 'MPL-2.0', 'EPL-2.0']
        
        if spdx_id in permissive:
            compatibility['is_permissive'] = True
            compatibility['compatibility_notes'].append('Permissive license with minimal restrictions')
        
        if spdx_id in copyleft:
            compatibility['is_copyleft'] = True
            compatibility['compatibility_notes'].append('Strong copyleft - derivative works must use same license')
        
        if spdx_id in weak_copyleft:
            compatibility['is_weak_copyleft'] = True
            compatibility['compatibility_notes'].append('Weak copyleft - linking permitted under certain conditions')
        
        if spdx_id in patent_grant:
            compatibility['patent_grant'] = True
            compatibility['compatibility_notes'].append('Includes express patent grant')
        
        # Special cases
        if spdx_id == 'CC0-1.0' or spdx_id == 'Unlicense':
            compatibility['compatibility_notes'].append('Public domain dedication - no restrictions')
        
        if 'GPL' in spdx_id:
            compatibility['compatibility_notes'].append('May have compatibility issues with non-GPL licenses')
        
        return compatibility