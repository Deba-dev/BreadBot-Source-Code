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
        while True:
            await self.bc.change_presence(activity=discord.Game(name=f"in {len(self.bc.guilds)} guilds | {self.bc.DEFAULTPREFIX}help"))
            await asyncio.sleep(5)
            await self.bc.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{self.bc.shards[0].shard_count} shards | {self.bc.DEFAULTPREFIX}help"))
            await asyncio.sleep(5)
            await self.bc.change_presence(activity=discord.Game(name=f"with server admins | {self.bc.DEFAULTPREFIX}help"))
            await asyncio.sleep(5)
        

def setup(bc):
    bc.add_cog(Startup(bc))