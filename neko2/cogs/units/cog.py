#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Listens to messages on all channels, and tests if any substrings can be found
that appear to be units of measurement.

A reaction is then added to the corresponding message for a given period of
time. Interacting with it will trigger the main layer of logic in this
extension.

On a positive hit, we convert those into an SI representation and then back to
every commonly used possibility.
"""

