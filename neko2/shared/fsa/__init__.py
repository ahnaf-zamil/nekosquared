#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

Discord.py-compatible finite state machines.

Finite-state automata bits and pieces. These are mini state-machines for dealing
with things such as user input, pagination of messages, and tracking user
interaction in a stateful way using async iterators.
"""

# Assumes __all__ attributes are set correctly in each file.
from .button import *
from .abstractmachines import *
from .pag import *
from .options import *
