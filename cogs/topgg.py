import dbl
import discord
from discord.ext import commands
import asyncio

class TopGG(commands.Cog): 
    """Handles interactions with the top.gg API"""
    def __init__(self, bc): 
        self.bc = bc 
        self.token = self.bc.dbltoken # set this to your DBL token 
        self.dblpy = dbl.DBLClient(bot=self.bc, token=self.token)

    @commands.command()
    async def botvotes(self,ctx):
        votes = await self.dblpy.get_bot_upvotes()
        await ctx.send("BreadBot has {} votes on top.gg!".format(len(votes)))

    @commands.Cog.listener()
    async def on_dbl_upvote(self, data):
        """An event that is called whenever someone votes for the bot on top.gg."""
        print("Received an upvote:", "\n", data, sep="")

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        """An event that is called whenever someone tests the webhook system for your bot on top.gg."""
        print("Received a test upvote:", "\n", data, sep="")

def setup(bc):
    bc.add_cog(TopGG(bc))