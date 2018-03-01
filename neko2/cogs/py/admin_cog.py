#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
Admin utilities for the cacher.

This expects a config file called neko2.cogs.py.targets.yaml to exist in the
config directory. This should be a list of Python modules to index when we are
directed to.
"""
import asyncpg

from neko2.engine import commands
from neko2.shared import configfiles
from neko2.shared import fsa
from neko2.shared import traits


config_file = 'neko2.cogs.py.targets.yaml'


class PyAdminCog(traits.PostgresPool, traits.Scribe):
    """
    Manages generating the database of caches. This is essentially a specific
    schema. This is a separate cog to the main interface for this module, as
    it is just easier to segment the logic. Only the owner should be able to
    use these functions, however.
    """
    def __init__(self):
        self.cache_config = configfiles.get_config_data(config_file)

    @staticmethod
    async def __local_check(ctx):
        """Ensures that the owner is the only one who can run commands here."""
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def py_admin_show_config(self, ctx):
        """Dumps the config."""
        pag = fsa.Pag()
        pag.add_line(str(self.cache_config))

        for page in pag.pages:
            await ctx.send(page)

    @commands.command()
    async def py_admin_cache(self, ctx):
        """
        Uses the config file entries to produce caches. This is written
        to the database.
        """
        await ctx.send(str(await self._generate_schema()))

    @classmethod
    async def _generate_schema(cls):
        """Generates the schema if it does not exist."""
        async with await cls.acquire_db() as conn:
            conn: asyncpg.Connection
            res = await conn.fetchrow('SELECT 1, 2, 3, 4, 5;')
            return res
