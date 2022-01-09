import discord
from discord.ext import commands
import os
import aiohttp

class ChatBot(commands.Cog):
    def __init__(self,bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_message(self,msg):
        if not msg.guild:
            return
        if msg.author.bot:
            return
        data = await self.bc.chatbot.find(msg.guild.id)
        if data is None:
            return
        if not data["isenabled"]:
            return
        if msg.channel.id == data["channel"]:
            async with aiohttp.ClientSession(headers={"x-api-key": os.environ.get("prsawapi")}) as session:
                async with session.get("https://api.pgamerx.com/v4/ai", params={'type':"stable" , 'message':msg.content, "lang": "en", "uid": str(msg.author.id)}) as res:
                    text = await res.json()
                    await msg.reply(text)

            

def setup(bc):
    bc.add_cog(ChatBot(bc))