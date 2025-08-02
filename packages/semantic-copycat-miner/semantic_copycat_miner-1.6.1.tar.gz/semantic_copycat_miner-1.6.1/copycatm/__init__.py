"""
Semantic Copycat Miner (CopycatM)

A semantic analysis tool for detecting AI-generated code derived from copyrighted sources.
"""

__version__ = "1.6.1"
__author__ = "Oscar Valenzuela B."
__email__ = "oscar.valenzuela.b@gmail.com"

from .core import CopycatAnalyzer, AnalysisConfig
from .core.swhid import SWHID, SWHIDGenerator, SWHIDType, validate_swhid, normalize_swhid
from .core.exceptions import (
    CopycatError,
    UnsupportedLanguageError,
    ParseError,
    AnalysisError,
    ConfigurationError,
)

__all__ = [
    "CopycatAnalyzer",
    "AnalysisConfig",
    "SWHID",
    "SWHIDGenerator", 
    "SWHIDType",
    "validate_swhid",
    "normalize_swhid",
    "CopycatError",
    "UnsupportedLanguageError",
    "ParseError",
    "AnalysisError",
    "ConfigurationError",
] 