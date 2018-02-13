from nekosquared.engine import commands
from nekosquared.shared import fsa
from nekosquared.shared import nssm


class NssmSandboxCog:
    @commands.command(
        brief='Tokenises the given input source code.',
        usage='<code>')
    async def tokenise(self, ctx, *, src):
        """
        Tokenises the given input source code and outputs the generated tokens.
        """
        lex = nssm.Lexer(src)
        pag = fsa.LinedPag()
        for token in lex:
            pag.add_line(repr(token) + ' ' + str(token))

        fsm = fsa.FocusedPagMessage.from_paginator(
            pag=pag,
            bot=ctx.bot,
            invoked_by=ctx.message,
            timeout=60)

        await fsm.run()


def setup(bot):
    bot.add_cog(NssmSandboxCog())
