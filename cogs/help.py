import math
import random
import json
import discord
import platform
import asyncio
from discord.ext import commands
import time
import datetime
import sys
from utility import Pag

invite = discord.ui.Button(label='Invite', style=discord.ButtonStyle.link, url="https://discord.com/oauth2/authorize?client_id=760871722718855169&scope=bot&permissions=8")

support = discord.ui.Button(label='Support Server', style=discord.ButtonStyle.link, url="https://discord.gg/zuv2XW6tzb")

dashboard = discord.ui.Button(label='Dashboard', style=discord.ButtonStyle.link, url="https://dashboard.breadbot.me")

class Items(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(invite)
        self.add_item(support)
        self.add_item(dashboard)

class Support(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.cmds_per_page = 5

    def get_command_signature(self, command: commands.Command, ctx: commands.Context):
        aliases = "|".join(command.aliases)
        cmd_invoke = f"[{command.name}|{aliases}]" if command.aliases else command.name

        full_invoke = command.qualified_name.replace(command.name, "")

        signature = f"{ctx.prefix}{full_invoke}{cmd_invoke} {command.signature}"
        return signature

    async def return_filtered_commands(self, walkable, ctx):
        filtered = []

        for c in walkable.walk_commands():
            try:
                if c.hidden:
                    continue

                elif c.parent:
                    continue

                filtered.append(c)
            except commands.CommandError:
                continue

        return self.return_sorted_commands(filtered)

    def return_sorted_commands(self, commandList):
        return sorted(commandList, key=lambda x: x.name)

    async def setup_help_pag(self, ctx, entity=None, title=None):
        data = await self.bc.prefixes.find_by_id(ctx.guild.id)
        if not data or "prefix" not in data:
            prefix = self.bc.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        entity = entity or self.bc
        title = title or self.bc.description

        pages = []

        if isinstance(entity, commands.Command):
            filtered_commands = (
                list(set(entity.all_commands.values()))
                if hasattr(entity, "all_commands")
                else []
            )
            filtered_commands.insert(0, entity)

        else:
            filtered_commands = await self.return_filtered_commands(entity, ctx)

        for i in range(0, len(filtered_commands), self.cmds_per_page):
            next_commands = filtered_commands[i : i + self.cmds_per_page]
            commands_entry = ""

            for cmd in next_commands:
                desc = cmd.short_doc or cmd.description
                signature = self.get_command_signature(cmd, ctx)
                subcommand = "Has subcommands" if hasattr(cmd, "all_commands") else ""
                usage = cmd.usage if cmd.usage is not None else cmd.signature

                commands_entry += (
                    f"• **__{cmd.name}__**\n```\n{signature}\n```\n{desc}\n"
                    if isinstance(entity, commands.Command)
                    else f"• **__{cmd.name}__ | {desc}**\n`{prefix}{cmd.name} {usage}`\n"
                )
            pages.append(commands_entry)

        await Pag(title=title, color=random.choice(self.bc.color_list), entries=pages, length=1).start(ctx)

    @commands.command()
    @commands.has_any_role(897145238806749184, 897145301893283920)
    async def redeem(self,ctx,pack):
        data = await self.bc.packs.find(ctx.author.id)
        if not data:
            data = {
                "_id": ctx.author.id,
                "1ServerRedeemed": False,
                "2ServersRedeemed": False,
                "Supporter": False,
                "RemainingServers": 0,
                "GuildsPaid": []
            }
        if pack.lower() == "supporter":
            role = discord.utils.get(ctx.guild.roles, id=897145301893283920)
            if role in ctx.author.roles:
                data["RemainingServers"] = 0
                data["1ServerRedeemed"] = False
                data["2ServersRedeemed"] = False
                data["Supporter"] = True
                for guild in data["GuildsPaid"]:
                    self.bc.premium.delete(guild)
                data["GuildsPaid"] = []
                await ctx.send("You have been granted the perks stated under the supporter tier on patron!")
        if pack.lower() == "basic":
            role = discord.utils.get(ctx.guild.roles, id=897145301893283920)
            if role in ctx.author.roles:
                data["RemainingServers"] = 1
                data["1ServerRedeemed"] = True
                data["2ServersRedeemed"] = False
                for guild in data["GuildsPaid"]:
                    self.bc.premium.delete(guild)
                data["GuildsPaid"] = []
                await ctx.send("I have granted you 1 server to give premium!\n\nIf you have downgraded from value pack you must give a server premium again.")
        if pack.lower() == "value":
            role = discord.utils.get(ctx.guild.roles, id=897145238806749184)
            if role in ctx.author.roles:
                data["RemainingServers"] = 2
                data["1ServerRedeemed"] = False
                data["2ServersRedeemed"] = True
                for guild in data["GuildsPaid"]:
                    self.bc.premium.delete(guild)
                data["GuildsPaid"] = []
                await ctx.send("I have granted you 2 servers to give premium!\n\nIf you have upgraded from basic pack you must give a server premium again.")
        await self.bc.packs.upsert(data)

    @commands.command(
        name="help", aliases=["h", "commands"], description="The help command!"
    )
    async def help_command(self, ctx, *, entity=None):
        data = await self.bc.prefixes.get_by_id(ctx.guild.id)
        if not data or "prefix" not in data:
            prefix = self.bc.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        if not entity:
            em = discord.Embed(
                title="Commands",
                description="",
                color=random.choice(self.bc.color_list),
                timestamp=datetime.datetime.utcnow()
            )
            if ctx.guild.icon:
                em.set_thumbnail(url=ctx.guild.icon)
            em.add_field(name="Config | Page 1", value=f"`{prefix}help 1`")
            em.add_field(name="Economy | Page 2", value=f"`{prefix}help 2`")
            em.add_field(name="Fun | Page 3", value=f"`{prefix}help 3`")
            em.add_field(name="Moderation | Page 4", value=f"`{prefix}help 4`")
            em.add_field(name="Utility | Page 5", value=f"`{prefix}help 5`")
            em.add_field(name="Checking | Page 6", value=f"`{prefix}help 6`")
            em.add_field(name="Images | Page 7", value=f"`{prefix}help 7`")
            em.add_field(name="Music (SHUT DOWN) | Page 8", value=f"`{prefix}help 8`")
            em.add_field(name="Server Events | Page 9", value=f"`{prefix}help 9`")    
            em.add_field(name="How to get help for a command", value=f"`{prefix}help <command>`")
            em.set_footer(text=f"Want more help? try out my {prefix}info command", icon_url=ctx.author.avatar if ctx.author.avatar else ctx.author.default_avatar)
            await ctx.send(embed=em, view=Items())
        elif entity == "1":
            cog = self.bc.get_cog("Config")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "2":
            cog = self.bc.get_cog("Economy")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "3":
            cog = self.bc.get_cog("Fun")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "4":
            cog = self.bc.get_cog("Moderation")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "5":
            cog = self.bc.get_cog("Utility")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "6":
            cog = self.bc.get_cog("Checking")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "7":
            cog = self.bc.get_cog("Images")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "8":
            cog = self.bc.get_cog("Music")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "9":
            cog = self.bc.get_cog("ServerEvents")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        else:
            command = self.bc.get_command(entity)
            if command:
                await self.setup_help_pag(ctx, command, command.name)

            else:
                await ctx.send("Entity not found.")

    @commands.command(description='Shows bot version', usage='version')
    async def stats(self, ctx):
        version = self.bc.version
        dpyVersion = discord.__version__
        pythonVersion = platform.python_version()
        x = 0
        for command in self.bc.commands:
          x += 1
        em = discord.Embed(
          title='Bot Stats',
          color=0x0000ff
        )
        em.add_field(name='Version', value=version)
        em.add_field(name='Discord.py Version', value=dpyVersion)
        em.add_field(name='Python Version', value=pythonVersion)
        em.add_field(name='Guilds im in', value=len(self.bc.guilds))
        em.add_field(name='People in the guilds im in', value=len(set(self.bc.get_all_members())))
        em.add_field(name="All the channels I have access to:", value=len(set(self.bc.get_all_channels())))
        em.add_field(name="Shards",value=self.bc.shards[0].shard_count)
        em.add_field(name='Number of Commands', value=x)
        await ctx.send(embed=em)

    @commands.command(
        description="Check out the links of the bot",
        usage=" ",
        aliases=["about", "botinfo"]
    )
    async def info(self,ctx):
        em = discord.Embed(
            title="About BreadBot",
            color=random.choice(self.bc.color_list)
        )
        em.add_field(name="About",value="I am a bot that provides economy, moderation, configuration, and more!",inline=False)
        em.add_field(name="What do I provide?", value="**- Economy\n- Welcome system\n- Leave system\n- Moderation\n- Suspicious account detector\n- And More!**")
        em.add_field(name="Partners", value="Connect by UnsoughtConch#9225: [Invite Connect](https://bit.ly/discord-connect)")
        em.add_field(name="<a:tick:763428030320214036>| Important links",value="**[Support Server](https://discord.gg/zuv2XW6tzb) | [Invite Me!](https://discord.com/oauth2/authorize?client_id=760871722718855169&scope=bot&permissions=8) | [Vote For Me!](https://top.gg/bot/760871722718855169/vote) | [Very cool discord!](https://discord.gg/fz5EYUfEFp) | [Dashboard](https://dashboard.breadbot.me)**",inline=False)
        em.add_field(name="❓| Informative Links",value="**[breadbot docs](https://docs.breadbot.me) | [Bot Page](https://top.gg/bot/760871722718855169) | [My Own Discord Server](https://discord.gg/awy35MJ5pc) | Contact: BongoPlayzYT#1646**")
        await ctx.send(embed=em)

def setup(bc):
    bc.add_cog(Support(bc))
