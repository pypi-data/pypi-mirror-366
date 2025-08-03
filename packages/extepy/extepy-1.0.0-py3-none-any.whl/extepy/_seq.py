from copy import copy


def cycleperm(values, cycle):
    """Permutate a list according to cycle notation.

    Parameters:
        values (list): Sequence to permutate.
        cycle (list): Permutation rule in cyclc notation.

    Returns:
        list: Permutated sequence.

    Examples:
        Permutate a list of strings.

        >>> cycleperm(["a", "b", "c", "d", "e", "f", "g"], cycle=[1, 2, 4])
        ['a', 'c', 'e', 'd', 'b', 'f', 'g']

        Permutate a list of integers.

        >>> cycleperm(list(range(6)), cycle=[0, 1, 2])
        [1, 2, 0, 3, 4, 5]
    """
    results = copy(values)
    for i, v in enumerate(cycle):
        results[v] = values[cycle[(i+1) % len(cycle)]]
    return results


def swap(values, i=0, j=1):
    """Swap two elements in a list.

    Parameters:
        values (list): Sequence to permutate.
        i (int): Index of the first element to swap.
        j (int): Index of the second element to swap.

    Returns:
        list: Swapped sequence.

    Examples:
        Swap two elements for a list of strings.

        >>> swap(["a", "b", "c", "d", "e", "f", "g"], i=1, j=2)
        ['a', 'c', 'b', 'd', 'e', 'f', 'g']

        Swap two elements for a list of integers.

        >>> swap(list(range(6)), i=1, j=2)
        [0, 2, 1, 3, 4, 5]
    """
    return cycleperm(values, cycle=[i, j])


def prioritize(values, index, dup="multiple"):
    """Move some elements in the sequence to the beginning.

    Parameters:
        values (list | tuple | str): Sequence to permutate.
        index (int | list[int]): Index of the elements to move to the beginning.
            The index can be negative. If there are duplicated index values, the same
            element will appear multiple times.
        dup (``{"multiple", "unique", "raise"}``): Specify how to deal with the case that
            the same position is prioritized mutliple times.
            ``"multiple"``: The same element will appear multiple times.
            ``"unique"``: The same element will appear only once.
            ``"raise"``: Raise an error.

    Returns:
        list | tuple | str:

    Examples:

        Move a single positional argument to the beginning.

        >>> prioritize(["a", "b", "c", "d"], index=-2)
        ['c', 'a', 'b', 'd']

        Move multiple positional arguments to the beginning.

        >>> prioritize(["a", "b", "c", "d"], index=[0, 2, -2])
        ['a', 'c', 'c', 'b', 'd']
        >>> prioritize(["a", "b", "c", "d"], index=[0, 2, -2], dup="unique")
        ['a', 'c', 'b', 'd']
    """
    assert dup in ["multiple", "unique", "raise"]
    count = len(values)
    if isinstance(index, int):
        indices = [index]
    else:
        indices = list(index)
    useds = [False, ] * count
    results = []
    for idx in indices:
        if useds[idx]:
            if dup == "unique":
                continue
            elif dup == "raise":
                raise ValueError("duplicated index: %d", idx)
        useds[idx] = True
        result = values[idx]
        results.append(result)
    for idx, used in enumerate(useds):
        if not used:
            result = values[idx]
            results.append(result)
    results = type(values)(results)
    return results
