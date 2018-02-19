"""
Formats and makes use of the code-cogs equation editor API to generate
previews for LaTeX strings.
"""
import re

import discord

from neko2.engine import commands

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


def generate_url(content,
                 *,
                 engine: str='png',
                 size: int=12,
                 font: str='Latin Modern',
                 bg_colour: str='transparent',
                 fg_colour: str='black',
                 dpi: int=200) -> str:
    """
    Generates the URL containing the LaTeX preview for the given content.
    :param content: content to render.
    :param engine: the rendering engine to use. Must be in the ``engines`` set.
    :param size: default size. Must be in the ``sizes`` dict.
    :param font: default font. Must be in the ``fonts`` dict.
    :param bg_colour: default background colour. Must be in the ``backgrounds``
        dict.
    :param fg_colour: default text colour name. Refer to
        https://en.wikibooks.org/wiki/LaTeX/Colors#The_68_standard_colors_known_to_dvips
        for acceptable values. This is case sensitive, for at least some of the
        time.
    :param dpi: default dots per inch. Must be a non-zero positive integer.
    :returns: a formatted URL pointing to the image resource.
    """
    if engine not in engines:
        raise ValueError(
            f'Invalid engine {engine}. Valid engines are {", ".join(engines)}')
    elif size not in sizes:
        raise ValueError(
            f'Invalid size {size}. Valid sizes are {list(sizes.keys())}')
    elif font not in fonts:
        raise ValueError(
            f'Invalid font {font}. Valid fonts are {", ".join(list(fonts))}')
    elif bg_colour not in backgrounds:
        raise ValueError(
            f'Invalid background {bg_colour}. Valid colours are '
            f'{", ".join(list(backgrounds))}')
    elif dpi <= 0:
        raise ValueError('DPI must be positive.')
    else:
        def san(string):
            string = string.replace(' ', '&space;')
            string = string.replace('\n', '&space;')
            return string

        raw_str = ''
        raw_str += san(f'\\dpi{{{dpi}}}')
        raw_str += san(f'{backgrounds[bg_colour]}')
        raw_str += san(f'{fonts[font]}')
        raw_str += san(f'{sizes[size]}')
        raw_str += san(f'\\color{{{fg_colour}}} {content}')

        return f'{end_point}{engine}.latex?{raw_str}'


class LatexCog:
    @commands.command(
        name='latex', aliases=['tex'],
        brief='Attempts to parse the given LaTeX string and display a '
              'preview.')
    async def latex_cmd(self, ctx, *, content: str):
        url = generate_url(f'\\\\{content}',
                           bg_colour='white',
                           size=10)
        embed = discord.Embed(color=0)
        embed.set_image(url=url)
        embed.set_footer(text=content)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LatexCog())
