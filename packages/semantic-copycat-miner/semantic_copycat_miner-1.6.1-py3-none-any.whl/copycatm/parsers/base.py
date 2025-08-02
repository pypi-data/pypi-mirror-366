"""
Base parser interface for CopycatM.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseParser(ABC):
    """Base interface for code parsers."""
    
    @abstractmethod
    def parse(self, code: str, language: str) -> Any:
        """Parse code and return AST tree."""
        pass
    
    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Check if parser supports the given language."""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages."""
        pass
    
    def normalize_ast(self, ast_tree: Any) -> Any:
        """Normalize AST tree for consistent analysis."""
        # Default implementation - subclasses can override
        return ast_tree
    
    def extract_functions(self, ast_tree: Any) -> list[Any]:
        """Extract function definitions from AST."""
        # Default implementation - subclasses can override
        return []
    
    def extract_variables(self, ast_tree: Any) -> list[str]:
        """Extract variable names from AST."""
        # Default implementation - subclasses can override
        return []
    
    def extract_imports(self, ast_tree: Any) -> list[str]:
        """Extract import statements from AST."""
        # Default implementation - subclasses can override
        return []
    
    def get_node_type(self, node: Any) -> str:
        """Get the type of an AST node."""
        # Default implementation - subclasses can override
        return "unknown"
    
    def get_node_value(self, node: Any) -> str:
        """Get the value of an AST node."""
        # Default implementation - subclasses can override
        return ""
    
    def get_node_children(self, node: Any) -> list[Any]:
        """Get children of an AST node."""
        # Default implementation - subclasses can override
        return [] 