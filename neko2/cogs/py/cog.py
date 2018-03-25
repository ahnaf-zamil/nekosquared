#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
V2 of a cog implementation for Python document caching and lookup. This should
hopefully run faster this time, as it outsources most of the searching logic to
PostgreSQL fuzzy logic functions. This removes the overhead of moving tables
of tens of thousands of records across network sockets, and will also be faster
since most Postgres builtin functions are compiled C source rather than
interpreted Python source. Also the devs are probably a lot cleverer than I am.
"""
import asyncio
import json
import random
import time
import traceback

import asyncpg
from discomaton import book
from discomaton import optionpicker
from discomaton.factories import bookbinding
from discomaton.util import pag
import discord

from neko2.engine import commands
from neko2.shared import configfiles
from neko2.shared import scribe
from neko2.shared import sql
from neko2.shared import traits
from . import module_cacher


config_file = 'neko2.cogs.py.targets'


class PyCog2(traits.PostgresPool, traits.IoBoundPool, scribe.Scribe):
    gen_schema_sql = sql.SqlQuery('generate-schema')
    add_member_sql = sql.SqlQuery('add-member')
    add_module_sql = sql.SqlQuery('add-module')
    list_modules_sql = sql.SqlQuery('list-modules')
    get_top_10_sql = sql.SqlQuery('get-top-10')

    def __init__(self):
        self.modules = configfiles.get_config_data(config_file)

    @commands.group(
        name='py',
        brief='Searches the given module for the given attribute.',
        examples=['discord Bot.listen'],
        invoke_without_command=True)
    async def py_group(self, ctx, module: str, *, attribute: str=''):
        """
        Searches for documentation on the given module for the given
        attribute.
        """
        async with await self.acquire_db() as conn, ctx.typing():

            try:
                top_results = await conn.fetch(
                    self.get_top_10_sql,
                    module,
                    attribute)
            except asyncpg.NoDataFoundError:
                top_results = []

            if not top_results:
                return await ctx.send('No results were found...')

            # Get top 200 results.
            top_results = top_results[:200]

            # Paginate the results.
            options = {}

            for i, record in enumerate(top_results):
                s, fq_s, pk, name, fq_name, meta = list(record.values())[0]

                obj = {
                    'member_name': name,
                    'fq_member_name': fq_name,
                    'metadata': meta
                }

                options[fq_name] = obj

            if len(options) > 1:
                # Last 180 seconds
                chosen_result = await optionpicker.option_picker(
                    ctx,
                    *[f'`{option}`' for option in options.keys()],
                    timeout=180)

                # If we timed out...
                if chosen_result is None:
                    return

                # 1:-1 to trim backticks
                chosen_result = options[chosen_result[1:-1]]
            else:
                # Get the first (only) option.
                chosen_result = list(options.values())[0][1]

        await self._make_send_doc(ctx, chosen_result)

    @py_group.command(name='modules', brief='Lists any modules documented.')
    async def list_modules(self, ctx):
        async with await self.acquire_db() as conn:
            result = await conn.fetch(self.list_modules_sql)
            await ctx.send(', '.join(f'`{r["module_name"]}`' for r in result))

    @commands.is_owner()
    @py_group.command(name='showconfig')
    async def show_config(self, ctx):
        """Dumps the config."""
        book = bookbinding.StringBookBinder(ctx)
        book.add(str(self.modules))
        book.start()

    async def _wipe_schema(self):
        """Call this to create the schema the first time you run this."""
        async with await self.acquire_db() as conn:
            self.logger.warning('Destroying schema and rebuilding it.')
            await conn.execute(self.gen_schema_sql)

    async def _cache_modules(self, ctx, status: commands.StatusMessage):
        """Caches all the modules."""

        # Cache the modules
        # Run in a pool execution service to prevent blocking the
        # asyncio event loop.
        def cache_task(module_name, precondition_script=None):
            # Read the module data
            cache = module_cacher.ModuleCacher(
                module_name,
                precondition=precondition_script)
            cache = cache.make_cache()
            return cache

        tot = len(self.modules)

        async with await self.acquire_db() as conn:
            total_attrs = 0
            total_modules = 0

            for i, module in enumerate(self.modules):
                if isinstance(module, dict):
                    module, before = module['name'], module['init']
                else:
                    before = None

                globals()

                # Cache each module in a transaction.
                async with conn.transaction(
                        isolation='serializable',
                        readonly=False,
                        deferrable=False):

                    try:
                        self.logger.info(f'[{i+1}/{tot}] Analysing `{module}`')

                        asyncio.ensure_future(status.set_message(
                            f'[{i+1}/{tot}] Analysing `{module}`... '))

                        # Ideally I want to use CPU pool, but pickling becomes
                        # an issue, and that is required for IPC.
                        cache = await self.run_in_io_pool(cache_task,
                                                          [module, before])

                        module_name = cache['root']
                        hash_code = cache['hash']

                        # Insert an entry into the module index
                        await status.set_message(
                            f'[{i+1}/{tot}] Generating a new table for '
                            f'`{module}` dynamically in schema... '
                        )

                        self.logger.info(
                            f'[{i+1}/{tot}] Generating a new table for '
                            f'`{module}` dynamically in schema... '
                        )

                        module_tbl_name = await conn.fetchval(
                            self.add_module_sql,
                            module_name,
                            hash_code)

                        # Collect all arguments we are concerned with. This is
                        # each record to insert.
                        attrs = cache['attrs']
                        total_attrs += len(attrs)

                        arguments = []

                        for j, attr in enumerate(attrs.values()):
                            if not j or j % 250 == 249:
                                self.logger.info(
                                    f'[{i+1}/{tot}] In `{module}`:'
                                    f' Generating insert query [{j+1}'
                                    f'/{len(attrs)}] - `{attr["fqn"]}`')

                                asyncio.ensure_future(status.set_message(
                                    f'[{i+1}/{tot}] In `{module}`:'
                                    f' Generating insert query [{j+1}'
                                    f'/{len(attrs)}] - `{attr["fqn"]}`')
                                )

                            name = attr.pop('name')
                            fqn = attr.pop('fqn')
                            data = json.dumps(attr)

                            next_record = (module_tbl_name, name, fqn, data)
                            arguments.append(next_record)

                        self.logger.info(
                            f'[{i+1}/{tot}] In `{module}`; Executing '
                            f'{len(attrs)} insertions.')

                        asyncio.ensure_future(status.set_message(
                            f'[{i+1}/{tot}] In `{module}`; Executing '
                            f'{len(attrs)} insertions.'
                        ))

                        await conn.executemany(self.add_member_sql, arguments)

                        total_modules += 1
                    except BaseException as ex:
                        traceback.print_exc()
                        await ctx.send(f'\N{NO ENTRY SIGN} in {module}\n'
                                       f'{type(ex).__name__} {ex}')
        return total_attrs, total_modules

    @commands.is_owner()
    @py_group.command(brief='Recaches any missing or out-of-date modules.')
    async def recache(self, ctx):
        """
        This replaces any modules with a differing hash to the one we have
        stored, and modules that are not present.
        """
        self.logger.warning(f'{ctx.author} just invoked a complete recache.')

        start_time = time.time()

        status = commands.StatusMessage(ctx)
        with ctx.typing():
            await status.set_message('Rebuilding schema and installing '
                                     'extensions.')
            await self._wipe_schema()
            attrs, modules = await self._cache_modules(ctx, status)

            runtime = time.time() - start_time
            commands.acknowledge(ctx)

        message = (
            f'Generated schema, tables, and cached {attrs} attributes '
            f'across {modules} Python modules in approx {runtime:.2f}s.')
        await status.set_message(message)
        await ctx.author.send(message)

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

        if docstring:
            doc_pag = pag.Paginator(max_lines=20)
            for line in docstring.split('\n'):
                doc_pag.add_line(line)

            # Generate embeds.
            for page in doc_pag.pages:
                pages.append(discord.Embed(
                    title=f'`{element["member_name"]}`: Docstring',
                    description=page,
                    color=random.choice([0x4584b6, 0xffde57])))

        booklet = book.EmbedBooklet(ctx=ctx, pages=pages)
        booklet.start()
