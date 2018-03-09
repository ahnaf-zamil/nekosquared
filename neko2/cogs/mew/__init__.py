#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A bunch of catgirl reaction PNGs. I thought they were cool. Sue me.

Todo: find and cite author. These are awesome!
"""
import os
import random
import traceback

import discord

from neko2.engine import commands
from neko2.shared import configfiles
from neko2.shared import ioutil
from neko2.shared import scribe


# Relative to this directory.
bindings_file = 'bindings'
assets_directory = ioutil.in_here('assets')


class MewReactsCog(scribe.Scribe):
    """Reactions cog."""
    def __init__(self):
        bindings = configfiles.get_from_here(bindings_file).sync_get()

        # Attempt to locate all files to ensure paths are valid.
        potential_targets = set()
        for im_list in bindings.values():
            [potential_targets.add(im) for im in im_list]

        targets_to_path = {}

        for target in potential_targets:
            path = os.path.join(assets_directory, target)
            if os.path.exists(path) and os.path.isfile(path):
                self.logger.debug(f'Discovered {path}.')
                targets_to_path[target] = path
            else:
                self.logger.warning(f'Could not find {path}. Excluding image.')

        self.images = {}

        for react_name, binding_list in bindings.items():
            valid_list = []
            for image in binding_list:
                if image in targets_to_path and image not in valid_list:
                    valid_list.append(targets_to_path[image])

            if not valid_list:
                self.logger.warning(f'I am disabling {react_name} due to lack '
                                    'of _existing_ files.')
            else:
                self.images[react_name.lower()] = valid_list

    @commands.command(
        name='mew',
        brief='A bunch of reaction images I liked. Call with no argument for '
              'usage info.',
        examples=['gg', 'sleepy', 'owo'],
        aliases=['mewd'])
    async def post_reaction(self, ctx, *, react_name=''):
        """
        Posts a reaction. Run without any commands to see a list of reactions.

        Run `mewd` to destroy the calling message.
        """
        with ctx.typing():
            react_name = react_name.lower()

            # If the react is there, then send it!
            if react_name and react_name in self.images:
                try:
                    if ctx.invoked_with == 'mewd':
                        await ctx.message.delete()
                    file_name = random.choice(self.images[react_name])
                    await ctx.send(file=discord.File(file_name))
                except FileNotFoundError:
                    traceback.print_exc()
                    await ctx.send(
                        'Something broke and the dev '
                        'was shot. Please try again later ^w^', delete_after=15)
            # Otherwise, if the react doesn't exist, or wasn't specified, then
            # list the reacts available.
            else:
                await ctx.send('**Mew reactions:**\n\n' + ' '.join(
                        map(
                            lambda n: f'`{n}`',
                            sorted(self.images)
                        )
                    ) + '.\n\nThanks to Zcissors for providing the emotes and '
                    'command alias configurations.'
                )


def setup(bot):
    bot.add_cog(MewReactsCog())
