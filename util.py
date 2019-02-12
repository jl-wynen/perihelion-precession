"""
General utilies.
"""

def neighbours(iterable):
    """
    Iterate over pairs of neighbours in iterable.
    Yields pairs equivalent to (iterable[i], iterable[i+1]).
    Each element except for the very first and last appears twice, once as first and once
    as second element.
    """

    iterator = iter(iterable)
    try:
        first = next(iterator)
    except StopIteration:
        # no pairs if there are no elements in iterable
        return

    # the loop body never executes if iterable has only a single element
    for elem in iterator:
        second = elem
        yield first, second
        first = second
