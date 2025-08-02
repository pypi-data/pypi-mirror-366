"""
CLI components for CopycatM.
"""

from .commands import main
from .utils import setup_logging, get_verbosity_level

__all__ = ["main", "setup_logging", "get_verbosity_level"] 