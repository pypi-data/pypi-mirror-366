"""
Optional dependency management for CopycatM.

This module provides utilities for handling optional dependencies gracefully,
avoiding repetitive warning messages and providing clear feature availability.
"""

import logging
from typing import Optional, Callable, Any, Dict
from functools import wraps

logger = logging.getLogger(__name__)


class OptionalDependency:
    """Manages optional dependencies with singleton pattern to avoid repeated warnings."""
    
    _instances: Dict[str, 'OptionalDependency'] = {}
    _warnings_shown: Dict[str, bool] = {}
    
    def __new__(cls, package_name: str, feature_name: Optional[str] = None):
        """Create or return existing instance for package."""
        if package_name not in cls._instances:
            cls._instances[package_name] = super().__new__(cls)
        return cls._instances[package_name]
    
    def __init__(self, package_name: str, feature_name: Optional[str] = None):
        """Initialize optional dependency checker.
        
        Args:
            package_name: Name of the package to check
            feature_name: Human-readable feature name (defaults to package_name)
        """
        if hasattr(self, '_initialized'):
            return
        
        self.package_name = package_name
        self.feature_name = feature_name or package_name
        self._available = None
        self._module = None
        self._initialized = True
    
    @property
    def available(self) -> bool:
        """Check if dependency is available."""
        if self._available is None:
            try:
                self._module = __import__(self.package_name)
                self._available = True
            except ImportError:
                self._available = False
                self._show_warning_once()
        return self._available
    
    @property
    def module(self) -> Optional[Any]:
        """Get the imported module if available."""
        if self.available:
            return self._module
        return None
    
    def _show_warning_once(self):
        """Show warning only once per package."""
        if self.package_name not in self._warnings_shown:
            self._warnings_shown[self.package_name] = True
            logger.info(f"{self.feature_name} features disabled ({self.package_name} not installed)")
    
    def require(self, func: Callable) -> Callable:
        """Decorator to require this dependency for a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.available:
                raise ImportError(
                    f"{self.feature_name} requires {self.package_name}. "
                    f"Install with: pip install {self.package_name}"
                )
            return func(*args, **kwargs)
        return wrapper
    
    def optional(self, default: Any = None) -> Callable:
        """Decorator to make function optional based on dependency."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.available:
                    return default
                return func(*args, **kwargs)
            return wrapper
        return decorator


# Common optional dependencies
sklearn_dep = OptionalDependency('sklearn', 'Machine learning')
watchdog_dep = OptionalDependency('watchdog', 'File watching')
torch_dep = OptionalDependency('torch', 'PyTorch neural networks')
networkx_dep = OptionalDependency('networkx', 'Graph analysis')


def check_dependencies():
    """Check and report status of all optional dependencies."""
    deps = {
        'scikit-learn': sklearn_dep,
        'watchdog': watchdog_dep,
        'torch': torch_dep,
        'networkx': networkx_dep,
    }
    
    status = {}
    for name, dep in deps.items():
        status[name] = {
            'available': dep.available,
            'feature': dep.feature_name
        }
    
    return status


def requires(*dependencies: str):
    """Decorator to require multiple dependencies.
    
    Args:
        *dependencies: Package names required
        
    Example:
        @requires('sklearn', 'torch')
        def train_model():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            missing = []
            for dep_name in dependencies:
                dep = OptionalDependency(dep_name)
                if not dep.available:
                    missing.append(dep_name)
            
            if missing:
                raise ImportError(
                    f"Missing required dependencies: {', '.join(missing)}. "
                    f"Install with: pip install {' '.join(missing)}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator