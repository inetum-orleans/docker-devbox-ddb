import math
from typing import List, Iterable


def _get_content(content: str, line_length: int, centered: bool = True):
    left = ' '
    right = (line_length - len(content) - 1) * ' '

    if centered:
        left = math.floor((line_length - len(content)) / 2) * ' '
        right = math.ceil((line_length - len(content)) / 2) * ' '

    return left + content + right


def _max_length(cells: Iterable[Iterable[str]]) -> int:
    max_length = 0
    for cell in cells:
        for row in cell:
            length = len(row)
            if length > max_length:
                max_length = length
    return max_length


def get_table_display(blocks: Iterable[Iterable[str]], centered: bool = True):
    """
    Convert the input data into a table with centered text
    :param blocks: the blocks of the table. A block is an iterable of rows.
    :param centered: if the cell content is centered or not
    :return:
    """
    line_length = _max_length(blocks) + 2

    content = []
    for block in blocks:
        content.append('+' + (line_length * '-') + '+')
        for row in block:
            content.append('|' + _get_content(row, line_length, centered) + '|')
    if content:
        content.append('+' + (line_length * '-') + '+')
    return '\n'.join(content)
