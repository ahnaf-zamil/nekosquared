#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
YouTube player instance.

References:
    https://github.com/Rapptz/discord.py/blob/rewrite/examples/playlist.py
"""
import asyncio
import copy
import datetime
import os
from typing import Dict, Union

from async_timeout import timeout
from dataclasses import dataclass
import discord
import youtube_dl

from neko2.shared import commands
from neko2.shared import traits


if not discord.opus.is_loaded():
    if os.name == 'winnt':
        discord.opus.load_opus('libopus-0.dll')
    else:
        discord.opus.load_opus('libopus.so')


YOUTUBE_OPTS = {
    'format': 'webm[abr>0]/bestaudio/best',
    'ignoreerrors': True,
    'defaultsearch': 'auto',
    'source_address': '0.0.0.0',
    'quiet': True
}


def acknowledge(what, emoji=None):
    if emoji:
        return commands.acknowledge(what, emoji=emoji, timeout=None)
    else:
        return commands.acknowledge(what, timeout=None)


@dataclass()
class YouTubeVideo:
    requested_by: discord.Member    # Referrer
    when: datetime.datetime         # UTC
    yt_url: str                     # YouTube URL
    player: object                  # Not quite sure.


class Session(traits.CogTraits):
    def __init__(self,
                 bot: discord.Client,
                 voice_channel: discord.VoiceChannel,
                 text_channel: discord.TextChannel):
        self.voice_channel = voice_channel
        self.text_channel = text_channel

        # Our queue of tracks.
        self.queue = asyncio.Queue()

        # Event loop
        self.loop = bot.loop
        # Bot
        self.bot = bot

        # Get set later on.
        self.voice_client: discord.VoiceClient = None

        # Async event to trigger the next request.
        self.play_next_event = asyncio.Event()

        self.current_item = None

        self.loop.create_task(self.play_queue_runner())

        self.should_die = False

    async def initialise(self):
        # noinspection PyUnresolvedReferences
        self.voice_client = await self.voice_channel.connect()

    async def deinitialise(self):
        if self.voice_client:
            self.voice_client.stop()
            await self.voice_client.disconnect()

    @property
    def is_playing(self):
        if self.voice_client is None or self.current_item is None:
            return False
        else:
            return self.voice_client.is_playing()

    def next(self, error=None):
        if self.voice_client.is_playing():
            self.voice_client.stop()
            self.logger.info('Stopped VC client early.')

        if not error:
            self.play_next_event.set()
        else:
            print(error)

    async def play_queue_runner(self):
        """
        Asyncio loop to play audio from YouTube by using the queue.
        """
        while not self.should_die:
            self.logger.info('Iterating onto next item')

            # Clear the flag to transition to the next item.
            self.play_next_event.clear()

            await asyncio.sleep(1)

            # Get next song
            video = await self.queue.get()
            self.current_item = video

            embed = discord.Embed(title=f'NOW PLAYING {video.yt_url}')

            await self.text_channel.send(embed=embed)

            await self.run_in_io_executor(self.bot,
                                          self.voice_client.play,
                                          self.current_item.player,
                                          after=self.next)

            try:
                with timeout(600):
                    await self.play_next_event.wait()
            except asyncio.TimeoutError:
                await self.text_channel.send(
                    'You were idle too long \N{FROWNING FACE WITH OPEN MOUTH}')
                self.voice_client.stop()
                self.voice_channel = None
            finally:
                await self.voice_client.disconnect()
                self.voice_client = await self.voice_channel.connect()


class YouTubePlayerCog(traits.CogTraits):
    def __init__(self):
        # Maps tuples of guilds to their VC sessions.
        self.sessions: Dict[discord.Guild, Session] = {}

    @staticmethod
    async def __local_check(ctx):
        """Only allow use in guilds."""
        return bool(ctx.guild)

    @staticmethod
    def get_voice_channel(from_what: Union[discord.Member, commands.Context]):
        if isinstance(from_what, commands.Context):
            from_what = from_what.author

        voice_state: discord.VoiceState = from_what.voice
        voice_channel = voice_state.channel if voice_state else None
        return voice_channel

    @commands.group(invoke_without_subcommand=True)
    async def yt(self, ctx):
        pass

    @yt.command()
    async def here(self, ctx: commands.Context):
        text_channel = ctx.channel
        voice_channel = self.get_voice_channel(ctx)

        if not voice_channel:
            await ctx.send('Please enter a voice channel first!')
        elif ctx.guild in self.sessions:
            await self.sessions[ctx.guild].voice_client.move_to(voice_channel)
            acknowledge(ctx)
        else:
            sesh = Session(ctx.bot, voice_channel, text_channel)
            self.sessions[ctx.guild] = sesh
            await sesh.initialise()
            acknowledge(ctx)

    @yt.command(aliases=['stop', 'cya', 'bye'])
    async def leave(self, ctx: commands.Context):
        voice_channel = self.get_voice_channel(ctx)

        if not voice_channel:
            return await ctx.send('You are not in a voice channel.')
        elif ctx.guild not in self.sessions:
            return await ctx.send('I am not in your voice channel.')
        else:
            sesh = self.sessions[ctx.guild]
            await sesh.deinitialise()
            del self.sessions[ctx.guild]
            acknowledge(ctx)

    @yt.command()
    @commands.is_owner()
    async def leaveall(self, ctx: commands.Context):
        for channel in copy.copy(self.sessions):
            await self.sessions[channel].deinitialise()
            del self.sessions[channel]
        acknowledge(ctx)

    def make_player(self, url):
        yt_dl = youtube_dl.YoutubeDL(YOUTUBE_OPTS)
        info = yt_dl.extract_info(url, download=False)
        stream = discord.FFmpegPCMAudio(info['url'])
        return stream

    async def session_preamble(self, ctx):
        """
        Common checks to perform before alterring the state of the
        player. Namely, the author should be in the text channel of the
        session, the session channel should be valid, and the author should
        be in the same voice channel as the bot.

        If successful, the corresponding session to use is returned, otherwise
        we signal an invalid request by providing `None` as the result.
        """
        try:
            sesh = self.sessions[ctx.guild]

            if sesh.text_channel != ctx.channel:
                await ctx.send(f'Please move to {sesh.text_channel.mention}.')
                return None

            if sesh.voice_channel is None:
                await ctx.send('I am not in a channel.')
                await sesh.deinitialise()
                del self.sessions[ctx.guild]
                return None

            if sesh.voice_channel != self.get_voice_channel(ctx):
                # If we can, move the user to the right channel.
                try:
                    await ctx.author.move_to(
                        sesh.voice_channel,
                        reason='Tried to use me in a different VC to the one '
                               'I was already in.')
                    await ctx.send(f'{ctx.author.mention}: moved you to the '
                                   'channel I was already in!')
                    return sesh
                except discord.Forbidden:
                    await ctx.send(
                        f'I am currently in {sesh.voice_channel}... '
                        f'please move there.')
                    return None
            else:
                return sesh
        except KeyError:
            return None

    @yt.command(aliases=['enqueue', 'add'])
    async def play(self, ctx: commands.Context, *, url: str):

        sesh = await self.session_preamble(ctx)
        if not sesh:
            return

        try:
            player = await self.run_in_io_executor(
                ctx.bot, self.make_player, url)
        except TypeError:
            return await ctx.send('That doesn\'t seem to be a valid link.')

        video = YouTubeVideo(ctx.author,
                             datetime.datetime.now(),
                             url,
                             player)

        sesh.queue.put_nowait(video)

        await ctx.send(f'I have added <{url}> to the queue. It has '
                       f'{sesh.queue.qsize()} item(s) before it.')

    @yt.command()
    async def pause(self, ctx: commands.Context):
        sesh = await self.session_preamble(ctx)
        if not sesh:
            return
        else:
            await sesh.voice_client.pause()
            await ctx.send('Paused.')

    @yt.command()
    async def resume(self, ctx: commands.Context):
        sesh = await self.session_preamble(ctx)
        if not sesh:
            return
        else:
            await sesh.voice_client.resume()
            await ctx.send('Resumed.')

    @yt.command()
    async def next(self, ctx: commands.Context):
        sesh = await self.session_preamble(ctx)
        if not sesh:
            return
        else:
            if sesh.play_next_event.is_set():
                return await ctx.send('Reached the end of the queue.')
            sesh.next()
            acknowledge(ctx)

def setup(bot):
    bot.add_cog(YouTubePlayerCog())
