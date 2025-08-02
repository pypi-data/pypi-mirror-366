"""
Copyright and authorship information extraction for CopycatM.

This module extracts copyright statements, author information, and license
declarations from source code files for IP contamination detection.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class CopyrightExtractor:
    """Extract copyright, authorship, and license information from source files."""
    
    def __init__(self):
        """Initialize copyright extractor with pattern definitions."""
        # Copyright patterns with various formats
        self.copyright_patterns = [
            # Standard copyright formats
            r'(?i)copyright\s*(?:\(c\)|©)?\s*(\d{4}(?:\s*[-–]\s*\d{4})?)\s+(.+?)(?:\.|$)',
            r'(?i)copyright\s*(?:\(c\)|©)?\s*(\d{4}(?:\s*[-–]\s*\d{4})?)\s*by\s+(.+?)(?:\.|$)',
            r'(?i)(?:\(c\)|©)\s*(\d{4}(?:\s*[-–]\s*\d{4})?)\s+(.+?)(?:\.|$)',
            # SPDX format
            r'(?i)spdx-filecopyrighttext:\s*(?:\(c\)|©)?\s*(\d{4}(?:\s*[-–]\s*\d{4})?)\s+(.+?)(?:\.|$)',
            # Alternative formats
            r'(?i)copyrighted\s+by\s+(.+?)\s*[,.]?\s*(\d{4}(?:\s*[-–]\s*\d{4})?)',
            # Copyright without year
            r'(?i)copyright\s*(?:\(c\)|©)?\s*(?:by\s+)?([^0-9\n]+?)(?:\.|$)',
        ]
        
        # Author patterns
        self.author_patterns = [
            # Standard author formats
            r'(?i)author[s]?:\s*([^\n<]+?)(?:\s*<([^>]+)>)?(?:\n|$)',
            r'(?i)written\s+by\s*([^\n<]+?)(?:\s*<([^>]+)>)?(?:\n|$)',
            r'(?i)created\s+by\s*([^\n<]+?)(?:\s*<([^>]+)>)?(?:\n|$)',
            r'(?i)maintained\s+by\s*([^\n<]+?)(?:\s*<([^>]+)>)?(?:\n|$)',
            # @author tag (common in Java/JavaScript)
            r'@author\s+([^\n<]+?)(?:\s*<([^>]+)>)?(?:\n|$)',
            # Contributors
            r'(?i)contributor[s]?:\s*([^\n<]+?)(?:\s*<([^>]+)>)?(?:\n|$)',
        ]
        
        # License patterns
        self.license_patterns = [
            # SPDX identifier (highest priority)
            r'(?i)spdx-license-identifier:\s*([^\n]+)',
            # Licensed under
            r'(?i)licensed\s+under\s+(?:the\s+)?([^,\n]+?)(?:\s+license)?(?:[,\n]|$)',
            # License: format
            r'(?i)license:\s*([^\n]+)',
            # The X License format (e.g., "The MIT License")
            r'(?i)^the\s+([^,\n]+?)\s+license(?:\s+\([^)]+\))?',
            # This file is part of/distributed under
            r'(?i)(?:distributed|released)\s+under\s+(?:the\s+)?([^,\n]+?)(?:\s+license)?(?:[,\n]|$)',
            # Dual licensing
            r'(?i)dual\s+licensed\s+under\s+([^,\n]+?)\s+(?:and|or)\s+([^,\n]+)',
        ]
        
        # Common license name variations
        self.license_aliases = {
            # MIT variations
            'mit': 'MIT',
            'mit license': 'MIT',
            'the mit license': 'MIT',
            'expat': 'MIT',
            'x11': 'MIT',
            
            # GPL variations
            'gpl': 'GPL-3.0',
            'gplv2': 'GPL-2.0',
            'gpl v2': 'GPL-2.0',
            'gpl version 2': 'GPL-2.0',
            'gnu gpl v2': 'GPL-2.0',
            'gplv3': 'GPL-3.0',
            'gpl v3': 'GPL-3.0',
            'gpl version 3': 'GPL-3.0',
            'gnu gpl v3': 'GPL-3.0',
            
            # LGPL variations
            'lgpl': 'LGPL-3.0',
            'lgplv2': 'LGPL-2.0',
            'lgpl v2': 'LGPL-2.0',
            'lgplv2.1': 'LGPL-2.1',
            'lgpl v2.1': 'LGPL-2.1',
            'lgplv3': 'LGPL-3.0',
            'lgpl v3': 'LGPL-3.0',
            
            # Apache variations
            'apache': 'Apache-2.0',
            'apache 2': 'Apache-2.0',
            'apache 2.0': 'Apache-2.0',
            'apache license 2.0': 'Apache-2.0',
            'apache software license': 'Apache-2.0',
            'asl 2.0': 'Apache-2.0',
            
            # BSD variations
            'bsd': 'BSD-3-Clause',
            'bsd license': 'BSD-3-Clause',
            'bsd 3-clause': 'BSD-3-Clause',
            'bsd 3 clause': 'BSD-3-Clause',
            'bsd 3': 'BSD-3-Clause',
            'new bsd': 'BSD-3-Clause',
            'modified bsd': 'BSD-3-Clause',
            'bsd 2-clause': 'BSD-2-Clause',
            'bsd 2 clause': 'BSD-2-Clause',
            'simplified bsd': 'BSD-2-Clause',
            'freebsd': 'BSD-2-Clause',
            
            # Creative Commons
            'cc0': 'CC0-1.0',
            'cc by': 'CC-BY-4.0',
            'cc by 4.0': 'CC-BY-4.0',
            'cc by-sa': 'CC-BY-SA-4.0',
            'cc by-sa 4.0': 'CC-BY-SA-4.0',
            'cc by-nc': 'CC-BY-NC-4.0',
            'cc by-nd': 'CC-BY-ND-4.0',
            'cc by-nc-sa': 'CC-BY-NC-SA-4.0',
            'cc by-nc-nd': 'CC-BY-NC-ND-4.0',
            'creative commons': 'CC-BY-4.0',
            'creative commons zero': 'CC0-1.0',
            
            # Other common licenses
            'isc': 'ISC',
            'isc license': 'ISC',
            'mpl': 'MPL-2.0',
            'mpl 2': 'MPL-2.0',
            'mpl 2.0': 'MPL-2.0',
            'zlib': 'Zlib',
            'zlib license': 'Zlib',
            'wtfpl': 'WTFPL',
            'artistic': 'Artistic-2.0',
            'artistic 2': 'Artistic-2.0',
            'artistic 2.0': 'Artistic-2.0',
            'artistic license': 'Artistic-2.0',
            'boost': 'BSL-1.0',
            'boost software license': 'BSL-1.0',
            'bsl 1.0': 'BSL-1.0',
            'eclipse': 'EPL-2.0',
            'eclipse public license': 'EPL-2.0',
            'epl 2.0': 'EPL-2.0',
            'agpl': 'AGPL-3.0',
            'affero gpl': 'AGPL-3.0',
            'gnu agpl': 'AGPL-3.0',
            'json': 'JSON',
            'json license': 'JSON',
            'openssl': 'OpenSSL',
            'openssl license': 'OpenSSL',
            'php': 'PHP-3.01',
            'php license': 'PHP-3.01',
            'python': 'PSF-2.0',
            'psf': 'PSF-2.0',
            'python software foundation': 'PSF-2.0',
            'ruby': 'Ruby',
            'ruby license': 'Ruby',
            'vim': 'Vim',
            'vim license': 'Vim',
            'mozilla public license 2.0': 'MPL-2.0',
            'cc0': 'CC0-1.0',
            'unlicense': 'Unlicense',
            'public domain': 'Unlicense',
            'wtfpl': 'WTFPL',
            'agpl': 'AGPL-3.0',
            'agplv3': 'AGPL-3.0',
            'artistic': 'Artistic-2.0',
            'artistic 2': 'Artistic-2.0',
            'boost': 'BSL-1.0',
            'eclipse': 'EPL-2.0',
            'epl': 'EPL-2.0',
            'zlib': 'Zlib',
        }
    
    def extract(self, content: str, max_header_lines: int = 100) -> Dict[str, Any]:
        """
        Extract copyright and authorship information from file content.
        
        Args:
            content: File content as string
            max_header_lines: Maximum lines to search for copyright info
            
        Returns:
            Dictionary containing extracted information
        """
        # Focus on file header for better performance
        lines = content.split('\n')
        header_content = '\n'.join(lines[:max_header_lines])
        
        # Also check the end of file for some licenses
        footer_content = '\n'.join(lines[-20:]) if len(lines) > 20 else ''
        
        # Combine header and footer for searching
        search_content = header_content + '\n' + footer_content
        
        # Extract various components
        copyright_info = self._extract_copyright_statements(search_content)
        authors = self._extract_authors(search_content)
        license_info = self._extract_license_info(search_content)
        
        # Compile results
        result = {
            'copyright_statements': copyright_info['statements'],
            'copyright_years': copyright_info['years'],
            'copyright_holders': copyright_info['holders'],
            'authors': authors,
            'license_text': license_info['text'],
            'license_names': license_info['names'],
            'license_spdx_ids': license_info['spdx_ids'],
            'license_confidence': license_info['confidence'],
            'extraction_method': 'pattern_matching',
            'header_size': len(header_content),
            'total_file_size': len(content)
        }
        
        # Add summary info
        result['has_copyright'] = bool(result['copyright_statements'])
        result['has_license'] = bool(result['license_spdx_ids'])
        result['has_authors'] = bool(result['authors'])
        
        return result
    
    def _extract_copyright_statements(self, content: str) -> Dict[str, Any]:
        """Extract copyright statements and parse details."""
        statements = []
        years = set()
        holders = set()
        
        for pattern in self.copyright_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                statement = match.group(0).strip()
                if statement not in [s['text'] for s in statements]:
                    # Parse the match
                    groups = match.groups()
                    year_str = None
                    holder = None
                    
                    # Handle different pattern formats
                    if len(groups) >= 2 and groups[0] and len(groups[0].strip()) >= 4 and groups[0].strip()[:4].isdigit():
                        year_str = groups[0].strip()
                        holder = groups[1].strip() if groups[1] else None
                    elif len(groups) >= 2 and groups[1] and len(groups[1].strip()) >= 4 and groups[1].strip()[:4].isdigit():
                        holder = groups[0].strip() if groups[0] else None
                        year_str = groups[1].strip()
                    elif len(groups) >= 1:
                        # Try to extract year from the statement
                        year_match = re.search(r'\b(19|20)\d{2}\b', statement)
                        if year_match:
                            year_str = year_match.group(0)
                        holder = groups[0].strip() if groups[0] else None
                    
                    # Parse years (handle ranges)
                    if year_str:
                        year_parts = re.split(r'[-–]', year_str)
                        for part in year_parts:
                            part = part.strip()
                            if part.isdigit() and len(part) == 4:
                                years.add(int(part))
                    
                    # Clean holder
                    if holder:
                        holder = self._clean_copyright_holder(holder)
                        if holder:
                            holders.add(holder)
                    
                    statements.append({
                        'text': statement,
                        'years': sorted(list(years)) if years else [],
                        'holder': holder,
                        'line_number': content[:match.start()].count('\n') + 1
                    })
        
        return {
            'statements': statements,
            'years': sorted(list(years)),
            'holders': sorted(list(holders))
        }
    
    def _extract_authors(self, content: str) -> List[Dict[str, str]]:
        """Extract author information."""
        authors = []
        seen = set()
        
        for pattern in self.author_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                name = match.group(1).strip() if match.group(1) else None
                email = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else None
                
                if name:
                    # Clean name
                    name = self._clean_author_name(name)
                    
                    # Create unique key
                    key = (name.lower(), email.lower() if email else '')
                    if key not in seen:
                        seen.add(key)
                        authors.append({
                            'name': name,
                            'email': email,
                            'line_number': content[:match.start()].count('\n') + 1
                        })
        
        return authors
    
    def _extract_license_info(self, content: str) -> Dict[str, Any]:
        """Extract license information and normalize to SPDX."""
        license_names = []
        license_texts = []
        spdx_ids = []
        confidence_scores = []
        
        # First, look for explicit license mentions in comments
        comment_blocks = self._extract_comment_blocks(content)
        for block in comment_blocks:
            # Check for GNU licenses in comment text
            if re.search(r'GNU\s+(?:Lesser\s+)?General\s+Public\s+License', block, re.IGNORECASE):
                license_texts.append(block)
                # Extract version info
                version_match = re.search(r'version\s+(\d+(?:\.\d+)?)', block, re.IGNORECASE)
                if version_match:
                    version = version_match.group(1)
                    if 'lesser' in block.lower():
                        spdx_id = f"LGPL-{version}"
                    else:
                        spdx_id = f"GPL-{version}"
                    spdx_ids.append(spdx_id)
                    confidence_scores.append(0.9)
                    license_names.append(f"GNU {'Lesser ' if 'lesser' in block.lower() else ''}General Public License v{version}")
        
        # Check for MIT license pattern in full content
        if re.search(r'Permission\s+is\s+hereby\s+granted.*free\s+of\s+charge', content, re.IGNORECASE | re.DOTALL):
            # This is likely MIT license
            if 'MIT' in content.upper() or 'M.I.T.' in content.upper():
                spdx_ids.append('MIT')
                confidence_scores.append(0.95)
                license_names.append('MIT License')
                license_texts.append('MIT License detected from permission text')
        
        # Then check standard patterns
        for pattern in self.license_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Extract license text
                if 'dual' in pattern:
                    # Handle dual licensing
                    if len(match.groups()) >= 2:
                        licenses = [match.group(1).strip(), match.group(2).strip()]
                    else:
                        licenses = [match.group(0).strip()]
                else:
                    licenses = [match.group(1).strip() if match.group(1) else match.group(0).strip()]
                
                for license_text in licenses:
                    if license_text and license_text not in license_texts:
                        license_texts.append(license_text)
                        
                        # Try to normalize to SPDX
                        spdx_id, confidence = self._normalize_to_spdx(license_text)
                        if spdx_id:
                            spdx_ids.append(spdx_id)
                            confidence_scores.append(confidence)
                            license_names.append(license_text)
        
        # Calculate overall confidence
        overall_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        # Handle multiple licenses
        if len(spdx_ids) > 1:
            # Check if it's dual licensing or multiple files
            unique_spdx = list(set(spdx_ids))
            if len(unique_spdx) == 2:
                # Likely dual licensing
                combined_spdx = f"{unique_spdx[0]} OR {unique_spdx[1]}"
                spdx_ids = [combined_spdx]
        
        return {
            'text': ' | '.join(license_texts),
            'names': license_names,
            'spdx_ids': list(set(spdx_ids)),
            'confidence': overall_confidence
        }
    
    def _extract_comment_blocks(self, content: str) -> List[str]:
        """Extract comment blocks that might contain license information."""
        blocks = []
        
        # C-style block comments /* ... */
        c_block_pattern = r'/\*[\s\S]*?\*/'
        c_blocks = re.findall(c_block_pattern, content)
        for block in c_blocks:
            # Clean the block - remove /* and */ and leading asterisks
            cleaned = block.strip('/*').strip()
            # Remove leading asterisks from each line
            lines = cleaned.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('*'):
                    line = line[1:].strip()
                cleaned_lines.append(line)
            blocks.append('\n'.join(cleaned_lines))
        
        # Python/Shell style consecutive comment lines
        lines = content.split('\n')
        current_block = []
        in_comment_block = False
        
        for line in lines:
            # Check if line is a comment (# or //)
            stripped = line.strip()
            if stripped.startswith(('#', '//')):
                comment_text = stripped.lstrip('#/').strip()
                current_block.append(comment_text)
                in_comment_block = True
            else:
                if in_comment_block and current_block:
                    # End of comment block
                    blocks.append('\n'.join(current_block))
                    current_block = []
                in_comment_block = False
        
        # Don't forget the last block
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _normalize_to_spdx(self, license_text: str) -> Tuple[Optional[str], float]:
        """
        Normalize license text to SPDX identifier.
        
        Returns:
            Tuple of (SPDX ID, confidence score)
        """
        # Clean the license text
        cleaned = license_text.lower().strip()
        cleaned = re.sub(r'[^\w\s\d.-]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Check for exact SPDX ID first
        if re.match(r'^[A-Z][A-Za-z0-9.-]+(?:-\d+\.\d+)?(?:\+)?$', license_text.strip()):
            # Looks like an SPDX ID already
            return license_text.strip(), 1.0
        
        # Check aliases
        if cleaned in self.license_aliases:
            return self.license_aliases[cleaned], 0.95
        
        # Fuzzy matching for common patterns
        for alias, spdx_id in self.license_aliases.items():
            if alias in cleaned:
                # Check if it's a strong match
                if len(alias.split()) > 1 or len(cleaned.split()) <= 3:
                    return spdx_id, 0.8
        
        # Check for version patterns
        version_match = re.search(r'(?:version|v|ver)?\s*(\d+(?:\.\d+)?)', cleaned)
        if version_match:
            version = version_match.group(1)
            
            # Common versioned licenses
            if 'gpl' in cleaned and 'lesser' not in cleaned and 'library' not in cleaned:
                return f"GPL-{version}", 0.7
            elif ('lgpl' in cleaned) or ('lesser' in cleaned and 'gpl' in cleaned):
                return f"LGPL-{version}", 0.7
            elif 'apache' in cleaned:
                return f"Apache-{version}", 0.7
            elif 'mpl' in cleaned or 'mozilla' in cleaned:
                return f"MPL-{version}", 0.7
        
        return None, 0.0
    
    def _clean_copyright_holder(self, holder: str) -> str:
        """Clean and normalize copyright holder name."""
        # Remove common suffixes
        holder = re.sub(r'\s*[\.,;]\s*$', '', holder)
        holder = re.sub(r'\s+', ' ', holder)
        
        # Remove trailing "All rights reserved" etc
        holder = re.sub(r'(?i)\s*all\s+rights?\s+reserved\s*$', '', holder)
        holder = re.sub(r'(?i)\s*some\s+rights?\s+reserved\s*$', '', holder)
        
        # Remove quotes
        holder = holder.strip('"\'')
        
        return holder.strip()
    
    def _clean_author_name(self, name: str) -> str:
        """Clean and normalize author name."""
        # Remove common prefixes/suffixes
        name = re.sub(r'^\s*(?:by|from)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*[\.,;]\s*$', '', name)
        
        # Remove quotes
        name = name.strip('"\'')
        
        # Normalize whitespace
        name = re.sub(r'\s+', ' ', name)
        
        return name.strip()