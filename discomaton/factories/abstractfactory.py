#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Abstract factory consumer implementation.
"""
import abc
import typing


__all__ = ('AbstractFactory',)


InputT = typing.TypeVar('InputT')
OutputT = typing.TypeVar('OutputT')


class AbstractFactory(abc.ABC, typing.Generic[InputT, OutputT]):
    """Base class to derive factory types from."""

    @abc.abstractmethod
    def build(self) -> OutputT:
        """Builds the item from this factory."""
        pass
