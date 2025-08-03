try:
    from math import nan
except ImportError:
    nan = float('nan')


def fillerr(value=None):
    """Decorator that returns a default value when an error occurs.

    Parameters:
        value (optional): Default value to return when an error occurs.

    Returns:
        callable:

    Examples:
        >>> @fillerr()
        ... def f(x):
        ...     return 1.0 / x
        >>> f(0.0)  # Return None, print nothing.
        >>> f(1.0)
        1.0
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception:
                return value
        return wrapper
    return decorator


def fillwhen(check, value):
    """Decorator that returns a default value if a condition is met.

    Parameters:
        check (callable): Condition checker.
        value : Value to return when the condition is met.

    Returns:
        callable:

    Examples:
        >>> from math import isnan
        >>> @fillwhen(isnan, 0)
        ... def f(x):
        ...     return x
        >>> f(float('nan'))
        0
        >>> f(1)
        1
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if check(result):
                return value
            else:
                return result
        return wrapper
    return decorator


def fillnone(value=nan):
    """Decorator that returns a default value if the result is ``None``.

    Parameters:
        value : Value to return if the result is ``None``.

    Returns:
        callable:

    Examples:
        >>> @fillnone(-1)
        ... def f(x):
        ...     return x
        >>> f(None)
        -1
        >>> f(float('nan'))
        nan
        >>> f(False)
        False
        >>> f(0)
        0
    """
    def isnone(arg):
        return arg is None

    def decorator(f):
        return fillwhen(isnone, value)(f)
    return decorator
