#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
String manipulation utilities.
"""


__all__ = ('remove_single_lines',)


def remove_single_lines(string: str) -> str:
    """
    Attempts to remove single line breaks. This should take into account
    lists correctly this time! This will treat line breaks proceeded by
    anything that is not an alpha as a normal line break to keep. Thus, you
    must ensure each line of a continuing paragraph starts with an alpha
    character if you want it parsed correctly.

    The purpose of this is to fix textual paragraphs obtained from docstrings.

    Todo: implement something to prevent altering code blocks?
    """
    lines = []

    def previous_line():
        if lines:
            return lines[-1]
        else:
            return ''

    for line in string.splitlines():
        line = line.rstrip()

        # Empty line
        if not line:
            lines.append('')

        # Continuation
        elif line[0].isalpha():

            # Doing it this way prevents random leading whitespace.
            current_line = [line]
            if previous_line():
                current_line.insert(0, previous_line())
            current_line = ' '.join(current_line)

            if previous_line():
                lines[-1] = current_line
            else:
                lines.append(current_line)

        # Treat normally: do not alter.
        else:
            lines.append(line)

    return '\n'.join(lines)


def trunc(text, max_length: int=2000):
    """Truncates output if it is too long."""
    if len(text) <= max_length:
        return text
    else:
        return text[0:max_length - 3] + '...'
