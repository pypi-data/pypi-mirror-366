"""
Custom exceptions for CopycatM.
"""


class CopycatError(Exception):
    """Base exception for all CopycatM errors."""
    pass


class UnsupportedLanguageError(CopycatError):
    """Language not supported or parser unavailable."""
    pass


class ParseError(CopycatError):
    """Code parsing failed."""
    pass


class AnalysisError(CopycatError):
    """Analysis pipeline failed."""
    pass


class ConfigurationError(CopycatError):
    """Invalid configuration."""
    pass 