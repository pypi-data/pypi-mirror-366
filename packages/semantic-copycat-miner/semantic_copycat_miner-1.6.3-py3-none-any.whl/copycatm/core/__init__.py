"""
Core analysis components for CopycatM.
"""

# Import the enhanced analyzer as the main analyzer
from .analyzer import CopycatAnalyzer
from .three_tier_analyzer import ThreeTierAnalyzer
from .config import AnalysisConfig
from .exceptions import (
    CopycatError,
    UnsupportedLanguageError,
    ParseError,
    AnalysisError,
    ConfigurationError,
)

__all__ = [
    "CopycatAnalyzer",
    "ThreeTierAnalyzer",
    "AnalysisConfig",
    "CopycatError",
    "UnsupportedLanguageError",
    "ParseError",
    "AnalysisError",
    "ConfigurationError",
] 