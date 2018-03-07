#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Embed preview cog utility.
"""
import io                             # StringIO
import traceback                      # Traceback utils
from discord import embeds            # Embeds
from discord import utils             # OAuth2 URL generation
import yaml                           # YAML parser
from neko2.engine import commands     # Commands decorators
from neko2.shared.other import perms  # Permission bits.


class DiscordUtilCog:
    @commands.command(
        name='geninvite',
        brief='Generates an OAuth invite URL from a given snowflake client ID',
        help='Valid options: ```' +
             ', '.join(perms.Permissions.__members__.keys()) +
             '```')
    async def generate_invite(self, ctx, client_id: str, *permissions: str):
        perm_bits = 0

        for permission in permissions:
            if permission not in perms.Permissions:
                return await ctx.send(f'{permission} is not recognised.')
            else:
                perm_bits |= perms.Permissions[permission]

        await ctx.send(
            utils.oauth_url(
                client_id,
                permissions=perms.Permissions.to_discord_type(perm_bits),
                guild=ctx.guild
            ))

    @commands.command(
        name='embed',
        brief='Takes YAML input and generates a preview for an embed.')
    async def embed_preview(self, ctx, *, dom):
        """
        Available options:
        title, description, color, colour, footer_text, footer_icon,
        thumbnail, image, author_name, author_url, author_icon,
        url, fields.

        Field options:
        name (required), value (required), inline (boolean, defaults to
        True if not specified).

        Example:

        ---
        title: Hello
        description: World!
        color: 0xF0F0F0
        fields:
        - name: foo
          value: bar
        - name: baz
          value: bork
          inline: no
        ...
        """

        dom: str = dom.strip()

        if dom.startswith('```yaml\n'):
            dom = dom[8:]
        elif dom.startswith('```\n'):
            dom = dom[4:]

        if dom.endswith('```'):
            dom = dom[:-3]

        try:
            with io.StringIO(dom) as stream:
                dom: dict = yaml.load(stream)
                if not isinstance(dom, dict):
                    return await ctx.send('Expected YAML dictionary.')

                # For simplicity, translate color to colour.
                if 'color' in dom:
                    dom['colour'] = dom.pop('color')

            # Helper.
            def get(key: str,
                    *,
                    type_t=None,
                    default=embeds.EmptyEmbed,
                    target=dom):

                if type_t is None:
                    type_t = str

                k_value = target.get(key, default)
                if k_value != default and not isinstance(k_value, type_t):
                    raise TypeError(f'Expected {key} to be {type_t.__name__}')
                else:
                    return k_value

            # Embed to populate
            embed = embeds.Embed()

            # Any warning strings
            warnings = []

            embed.title = get('title')
            embed.description = get('description')

            colour = get('colour', type_t=(int, str))
            if isinstance(colour, str):
                colour = int(colour, 16)
            embed.colour = colour

            embed.set_footer(
                text=get('footer_text'),
                icon_url=get('footer_icon'))

            if 'thumbnail' in dom:
                embed.set_thumbnail(url=get('thumbnail'))

            if 'image' in dom:
                embed.set_image(url=get('image'))
                embed.set_author(
                    name=get('author_name'),
                    url=get('author_url'),
                    icon_url=get('author_icon'))

            for i, field in enumerate(get('fields',
                                          type_t=list,
                                          default=tuple())):

                name = get('name', target=field)
                value = get('value', target=field)
                inline = get('inline', type_t=bool, default=True, target=field)

                if name is embeds.EmptyEmbed or len(name.strip()) == 0:
                    warnings.append(f'Field #{i+1}\'s name is empty.')
                elif len(name) > 256:
                    warnings.append(f'Field #{i+1}\'s name is greater than '
                                    '256 chars')

                if value is embeds.EmptyEmbed or len(value.strip()) == 0:
                    warnings.append(f'Field #{i+1}\'s value is empty.')
                elif len(value) > 256:
                    warnings.append(f'Field #{i+1}\'s value is greater than '
                                    '2048 chars')

                embed.add_field(name=name, value=value, inline=inline)

            if colour is not embeds.EmptyEmbed:
                if not (0 <= colour <= 0xFFFFFF):
                    warnings.append('Colour should be in range [0x0, 0xFFFFFF]')
            if embed.title and len(embed.title) > 256:
                warnings.append('Title is greater than 256 chars')
            if embed.description and len(embed.description) > 2048:
                warnings.append('Description is greater than 2048 chars')
            if embed.fields and len(embed.fields) >= 25:
                warnings.append('There are more than 24 fields.')

            # Send any warnings first.
            if warnings:
                await ctx.send(f'Encountered one or more warnings!\n'
                               + '\n'.join(f'- {w}' for w in warnings))

            return await ctx.send('_Embed preview_', embed=embed)
        except BaseException as err:
            traceback.print_exc()
            return await ctx.send(str(err))


def setup(bot):
    bot.add_cog(DiscordUtilCog())
