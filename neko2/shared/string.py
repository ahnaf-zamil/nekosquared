#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
String manipulation utilities.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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


def trunc(text, max_length: int = 2000):
    """Truncates output if it is too long."""
    if len(text) <= max_length:
        return text
    else:
        return text[0:max_length - 3] + '...'


def plur_simple(cardinality: int, word: str, suffix='s'):
    """Pluralises words that just have a suffix if pluralised."""
    if cardinality - 1:
        word += suffix
    return f'{cardinality} {word}'


def plur_diff(cardinality: int, singular: str, plural: str):
    """Pluralises words that change spelling when pluralised."""
    return f'{cardinality} {plural if cardinality - 1 else singular}'


def yn(boolean: bool) -> str:
    """Converts 'True' or 'False' to 'Yes' or 'No'"""
    return 'Yes' if boolean else 'No'


def cap(string):
    """Capitalises stuff."""
    return string[0:1].upper() + string[1:]
