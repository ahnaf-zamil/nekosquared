#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Formats and makes use of the code-cogs equation editor API to generate
previews for LaTeX strings.
"""
import io

import discord
import PIL.Image
import PIL.ImageDraw

from neko2.engine import commands
from neko2.shared import traits

# URL endpoint to use.
end_point = 'http://latex.codecogs.com/'

# Rendering engines
engines = {'png', 'gif', 'pdf', 'swf', 'emf', 'svg'}

# Additional arguments to alter font size.
sizes = {
    5: '\\tiny ',
    9: '\\small ',
    10: '',
    12: '\\large ',
    18: '\\LARGE ',
    20: '\\huge '
}

# Fonts available.
fonts = {
    'Latin Modern': '',
    'Verdana': '\\fn_jvn ',
    'Comic Sans': '\\fn_cs ',
    'Computer Modern': '\\fn_cm ',
    'Helvetica': '\\fn_phv '
}

# Background colours.
backgrounds = {
    'transparent': '',
    'black': '\\bg_black ',
    'white': '\\bg_white ',
    'red': '\\bg_red ',
    'green': '\\bg_green ',
    'blue': '\\bg_blue '
}

# We pad the image slightly
padding_pct_height = 1.2
padding_pct_width = 1.5


class LatexCog(traits.IoBoundPool, traits.HttpPool, traits.CpuBoundPool):
    @staticmethod
    def generate_url(content,
                     *,
                     engine: str = 'png',
                     size: int = 12,
                     font: str = 'Latin Modern',
                     bg_colour: str = 'transparent',
                     fg_colour: str = 'black',
                     dpi: int = 200) -> str:
        """
        Generates the URL containing the LaTeX preview for the given content.
        :param content: content to render.
        :param engine: the rendering engine to use. Must be in the
        ``engines`` set.
        :param size: default size. Must be in the ``sizes`` dict.
        :param font: default font. Must be in the ``fonts`` dict.
        :param bg_colour: default background colour. Must be in the
        ``backgrounds``
            dict.
        :param fg_colour: default text colour name. Refer to
            https://en.wikibooks.org/wiki/LaTeX/Colors
            #The_68_standard_colors_known_to_dvips
            for acceptable values. This is case sensitive, for at least some
            of the
            time.
        :param dpi: default dots per inch. Must be a non-zero positive integer.
        :returns: a formatted URL pointing to the image resource.
        """
        if engine not in engines:
            raise ValueError(
                f'Invalid engine {engine}. Valid engines are '
                f'{", ".join(engines)}')
        elif size not in sizes:
            raise ValueError(
                f'Invalid size {size}. Valid sizes are {list(sizes.keys())}')
        elif font not in fonts:
            raise ValueError(
                f'Invalid font {font}. Valid fonts are '
                f'{", ".join(list(fonts))}')
        elif bg_colour not in backgrounds:
            raise ValueError(
                f'Invalid background {bg_colour}. Valid colours are '
                f'{", ".join(list(backgrounds))}')
        elif dpi <= 0:
            raise ValueError('DPI must be positive.')
        else:
            def sanitise(string):
                string = string.replace(' ', '&space;')
                string = string.replace('\n', '&space;')
                return string

            raw_str = ''
            raw_str += sanitise(f'\\dpi{{{dpi}}}')
            raw_str += sanitise(f'{backgrounds[bg_colour]}')
            raw_str += sanitise(f'{fonts[font]}')
            raw_str += sanitise(f'{sizes[size]}')
            raw_str += sanitise(f'\\color{{{fg_colour}}} {content}')

            return f'{end_point}{engine}.latex?{raw_str}'

    @classmethod
    async def pad_convert_image(cls,
                                in_img: io.BytesIO,
                                out_img: io.BytesIO,
                                bg_colour: int):
        """
        Takes input image bytes and constructs the image in memory in a
        CPU worker. We then add a padded border around the edge of the image
        and stream it back into the given output bytes IO object. We do this
        as the default rendered LaTeX has no border, and on a contrasting
        background this can look awkward and is harder to read.

        This assumes both the input and output are to be PNG format.

        EDIT: this has to be done on a Thread, not a Process. We cannot pickle
        BytesIO objects.
        """
        def cpu_work():
            old_img: PIL.Image.Image = PIL.Image.open(in_img)

            new_w = int(old_img.width * padding_pct_width)
            new_h = int(old_img.height * padding_pct_height)

            new_x = int((new_w - old_img.width) / 2)
            new_y = int((new_h - old_img.height) / 2)

            new_img = PIL.Image.new(
                'RGB',
                (new_w, new_h),
                bg_colour
            )

            new_img.paste(
                old_img,
                (new_x, new_y)
            )

            new_img.save(out_img, 'PNG')

        await cls.run_in_io_pool(cpu_work)

    @commands.command(
        name='tex', aliases=['latex'],
        brief='Attempts to parse the given LaTeX string and display a '
              'preview.')
    async def latex_cmd(self, ctx, *, content: str):
        async with ctx.typing():
            # Append a tex newline to the start to force the content to
            # left-align.
            url = self.generate_url(f'\\\\{content}',
                                    bg_colour='white',
                                    size=10)
            with await self.acquire_http() as conn:
                resp = await conn.get(url)
                data = await resp.read()

            with io.BytesIO(data) as in_data, io.BytesIO() as out_data:
                in_data.seek(0)
                await self.pad_convert_image(in_data, out_data, 0xFFFFFF)
                out_data.seek(0)
                file = discord.File(out_data, 'latex.png')

                await ctx.send(
                    content=f'`{content}`',
                    file=file)


def setup(bot):
    bot.add_cog(LatexCog())
