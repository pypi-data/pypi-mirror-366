"""
Software Heritage ID (SWHID) support for CopycatM.

This module provides functionality to generate, validate, and work with
Software Heritage persistent identifiers (SWHIDs) as described in the
SWHID specification.

Based on the specification at:
https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html
"""

import hashlib
import re
import os
from typing import Dict, List, Optional, Any
from urllib.parse import quote, unquote


class SWHIDError(Exception):
    """Base exception for SWHID-related errors."""


class InvalidSWHIDError(SWHIDError):
    """Raised when a SWHID is malformed or invalid."""


class SWHIDType:
    """SWHID object types."""
    CONTENT = "cnt"      # File content
    DIRECTORY = "dir"    # Directory
    REVISION = "rev"     # Commit/revision
    RELEASE = "rel"      # Release/tag
    SNAPSHOT = "snp"     # Repository snapshot

    ALL_TYPES = {CONTENT, DIRECTORY, REVISION, RELEASE, SNAPSHOT}


class SWHID:
    """
    Software Heritage ID implementation.
    
    Supports generation, validation, and parsing of SWHIDs according to
    the v1.6 specification.
    """
    
    SCHEME_VERSION = "1"
    PREFIX = "swh"
    
    # SWHID regex pattern
    SWHID_PATTERN = re.compile(
        r'^swh:1:(cnt|dir|rev|rel|snp):([0-9a-f]{40})(;.*)?$'
    )
    
    def __init__(self, object_type: str, object_id: str, qualifiers: Optional[Dict[str, str]] = None):
        """
        Initialize a SWHID.
        
        Args:
            object_type: Object type (cnt, dir, rev, rel, snp)
            object_id: 40-character hex SHA1 hash
            qualifiers: Optional qualifiers dict
        """
        if object_type not in SWHIDType.ALL_TYPES:
            raise InvalidSWHIDError(f"Invalid object type: {object_type}")
        
        if not re.match(r'^[0-9a-f]{40}$', object_id):
            raise InvalidSWHIDError(f"Invalid object ID: {object_id}")
        
        self.object_type = object_type
        self.object_id = object_id
        self.qualifiers = qualifiers or {}
    
    @classmethod
    def parse(cls, swhid_string: str) -> 'SWHID':
        """
        Parse a SWHID string into a SWHID object.
        
        Args:
            swhid_string: SWHID string to parse
            
        Returns:
            SWHID object
            
        Raises:
            InvalidSWHIDError: If the SWHID is malformed
        """
        match = cls.SWHID_PATTERN.match(swhid_string)
        if not match:
            raise InvalidSWHIDError(f"Invalid SWHID format: {swhid_string}")
        
        object_type = match.group(1)
        object_id = match.group(2)
        qualifiers_str = match.group(3)
        
        qualifiers = {}
        if qualifiers_str:
            # Remove leading semicolon and parse qualifiers
            qualifiers_str = qualifiers_str[1:]  # Remove leading ;
            for qualifier in qualifiers_str.split(';'):
                if '=' in qualifier:
                    key, value = qualifier.split('=', 1)
                    # URL decode the value
                    qualifiers[key] = unquote(value)
        
        return cls(object_type, object_id, qualifiers)
    
    def __str__(self) -> str:
        """Return the SWHID as a string."""
        core = f"{self.PREFIX}:{self.SCHEME_VERSION}:{self.object_type}:{self.object_id}"
        
        if self.qualifiers:
            # Sort qualifiers for consistency
            qualifier_order = ['origin', 'visit', 'anchor', 'path', 'lines']
            ordered_qualifiers = []
            
            # Add qualifiers in preferred order
            for key in qualifier_order:
                if key in self.qualifiers:
                    value = quote(str(self.qualifiers[key]), safe='/:')
                    ordered_qualifiers.append(f"{key}={value}")
            
            # Add any remaining qualifiers
            for key, value in sorted(self.qualifiers.items()):
                if key not in qualifier_order:
                    value = quote(str(value), safe='/:')
                    ordered_qualifiers.append(f"{key}={value}")
            
            if ordered_qualifiers:
                core += ";" + ";".join(ordered_qualifiers)
        
        return core
    
    def __eq__(self, other) -> bool:
        """Check equality with another SWHID."""
        if not isinstance(other, SWHID):
            return False
        return (self.object_type == other.object_type and 
                self.object_id == other.object_id and
                self.qualifiers == other.qualifiers)
    
    def __hash__(self) -> int:
        """Make SWHID hashable."""
        return hash((self.object_type, self.object_id, tuple(sorted(self.qualifiers.items()))))
    
    @property
    def core_swhid(self) -> str:
        """Return just the core SWHID without qualifiers."""
        return f"{self.PREFIX}:{self.SCHEME_VERSION}:{self.object_type}:{self.object_id}"


class SWHIDGenerator:
    """
    Generator for Software Heritage IDs from file system objects.
    
    Follows the Git object model for computing intrinsic identifiers.
    """
    
    @staticmethod
    def git_sha1(content: bytes, object_type: str = "blob") -> str:
        """
        Compute Git-style SHA1 hash.
        
        Args:
            content: Content bytes
            object_type: Git object type (blob, tree, commit, tag)
            
        Returns:
            40-character hex SHA1 hash
        """
        header = f"{object_type} {len(content)}\0".encode('ascii')
        return hashlib.sha1(header + content).hexdigest()
    
    @classmethod
    def content_swhid(cls, file_path: str, qualifiers: Optional[Dict[str, str]] = None) -> SWHID:
        """
        Generate SWHID for file content.
        
        Args:
            file_path: Path to the file
            qualifiers: Optional qualifiers
            
        Returns:
            SWHID for the file content
        """
        with open(file_path, 'rb') as f:
            content = f.read()
        
        object_id = cls.git_sha1(content, "blob")
        return SWHID(SWHIDType.CONTENT, object_id, qualifiers)
    
    @classmethod
    def directory_swhid(cls, dir_path: str, qualifiers: Optional[Dict[str, str]] = None) -> SWHID:
        """
        Generate SWHID for directory.
        
        Args:
            dir_path: Path to the directory
            qualifiers: Optional qualifiers
            
        Returns:
            SWHID for the directory
        """
        # Create directory manifest like Git tree object
        entries = []
        
        try:
            for item in sorted(os.listdir(dir_path)):
                item_path = os.path.join(dir_path, item)
                
                # Skip hidden files and common ignore patterns
                if item.startswith('.'):
                    continue
                
                if os.path.isfile(item_path):
                    # File entry
                    with open(item_path, 'rb') as f:
                        content = f.read()
                    file_hash = cls.git_sha1(content, "blob")
                    # Mode 100644 for regular files
                    entries.append(f"100644 {item}\0{bytes.fromhex(file_hash)}")
                elif os.path.isdir(item_path):
                    # Directory entry (recursive)
                    subdir_swhid = cls.directory_swhid(item_path)
                    # Mode 040000 for directories
                    entries.append(f"040000 {item}\0{bytes.fromhex(subdir_swhid.object_id)}")
        except (PermissionError, OSError):
            # Handle permission errors gracefully
            pass
        
        # Sort entries by name (Git tree order)
        entries.sort()
        
        # Create tree content
        tree_content = b""
        for entry in entries:
            if isinstance(entry, str):
                # Handle mixed string/bytes for mode and name
                parts = entry.split('\0')
                if len(parts) == 2:
                    mode_name = parts[0].encode('ascii')
                    hash_bytes = parts[1] if isinstance(parts[1], bytes) else parts[1].encode('ascii')
                    tree_content += mode_name + b'\0' + hash_bytes
            else:
                tree_content += entry
        
        object_id = cls.git_sha1(tree_content, "tree")
        return SWHID(SWHIDType.DIRECTORY, object_id, qualifiers)
    
    @classmethod
    def from_analysis_result(cls, analysis_result: Dict[str, Any], 
                           enable_swhid: bool = False,
                           include_directory: bool = False) -> List[SWHID]:
        """
        Generate SWHIDs from CopycatM analysis results.
        
        Args:
            analysis_result: CopycatM analysis result
            enable_swhid: Whether SWHID generation is enabled
            include_directory: Whether to include directory SWHID (performance impact)
            
        Returns:
            List of relevant SWHIDs
        """
        if not enable_swhid:
            return []
            
        swhids = []
        
        # File-level SWHID
        file_path = analysis_result.get('file_path', '')
        if file_path and os.path.exists(file_path):
            qualifiers = {}
            
            # Add origin if available
            if 'metadata' in analysis_result:
                metadata = analysis_result['metadata']
                if 'repository_url' in metadata:
                    qualifiers['origin'] = metadata['repository_url']
            
            try:
                content_swhid = cls.content_swhid(file_path, qualifiers)
                swhids.append(content_swhid)
            except (OSError, IOError):
                pass
        
        # Algorithm-specific SWHIDs with line qualifiers (lightweight)
        algorithms = analysis_result.get('algorithms', [])
        for algo in algorithms:
            if 'location' in algo and file_path:
                location = algo['location']
                start_line = location.get('start')
                end_line = location.get('end')
                
                if start_line and end_line:
                    algo_qualifiers = qualifiers.copy() if qualifiers else {}
                    
                    # Add function path qualifier
                    func_name = algo.get('function_name', 'unknown')
                    if func_name != 'unknown':
                        algo_qualifiers['path'] = f"/{func_name}"
                    
                    # Add line range
                    if start_line == end_line:
                        algo_qualifiers['lines'] = str(start_line)
                    else:
                        algo_qualifiers['lines'] = f"{start_line}-{end_line}"
                    
                    try:
                        algo_swhid = cls.content_swhid(file_path, algo_qualifiers)
                        swhids.append(algo_swhid)
                    except (OSError, IOError):
                        pass
        
        # Directory SWHID (optional, performance impact)
        if include_directory and file_path:
            try:
                dir_path = os.path.dirname(file_path)
                if dir_path and os.path.exists(dir_path):
                    dir_swhid = cls.directory_swhid(dir_path, qualifiers.copy() if qualifiers else {})
                    swhids.append(dir_swhid)
            except (OSError, IOError):
                pass
        
        return swhids


def validate_swhid(swhid_string: str) -> bool:
    """
    Validate a SWHID string.
    
    Args:
        swhid_string: SWHID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        SWHID.parse(swhid_string)
        return True
    except InvalidSWHIDError:
        return False


def normalize_swhid(swhid_string: str) -> str:
    """
    Normalize a SWHID string (fix common issues like case).
    
    Args:
        swhid_string: SWHID string to normalize
        
    Returns:
        Normalized SWHID string
        
    Raises:
        InvalidSWHIDError: If the SWHID cannot be normalized
    """
    # Basic normalization: lowercase the core identifier
    parts = swhid_string.split(';', 1)
    core = parts[0].lower()
    
    # Reconstruct
    if len(parts) > 1:
        normalized = core + ';' + parts[1]
    else:
        normalized = core
    
    # Validate the result
    if not validate_swhid(normalized):
        raise InvalidSWHIDError(f"Cannot normalize invalid SWHID: {swhid_string}")
    
    return normalized


# Export main classes and functions
__all__ = [
    'SWHID',
    'SWHIDType', 
    'SWHIDGenerator',
    'SWHIDError',
    'InvalidSWHIDError',
    'validate_swhid',
    'normalize_swhid'
]