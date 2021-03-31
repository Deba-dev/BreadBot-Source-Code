import discord
from discord.ext import commands
import asyncio
import os
import random
import json
import traceback
import time
import datetime
from PIL import Image, ImageDraw, ImageOps, ImageFont
import contextlib
import sys
import string
import io
from dateutil.relativedelta import relativedelta

def gen_code():
    chars = list(string.hexdigits) + list(string.octdigits)
    num = list(string.digits) + list(string.hexdigits) + list(string.octdigits)
    former = []
    for i in range(random.randint(5, 8)):
        x = ('y', 'n')
        if random.choice(x) == 'y':
            if random.choice(x) == 'y':
                former.append(random.choice(chars).lower())
            else:
                former.append(random.choice(chars).upper())
        else:
            former.append(random.choice(num))
    return ''.join(map(str, former))

class example(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot == True:
            pass
        else:
            guild = message.guild
            with open('snipe.json', 'r') as f:
                snipe = json.load(f)
            snipe[str(message.guild.id)] = {}
            snipe[str(message.guild.id)]["content"] = f'{message.content}'
            snipe[str(message.guild.id)]["author"] = f'{message.author}'
            snipe[str(message.guild.id)]["avatar"] = f'{message.author.avatar_url}'
            snipe[str(guild.id)]["timedelete"] = f"{datetime.datetime.utcnow()}"
            with open('snipe.json', 'w') as f:
                json.dump(snipe, f, indent=4)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        bots = 0
        for membercheck in member.guild.members:
            if membercheck.bot == True:
                bots += 1
            else:
                pass
        data = await self.bc.leaves.find(member.guild.id)
        if not data["channel"]:
            pass
        else:
            try:
                channel = int(data["channel"])
                channel = self.bc.get_channel(int(channel))
                await channel.send("{} left {} we now have {} members".format(
                    member, member.guild.name,
                    len(member.guild.members)))
            except KeyError:
                pass

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        if after.nick is None:
            return
        data2 = await self.bc.modroles.find(before.guild.id)
        data3 = await self.bc.censor.find(before.guild.id)
        if data3:
            if data2 is not None:
                for i in data2["roles"]:
                    role = discord.utils.get(before.guild.roles,id=i)
                    if role in before.roles:
                        return
                    else:
                        continue
            else:
                pass
            for i in data3["words"]:
                if str(i) in str(after.nick) and data3["toggled"]:
                    await after.edit(nick="Moderated Nickname " + gen_code())
                    break
                else:
                    continue
        else:
            pass

    @commands.command()
    async def dat(self, ctx):
        year = int(datetime.datetime.now().strftime("%Y")) - int(
            ctx.author.created_at.strftime("%Y"))

        month = int(datetime.datetime.now().strftime("%m")) - int(
            ctx.author.created_at.strftime("%m"))
        if month < 0:
            month = month + 12
        day = int(datetime.datetime.now().strftime("%d")) - int(
            ctx.author.created_at.strftime("%d"))
        if day < 0:
            day = day + 30
        hour = int(datetime.datetime.utcnow().strftime("%H")) - int(
            ctx.author.created_at.strftime("%H"))
        if hour < 0:
            hour = hour + 24
        minute = int(datetime.datetime.now().strftime("%M")) - int(
            ctx.author.created_at.strftime("%M"))
        if minute < 0:
            minute = minute + 60
        await ctx.send(
            "{} years, {} months, {} days {} hours {} minutes ago".format(
                year, month, day, hour, minute))

    async def open_wel(self, guild):
        welcome = self.get_channels()

        if str(guild.id) in welcome:
            return False
        else:
            welcome[str(guild.id)] = {}
            welcome[str(guild.id)]["channel"] = "Not Set"

        with open("welcomes.json", "w") as f:
            json.dump(welcome, f, indent=4)
        return True

    async def get_channels(self):
        with open("welcomes.json", "r") as f:
            welcome = json.load(f)

        return welcome


def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file)


def setup(bc):
    bc.add_cog(example(bc))
