#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


def _(module: str):
    return f'neko2.cogs.{module}'


modules = frozenset({
    _('coliru'),
    _('mew'),
    _('admin'),
    _('cat'),
    _('cpp'),
    _('discord'),
    _('f'),
    _('botupdate'),
    _('latex'),
    _('man'),
    _('py'),
    _('tldr'),
    _('ud'),
    _('urlshorten'),
    _('wordnik'),
})
