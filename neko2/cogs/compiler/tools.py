#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other utility bits and pieces.
"""
import re


__inline_block = r'`([^\s`][^`]*?)`'

# Matches the file name and source in a block formatted like so.
#
# `foobar.py`
# ```python
# def foobar():
#     return baz
# ```
#
# ... language is ignored
__fnab = (
    r'`((?:[^.\s\\/`][^`\\/]*){1}?)`'
    r'\s*```(?:[a-zA-Z0-9]+)?\s([\s\S(^\\`{3})]*?)\s*```'
)
__highlighted_block = r'```([a-zA-Z0-9]+)\s([\s\S(^\\`{3})]*?)\s*```'

# Used to detect code blocks.
code_block_re = re.compile(__highlighted_block)

# A general inline block
inline_block_re = re.compile(__inline_block)

# Detects a backticked filename
file_name_and_block_re = re.compile(__fnab)

# Used to detect four-space indentation in Makefiles so that they can be
# replaced with tab control characters.
four_space_re = re.compile(r'^ {4}')


def fix_makefile(input_code: str) -> str:
    """
    Fixes makefiles so they actually compile. This converts any leading
    quadruple spaces on a line to a horizontal tab character.
    :param input_code: the input string.
    :return: the makefile-friendly string.
    """
    strings = []
    for line in input_code.splitlines():
        while four_space_re.match(line):
            line = four_space_re.sub('\t', line)
        strings.append(line)
    return '\n'.join(strings)
