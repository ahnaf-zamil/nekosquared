#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Allows the bot owner to update the bot using Git, if it is installed.
"""
import asyncio                      # Asyncio subprocess
import io                           # StringIO
import os                           # File path utils
import random
import shutil                       # which (find in $PATH env-var)
import traceback                    # Traceback utils

from discomaton.util import pag

from neko2.shared import scribe, commands  # Scribe


keks = (
    '*sigh*',
    'k.',
    'Please don\'t break anything this time...',
    'Again?!',
    '\N{OK HAND SIGN}',
    'https://media1.tenor.com/images/'
    '5c0e9a59364291b87ad912d88d37438c/tenor.gif?itemid=5682066',
    '(╯°□°）╯︵ ┻━┻',
    '( ͡° ͜ʖ ͡°)',
    'ಠ_ಠ',
    'ノ┬─┬ノ ︵ ( \o°o)\\n(In Soviet Russia... table flips **you**.',
    'ᕕ( ᐛ )ᕗ *off we go to break some more!*',
    'ლ(ಠ_ಠლ)\nY U NO WRITE GOOD CODE',
    '(づ￣ ³￣)づ *new commits*',
    'ᕦ(ò_óˇ)ᕤ 1v1 me irl',
    '(∩｀-´)⊃━☆ﾟ.*･｡ﾟ *bad code*',
    'o(╥﹏╥)o I give up trying to fight you',
    '(ง •̀_•́)ง',
    '(me) --> (╯°Д°）╯︵/(.□ . \) <-- (you)',
    '(╥_╥)', 'ᕙ(⇀‸↼‶)ᕗ', '(ง •̀_•́)ง ผ(•̀_•́ผ)',
    'f(ಠ‿↼)z',
    '(ノಠ益ಠ)ノ',
    'OH BOY\nNEW COMMITS!\nヽ(⌐■_■)ノ♪♬  ٩( ᐛ )و   ᕕ( ᐛ )ᕗ',
    '(◍•﹏•)',
    'I _will_ be back...\n┬┴┬┴┤ ͜ʖ ͡°) ├┬┴┬┴'
)


class GitCog(scribe.Scribe):
    @commands.is_owner()
    @commands.command(
        brief='Clears the stash, and ensures we are up to date with master, '
              'even if it means destroying the current code base. Use this to '
              'invoke a bot update remotely.')
    async def update(self, ctx, *args):
        """
        This will DM you the results.

        The following assumptions are made:
          - The current system user has permission to modify the `.git`
            directory, and modify the contents of this directory.
          - That git is installed.
          - That the current working directory contains the `.git` directory.

        As of v1.3, the bot will not automatically restart. To force the bot
        to restart, provide the `--restart` or `-r` flag with the command
        invocation.
        """

        should_restart = '--restart' in args or '-r' in args

        # Ensure git is installed first
        git_path = shutil.which('git')

        msg = await ctx.send(random.choice(keks))

        did_fail = False

        async with msg.channel.typing():
            if not git_path:
                return await ctx.author.send('I can\'t seem to find git!')

            # Ensure that we have a `.git` folder in the current directory
            if os.path.exists('.git'):
                if os.path.isdir('.git'):
                    pass
                else:
                    return await ctx.author.send('.git is not a directory')
            else:
                return ctx.author.send('.git does not exist. Is this a repo?')

            with io.StringIO() as out_s:
                shell = os.getenv('SHELL')
                if shell is None:
                    shell = shutil.which('sh')
                    if shell is None:
                        shell = '?? '

                async def call(cmd):
                    nonlocal did_fail
                    out_s.write(f'{shell} -c {cmd}')
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE)
                    out_s.write(f'> Invoked PID {process.pid}\n')
                    # Might deadlock?
                    out_s.write((await process.stdout.read()).decode())
                    out_s.write((await process.stderr.read()).decode())
                    code = process.returncode if process.returncode else 0

                    if code:
                        did_fail = True
                    out_s.write(f'> Terminated with code {code}\n\n')

                try:
                    await call(f'{git_path} fetch --all')
                    print('The following changes will be lost:')
                    await call(f'{git_path} diff --stat HEAD origin/master')
                    print('And replaced with')
                    await call(f'{git_path} show --stat | '
                               'sed "s/<.*@.*[.].*>/<email>/g"')
                    print()
                    print('Status:')
                    await call(f'{git_path} status --porcelain')
                    print()
                    print('Overwriting local history with remote history.')
                    await call(f'{git_path} reset --hard origin/$(git '
                               'rev-parse --symbolic-full-name --abbrev-ref '
                               'HEAD)')
                    await call(f'{git_path} stash list && {git_path} stash '
                               'drop')
                except BaseException as ex:
                    err = traceback.format_exception(
                        type(ex), ex, ex.__traceback__)
                    # Seems that lines might have newlines. This is annoying.

                    err = ''.join(err).split('\n')
                    err = [f'# {e_ln}\n' for e_ln in err]

                    # Remove last comment.
                    err = ''.join(err)[:-1]
                    out_s.write(err)
                    traceback.print_exception(type(ex), ex, ex.__traceback__)
                    did_fail = True
                finally:
                    log = out_s.getvalue()

                    self.logger.warning(
                        f'{ctx.author} Invoked destructive update from '
                        f'{ctx.guild}@#{ctx.channel}\n{log}')

                    p = pag.Paginator()

                    for line in log.split('\n'):
                        p.add_line(line)

                    await ctx.author.send(
                        f'Will send {len(p.pages)} messages of output!')

                    for page in p.pages:
                        if page:
                            await ctx.author.send(page)

        if did_fail:
            await ctx.author.send('The fix process failed at some point '
                                  'I won\'t restart. Please update '
                                  'manually.')
            self.logger.fatal('Fix failure.')
        else:
            if should_restart:
                await ctx.send(
                    'The fix process succeeded. I will now '
                    'shut down!')
                self.logger.warning(
                    'Successful fix! Going offline in 2 seconds')
                await asyncio.sleep(2)
                await ctx.bot.logout()
            else:
                await ctx.send('Completed. I sent the results to you via DMs.')


def setup(bot):
    bot.add_cog(GitCog())
