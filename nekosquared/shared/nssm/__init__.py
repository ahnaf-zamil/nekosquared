"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Nekozilla small scripting module

This is being redesigned from scratch. The aim this time is to make it less
C-like and closer to shell scripting languages such as bash. These should be
easier to parse than C-style languages on the basis that the tokens for ending
scope blocks is much more discrete.

The reason behind this module is that there is no safe way currently of
sand-boxing an existing language for use on Discord without exposing security
vulnerabilities either in the form of the ability to segfault the interpreter
or to access the underlying file system, perform I/O, etc. It is therefore
much simpler to just write my own implementation of a scripting module.

This consists of five main files

- ``ast.py`` - this contains implementations of various abstract syntax tree
    constructs.
- ``interpreter.py`` - this executes a given AST with a given collection
    of globals.
- ``lexer.py`` - this takes string input and tokenizes it, outputting a stream
    of token objects.
- ``parser.py`` - this consumes a stream of token objects and generates an
    abstract syntax tree from it.
- ``tokens.py`` - contains implementations of token data types.

There is also an entry point to provide a primitive interpreter session, and
``util.py`` which holds some shared utilities between the modules in this
package.
"""