"""
Comprehensive error handling utilities for CopycatM.

This module provides decorators and utilities for consistent error handling,
logging, and recovery across the codebase.
"""

import functools
import logging
import traceback
import time
from typing import Callable, Optional, Any, Type, Tuple, Dict

from ..core.exceptions import (
    ParseError,
    AnalysisError,
    ConfigurationError
)

logger = logging.getLogger(__name__)


class ErrorContext:
    """Context manager for detailed error tracking."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """Initialize error context.
        
        Args:
            operation: Description of operation being performed
            details: Additional context details
        """
        self.operation = operation
        self.details = details or {}
        self.start_time = None
    
    def __enter__(self):
        """Enter context."""
        self.start_time = time.time()
        logger.debug(f"Starting {self.operation}", extra=self.details)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context with error handling."""
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.debug(f"Completed {self.operation} in {duration:.2f}s", extra=self.details)
        else:
            logger.error(
                f"Failed {self.operation} after {duration:.2f}s: {exc_val}",
                extra={**self.details, 'traceback': traceback.format_exc()}
            )
        
        # Don't suppress exceptions
        return False


def safe_operation(
    operation_name: str,
    default_return: Any = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_errors: bool = True,
    reraise: bool = False
) -> Callable:
    """Decorator for safe operation execution with error handling.
    
    Args:
        operation_name: Name of operation for logging
        default_return: Value to return on error
        exceptions: Tuple of exceptions to catch
        log_errors: Whether to log errors
        reraise: Whether to reraise exceptions
        
    Example:
        @safe_operation("parse_file", default_return={})
        def parse_file(path):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_errors:
                    # Extract meaningful context from args
                    context = {}
                    if args and hasattr(args[0], '__class__'):
                        context['class'] = args[0].__class__.__name__
                    if args and len(args) > 1:
                        context['first_arg'] = str(args[1])[:100]
                    
                    logger.error(
                        f"{operation_name} failed: {e}",
                        extra={
                            'function': func.__name__,
                            'context': context,
                            'error_type': type(e).__name__
                        }
                    )
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """Decorator to retry operations on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        backoff: Multiplier for delay after each attempt
        exceptions: Exceptions to retry on
        
    Example:
        @retry_on_error(max_attempts=3, exceptions=(ParseError,))
        def parse_code(code):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
        
        return wrapper
    return decorator


def handle_file_errors(func: Callable) -> Callable:
    """Decorator to handle common file operation errors.
    
    Converts OS-level errors to CopycatM exceptions with better messages.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            file_path = args[1] if len(args) > 1 else 'unknown'
            raise AnalysisError(f"File not found: {file_path}") from e
        except PermissionError as e:
            file_path = args[1] if len(args) > 1 else 'unknown'
            raise AnalysisError(f"Permission denied: {file_path}") from e
        except IsADirectoryError as e:
            file_path = args[1] if len(args) > 1 else 'unknown'
            raise AnalysisError(f"Expected file but got directory: {file_path}") from e
        except OSError as e:
            file_path = args[1] if len(args) > 1 else 'unknown'
            raise AnalysisError(f"OS error accessing {file_path}: {e}") from e
    
    return wrapper


def validate_input(
    param_name: str,
    validator: Callable[[Any], bool],
    error_message: Optional[str] = None
) -> Callable:
    """Decorator to validate function inputs.
    
    Args:
        param_name: Name of parameter to validate
        validator: Function that returns True if valid
        error_message: Custom error message
        
    Example:
        @validate_input('file_path', lambda x: Path(x).exists())
        def analyze_file(self, file_path):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get parameter value
            from inspect import signature
            sig = signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            if param_name in bound_args.arguments:
                value = bound_args.arguments[param_name]
                if not validator(value):
                    msg = error_message or f"Invalid {param_name}: {value}"
                    raise ConfigurationError(msg)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class ErrorRecovery:
    """Strategies for recovering from errors."""
    
    @staticmethod
    def with_fallback(primary: Callable, fallback: Callable, 
                     exceptions: Tuple[Type[Exception], ...] = (Exception,)) -> Any:
        """Execute primary function with fallback on error.
        
        Args:
            primary: Primary function to execute
            fallback: Fallback function if primary fails
            exceptions: Exceptions to catch
            
        Returns:
            Result from primary or fallback function
        """
        try:
            return primary()
        except exceptions as e:
            logger.warning(f"Primary operation failed: {e}. Using fallback.")
            return fallback()
    
    @staticmethod
    def partial_results(func: Callable, items: list, 
                       continue_on_error: bool = True) -> Tuple[list, list]:
        """Process items collecting partial results even if some fail.
        
        Args:
            func: Function to apply to each item
            items: List of items to process
            continue_on_error: Whether to continue on error
            
        Returns:
            Tuple of (successful_results, errors)
        """
        results = []
        errors = []
        
        for item in items:
            try:
                result = func(item)
                results.append(result)
            except Exception as e:
                error_info = {
                    'item': item,
                    'error': str(e),
                    'type': type(e).__name__
                }
                errors.append(error_info)
                
                if not continue_on_error:
                    break
        
        return results, errors


def create_error_report(exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create detailed error report for logging or analysis.
    
    Args:
        exception: The exception that occurred
        context: Additional context information
        
    Returns:
        Dictionary with error details
    """
    import sys
    import platform
    
    report = {
        'error': {
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_exc()
        },
        'system': {
            'platform': platform.system(),
            'python_version': sys.version,
            'copycatm_version': 'unknown'  # Would need to import version
        },
        'timestamp': time.time(),
        'context': context or {}
    }
    
    # Try to get CopycatM version
    try:
        from .. import __version__
        report['system']['copycatm_version'] = __version__
    except:
        pass
    
    return report


# Pre-configured decorators for common use cases
safe_parse = functools.partial(
    safe_operation,
    operation_name="parse",
    exceptions=(ParseError, UnicodeDecodeError),
    default_return=None
)

safe_analyze = functools.partial(
    safe_operation,
    operation_name="analyze",
    exceptions=(AnalysisError,),
    default_return={'algorithms': [], 'error': True}
)

retry_parse = functools.partial(
    retry_on_error,
    max_attempts=2,
    exceptions=(ParseError,),
    delay=0.5
)