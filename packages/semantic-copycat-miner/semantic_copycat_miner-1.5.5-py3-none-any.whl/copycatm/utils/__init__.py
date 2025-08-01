"""
Utility components for CopycatM.
"""

from .file_utils import get_file_extension, is_supported_language
from .json_utils import format_output
from .logging_utils import setup_logging

__all__ = [
    "get_file_extension",
    "is_supported_language",
    "format_output",
    "setup_logging",
] 