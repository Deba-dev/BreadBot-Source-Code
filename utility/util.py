import asyncio

import discord
from discord.ext import commands

class Paginator(discord.ui.View):
    def __init__(self, entries, color, title, ctx):
        self.page = 0
        self.entries = entries
        self.color = color
        self.title = title
        self.ctx = ctx
        super().__init__()

    @discord.ui.button(label="<<", style=discord.ButtonStyle.green)
    async def flipfront(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot flip through this person's help command!", ephemeral=True)
            return
        self.page = 0
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page]
        )
        await interation.message.edit(view=self, embed=embed)  
    
    @discord.ui.button(label="<", style=discord.ButtonStyle.green)
    async def flipback(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot flip through this person's help command!", ephemeral=True)
            return
        if self.page == 0:
            return
        self.page -= 1
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page]
        )
        await interation.message.edit(view=self, embed=embed)    

    @discord.ui.button(label=">", style=discord.ButtonStyle.green)
    async def flipforward(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot flip through this person's help command!", ephemeral=True)
            return
        if self.page + 1 == len(self.entries):
            return
        self.page += 1
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page]
        )
        await interation.message.edit(view=self, embed=embed)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.green)
    async def fliplast(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot flip through this person's help command!", ephemeral=True)
            return
        self.page = len(self.entries) - 1
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page]
        )
        await interation.message.edit(view=self, embed=embed)  

class Pag:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.color = kwargs.get("color")
        self.entries = kwargs.get("entries")
    
    async def start(self, ctx: commands.Context):
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[0]
        )
        await ctx.send(embed=embed, view=Paginator(self.entries, self.color, self.title, ctx))

async def GetMessage(
    bc, ctx, contentOne="Default Message", contentTwo="\uFEFF", timeout=100
):
    """
    This function sends an embed containing the params and then waits for a message to return
    Params:
     - bot (commands.Bot object) :
     - ctx (context object) : Used for sending msgs n stuff
     - Optional Params:
        - contentOne (string) : Embed title
        - contentTwo (string) : Embed description
        - timeout (int) : Timeout for wait_for
    Returns:
     - msg.content (string) : If a message is detected, the content will be returned
    or
     - False (bool) : If a timeout occurs
    """
    embed = discord.Embed(title=f"{contentOne}", description=f"{contentTwo}",)
    sent = await ctx.send(embed=embed)
    try:
        msg = await bc.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if msg:
            return msg.content
    except asyncio.TimeoutError:
        return False