"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Entry point to a standalone interpreter session.
"""
import io
import sys

from . import *


with io.StringIO() as ss:
    ss.writelines(sys.stdin.readlines())
    string = ss.getvalue()
    del ss

lex = Lexer(string)


for token in lex:
    print(token)