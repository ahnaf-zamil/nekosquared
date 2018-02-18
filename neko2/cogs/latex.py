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
                 dpi: int=200,
                 sanitise: bool=True) -> str:
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
    :param sanitise: whether or not to sanitise the URL first. Defaults to true.
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
            if sanitise:
                string = string.replace(' ', '&space;')
            return string

        raw_str = ''
        raw_str += san(f'\\dpi{{{dpi}}}')
        raw_str += san(f'{backgrounds[bg_colour]}')
        raw_str += san(f'{fonts[font]}')
        raw_str += san(f'{sizes[size]}')
        raw_str += san(f'{{\\color{{{fg_colour}}} {content}}}')
        return f'{end_point}{engine}.latex?{raw_str}'


def reformat_inline(content: str):
    """Does some string manipulation to make the content appear in-lined."""
    content = content.strip()
    inline_str = ''

    # Converts \$ to %24 (html $).
    content = re.sub(r'(^|(?:[^\\]))\\\$', ' %24 ', content)

    if not content.startswith('$'):
        is_math = False
    else:
        is_math = True

    content = content.split('$')

    for block in content:
        if all(c in '\n\r\t ' for c in block):
            continue
        if not is_math:
            inline_str += f'\\text{{{block}}} '
        else:
            inline_str += block + ' '

        is_math = not is_math

    return inline_str.replace(' %24 ', '\\$ ')


class LatexCog:
    @commands.command(
        name='latex', aliases=['tex'],
        brief='Attempts to parse the given LaTeX string and display a '
              'preview.')
    async def latex_cmd(self, ctx, *, content: str):
        """
        Pass the `-inl` flag as the first argument to enable inline rendering
        mode.
        """
        inline_flag = '-inl'

        if content == inline_flag:
            raise commands.MissingRequiredArgument('content')
        elif content.startswith(inline_flag + ' '):
            content = reformat_inline(content[len(inline_flag) + 1:])

        url = generate_url(content,
                           fg_colour='RoyalBlue',
                           size=10)

        embed = discord.Embed()
        embed.set_image(url=url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LatexCog())
