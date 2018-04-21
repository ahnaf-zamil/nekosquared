#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


def _(module: str):
    return f'neko2.cogs.{module}'


modules = frozenset({
    _('compiler'),
    _('mew'),
    _('admin'),
    _('cat'),
    _('cppref'),
    _('discord'),
    _('botupdate'),
    _('man'),
    _('py'),
    _('tldr'),
    _('ud'),
    _('googl'),
    _('wordnik'),
    _('beats'),
    _('unicode'),
    _('rpn'),
    _('xkcd'),
    _('units')
})
