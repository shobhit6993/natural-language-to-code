import numpy as np

from constants import *


def channel_template():
    return {ID: "", CONF: 0., FUNCTION: functions_template()}


def functions_template():
    return {ID: "", CONF: 0., FIELDS: []}


def fields_template():
    return {ID: "", VALUE: "", CONF: 0.}


def levenshtein_distance(source, target):
    """Computes edit-distance between the `source` and `target` strings.

    Args:
        source (str): Source string.
        target (str): Target string.

    Returns:
        int: Edit-distance between the two strings.
    """
    if len(source) < len(target):
        return levenshtein_distance(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
            current_row[1:],
            np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
            current_row[1:],
            current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


def longest_common_subsequence(a, b):
    """Computes the length of longest common subsequence between two strings

    Args:
        a (str): First string.
        b (str): Second string.

    Returns:
        int: Length of longest common subsequence.
    """
    # Source: https://rosettacode.org/wiki/Longest_common_subsequence#Python
    lengths = [[0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j],
                                            lengths[i][j + 1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x - 1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y - 1]:
            y -= 1
        else:
            assert a[x - 1] == b[y - 1]
            result = a[x - 1] + result
            x -= 1
            y -= 1
    return len(result)
