import os
import time
import asyncio
import random
import discord
import dbcontrol
import datetime
from constants import *
from discord.ext import commands
from dislash import slash_commands, Option, Type
from dislash.interactions import *


async def give_role(ctx, member: discord.Member, role: discord.Role):
    if ctx.author.id == 577583607581769729:
        await member.add_roles(role)


async def set_role(ctx, member: discord.Member, role: discord.Role):
    if ctx.author.id == 577583607581769729:
        await member.edit(roles=[role])
#
# @bot.command()
# async def new_gay(ctx, member:discord.Member):
#     dbcontrol.new_profile(member)
#     await member.edit(roles=[member.guild.get_role(roles[0])])

#
# @bot.command()
# async def ping(ctx, member: discord.Member):
#     for i in range(100):
#         m = await ctx.send(member.mention)
#         await m.delete()


async def rang(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    profile = dbcontrol.load_profile(member)
    xp = int("{0:.{1}f}".format(profile["xp"], 0))
    endLevel = profile['xp_l'] - xp
    embed = discord.Embed(title="Ранг:", description=f"{xp}/{profile['xp_l']}", color=member.roles[1].color)
    embed.add_field(name=f"Твой уровень: {profile['level']}", value=f"Осталось до следущего уровня: {endLevel}")
    embed.add_field(name=f"Время в войсе", value=f"{str(datetime.timedelta(seconds=profile.get('VoiceTime')))}")
    embed.add_field(name="Роль", value=f"{member.roles[1].mention}")
    embed.set_thumbnail(url=member.avatar_url_as())
    await ctx.send(embed=embed)


async def desc(ctx, member: discord.Member = None):
    ids = []
    gymcolor = None
    gymhero = None
    gymlocation = None
    descreption = ""
    if member is None:
        member = ctx.author
    for r in member.roles:
        ids.append(r.id)
    for id in ids:
        if id == 577583607581769729:
            descreption = "С мамой"
        if id in roles:
            gymhero = ctx.guild.get_role(id)
        if id in reactions:
            gymcolor = ctx.guild.get_role(id)
        if id in locations:
            gymlocation = ctx.guild.get_role(id)
    color = member.top_role.color
    emb = discord.Embed(title=member.display_name, descreption=descreption, color=color)
    if gymhero is not None:
        emb.add_field(name=f"Роль: {gymhero.name}", value=f"{gymHistory[gymhero.id]}", inline=False)
    if gymcolor is not None:
        emb.add_field(name="Цвет:", value=gymcolor.name, inline=False)
    if gymlocation is not None:
        emb.add_field(name=f"Локация: {gymlocation.name}", value=f"{locationDesc[gymlocation.id]}", inline=False)
    emb.add_field(name="Присоеденился", value=member.joined_at)
    emb.add_field(name="Аккаунт создан", value=member.created_at)
    await ctx.send(embed=emb)


async def color(ctx, bot=None):
    member = ctx.author
    ids = []
    for r in ctx.author.roles:
        ids.append(r.id)
    if roles[5] in ids:
        emb = discord.Embed(title="Выбери цвет!", color=ctx.author.top_role.color)
        row = ActionRow(
            Button(style=ButtonStyle.blurple, label="Красный   ", custom_id="❤"),
            Button(style=ButtonStyle.blurple, label="Оранжевый ", custom_id="🧡"),
            Button(style=ButtonStyle.blurple, label="Желтый    ", custom_id="💛"),
            Button(style=ButtonStyle.blurple, label="Зелёный   ", custom_id="💚")
        )
        row1 = ActionRow(
            Button(style=ButtonStyle.blurple, label="Голубой   ", custom_id="💙"),
            Button(style=ButtonStyle.blurple, label="Феолетовый", custom_id="💜"),
            Button(style=ButtonStyle.blurple, label="Негр      ", custom_id="🖤"),
            Button(style=ButtonStyle.blurple, label="Норм мен  ", custom_id="🤍")
        )
        msg = await ctx.send(embed=emb, components=[row, row1])
        resp = await bot.wait_for("button_click")
        if resp.author == ctx.author:
            role = member.guild.get_role(reactions[colorEmoji.index(resp.component.custom_id)])
            ids = []
            for r in member.roles:
                ids.append(r.id)
            for id in ids:
                if id not in reactions:
                    try:
                        await member.add_roles(member.guild.get_role(id))
                    except Exception:
                        pass
                else:
                    await member.remove_roles(member.guild.get_role(id))
            await member.add_roles(role)
            await resp.respond(content=f"Цвет изменён{resp.component.custom_id}")
        else:
            pass


async def location(ctx, bot):
    ids = []
    member = ctx.author
    for r in ctx.author.roles:
        ids.append(r.id)
    if roles[5] in ids:
        emb = discord.Embed(title="Выбери локацию!", color=ctx.author.top_role.color)
        row = ActionRow(
            Button(style=ButtonStyle.blurple, label="Gym", custom_id="Gym"),
            Button(style=ButtonStyle.blurple, label="Dungeon", custom_id="Dungeon")
        )
        row1 = ActionRow(
            Button(style=ButtonStyle.blurple, label="Anal", custom_id="Anal"),
            Button(style=ButtonStyle.blurple, label="Home", custom_id="Home")
        )
        msg = await ctx.send(embed=emb, components=[row, row1])
        resp = await bot.wait_for("button_click")
        if resp.author == ctx.author:
            role = None
            if resp.component.custom_id == "Gym":
                role = member.guild.get_role(locations[0])
            if resp.component.custom_id == "Dungeon":
                role = member.guild.get_role(locations[1])
            if resp.component.custom_id == "Anal":
                role = member.guild.get_role(locations[2])
            if resp.component.custom_id == "Home":
                role = member.guild.get_role(locations[3])
            ids = []
            for r in member.roles:
                ids.append(r.id)
            for id in ids:
                if id not in locations:
                    try:
                        await member.add_roles(member.guild.get_role(id))
                    except Exception:
                        pass
                else:
                    await member.remove_roles(member.guild.get_role(id))
            await member.add_roles(role)
            await resp.respond(content="Локация выбрана")
        else:
            await resp.respond(content="Это не твой сообщение!")


async def buy(ctx, cmd, options):
    cmd = shopList[cmd]
    p = dbcontrol.load_profile(ctx.author)
    if cmd == 0 and p["xp"] >= 0:
        text = f"Текущий лист услуг:\n1. Изменение никнейма бота - 100.000xp (ник стоит до тех пор, пока его не сменит кто-то другой). Для использования -buy ник <ник>\n2. Закрепление вашего сообщения. Для использования -buy закреп <id сообщения> - 50.000xp\n3. Открепление закрепленного сообщения. Для использования -buy откреп <id сообщения> - 60.000xp\n4. Управление пк (есть ограничения). Для использования -buy пк. - 10 .000.000xp"
        await ctx.send(text)
    if cmd == 1 and p["xp"] >= 10000000:
        m = ctx.guild.get_member(577583607581769729)
        code = ""
        for i in range(6):
            c = random.choice("qwertyuiopasdfghjklzxcvbnm")
            if random.choice([0, 1]) == 1:
                c = c.upper()
            code += c
        text = f"Твой код для активации: {code}"
        await ctx.author.send(text + "\n скинь этот код Abram")
        await m.send(text)
        p["xp"] -= 10000000
    if cmd == 2 and p["xp"] >= 60000:
        msg = await ctx.channel.fetch_message(int(options[0]))
        await msg.unpin()
        await ctx.send("Успешно!")
        p["xp"] -= 60000
    if cmd == 3 and p["xp"] >= 50000:
        msg = await ctx.channel.fetch_message(int(options[0]))
        await msg.pin()
        await ctx.send("Успешно!")
        p["xp"] -= 50000
    if cmd == 4 and p["xp"] >= 100000:
        t = ""
        for i in options:
            t += i + " "
        m = ctx.guild.get_member(856959819993841664)
        await m.edit(nick=t)
        await ctx.send("Успешно!")
        p["xp"] -= 100000
    dbcontrol.save_profile(p, ctx.author)


async def event(ctx):
    text = f"Сегодня задание: Просидеть в войсе 2 часа"
    await ctx.send(text)