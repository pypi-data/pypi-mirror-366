"""
Custom exceptions for CopycatM.
"""


class CopycatError(Exception):
    """Base exception for all CopycatM errors."""


class UnsupportedLanguageError(CopycatError):
    """Language not supported or parser unavailable."""


class ParseError(CopycatError):
    """Code parsing failed."""


class AnalysisError(CopycatError):
    """Analysis pipeline failed."""


class ConfigurationError(CopycatError):
    """Invalid configuration."""
