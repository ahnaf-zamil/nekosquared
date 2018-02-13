from nekosquared.engine import commands
from nekosquared.shared import fsa
from nekosquared.shared import nssm


class Cog:
    @commands.command()
    async def test_lex(self, ctx, *, src):
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
    bot.add_cog(Cog())
