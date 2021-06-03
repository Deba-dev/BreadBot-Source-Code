import discord
from discord.ext import commands
import os
import asyncio
import sys

class Startup(commands.Cog):
    def __init__(self,bc):
        self.bc = bc
    
    @commands.Cog.listener()
    async def on_ready(self):
            await self.bc.change_presence(activity=discord.Game(name=f"in {len(self.bc.guilds)} guilds | {self.bc.DEFAULTPREFIX}help"))
        

def setup(bc):
    bc.add_cog(Startup(bc))