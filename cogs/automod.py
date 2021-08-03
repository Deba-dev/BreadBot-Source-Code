import discord
import asyncio
import aiohttp
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
    ".org",
    ".wtf",
    ".lol",
    ".tk",
    ".cf",
    ".ga",
    ".org"
]
otherdomains = [
    "com",
    "net",
    "xyz",
    "it",
    "org",
    "wtf",
    "lol",
    "tk",
    "cf",
    "ga",
    "org"
]

class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        try:
            default = {
                # 'response_class': ClientResponse,
                'rickroll_queries': ["rickroll","rick roll","rick astley","never gonna give you up", "dQw4w9WgXcQ"],
                'block': [],
                'timeout': aiohttp.ClientTimeout(total=100000000000000, sock_read=10)  # to prevent attacks relating to sending massive payload and lagging the client
            }
            default.update(kwargs)

            self.rickroll_regex = re.compile('|'.join(default['rickroll_queries']), re.IGNORECASE)
            self.block_list = default['block']
            del default['rickroll_queries']
            del default['block']
            super().__init__(*args, **default)
        except:
            raise
            super().__init__(*args, **kwargs)

    async def _request(self, *args, **kwargs):
        req = await super()._request(*args, **kwargs)
        regex = self.rickroll_regex
        content = str(await req.content.read())
        req.rickroll = bool(regex.search(content))
        blocked_urls = self.block_list
        urls = [str(redirect.url_obj) for redirect in req.history]
        return req

class AutoMod(commands.Cog):
    def __init__(self,bc):
        self.session = ClientSession()
        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.bc = bc

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        data = await self.bc.rickroll.find(after.guild.id)
        if data:
            if data["enabled"]:
                hl = []
                status_map = {
                    1: '\U0001f504',
                    2: '\U00002705',
                    3: '\U000027a1',
                    4: '\U0000274c',
                    5: '\U000026a0'
                    }
                def build_string(res):
                    return f'{status_map[int(res.status / 100)]} [{(res.url_obj.host + res.url_obj.path).strip("/")}]({res.url_obj}) ({res.status} {res.reason})'
                for word in after.content.replace("<", "").replace(">", "").split():
                    try:
                        r = await self.session.get(word)
                        text = await r.html()
                        for res in r.history:
                            hl.append(build_string(res))
                        hl.append(build_string(r))
                        rickroll = r.rickroll
                        if rickroll or "dQw4w9WgXcQ" in text:
                            await after.reply("Rickroll detected")
                    except:
                        try:
                            r = await self.session.get("http://" + word)
                            for res in r.history:
                                hl.append(build_string(res))
                            hl.append(build_string(r))
                            rickroll = r.rickroll
                            if rickroll:
                                await after.reply("Rickroll detected")
                        except:
                            pass
        def _check(m):
            return (m.author == after.author
					and len(m.mentions)
					and (datetime.datetime.utcnow()-m.created_at).seconds < 4)
        #print(f"{message.content} in {message.guild.name}")
        if not after.author.bot:
            try:
                data1 = await self.bc.linksonly.find(after.guild.id)
                data2 = await self.bc.modroles.find(after.guild.id)
                #Antispam Mentions
                msgs = list(filter(lambda m: _check(m), self.bc.cached_messages))
                if len(msgs) >= 3:
                    await after.channel.send("{} Don't spam mentions please!".format(after.author.mention), delete_after=10)
                    try:
                        await after.delete()
                    except:
                        pass

                #Anti Links in channels
                
                elif after.channel.id not in data1["channels"]:
                    if data1 is None:
                        return
                    if data2 is not None:
                        for i in data2["roles"]:
                            role = discord.utils.get(after.guild.roles,id=i)
                            if role in after.author.roles:
                                return
                    if search(self.url_regex, after.content):
                        await after.channel.send(after.author.mention + " You can't send links in this channel.", delete_after=10)
                        try:
                            await after.delete()
                        except:
                            pass
                    else:
                        linkstr = after.content
                        words = linkstr.split()
                        for word in words:
                            if word in domains:
                                word = words[words.index(word) - 1] + word
                            elif word in otherdomains:
                                if "." in words[words.index(word) - 1]:
                                    word = words[words.index(word) - 2] + words[words.index(word) - 1] + word
                            try:
                                res = await self.session.get(word)
                            except:
                                try:
                                    res = await self.session.get("http://" + word)
                                except:
                                    pass
                            status_code = res.status
                        if status_code == 200:
                            await after.channel.send(after.author.mention + " You can't send links in this channel.", delete_after=10)
                            try:
                                await after.delete()
                            except:
                                pass
            except:
                pass

    @commands.Cog.listener()
    async def on_message(self,message):
        data = await self.bc.rickroll.find(message.guild.id)
        if data:
            if data["enabled"]:
                hl = []
                status_map = {
                    1: '\U0001f504',
                    2: '\U00002705',
                    3: '\U000027a1',
                    4: '\U0000274c',
                    5: '\U000026a0'
                    }
                def build_string(res):
                    return f'{status_map[int(res.status / 100)]} [{(res.url_obj.host + res.url_obj.path).strip("/")}]({res.url_obj}) ({res.status} {res.reason})'
                for word in message.content.replace("<", "").replace(">", "").split():
                    try:
                        r = await self.session.get(word)
                        for res in r.history:
                            hl.append(build_string(res))
                        hl.append(build_string(r))
                        rickroll = r.rickroll
                        if rickroll:
                            await message.reply("Rickroll detected")
                    except:
                        try:
                            r = await self.session.get("http://" + word)
                            for res in r.history:
                                hl.append(build_string(res))
                            hl.append(build_string(r))
                            rickroll = r.rickroll
                            if rickroll:
                                await message.reply("Rickroll detected")
                        except:
                            pass
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
                                res = await self.session.get(word)
                            except:
                                try:
                                    res = await self.session.get("http://" + word)
                                except:
                                    pass
                            status_code = res.status
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