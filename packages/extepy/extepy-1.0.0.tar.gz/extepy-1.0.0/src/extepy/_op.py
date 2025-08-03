from copy import copy as shallowcopy, deepcopy

import sys
if sys.version_info[0] == 2:  # Python 2
    string_types = (basestring,)  # noqa: F821
else:  # Python 3.1+
    string_types = (str,)


def argchecker(*keys):
    """Return a callable object to check the existences of argument(s).

    Args:
        *keys (int | str):
            If it is an ``int`` (can be negative), it is the index of the positional argument to be fetched.
            If it is a ``str``, it is the name of keyword argument to be fetched.

    Returns:
        bool | tuple[bool]:

    Examples:
        >>> getter = argchecker(-1, 0, 1, 5, "key", "other")
        >>> getter("a", "b", "c", key="value")
        (True, True, True, False, True, False)

    """
    def checker(*args, **kwargs):
        count = len(args)
        results = []
        for key in keys:
            if isinstance(key, string_types):
                result = key in kwargs
            else:
                result = (-count <= key < count)
            results.append(result)
        if len(results) == 1:
            # If only one result, return it directly
            return results[0]
        return tuple(results)
    return checker


def arggetter(*keys):
    """Return a callable object that fetches the argument(s) from its operand.

    Args:
        *keys (int | str):
            If it is an ``int`` (can be negative), it is the index of the positional argument to be fetched.
            If it is a ``str``, it is the name of keyword argument to be fetched.

    Returns:
        callable:

    Raises:
        KeyError | IndexError: Raises when the argument is not found.

    Examples:
        Get the first positional argument.

        >>> getter = arggetter(0)
        >>> getter("a", "b", "c", key="value")
        'a'

        Get the positional arguments and keyword arguments.

        >>> getter = arggetter(-1, 0, 1, "key")
        >>> getter("a", "b", "c", key="value")
        ('c', 'a', 'b', 'value')

        Raise an error if the index is out of range.

        >>> getter = arggetter(0, 1, 2)
        >>> getter("A", key="value")
        Traceback (most recent call last):
        ...
        IndexError: positional argument index is out of range
    """
    def getter(*args, **kwargs):
        results = []
        for key in keys:
            if isinstance(key, string_types):
                if key in kwargs:
                    result = kwargs[key]
                else:
                    raise KeyError("keyword argument '%s' is missing" % key)
            else:
                count = len(args)
                if -count <= key < count:
                    result = args[key]
                else:
                    raise IndexError("positional argument index is out of range")
                result = args[key]
            results.append(result)
        if len(results) == 1:
            # If only one result, return it directly
            return results[0]
        return tuple(results)
    return getter


def _check_attr(obj, attr):
    """Auxiliary function for attrchecker."""
    for name in attr.split("."):
        if hasattr(obj, name):
            obj = getattr(obj, name)
        else:
            return False
    return True


def attrchecker(*attrs):
    """Return a callable object to check the existence of the given attribute(s).

    Args:
        *attrs (str): Attribute names.

    Examples:
        >>> c = attrchecker("mro", "type")
        >>> c(type)
        (True, False)

        >>> import os
        >>> c = attrchecker("path", "path.sep", "sep.path")
        >>> c(os)
        (True, True, False)
    """
    if len(attrs) == 1:
        attr = attrs[0]

        def c(obj):
            return _check_attr(obj, attr)
    else:

        def c(obj):
            return tuple(_check_attr(obj, attr) for attr in attrs)
    return c


def _check_item(obj, item):
    """Auxiliary function for itemchecker."""
    if not isinstance(item, list):
        item = [item]
    for i in item:
        try:
            obj = obj[i]
        except (IndexError, KeyError):
            return False
    return True


def itemchecker(*items):
    """Return a callable object to check the existence of the given item(s).

    Examples:
        >>> data = {"name": {"first": "Zhiqing", "last": "Xiao"}, "city": "Beijing"}
        >>> c = itemchecker(["name", "first"], ["name", "middle"], ["name", "last"], "city", "sex")
        >>> c(data)
        (True, False, True, True, False)

        >>> itemchecker(-3, 0, 3)([1, 2, 3])
        (True, True, False)
    """
    if len(items) == 1:
        item = items[0]

        def c(obj):
            return _check_item(obj, item)
    else:

        def c(obj):
            return tuple(_check_item(obj, item) for item in items)
    return c


class constantcreator:
    """Callable that returns the same constant when it is called.

    Args:
        value : Constant value to be returned.
        copy : If ``True``, return a new copy of the constant value.

    Returns:
        callable: Callable object that returns ``value``, ignoring its parameters.

    Examples:
        Always return the string ``"value"``.

        >>> creator = constantcreator("value")
        >>> creator()
        'value'

        Create a pd.DataFrame whose elements are all empty lists.

        >>> import pandas as pd
        >>> df = pd.DataFrame(index=range(3), columns=["A"])
        >>> (df.map if hasattr(df, "map") else df.applymap)(constantcreator([]))
            A
        0  []
        1  []
        2  []

        Return a new copy when ``copy=True``.

        >>> import pandas as pd
        >>> df = pd.DataFrame(index=range(3), columns=["A"])
        >>> constantcreator(df, copy=True)() is df
        False
    """
    def __init__(self, value, copy=False):
        self.value = value
        if copy:
            if copy in ["shallow", shallowcopy]:
                copy = shallowcopy
            else:
                copy = deepcopy
        else:
            copy = arggetter(0)
        self.copy = copy

    def __call__(self, *args, **kwargs):
        return self.copy(self.value)
