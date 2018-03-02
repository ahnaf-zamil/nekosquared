#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
Search and admin utilities for the cache system.

This expects a config file called neko2.cogs.py.targets.yaml to exist in the
config directory. This should be a list of Python modules to index when we are
directed to.
"""
import json
import os
import time

import asyncpg
import discord

from neko2.engine import commands
from neko2.shared import configfiles
from neko2.shared import fsa
from neko2.shared import sql
from neko2.shared import traits
from neko2.shared.other import fuzzy

from . import module_cacher

config_file = 'neko2.cogs.py.targets.yaml'


class PyCog(traits.PostgresPool, traits.IoBoundPool, traits.Scribe):
    """
    Manages generating the database of caches, and providing some form of user
    interface into it.
    """

    def __init__(self):
        self.cache_config = configfiles.get_config_data(config_file)

    ############################################################################
    # SQL queries we utilise in this class. This loads them from disk.         #
    ############################################################################

    add_member = sql.SqlQuery('add_member.sql')
    add_module = sql.SqlQuery('add_module.sql')
    get_count = sql.SqlQuery('get_count.sql')
    get_members = sql.SqlQuery('get_members.sql')
    get_modules = sql.SqlQuery('get_modules.sql')
    list_modules = sql.SqlQuery('list_modules.sql')
    schema_definition = sql.SqlQuery('generate_schema.sql')

    ############################################################################
    # Commands and events.                                                     #
    ############################################################################

    @commands.group(
        name='py',
        brief='Searches the given module for the given attribute.',
        usage='discord Client.event',
        invoke_without_command=True)
    async def py_group(self, ctx, module: str, *, attribute: str = ''):
        """
        Searches for documentation on the given module for the given
        attribute.
        """
        async with await self.acquire_db() as conn:

            # Type hinting in PyCharm :P
            conn: asyncpg.Connection = conn

            module = await conn.fetchrow(self.get_modules, module)

            if not module:
                return await ctx.send('I couldn\'t find a module for that.')

            # Unpack
            pk, name = module

            # Todo: find a way of fuzzy matching in Postgres properly, as there
            # are extensions for it, I just cannot get them to work at the
            # moment.

            # Get all members for that module.
            members = await conn.fetch(self.get_members, pk)

            # Perform fuzzy matching. Get the 10 best results for the
            # fully qualified name.

            # Construct a mapping of the qualified name to all other fields
            # first
            mapping = {
                r.get('fq_member_name').replace('.', ' '): r for r in
                # Cast each record to a dictionary so we can manipulate it
                # properly.
                (dict(rec) for rec in members)
            }

            top_results = fuzzy.extract(
                attribute,
                mapping.keys(),
                scoring_algorithm=fuzzy.deep_ratio)

            if not top_results:
                return await ctx.send('No results were found...')

            # Paginate the results.
            options = {}

            for i, (result, score) in enumerate(top_results):
                obj = mapping[result]
                string = mapping[result]['fq_member_name']

                if (i + 1) < 10:
                    emoji = f'{i + 1}\N{COMBINING ENCLOSING KEYCAP}'
                else:
                    emoji = '\N{KEYCAP TEN}'
                options[emoji] = (string, obj)

            # Last 180 seconds
            picker = fsa.FocusedOptionPicker(options, ctx.bot, ctx, 180)

            chosen_result = await picker.run()

            # If we timed out...
            if chosen_result is None:
                return

            # Otherwise, get the documentation:
            embed = discord.Embed(title=chosen_result.pop('fq_member_name'))
            metadata = json.loads(chosen_result.pop('metadata'))
            docstring = metadata.pop('docstring')
            if not docstring:
                docstring = ''

            embed.set_footer(text=metadata.pop('file'))

            await ctx.send(embed=embed)

            # Send docstring separately
            if docstring:
                docstring_pag = fsa.LinedPag(prefix='```rst', suffix='```')
                for line in docstring.split('\n'):
                    docstring_pag.add_line(line)

                dsp = fsa.FocusedPagMessage.from_strings(
                    *docstring_pag.pages, bot=ctx.bot, invoked_by=ctx,
                    timeout=300)
                dsp.nowait(dsp.run())

    @py_group.command(name='modules', brief='Lists any modules documented.')
    async def list_modules(self, ctx):
        async with await self.acquire_db() as conn:
            result = await conn.fetch(self.list_modules)
            await ctx.send(', '.join(f'`{r["module_name"]}`' for r in result))

    @commands.is_owner()
    @py_group.command(name='showconfig')
    async def show_config(self, ctx):
        """Dumps the config."""
        pag = fsa.Pag()
        pag.add_line(str(self.cache_config))

        for page in pag.pages:
            await ctx.send(page)

    @commands.is_owner()
    @py_group.command()
    async def recache(self, ctx):
        """
        Sets up the cache. This first destroys any existing schema, and
        proceeds to generate a fresh schema and tables.
        """
        await ctx.send('Warning! This may take from a few minutes to a few '
                       'hours, depending on the number of members being '
                       'cached. Please be patient!')

        status = await ctx.send('Starting cache process.')

        start_time = time.time()

        # noinspection PyUnusedLocal
        async with await self.acquire_db() as conn, ctx.typing():
            conn: asyncpg.Connection

            self.logger.warning(f'{ctx.author} invoked re-cache operation.')
            await status.edit(content='Connected. Ensuring schema exists.')

            await conn.execute(self.schema_definition)

            # Start caching modules
            tot = len(self.cache_config)

            # Run in a thread pool execution service to prevent blocking the
            # asyncio event loop.
            def cache_task(module_name):
                # Read the module data
                cache = module_cacher.ModuleCacher(module_name)
                cache = cache.make_cache()
                return cache

            for i, module in enumerate(self.cache_config):
                # Cache each module in a transaction.
                async with conn.transaction(
                        isolation='serializable',
                        readonly=False,
                        deferrable=False):

                    try:
                        await status.edit(
                            content=f'[{i+1}/{tot}] Caching `{module}`...')

                        cache = await self.run_in_io_pool(cache_task, module)

                        module_name = cache['root']
                        hash_code = str(cache['hash'])

                        # Insert an entry into the module index
                        module_pk = await conn.fetchval(
                            self.add_module,
                            module_name,
                            hash_code)

                        # Collect all arguments we are concerned with. This is
                        # each record to insert.
                        attrs = cache['attrs']
                        arguments = []

                        for j, attr in enumerate(attrs.values()):
                            if j % 100 == 0:
                                await status.edit(
                                    content=f'[{i+1}/{tot}] In `{module}`:'
                                            f' Caching attribute [{j+1}'
                                            f'/{len(attrs)}] - `{attr["fqn"]}`')

                            name = attr.pop('name')
                            fqn = attr.pop('fqn')
                            data = json.dumps(attr)

                            next_record = (module_pk, name, fqn, data)
                            arguments.append(next_record)

                        await conn.executemany(self.add_member, arguments)
                    except ModuleNotFoundError as ex:
                        await ctx.send(f'\N{NO ENTRY SIGN} {ex}')

                module_count, member_count = await conn.fetchrow(self.get_count)
            runtime = time.time() - start_time

            await status.edit(
                content=f'[{tot}/{tot}] Completed. Cached {member_count:,} '
                        f'members across {module_count:,} modules in approx. '
                        f'{int(runtime/60)} minutes, {int(runtime % 60)} '
                        f'seconds.')
