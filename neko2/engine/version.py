#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a version message.
"""
import inspect                          # Object introspection
import platform                         # Platform information
import subprocess                       # Process forking
from discord import embeds              # Embeds
import neko2                            # neko2 package info
from neko2.engine import commands       # commands
from neko2.shared import string         # string manipulations


# I like numbers
try:
    lines_of_code: str = subprocess.check_output(
        [
            '/bin/sh',
            '-c',
            'wc -l $(find neko2 -name "*.py" -o -name "*.sql")'
        ],
        universal_newlines=True)
    # Gets the number from the total line of the output for wc
    lines_of_code = lines_of_code.strip().split('\n')[-1].strip().split(' ')[0]
    lines_of_code = f'{int(lines_of_code):,} lines of code!'
except:
    lines_of_code = 'No idea on how many lines of code!'


@commands.command()
async def version(ctx):
    """Shows versioning information and some other useful statistics."""
    author = neko2.__author__
    contrib = [*neko2.__contributors__]
    license = neko2.__license__
    repo = neko2.__repository__
    version = neko2.__version__
    owner = ctx.bot.get_user(ctx.bot.owner_id)
    uptime = ctx.bot.uptime
    docstring = inspect.getdoc(neko2)
    if docstring:
        docstring = string.remove_single_lines(inspect.cleandoc(docstring))
    else:
        docstring = embeds.EmptyEmbed

    # Remove me from contributors.
    contrib.remove(author)

    info = '\n\n'.join([
        f'- Created by {author}, under the {license}',
        f'- Bot account owned by {owner}',
        '- Contributed to by ' + ', '.join(contrib) + '\n' if contrib else '',
    ]).strip()

    environment = '\n'.join([
        f'- {platform.system()} {platform.release()} {platform.machine()}',
        '',
        f'- Python {platform.python_version()} '
        f'({platform.python_implementation()}) ',
        f'   compiled with {platform.python_compiler()}',
        f'   built on {platform.python_build()[1]}',
        '',
        f'- {lines_of_code}'
    ])

    embed = embeds.Embed(
        title=f'Neko² v{version}',
        colour=0xc70025,
        description=docstring,
        url=repo)

    embed.add_field(name='Ownership and licensing', value=info, inline=False)
    embed.add_field(name='Techspecs for nerds', value=environment, inline=False)
    embed.set_author(name=f'{author} presents...')

    if uptime >= 60 * 60 * 24:
        uptime /= (60.0 * 60 * 24)
        uptime = round(uptime, 1)
        uptime = f'{uptime} day{"s" if uptime != 1 else ""}'
    elif uptime >= 60 * 60:
        uptime /= (60.0 * 60)
        uptime = round(uptime, 1)
        uptime = f'{uptime} hour{"s" if uptime != 1 else ""}'
    elif uptime >= 60:
        uptime /= 60.0
        uptime = round(uptime, 1)
        uptime = f'{uptime} minute{"s" if uptime != 1 else ""}'
    else:
        uptime = int(uptime)
        uptime = f'{uptime} second{"s" if uptime != 1 else ""}'

    embed.set_footer(text=f'Uptime: {uptime}')

    embed.set_thumbnail(url=ctx.bot.user.avatar_url)

    await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(version)
