def flattenSequence(seq):
    if not isinstance(seq, (list, tuple)):
        raise TypeError("The seq is not a list or a tuple.")
    def flattenSub(seq, res):
        for element in seq:
            if isinstance(element, (list, tuple)):
                flattenSub(element, res)
            else:
                res.append(element)
    res = []
    flattenSub(seq, res)
    return res

def ensureInstanceOfType(obj, type_, ignoreErrorTypes=None, default=None):
    if isinstance(obj, type_):
        return obj
    if ignoreErrorTypes is not None:
        ignoreErrorTypes = tuple(flattenSequence(seq))
    else:
        ignoreErrorTypes = ()
    try:
        res = type_(obj)
    except ignoreErrorTypes:
        res = default
    return res

def findNum(l: list, num):
    """Find the position of the num in the sorted list.
    Return the left index,
    or None if the num is less than the first element."""
    assert isinstance(l, list)
    if not l:
        return None
    l = sorted(l)
    if num < l[0]:
        return None
    if num > l[-1]:
        return len(l) - 1
    left = 0
    right = len(l) - 1
    middle = (left + right) // 2
    while middle > left:
        if num < l[middle]:
            right = middle
        elif num > l[middle]:
            left = middle
        else:
            break
        middle = (left + right) // 2
    return middle
