import discord
from discord.ext import commands
from prsaw import RandomStuff
import os
rs = RandomStuff(api_key = os.environ.get("prsawapi"))

class ChatBot(commands.Cog):
    def __init__(self,bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_message(self,msg):
        if msg.author.bot:
            return
        data = await self.bc.chatbot.find(msg.guild.id)
        if data is None:
            return
        if not data["isenabled"]:
            return
        if msg.channel.id == data["channel"]:
            response =  rs.get_ai_response(msg.content)
            await msg.reply(response)
            

def setup(bc):
    bc.add_cog(ChatBot(bc))