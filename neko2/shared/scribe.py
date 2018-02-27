#!/usr/bin/env python3.6
# -*- coding: utf-8
"""
Loggable class.
"""
import logging

__all__ = ('Scribe',)


class Scribe:
    """Adds functionality to a class to allow it to log information."""
    logger: logging.Logger

    logging.basicConfig(level='INFO')

    def __init_subclass__(cls, **_):
        cls.logger: logging.Logger = logging.getLogger(cls.__name__)
