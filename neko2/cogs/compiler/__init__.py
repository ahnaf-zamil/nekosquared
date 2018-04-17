#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
from . import coliru


def setup(bot):
    bot.add_cog(coliru.ColiruCog())
