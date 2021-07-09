from typing import Dict, Any

import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import asyncio
import os
import json
import time
from dislash import slash_commands, Option, Type
from dislash.interactions import *
from constants import *
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
queues = {}


def check_queue(id, ctx, loop):
    global queues
    if loop:
        m = queues[id].pop(0)
        queues[id].append(m)
        return ctx.voice_client.play(m, after=lambda e: check_queue(id, ctx, loop))
    else:
        return ctx.voice_client.play(queues[id].pop(0), after=lambda e: check_queue(id, ctx, loop))


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5, ctx):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.id = data.get('id')
        self.duration = data.get('duration')
        self.channel = data.get('uploader')
        self.channel_id = data.get('channel_id')
        self.streaming_from = 'Youtube'
        self.streaming_from_url = 'https://youtube.com'
        self.start_playing = time.time()
        self.resquest_by = ctx.message.author

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True, ctx):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        if ctx.guild.id in queues:
            queues[ctx.guild.id].append(cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, before_options=ffmpeg_before_opts), data=data, ctx=ctx))
        else:
            queues.update({ctx.guild.id: []})
            queues[ctx.guild.id].append(cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, before_options=ffmpeg_before_opts), data=data, ctx=ctx))
        return queues[ctx.guild.id][len(queues[ctx.guild.id]) - 1]


class Music(commands.Cog):
    test_guilds = [856942427821441025]
    def __init__(self, bot):
        global slash
        self.bot = bot
        self.loop = False


    @commands.command(aliases=['join', 'j'])
    async def _join(self, ctx, *, channel: discord.VoiceChannel=None):
        """Joins a voice channel"""
        channel = channel or ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(aliases=['l', 'leave'])
    async def _leave(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
            return
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        await voice.disconnect()
        emb = discord.Embed(
            title="Disconnect!",
            color=ctx.author.top_role.color
        )
        await ctx.send(embed=emb)
        for l in queues[ctx.guild.id]:
            l.pop(len(queues[ctx.guild.id]) - 1)

    @commands.command(aliases=['play', 'p'])
    async def _play(self, ctx, *, url):
        count = queues.get(ctx.guild.id)
        if not ctx.author.voice:
            await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
            return
        if count is None:
            count = []
        desc = ""
        if ctx.voice_client.is_playing():
            desc = "добавлено в очередь"
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, ctx=ctx)
        stitle = str(player.title.replace("[", " ").replace("]", " ")[:44] + "...") if len(
            player.title) > 45 else player.title
        channel_yt = player.channel
        channel_yt_id = player.channel_id
        duration = time.strftime('%H:%M:%S',
                                 time.gmtime(player.duration)) if player.duration > 3600 else time.strftime('%M:%S',
                                                                                                            time.gmtime(
                                                                                                                player.duration))
        yt_icon_url = f'https://i.ytimg.com/vi/{player.id}/hqdefault.jpg?'
        channel_yt_SS = f'https://www.youtube.com/channel/{channel_yt_id}'
        embed = discord.Embed(
            title=f'{stitle}',
            color=ctx.author.top_role.color,
            description=desc,
            url=f'https://www.youtube.com/watch?v={player.id}'
            # description = f'Playing [{stitle}](https://www.youtube.com/watch?v={player.id}) in *{get(self.bot.voice_clients, guild = ctx.guild).channel}*'
        )
        embed.set_author(
            name=str(ctx.guild),
            icon_url=ctx.guild.icon_url,
        )
        embed.set_thumbnail(
            url=yt_icon_url
        )
        embed.add_field(
            name='Ютубер',
            value=f"[{channel_yt}]({channel_yt_SS})",
            inline=True
        )
        embed.add_field(
            name='Канал',
            value=f'[{get(self.bot.voice_clients, guild=ctx.guild).channel}](https://discordapp.com/channels/{str(ctx.guild.id)}/{str(get(self.bot.voice_clients, guild=ctx.guild).channel.id)})',
            inline=True
        )
        embed.add_field(
            name='Запросил',
            value=ctx.author.mention,
            inline=True
        )
        embed.add_field(
            name='Длина видео',
            value=duration,
            inline=True
        )
        embed.set_footer(
            text=ctx.author.name,
            icon_url=ctx.author.avatar_url
        )
        now_playing = await ctx.send(embed=embed)
        if ctx.voice_client.is_playing() is False:
            self.ctx = ctx
            self.url = url
            check_queue(ctx.guild.id, ctx, self.loop)

    @commands.command(aliases=['queue', 'q'])
    async def _q(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
            return
        desc = ""
        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing():
                playing_data = ctx.voice_client.source
                video_url = f'https://www.youtube.com/watch?v={playing_data.id}'
                video_title = playing_data.title
                stitle = str(video_title.replace("[", " ").replace("]", " ")[:44] + "...") if len(
                    video_title) > 45 else video_title
                desc = f"**Текущий трек**\n[{video_title}]({video_url})"
        embed = discord.Embed(
            title="Список треков",
            description=desc,
            color=ctx.author.top_role.color
        )
        a = 1
        tim = 0
        for player in queues[ctx.guild.id]:
            stitle = str(player.title.replace("[", " ").replace("]", " ")[:44] + "...") if len(
                player.title) > 45 else player.title
            channel_yt = player.channel
            channel_yt_id = player.channel_id
            duration = time.strftime('%H:%M:%S',
                                     time.gmtime(player.duration)) if player.duration > 3600 else time.strftime('%M:%S',
                                                                                                                time.gmtime(
                                                                                                                    player.duration))
            yt_icon_url = f'https://i.ytimg.com/vi/{player.id}/hqdefault.jpg?'
            mem = get(ctx.guild.members, id=self.bot.user.id)
            channel_yt_SS = f'https://www.youtube.com/channel/{channel_yt_id}'
            b = False
            if a % 2 == 0:
                b = True
            embed.add_field(
                name=f"[{a}] {stitle}",
                value=f"{duration}\n[{channel_yt}]({channel_yt_SS})",
                inline=b
            )
            a += 1
            tim += player.duration
        playing_data = ctx.voice_client.source
        if len(queues[ctx.guild.id]) != 0:
            tim += int(playing_data.duration - (time.time() - playing_data.start_playing))
            tim = time.strftime('%H:%M:%S', time.gmtime(tim)) if tim > 3600 else time.strftime('%M:%S', time.gmtime(tim))
            embed.set_footer(text=f"Общее время: {tim}")
        else:
            embed.set_footer(text="Треков нету")
        await ctx.send(embed=embed)

    @commands.command(aliases=['qs', 'queueskip'])
    async def _qs(self, ctx, index: int):
        vc = ctx.voice_client
        if not ctx.author.voice:
            await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
            return
        if not vc or not vc.is_connected():
            return await ctx.send('Я вообще сейчас ничего не воизпровожу!', delete_after=20)
        if index - 1 <= len(queues):
            player = queues[ctx.guild.id].pop(index - 1)
            title = str(player.title.replace("[", " ").replace("]", " ")[:44] + "...") if len(
                player.title) > 45 else player.title
            channel_yt = player.channel
            channel_yt_id = player.channel_id
            channel_yt_SS = f'https://www.youtube.com/channel/{channel_yt_id}'
            emb = discord.Embed(
                title="Skipped!",
                description=f"[{title}](https://www.youtube.com/watch?v={player.id})\n[{channel_yt}]({channel_yt_SS})",
                color=ctx.author.top_role.color
            )
            await ctx.send(embed=emb)
        elif index == 0:
            if vc.is_paused():
                pass
            elif not vc.is_playing():
                return

            emb = discord.Embed(
                title="Skipped!",
                color=ctx.author.top_role.color
            )
            await ctx.send(embed=emb)
            vc.stop()
            check_queue(ctx.guild.id, ctx, self.loop)
        else:
            await ctx.send("У меня нет в очереди столько треков!")

    @commands.command(aliases=['ql', 'queueloop'])
    async def _ql(self, ctx):
        self.loop = True
        emb = discord.Embed(
            title="Queue loop!",
            color=ctx.author.top_role.color
        )
        await ctx.send(embed=emb)

    @commands.command(aliases=['volume', 'v'])
    async def _volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send(f'{ctx.message.author.mention}, зайди в войс')

        ctx.voice_client.source.volume = volume / 100

        emb = discord.Embed(
            title="Changed volume!",
            description=f"Volume: {ctx.voice_client.source.volume * 100}",
            color=ctx.author.top_role.color
        )
        await ctx.send(embed=emb)

    @commands.command(aliases=['skip', 's'])
    async def _skip(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client
        if not ctx.author.voice:
            await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
            return
        if not vc or not vc.is_connected():
            return await ctx.send('Я вообще сейчас ничего не воизпровожу!', delete_after=20)
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        emb = discord.Embed(
            title="Skipped!",
            color=ctx.author.top_role.color
        )
        await ctx.send(embed=emb)
        vc.stop()
        check_queue(ctx.guild.id, ctx, self.loop)


    @commands.command()
    async def np(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
            return
        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                playing_data = ctx.voice_client.source
                video_url = f'https://www.youtube.com/watch?v={playing_data.id}'
                video_title = playing_data.title
                stitle = str(video_title.replace("[", " ").replace("]", " ")[:44] + "...") if len(
                    video_title) > 45 else video_title
                streaming_from = playing_data.streaming_from
                streaming_from_url = playing_data.streaming_from_url
                duration = time.strftime('%H:%M:%S', time.gmtime(
                    playing_data.duration)) if playing_data.duration > 3600 else time.strftime('%M:%S', time.gmtime(
                    playing_data.duration))
                channel = 'Канал автора: ' if playing_data.channel is None else playing_data.channel
                channel_url = f'https://youtube.com/channel/{playing_data.channel_id}'
                thumbnail = f'https://i.ytimg.com/vi/{playing_data.id}/hqdefault.jpg?'
                resquest_by = playing_data.resquest_by
                current_playing_time = time.strftime('%H:%M:%S', time.gmtime(
                    time.time() - playing_data.start_playing)) if playing_data.duration > 3600 else time.strftime(
                    '%M:%S', time.gmtime(time.time() - playing_data.start_playing))
                duration_player_pos = int((time.time() - playing_data.start_playing) / (playing_data.duration / 25))
                duration_player_final = ''.join([char * duration_player_pos for char in '▬']) + '⚪' + ''.join(
                    [char * (24 - duration_player_pos) for char in '▬'])

                embed = discord.Embed(
                    title='',
                    color=ctx.author.top_role.color,
                    description=f'{ctx.message.author.mention}\n**Играет в *{get(self.bot.voice_clients, guild=ctx.guild).channel}*...**\n\nТрек: [{stitle}]({video_url})\nКанал автора: [{channel}]({channel_url})\nЗапросил: {resquest_by.mention}\n\n{current_playing_time} | {duration}\n{duration_player_final}\n'
                )
                embed.set_footer(text='Манил etc.')
                embed.set_thumbnail(url=thumbnail)
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                now_playing = await ctx.send(embed=embed)
            else:
                await ctx.send('Я вообще сейчас ничего не воизпровожу!', delete_after=20)
        else:
            await ctx.send(f'{ctx.message.author.mention}, я не подключен к каналу')

    @commands.command(name='pause')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
            emb = discord.Embed(
                title="Pause!",
                color=ctx.author.top_role.color
            )
            await ctx.send(embed=emb)
        else:
            await ctx.send('Я вообще сейчас ничего не воизпровожу!', delete_after=20)

    @commands.command(name='resume')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
            emb = discord.Embed(
                title="Resume!",
                color=ctx.author.top_role.color
            )
            await ctx.send(embed=emb)
        else:
            await ctx.send('Я вообще сейчас ничего не воизпровожу!', delete_after=20)

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @_play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
                raise commands.CommandError("Author not connected to a voice channel.")
        if ctx.author.voice.channel is None:
            if not ctx.author.voice:
                await ctx.send(f'{ctx.message.author.mention}, зайди в войс')
                return
            async with ctx.typing():
                url = self.url
                player = await YTDLSource.from_url(url=url, loop=self.bot.loop, stream=True, ctx=ctx)
                self.player = player
            pass


def setup(bot):
    bot.add_cog(Music(bot))