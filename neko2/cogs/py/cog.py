#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Search and admin utilities for the cache system.

This expects a config file called neko2.cogs.py.targets.yaml to exist in the
config directory. This should be a list of Python modules to index when we are
directed to.
"""
import asyncio                          # asyncio.gather
import json                             # json deserialiser
import random                           # rng
import time                             # time.time
import asyncpg                          # postgres
import discord                          # discord.Embed
from neko2.engine import commands       # command decorator
from neko2.shared import configfiles    # config files
from neko2.shared import fsa            # finite state machines
from neko2.shared import sql            # SqlQuery
from neko2.shared import traits         # PostgresPool, IoBoundPool, Scribe
from neko2.shared.other import fuzzy    # Fuzzy string logic
from . import module_cacher             # Module cacher

config_file = 'neko2.cogs.py.targets.json'


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
    get_all_members_fqn = sql.SqlQuery('get_all_members_fqn.sql')
    get_members = sql.SqlQuery('get_members.sql')
    get_members_fqn = sql.SqlQuery('get_members_fqn.sql')
    get_modules = sql.SqlQuery('get_modules.sql')
    list_all_modules = sql.SqlQuery('list_modules.sql')
    schema_definition = sql.SqlQuery('generate_schema.sql')

    ############################################################################
    # Commands and events.                                                     #
    ############################################################################

    @commands.group(
        name='py',
        brief='Searches the given module for the given attribute.',
        examples=['discord Bot.listen', 'discord.ext.commands.bot.Bot.listen'],
        invoke_without_command=True)
    async def py_group(self, ctx, module: str, *, attribute: str = ''):
        """
        Searches for documentation on the given module for the given
        attribute.

        You can either specify a module name followed by an attribute contained
        somewhere within the module, or you can provide the fully qualified
        attribute name alone.
        """
        if not attribute:
            if not await ctx.bot.is_owner(ctx.author):
                await ctx.send('Please provide a module and attribute. The '
                               'ability to search the entire namespace has '
                               'been disabled until a faster device can host '
                               'this bot, as it consumes too much processing '
                               'time.', delete_after=30)
                return
            else:
                await ctx.send('This will probably be slow..!', delete_after=5)

        try:
            async with await self.acquire_db() as conn, ctx.typing():

                # Type hinting in PyCharm :P
                conn: asyncpg.Connection = conn

                async def fetch(query, *args):
                    return await asyncio.wait_for(
                        conn.fetch(query, *args),
                        timeout=10)

                if '.' not in module:
                    module = await conn.fetchrow(self.get_modules, module)

                    if not module:
                        members = await fetch(self.get_all_members_fqn)
                    else:
                        # Unpack
                        pk, name = module

                        # Get all members for that module. This may take a few
                        # seconds, so we show typing.
                        members = await fetch(self.get_members, pk)
                else:

                    members = await fetch(self.get_members_fqn, module)

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

                if len(options) > 1:
                    # Last 180 seconds
                    picker = fsa.FocusedOptionPicker(options, ctx.bot, ctx, 180)

                    chosen_result = await picker.run()

                    # If we timed out...
                    if chosen_result is None:
                        return
                else:
                    # Get the first (only) option.
                    chosen_result = list(options.values())[0][1]

            await self._make_send_doc(ctx, chosen_result)
        except asyncio.TimeoutError:
            await ctx.send('Query timed out... try being less vague, or give '
                           'me a faster computer to run on!',
                           delete_after=15)

    @py_group.command(name='modules', brief='Lists any modules documented.')
    async def list_modules(self, ctx):
        async with await self.acquire_db() as conn:
            result = await conn.fetch(self.list_all_modules)
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
                       'cached. Please be patient! This will also block while '
                       'modules are loaded. You have been warned.')

        status = await ctx.send('Starting cache process.')

        start_time = time.time()

        # noinspection PyUnusedLocal
        async with await self.acquire_db() as conn, ctx.typing():
            self.logger.warning(f'{ctx.author} invoked re-cache operation.')
            asyncio.ensure_future(
                status.edit(content='Connected. Ensuring schema exists.'))

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
                        asyncio.ensure_future(status.edit(
                            content=f'[{i+1}/{tot}] Caching `{module}`... '
                                    f'collecting required data from source code'
                                    f'...'))

                        cache = await self.run_in_io_pool(cache_task, [module])

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
                            if not j or j % 250 == 249:
                                asyncio.ensure_future(status.edit(
                                    content=f'[{i+1}/{tot}] In `{module}`:'
                                            f' Storing attribute [{j+1}'
                                            f'/{len(attrs)}] - `{attr["fqn"]}`')
                                )

                            name = attr.pop('name')
                            fqn = attr.pop('fqn')
                            data = json.dumps(attr)

                            next_record = (module_pk, name, fqn, data)
                            arguments.append(next_record)

                        await conn.executemany(self.add_member, arguments)
                    except BaseException as ex:
                        await ctx.send(f'\N{NO ENTRY SIGN} in {module}\n'
                                       f'{type(ex).__name__} {ex}')

                module_count, member_count = await conn.fetchrow(self.get_count)
            runtime = time.time() - start_time

            await status.edit(
                content=f'[{tot}/{tot}] Completed. Cached {member_count:,} '
                        f'members across {module_count:,} modules in approx. '
                        f'{int(runtime/60)} minutes, {int(runtime % 60)} '
                        f'seconds.')

    ############################################################################
    # Helpers and other bits and pieces.                                       #
    ############################################################################
    @staticmethod
    async def _make_send_doc(ctx, element):
        """Makes the documentation for us."""
        meta = json.loads(element['metadata'])

        category = meta['category']

        embed = discord.Embed(
            title=f'`{element["member_name"]}`: {category}',
            colour=random.choice([0x4584b6, 0xffde57]))

        docstring = meta.pop('docstring')
        file = meta.pop('file')
        start_line = meta.pop('start_line')
        end_line = meta.pop('end_line')

        if start_line < end_line:
            sig = f'{start_line}⟶{end_line}'
        elif start_line == end_line == 1:
            sig = ''
        else:
            sig = f'{start_line}'

        embed.set_footer(text=f'{file}:{sig}')

        actual_fqn = meta.pop('actual_fqn')

        description = []

        sig = meta.pop('sig', '')

        if sig:
            description.append(f'`{sig}`')

        if actual_fqn != element['fq_member_name']:
            description.append(f'Alias for {actual_fqn}')

        if description:
            embed.description = '\n\n'.join(description)

        params = meta.pop('params', {})
        if params:
            param_str = []
            for param in params.values():
                sig = f'`{param["name"]}'
                if param['annotation']:
                    sig += f': {param["annotation"]}'
                if param['default']:
                    sig += f' = {param["default"]}'

                sig += '`'
                line = [sig]
                positionality = f'({param["kind"]})'
                docstring = param['docstring']

                if docstring:
                    line.append(docstring)

                line.append(positionality)

                param_str.append(' - '.join(line))

            embed.add_field(
                name='Parameters',
                value='\n'.join(param_str)[:1024],
                inline=False)

        embed.set_author(name=meta.pop('parent'))

        ops = meta.pop('ops', [])
        returns = meta.pop('returns', '')
        hint = meta.pop('hint', '')
        raises = meta.pop('raises', '')
        init = meta.pop('init', '')
        new = meta.pop('new', '')

        attrs = [f'`{attr}`' for attr in sorted(meta.pop('attrs', []))]
        attrs = [*filter(lambda a: not a.startswith('_'), attrs)]

        prop = [f'`{p}`' for p in sorted(meta.pop('properties', []))]
        prop = [*filter(lambda a: not a.startswith('_'), prop)]

        roprop = [f'`{rop}`' for rop in
                  sorted(meta.pop('readonly_properties', []))]
        roprop = [*filter(lambda a: not a.startswith('_'), roprop)]

        type_t = meta.pop('type', '')
        meta_class = meta.pop('metaclass', '')
        bases = [f'`{base}`' for base in sorted(meta.pop('bases', []))]
        str_v = meta.pop('str', '')
        repr_v = meta.pop('repr', '')

        if ops:
            embed.add_field(
                name='Operators',
                value=', '.join(f'`{o}`' for o in ops))

        if returns:
            embed.add_field(name='Returns', value=returns)
        if hint:
            embed.add_field(name='Type hint', value=f'`{hint}`')
        if raises:
            embed.add_field(name='Raises', value=raises)
        if init:
            embed.add_field(name='`__init__` signature', value=f'`{init}`')
        if new:
            embed.add_field(name='`__new__` signature', value=f'`{new}`')
        if bases:
            for i in range(0, len(bases), 50):
                embed.add_field(
                    name='Base classes',
                    value='\n'.join(bases[i:i+20]))
        if meta_class:
            embed.add_field(name='Metaclass', value=f'`{meta_class}`')
        if type_t:
            embed.add_field(name='Type', value=f'`{type_t}`')
        if str_v:
            embed.add_field(name='`str()` string', value=f'`{str_v}`')
        if repr_v:
            embed.add_field(name='`repr()` string', value=f'`{repr_v}`')

        ########################################################################
        # Attributes have their own page                                       #
        ########################################################################

        pages = [embed]

        if roprop:
            # Ignore protected/private members.
            text = ', '.join(attrs)

            pages.append(discord.Embed(
                title=f'`{element["member_name"]}`: Read-only properties',
                colour=random.choice([0x4584b6, 0xffde57]),
                description=text[:2000]))

        if prop:
            # Ignore protected/private members.
            text = ', '.join(prop)

            pages.append(discord.Embed(
                title=f'`{element["member_name"]}`: Properties',
                colour=random.choice([0x4584b6, 0xffde57]),
                description=text[:2000]))

        if attrs:
            # Ignore protected/private members.
            text = ', '.join(attrs)

            pages.append(discord.Embed(
                title=f'`{element["member_name"]}`: Attributes',
                colour=random.choice([0x4584b6, 0xffde57]),
                description=text[:2000]))

        if len(pages) > 1:
            asyncio.ensure_future(fsa.FocusedPagEmbed.from_embeds(
                pages,
                bot=ctx.bot,
                invoked_by=ctx,
                timeout=600).run())
        else:
            await ctx.send(embed=pages.pop())

        # Send paginator for the docstring, if applicable.
        if docstring:
            pag = fsa.LinedPag(max_lines=15, prefix='```\nDocstring:',
                               suffix='```')
            for line in docstring.split('\n'):
                pag.add_line(f'  {line}')

            # Keep alive for two minutes or so.
            fsm = fsa.FocusedPagMessage.from_paginator(
                pag=pag, bot=ctx.bot, invoked_by=ctx, timeout=600)

            await fsm.run()
