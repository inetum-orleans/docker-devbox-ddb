def build_or_pattern(patterns):
    """
    Build a or pattern string from a list of possible patterns
    :param patterns:
    :type patterns:
    :param name:
    :type name:
    :param escape:
    :type escape:
    :return:
    :rtype:
    """
    if len(patterns) == 1:
        return patterns[0]
    or_pattern = []
    for pattern in patterns:
        if or_pattern:
            or_pattern.append('|')
        else:
            or_pattern.append('(?:')
        or_pattern.append(pattern)
    if or_pattern:
        or_pattern.append(')')
    return ''.join(or_pattern)
