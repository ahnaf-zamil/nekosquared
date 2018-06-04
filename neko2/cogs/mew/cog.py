#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation of the Mew command and cog.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os
import random
import traceback

import discord

from neko2.shared import commands, configfiles, ioutil, scribe

# Relative to this directory.
bindings_file = "bindings"
assets_directory = ioutil.in_here("assets")


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
                self.logger.debug(f"Discovered {path}.")
                targets_to_path[target] = path
            else:
                self.logger.warning(f"Could not find {path}. Excluding image.")

        self.images = {}

        for react_name, binding_list in bindings.items():
            valid_list = []
            for image in binding_list:
                if image in targets_to_path and image not in valid_list:
                    valid_list.append(targets_to_path[image])

            if not valid_list:
                self.logger.warning(
                    f"I am disabling {react_name} due to lack " "of _existing_ files."
                )
            else:
                self.images[react_name.lower()] = valid_list

    @commands.command(
        name="mew",
        brief="A bunch of reaction images I liked. Call with no argument for "
        "usage info.",
        examples=["gg", "sleepy", "owo"],
        aliases=["mewd"],
    )
    async def post_reaction(self, ctx, *, react_name=""):
        """
        Posts a reaction. Run without any commands to see a list of reactions.

        Run `mewd` to destroy the calling message.
        """
        with ctx.typing():
            react_name = react_name.lower()

            # If the react is there, then send it!
            if react_name and react_name in self.images:
                try:
                    if ctx.invoked_with == "mewd":
                        await ctx.message.delete()
                    file_name = random.choice(self.images[react_name])
                    await ctx.send(file=discord.File(file_name))
                except FileNotFoundError:
                    traceback.print_exc()
                    await ctx.send(
                        "Something broke and the dev "
                        "was shot. Please try again later ^w^",
                        delete_after=15,
                    )
            # Otherwise, if the react doesn't exist, or wasn't specified, then
            # list the reacts available.
            elif not react_name:
                await ctx.author.send(
                    "**Mew reactions:**\n\n"
                    + " ".join(map(lambda n: f"`{n}`", sorted(self.images)))
                    + ".\n\nThanks to Zcissors for providing the emotes and "
                    "command alias configurations."
                )
            else:
                await ctx.send(
                    "That wasn't found. Run without a name to get a "
                    "list sent to you via DMs.",
                    delete_after=15,
                )
