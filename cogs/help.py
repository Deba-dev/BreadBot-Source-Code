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
from tools.util import Pag

def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file, indent=4)


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
                usage = cmd.usage if cmd.usage is not None else ""

                commands_entry += (
                    f"• **__{cmd.name}__**\n```\n{signature}\n```\n{desc}\n"
                    if isinstance(entity, commands.Command)
                    else f"• **__{cmd.name}__ | {desc}**\n`{prefix}{cmd.name} {usage}`\n"
                )
            pages.append(commands_entry)

        await Pag(title=title, color=random.choice(self.bc.color_list), entries=pages, length=1).start(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} cog has been loaded\n-----")

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
                color=random.choice(self.bc.color_list),
                timestamp=datetime.datetime.utcnow()
            )
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.add_field(name="Config | Page 1", value=f"`{prefix}help 1`")
            em.add_field(name="Economy | Page 2", value=f"`{prefix}help 2`")
            em.add_field(name="Fun | Page 3", value=f"`{prefix}help 3`")
            em.add_field(name="Moderation | Page 4", value=f"`{prefix}help 4`")
            em.add_field(name="Utility | Page 5", value=f"`{prefix}help 5`")
            em.add_field(name="Checking | Page 6", value=f"`{prefix}help 6`")
            em.add_field(name="Images | Page 7", value=f"`{prefix}help 7`")
            em.add_field(name="Reaction Roles | Page 8", value=f"`{prefix}help 8`")
            em.add_field(name="Music (beta) | Page 9", value=f"`{prefix}help 9`")
            em.add_field(name="Server Events | Page 10", value=f"`{prefix}help 10`")    
            em.add_field(name="How to get help for a command", value=f"`{prefix}help <command>`")
            em.set_footer(text=f"Want more help? try out my {prefix}info command", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
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
            cog = self.bc.get_cog("ReactionRoles")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "9":
            cog = self.bc.get_cog("Music")
            await self.setup_help_pag(ctx, cog, f"Page {entity} | {cog.qualified_name}")
        elif entity == "10":
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
        em.add_field(name="Shards",value=self.bc.shards[0].shard_count)
        em.add_field(name='Number of Commands', value=x)
        await ctx.send(embed=em)

    @commands.command(
        description="Check out the links of the bot",
        usage=" ",
        aliases=["about"]
    )
    async def info(self,ctx):
        em = discord.Embed(
            title="About BreadBot",
            color=random.choice(self.bc.color_list)
        )
        em.add_field(name="About",value="I am a bot that provides economy, moderation, configuration, and more!",inline=False)
        em.add_field(name="What do I provide?", value="**- Economy\n- Welcome system\n- Leave system\n- Moderation\n- Suspicious account detector\n- And More!**")
        em.add_field(name="<a:tick:763428030320214036>| Important links",value=f"**[Support Server](https://discord.gg/zuv2XW6tzb) | [Invite Me!](https://discord.com/oauth2/authorize?client_id=760871722718855169&scope=bot&permissions=2146958839) | [Vote For Me!](https://top.gg/bot/760871722718855169/vote) | [Very cool discord!](https://discord.gg/fz5EYUfEFp)**",inline=False)
        em.add_field(name="❓| Informative Links",value="**[discord.py docs](https://discordpy.readthedocs.io/en/latest/) | [Bot Page](https://top.gg/bot/760871722718855169) | [My Own Discord Server](https://bit.ly/BongoDiscord) | Contact: dank BongoPlayzYT#1508**")
        em.add_field(name="Easy Way to contact me", value="Just dm me (the bot) if you have an issue, suggestion, or someone u want to report abusing the bot.", inline=False)
        await ctx.send(embed=em)

def setup(bc):
    bc.add_cog(Support(bc))
