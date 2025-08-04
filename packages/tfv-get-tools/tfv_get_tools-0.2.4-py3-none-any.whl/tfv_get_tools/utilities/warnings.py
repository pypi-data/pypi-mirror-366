import warnings
import functools


def deprecated(new_func):
    """
    Decorator to mark functions as deprecated.
    
    This decorator will result in a warning being emitted
    when the decorated function is used.
    
    Args:
        new_func (callable): The new function to be used instead of the deprecated function.
    
    Returns:
        callable: A decorator function.
    
    Example:
        >>> def new_function(x, y):
        ...     return x + y
        ...
        >>> @deprecated(new_function)
        ... def old_function(x, y):
        ...     return new_function(x, y)
        ...
        >>> old_function(1, 2)
        3
        # Warning: Call to deprecated function old_function. Use new_function instead.
    """
    def decorator(old_func):
        @functools.wraps(old_func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"Call to deprecated function {old_func.__name__}. "
                          f"Use {new_func.__name__} instead.",
                          category=DeprecationWarning, stacklevel=2)
            return new_func(*args, **kwargs)
        return wrapper
    return decorator