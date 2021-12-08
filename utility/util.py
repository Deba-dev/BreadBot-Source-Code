import asyncio

import discord
from discord.ext import commands
import json

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
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        self.page = 0
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page] if not type(self.entries[self.page]) == dict else self.entries[self.page]["content"]
        )
        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)  
    
    @discord.ui.button(label="<", style=discord.ButtonStyle.green)
    async def flipback(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        if self.page == 0:
            return
        self.page -= 1
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page] if not type(self.entries[self.page]) == dict else self.entries[self.page]["content"]
        )
        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)    

    @discord.ui.button(label=">", style=discord.ButtonStyle.green)
    async def flipforward(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        if self.page + 1 == len(self.entries):
            return
        self.page += 1
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page] if not type(self.entries[self.page]) == dict else self.entries[self.page]["content"]
        )
        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
        await interation.message.edit(view=self, embed=embed)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.green)
    async def fliplast(self, button: discord.ui.Button, interation: discord.Interaction):
        if interation.user.id != self.ctx.author.id:
            await interation.response.send_message("You cannot use this!", ephemeral=True)
            return
        self.page = len(self.entries) - 1
        embed = discord.Embed(
            title = self.title,
            color = self.color,
            description = self.entries[self.page] if not type(self.entries[self.page]) == dict else self.entries[self.page]["content"]
        )
        if type(self.entries[self.page]) == dict:
            embed.set_image(url=self.entries[self.page]["image"])
        embed.set_footer(text="Page ({}/{})".format(self.page + 1, len(self.entries)))
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
            description = self.entries[0] if not type(self.entries[0]) == dict else self.entries[0]["content"]
        )
        if type(self.entries[0]) == dict:
            embed.set_image(url=self.entries[0]["image"])
        embed.set_footer(text="Page (1/{})".format(len(self.entries)))
        await ctx.send(embed=embed, view=Paginator(self.entries, self.color, self.title, ctx))

async def docs(command, category, bc, ctx):
        command = bc.get_command(command)
        cog = command.cog
        with open("utility/storage/json/docs.json", "r") as f:
            data = json.load(f)
        data[category] = []
        for command in cog.walk_commands():
            if command.hidden:
                continue
            if hasattr(command, "all_commands"):
                for command in list(set(command.all_commands.values())):
                    aliases = "|".join(command.aliases)
                    if not command.checks:
                        data[category].append({"name": command.qualified_name, "description": command.description, "usage": "={}{} {}".format(command.qualified_name.replace(command.name, ""), f"[{command.name}|{aliases}]" if command.aliases else command.name, command.usage if command.usage else command.signature), "permission": "No permissions required"})
                    else:
                        try:
                            command.checks[0](ctx)
                        except Exception as e:
                            data[category].append({"name": command.qualified_name, "description": command.description, "usage": "={}{} {}".format(command.qualified_name.replace(command.name, ""), f"[{command.name}|{aliases}]" if command.aliases else command.name, command.usage if command.usage else command.signature), "permission": str(e).replace("You are missing ", "").replace(" permission(s) to run this command.", "")})
            else:
                if command.parent:
                    continue
                aliases = "|".join(command.aliases)
                if not command.checks:
                    data[category].append({"name": command.qualified_name, "description": command.description, "usage": "={}{} {}".format(command.qualified_name.replace(command.name, ""), f"[{command.name}|{aliases}]" if command.aliases else command.name, command.usage if command.usage else command.signature), "permission": "No permissions required"})
                else:
                    try:
                        command.checks[0](ctx)
                    except Exception as e:
                        data[category].append({"name": command.qualified_name, "description": command.description, "usage": "={}{} {}".format(command.qualified_name.replace(command.name, ""), f"[{command.name}|{aliases}]" if command.aliases else command.name, command.usage if command.usage else command.signature), "permission": str(e).replace("You are missing ", "").replace(" permission(s) to run this command.", "")})
        with open("utility/storage/json/docs.json", "w") as f:
            json.dump(data, f)

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