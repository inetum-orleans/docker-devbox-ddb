import math


def _get_content(content: str, line_length: int, centered: bool = True):
    left = ' '
    right = (line_length - len(content) - 1) * ' '

    if centered:
        left = math.floor((line_length - len(content)) / 2) * ' '
        right = math.ceil((line_length - len(content)) / 2) * ' '

    return left + content + right


def _max_length(header: str, cells) -> int:
    max_length = len(header)
    for cell in cells:
        for row in cell:
            length = len(row)
            if length > max_length:
                max_length = length
    return max_length


def get_table_display(header: str, cells, centered: bool = True):
    """
    Convert the input data into a table with centered text
    :param header: the header of the table
    :param cells: the different cells. A cell is a set of rows
    :param centered: if the cell content is centered or not
    :return:
    """
    line_length = _max_length(header, cells) + 2

    content = [
        ('+' + (line_length * '-') + '+'),
        ('|' + _get_content(header, line_length, centered) + '|'),
        ('+' + (line_length * '-') + '+')
    ]

    for cell in cells:
        for row in cell:
            content.append('|' + _get_content(row, line_length, centered) + '|')
        content.append('+' + (line_length * '-') + '+')
    return '\n'.join(content)
