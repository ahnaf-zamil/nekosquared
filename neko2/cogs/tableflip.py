#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
from neko2.shared import alg


class TableFlipCog:
  binds = {
      '/shrug': '¯\_(ツ)_/¯',
      '/tableflip': '(╯°□°）╯︵ ┻━┻',
      '/unflip': '┬──┬﻿ ノ(° - °ノ)'
  }
  
  async def on_message(self, message):
      if not message.author.bot:
          # Attempt to find one of the binds
          bind = alg.find(lambda m: m == message.content, self.binds)
          if bind:
              try:
                  await message.delete()
              except:
                  pass
              finally:
                  await message.channel.send(f'{message.author}:\n{self.binds[bind]}')
  

def setup(bot):
    bot.add_cog(TableFlipCog())
