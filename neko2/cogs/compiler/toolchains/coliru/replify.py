#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executes a file as if it were in the interactive Python shell.

Thanks to @Dusty.P￱￲#6857 for the idea!

References:
    https://docs.python.org/3/library/ast.html#abstract-grammar
    https://greentreesnakes.readthedocs.io/en/latest/tofrom.html#fix-locations
    https://greentreesnakes.readthedocs.io/en/latest/manipulating.html#modifying-the-tree
    https://docs.python.org/3/library/functions.html#compile
    https://docs.python.org/3/library/sys.html#sys.displayhook
    
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
import ast
import fileinput
import inspect
import sys
import textwrap


def main():
    # How to parse each module level statement.
    FIRST_MODE = "exec"
    # How to parse each individual statement.
    SECOND_MODE = "single"
    FILENAME = "<discord>"
    # Number of digits to display for the line number
    DISPLAY_HOOK_DIGITS = 5

    # Note When compiling a string with multi-line code in 'single' or 'eval'
    # mode, input must be terminated by at least one newline character. This
    # is to facilitate detection of incomplete and complete statements in
    # the code module.
    source = "".join(fileinput.input())

    while not source.endswith("\n\n"):
        source += "\n"

    # Parse the entire tree first.
    tree = ast.parse(source, FILENAME, FIRST_MODE)

    # The namespace to execute in. Emulates the default namespace
    # minus the clutter we just created in this file.
    gs = globals()
    ns = dict(
        __loader__=gs["__loader__"],
        __name__="__main__",
        __package__=None,
        __doc__=None,
        __spec__=None,
        __annotations__={},
        __builtins__=gs["__builtins__"],
    )

    # Walk each statement, and execute interactively.
    for stmt in tree.body:
        try:
            # Generate the interactive statement.
            curr = ast.Interactive(body=[stmt])
            # Compile the statement
            code = compile(curr, FILENAME, SECOND_MODE)
        except Exception as ex:
            traceback.print_exc()
            exit(2)

        # Set up hooks. We do this on each statement to ensure the
        # hooks print out the info I want them to. It probably isn't
        # overly necesarry to do this, but whatever. Not like it is
        # going to make that much of a difference for our applications.

        # Set up a custom display hook to output more useful information
        # than the default one does for the Python repl.
        def displayhook(value):
            if value is None:
                return

            if not isinstance(value, str):
                value = repr(value)
            first, nl, rest = value.partition("\n")

            if nl and rest:
                rest = textwrap.indent(
                    rest,
                    DISPLAY_HOOK_DIGITS * " " + " |",
                    lambda _: True,  # Ensures empty lines get output.
                )

            string = first + nl + rest

            print(("#{:0%s}" % DISPLAY_HOOK_DIGITS).format(stmt.lineno), string)

        # Modify the except hook to cause the code to terminate. Since this
        # is an entire source code file behaving as a repl input, continuing
        # after an error would be potentially undesirable, or produce a
        # chain of errors.
        def excepthook(type, value, tb):
            traceback.print_exception(type, value, tb)
            sys.stderr.write("I won't bother continuing...\n")
            exit(3)

        sys.displayhook = displayhook
        sys.excepthook = excepthook

        exec(code, ns)


if __name__ == "__main__":
    main()
