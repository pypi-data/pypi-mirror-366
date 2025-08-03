from ._fun import skewer


def groupby(values, by):
    """Partition values into several groups, and return a dict.

    Parameters:
        values (iterable):
        by (callable): The function to get the group of a value.

    Returns:
        groups (dict[hashable, list])

    Raises:
        TypeError: Raises when a return value of ``by()`` is not hashable.

    Examples:
        >>> groupby(range(10), lambda x: x % 3)
        {0: [0, 3, 6, 9], 1: [1, 4, 7], 2: [2, 5, 8]}

        >>> groupby([0, "", False, float('nan'), "Hello"], by=bool)
        {False: [0, '', False], True: [nan, 'Hello']}
    """
    groups = {}
    for value in values:
        group = by(value)
        groups.setdefault(group, []).append(value)
    return groups


def partition(values, by, count=None):
    """Partition values into several groups, and return lists.

    Parameters:
        values (iterable):
        by (callable): Function to get the group index of a value.
            Its return value will be wrapped by ``int()``.
        count (int, Optional): Number of groups.

    Returns:
        results (list[list]):

    Examples:
        >>> partition(range(10), by=lambda x: x % 3)
        [[0, 3, 6, 9], [1, 4, 7], [2, 5, 8]]

        Specify the number of groups.

        >>> partition([0, "", False, float('nan'), "Hello"], by=bool, count=3)
        [[0, '', False], [nan, 'Hello'], []]

        Raise error when the group index exceeds range.

        >>> partition([-1, 1], by=int)
        Traceback (most recent call last):
        ...
        ValueError: Group index should be >= 0.
    """
    groups = groupby(values, by=skewer(by, int))
    mingroup = min(groups)
    maxgroup = max(groups)
    if mingroup < 0:
        raise ValueError("Group index should be >= 0.")
    if count is not None:
        if maxgroup >= count:
            raise ValueError("Group index should be < count.")
    assert mingroup >= 0
    assert (count is None) or (maxgroup < count)
    count = count or maxgroup + 1
    results = []
    for key in range(count):
        result = groups.get(key, [])
        results.append(result)
    return results
