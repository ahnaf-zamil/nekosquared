#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Ported from Neko v1. Plots the ISS's location on a map.

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
import datetime
import enum
import io

import PIL.Image as image
import PIL.ImageDraw as draw
import discord

from neko2.shared import commands, ioutil, traits

default_map_image = image.open(ioutil.in_here('mercator-small.png'))


class MapCoordinate(enum.Enum):
    long_lat = enum.auto()
    xy = enum.auto()


class MercatorProjection:
    """
    Holds a PIL image and allows for manipulation using longitude-latitude
    locations.

    :param map_image: the image object to use for the projection.
    """

    def __init__(self, map_image: image.Image = None):
        """
        Creates a mercator projection from the given Image object.

        This assumes that 0E,0N is at the central pixel.

        If no image is given, the default mercator bitmap is used.
        """
        if map_image is None:
            map_image = default_map_image.copy()

        self.image = map_image
        self.ox, self.oy = map_image.width / 2, map_image.height / 2

        # Differential of X in pixels per degree
        self.dx = map_image.width / 360

        # Differential of Y in pixels per degree
        self.dy = map_image.height / 180

    @property
    def width(self):
        return self.image.width

    @property
    def height(self):
        return self.image.height

    def swap_units(self, vertical, horizontal, input_measurement):
        """
        Converts between X,Y and Lat,Long, depending on measurement.

        :return a tuple of (x,y) or (lat,long)
        """
        if input_measurement == MapCoordinate.long_lat:
            horizontal = (horizontal * self.dx) + self.ox
            vertical = self.oy - vertical * self.dy

            return (horizontal, vertical)
        elif input_measurement == MapCoordinate.xy:
            horizontal = (horizontal - self.ox) / self.dx
            vertical = (self.oy - vertical) / self.dy
            return (vertical, horizontal)
        else:
            raise TypeError('Unknown measurement')

    def duplicate(self):
        """Deep copy the projection."""
        return MercatorProjection(self.image.copy())

    def pen(self) -> draw.ImageDraw:
        """Gets an object capable of drawing over the projection."""
        return draw.ImageDraw(self.image)


class SpaceCog(traits.CogTraits):
    async def plot(self, latitude, longitude, bytesio):
        """
        Plots a longitude and latitude on a given mercator projection.

        :param latitude: the latitude.
        :param longitude: the longitude.
        :param bytesio: the bytes IO to dump PNG data to.
        """

        def _plot():
            mercator = MercatorProjection()

            x, y = mercator.swap_units(
                latitude,
                longitude,
                MapCoordinate.long_lat
            )

            x, y = int(x), int(y)

            pen = mercator.pen()

            """
            pixels = [
                (x - 1, y - 1), (x - 1, y + 1),
                (x, y),
                (x + 1, y - 1), (x + 1, y + 1),
            ]

            pen.point([(x % mercator.width, y) for x, y in pixels], (255, 0, 
            0))
            """
            pen.ellipse([(x - 4, y - 4), (x + 4, y + 4)], (255, 0, 0))

            return mercator.image

        img = await self.run_in_io_executor(_plot)

        img.save(bytesio, 'PNG')

        # Seek back to the start
        bytesio.seek(0)

    @commands.command(brief='Shows you where the ISS is.')
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def iss(self, ctx):
        """
        Calculates where above the Earth's surface the ISS is currently,
        and plots it on a small map.
        """

        with ctx.channel.typing():
            # Plot the first point
            with io.BytesIO() as b:
                http = await self.acquire_http()
                res = await http.request(
                    'GET',
                    'https://api.wheretheiss.at/v1/satellites/25544')

                data = await res.json()
                image_fut = self.plot(data['latitude'], data['longitude'], b)

                assert isinstance(data, dict), 'I...I don\'t understand...'

                long = data['longitude']
                lat = data['latitude']
                time = datetime.datetime.fromtimestamp(data['timestamp'])
                altitude = data['altitude']
                velocity = data['velocity']

                is_day = data['visibility'] == 'daylight'

                desc = '\n'.join([
                    f'**Longitude**: {long:.3f}°E',
                    f'**Latitude**: {abs(lat):.3f}°{"N" if lat >= 0 else "S"}',
                    f'**Altitude**: {altitude:.3f} km',
                    f'**Velocity**: {velocity:.3f} km/h',
                    f'**Timestamp**: {time} UTC'
                ])

                embed = discord.Embed(
                    title='International space station location',
                    description=desc,
                    color=0xFFFF00 if is_day else 0x0D293B,
                    url='http://www.esa.int/Our_Activities/Human_Spaceflight'
                        '/International_Space_Station'
                        '/Where_is_the_International_Space_Station '
                )

                embed.set_footer(text='Data provided by whereistheiss.at')

                await image_fut
                file = discord.File(b, 'iss.png')

                await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(SpaceCog())
