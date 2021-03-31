import discord
import asyncio
import datetime
from re import search
import re
import requests
from discord.ext import commands

domains = [
    ".com",
    ".net",
    ".xyz",
    ".it",
    ".org"
]
otherdomains = [
    "com",
    "net",
    "xyz",
    "it",
    "org"
]

class AutoMod(commands.Cog):
    def __init__(self,bc):
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.bc = bc


    @commands.Cog.listener()
    async def on_message(self,message):
        def _check(m):
            return (m.author == message.author
					and len(m.mentions)
					and (datetime.datetime.utcnow()-m.created_at).seconds < 4)
        #print(f"{message.content} in {message.guild.name}")
        
        if not message.author.bot:
            try:
                data1 = await self.bc.linksonly.find(message.guild.id)
                data2 = await self.bc.modroles.find(message.guild.id)
                #Antispam Mentions
                msgs = list(filter(lambda m: _check(m), self.bc.cached_messages))
                if len(msgs) >= 3:
                    await message.channel.send("{} Don't spam mentions pls or else!".format(message.author.mention), delete_after=10)
                    try:
                        await message.delete()
                    except:
                        pass

                #Anti Links in channels
                
                elif message.channel.id not in data1["channels"]:
                    if data1 is None:
                        return
                    if data2 is not None:
                        for i in data2["roles"]:
                            role = discord.utils.get(message.guild.roles,id=i)
                            if role in message.author.roles:
                                return
                    if search(self.url_regex, message.content):
                        await message.channel.send(message.author.mention + " You can't send links in this channel.", delete_after=10)
                        try:
                            await message.delete()
                        except:
                            pass
                    else:
                        linkstr = message.content
                        words = linkstr.split()
                        for word in words:
                            if word in domains:
                                word = words[words.index(word) - 1] + word
                            elif word in otherdomains:
                                if "." in words[words.index(word) - 1]:
                                    word = words[words.index(word) - 2] + words[words.index(word) - 1] + word
                            try:
                                res = requests.get("http://" + word)
                            except:
                                continue
                            else:
                                status_code = res.status_code
                        if status_code == 200:
                            await message.channel.send(message.author.mention + " You can't send links in this channel.", delete_after=10)
                            try:
                                await message.delete()
                            except:
                                pass
            except:
                pass

def setup(bc):
  bc.add_cog(AutoMod(bc))

                

                
                
                

def setup(bc):
    bc.add_cog(AutoMod(bc))