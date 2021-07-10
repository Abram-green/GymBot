import os
import time
import asyncio
import random
import discord
import dbcontrol
import datetime
import event
import commands as c
from constants import *
from discord import utils
from discord.ext import commands
from dislash import slash_commands, Option, Type
from dislash.interactions import *
from discord_components import Button, ButtonStyle, DiscordComponents


bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())
slash = slash_commands.SlashClient(bot)
test_guilds = [856942427821441025]


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name="gachimuchi", type=discord.ActivityType.watching))
    guild = bot.get_guild(856942427821441025)


@bot.event
async def on_member_join(member):
    try:
        b = dbcontrol.load_profile(member)
    except Exception:
        dbcontrol.new_profile(member)
        await member.add_roles(member.guild.get_role(roles[0]))


@bot.event
async def on_message(ctx):
    await bot.process_commands(ctx)
    profile = dbcontrol.load_profile(ctx.author)
    event.check(ctx.author)
    xp = len(ctx.content) + 25
    text = 'gachimuchi'
    ids = []
    homes = False
    for r in ctx.author.roles:
        ids.append(r.id)
    for id in ids:
        if id in locations:
            homes = id
    if "🤼‍♂️" in ctx.content:
        xp *= 3
        profile["gym_emoji"] += 1
    profile["xp"] += xp
    if profile["xp"] >= 200:
        profile["level"] = 2
        profile["xp_l"] = 600
    if profile["xp"] >= profile["xp_l"]:
        profile["level"] = 3
        profile["xp_l"] = 1200
    if profile["xp"] >= profile["xp_l"]:
        profile["level"] = 4
        profile["xp_l"] = 2400
    if profile["xp"] >= profile["xp_l"]:
        profile["level"] = 5
        profile["xp_l"] = 3600
    if profile["level"] == 5 and 856945820162064416 in ids:
        profile["xp_l"] = 1000000
    if profile["xp"] >= profile["xp_l"]:
        profile["level"] = 777
        profile["xp_l"] = 1000000000 * 10**100
        text = f"the anal of my friend {ctx.author.name}"
    if profile["level"] == 777:
        text = f"the anal of my friend {ctx.author.name}"
    await bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.watching))
    if profile["level"] == 5 and 856945820162064416 not in ids:
        try:
            role = ctx.guild.get_role(roles[roles.index(ctx.author.roles[1].id) + 1])
            await ctx.author.edit(roles=[role])
            data = {
                "level": 1,
                "xp": 0,
                "xp_l": 100,
                "gym_emoji": 0
            }
            profile["level"] = data["level"]
            profile["xp"] = data["xp"]
            profile["xp_l"] = data["xp_l"]
            await ctx.channel.send(f"Ого! Ты уже {role.mention}")
        except Exception:
            pass
    if homes:
        home = ctx.guild.get_role(homes)
        for m in home.members:
            if m.id == ctx.author.id:
                dbcontrol.save_profile(profile, ctx.author)
            else:
                profile1 = dbcontrol.load_profile(m)
                profile1["xp"] += xp
                if profile1["xp"] >= 200:
                    profile1["level"] = 2
                    profile1["xp_l"] = 600
                if profile1["xp"] >= profile["xp_l"]:
                    profile1["level"] = 3
                    profile1["xp_l"] = 1200
                if profile1["xp"] >= profile["xp_l"]:
                    profile1["level"] = 4
                    profile1["xp_l"] = 2400
                if profile1["xp"] >= profile["xp_l"]:
                    profile1["level"] = 5
                    profile1["xp_l"] = 3600
                if profile1["level"] == 5 and 856945820162064416 in ids:
                    profile1["xp_l"] = 1000000
                if profile1["xp"] >= profile["xp_l"]:
                    profile1["level"] = 777
                    profile1["xp_l"] = 1000000000 * 10 ** 100
                    text = f"the anal of my friend {ctx.author.name}"
                if profile1["level"] == 777:
                    text = f"the anal of my friend {ctx.author.name}"
                await bot.change_presence(activity=discord.Activity(name=text, type=discord.ActivityType.watching))
                if profile1["level"] == 5 and 856945820162064416 not in ids:
                    try:
                        role = ctx.guild.get_role(roles[roles.index(ctx.author.roles[1].id) + 1])
                        await ctx.author.edit(roles=[role])
                        data = {
                            "level": 1,
                            "xp": 0,
                            "xp_l": 100,
                            "gym_emoji": 0
                        }
                        profile1["level"] = data["level"]
                        profile1["xp"] = data["xp"]
                        profile1["xp_l"] = data["xp_l"]
                        await ctx.channel.send(f"Ого! Ты уже {role.mention}")
                    except Exception:
                        pass
                dbcontrol.save_profile(profile1, m)
    else:
        dbcontrol.save_profile(profile, ctx.author)


@bot.event
async def on_voice_state_update(member, before, after):
    global VoiceMembers
    if member.voice is not None:
        if member.voice.afk is not True:
            VoiceMembers.update({member.id: True})
            while VoiceMembers[member.id]:
                await dbcontrol.update_voice_time(member, f"{datetime.datetime.today().day}:{datetime.datetime.today().hour}:{datetime.datetime.today().minute}:{datetime.datetime.today().second}")
                await asyncio.sleep(1)
                await dbcontrol.update_voice_time(member, f"{datetime.datetime.today().day}:{datetime.datetime.today().hour}:{datetime.datetime.today().minute}:{datetime.datetime.today().second}", True)
    if before.channel is not None:
        if before.afk is not True:
            VoiceMembers.update({member.id: False})


@slash.command(name="rang", description="Show rang", guild_ids=test_guilds, options=[Option("member", "Enter the member", Type.USER)])
async def _rang(inter, member=None):
    await c.rang(inter, member)


@bot.command()
async def rang(ctx, member: discord.Member = None):
    await c.rang(ctx, member)


@slash.command(name="desc", description="Show desc", guild_ids=test_guilds, options=[Option("member", "Enter the member", Type.USER)])
async def _desc(inter, member=None):
    await c.desc(inter, member)


@bot.command()
async def desc(ctx, member: discord.Member = None):
    await c.desc(ctx, member)


@slash.command(name="color", description="Change color", guild_ids=test_guilds)
async def _color(ctx):
    await c.color(ctx, bot)


@bot.command()
async def color(ctx):
    await c.color(ctx, bot)


@slash.command(name="location", description="Change location", guild_ids=test_guilds)
async def _location(ctx):
    await c.location(ctx, bot)


@bot.command()
async def location(ctx):
    await c.location(ctx, bot)


@slash.command(name="buy", description="Purchasing for xp", guild_ids=test_guilds)
async def _buy(ctx):
    await c.buy(ctx, "лист", None)


@bot.command()
async def buy(ctx, cmd, *options):
    await c.buy(ctx, cmd, options)


@slash.command(name="event", description="Show event for this game", guild_ids=test_guilds)
async def _event(ctx):
    await c.event(ctx)


bot.run(token)