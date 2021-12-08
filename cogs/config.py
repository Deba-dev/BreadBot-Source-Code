import discord
from discord.ext import commands, tasks
import json
import re
import random
from random import choice
import time
from traceback import format_exception
import io
from copy import deepcopy
import contextlib
import textwrap
import sys

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

def create_embed(content, count,bc):
    embed = discord.Embed(
        description='[Original Message]({})'.format(content.jump_url),
        color = random.choice(bc.color_list)
    )
    embed.add_field(name="Message:",value=content.content)
    embed.set_author(name=content.author,icon_url=content.author.avatar)
    counter = f"⭐ **{count}**"
    return embed, counter

class Placeholder:
    @property
    def name(self):
        return "arg"

class Hybrid(commands.Converter):
    async def convert(self,ctx,argument):
        try:
            return await commands.RoleConverter().convert(ctx, argument)
        except:
            try:
                return await commands.TextChannelConverter().convert(ctx,argument)
            except:
                raise commands.MissingRequiredArgument(Placeholder())

class Config(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.payment = self.check_if_paid.start()

    def cog_unload(self):
        self.payment.cancel()

    @tasks.loop(seconds=15)
    async def check_if_paid(self):
        guild = await self.bc.fetch_guild(760950684849537124)
        all = await self.bc.packs.get_all()
        _ = [_data["_id"] for _data in await self.bc.premium.get_all()]
        for _guild in _:
            found = False
            for data in all:
                if _guild in data["GuildsPaid"]:
                    found = True
                    break
            if not found:
                await self.bc.premium.delete(_guild)
        for data in all:
            try:
                payer = await guild.fetch_member(data["_id"])
            except:
                await self.bc.packs.delete(data["_id"])
            else:
                payer = await guild.fetch_member(data["_id"])
            role = discord.utils.get(guild.roles, id=897215523861958707)
            if role not in payer.roles:
                for guild in data["GuildsPaid"]:
                    await self.bc.premium.delete(guild)
                await self.bc.packs.delete(data["_id"])
            if data["Supporter"]:
                role = discord.utils.get(guild.roles, name="Supporter Pack")
                if role not in payer.roles:
                    for guild in data["GuildsPaid"]:
                        await self.bc.premium.delete(guild)
                    await self.bc.packs.delete(data["_id"])
            if data["1ServerRedeemed"]:
                role = discord.utils.get(guild.roles, name="1 Premium Pack")
                if role not in payer.roles:
                    for guild in data["GuildsPaid"]:
                        await self.bc.premium.delete(guild)
                    await self.bc.packs.delete(data["_id"])
            if data["2ServersRedeemed"]:
                role = discord.utils.get(guild.roles, name="2 Premium Pack")
                if role not in payer.roles:
                    for guild in data["GuildsPaid"]:
                        await self.bc.premium.delete(guild)
                    await self.bc.packs.delete(data["_id"])

    @commands.command(description="Give a server premium perks (according to what patreon tier you got)")
    async def premium(self,ctx):
        data = await self.bc.packs.find(ctx.author.id)
        premium = await self.bc.premium.find(ctx.guild.id)
        if premium:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="This server is already premium")
            return await ctx.send(embed=em)
        if not data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Bro you aren't even a patreon")
            return await ctx.send(embed=em)
        if data["RemainingServers"] == 0:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You do not have anymore premium tokens to give...")
            return await ctx.send(embed=em)
        data["RemainingServers"] -= 1
        data["GuildsPaid"].append(ctx.guild.id)
        premium = {"_id": ctx.guild.id}
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="This server now has premium privilages")
        await ctx.send(embed=em)
        await self.bc.packs.upsert(data)
        await self.bc.premium.upsert(premium)

    @commands.command(description="Revoke a server's premium privilages if you are paying for them")
    async def unpremium(self,ctx):
        data = await self.bc.packs.find(ctx.author.id)
        premium = await self.bc.premium.find(ctx.guild.id)
        if not premium:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="This server was never premium")
            return await ctx.send(embed=em)
        if not data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Bro you aren't even a patreon")
            return await ctx.send(embed=em)
        if ctx.guild.id not in data["GuildsPaid"]:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You are not paying for this server")
            return await ctx.send(embed=em)
        data["RemainingServers"] += 1
        data["GuildsPaid"].remove(ctx.guild.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have removed this server's premium privilages")
        await ctx.send(embed=em)
        await self.bc.packs.upsert(data)
        await self.bc.premium.delete(ctx.guild.id)

    @commands.group(invoke_without_command=True, aliases=["restrict", "editbot", "eb"])
    async def restrictions(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="restrictions")

    @restrictions.group(invoke_without_command=True, aliases=["bl"], name="blacklist")
    async def eb_bl(self, ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="eb bl")

    @eb_bl.group(invoke_without_command=True, aliases=[], name="add")
    @commands.has_permissions(manage_guild=True)
    async def eb_bl_add(self,ctx,arg:Hybrid):
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if type(arg) == discord.Role:
            if arg.id in data["roles_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role is already blacklisted!")
                return await ctx.send(embed=em)
            if data["roles_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["roles_bl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now ignoring anyone with the {} role".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id in data["channels_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel is already blacklisted!")
                return await ctx.send(embed=em)
            if data["channels_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["channels_bl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now ignoring any command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @eb_bl_add.group(invoke_without_command=True, aliases=["cmd"], name="command")
    @commands.has_permissions(manage_guild=True)
    async def eb_bl_add_cmd(self,ctx,cmd,arg:Hybrid):
        cmd = self.bc.get_command(cmd)
        if not cmd:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Command does not exist!")
            return await ctx.send(embed=em)
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if cmd.qualified_name not in data["commands"]:
            data["commands"][cmd.qualified_name] = {}
            data["commands"][cmd.qualified_name]["roles_bl"] = []
            data["commands"][cmd.qualified_name]["roles_wl"] = []
            data["commands"][cmd.qualified_name]["channels_bl"] = []
            data["commands"][cmd.qualified_name]["channels_wl"] = []
        if type(arg) == discord.Role:
            if arg.id in data["commands"][cmd.qualified_name]["roles_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role is already blacklisted!")
                return await ctx.send(embed=em)
            if data["commands"][cmd.qualified_name]["roles_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["roles_bl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now ignoring anyone with the {} role for this command".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id in data["commands"][cmd.qualified_name]["channels_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel is already blacklisted!")
                return await ctx.send(embed=em)
            if data["commands"][cmd.qualified_name]["channels_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["channels_bl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now ignoring this command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @eb_bl.group(invoke_without_command=True, aliases=[], name="remove")
    @commands.has_permissions(manage_guild=True)
    async def eb_bl_remove(self,ctx,arg:Hybrid):
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if type(arg) == discord.Role:
            if arg.id not in data["roles_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role was never blacklisted!")
                return await ctx.send(embed=em)
            data["roles_bl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer ignoring anyone with the {} role".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id not in data["channels_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel was never blacklisted!")
                return await ctx.send(embed=em)
            data["channels_bl"].remove(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer ignoring any command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @eb_bl_remove.group(invoke_without_command=True, aliases=["cmd"], name="command")
    @commands.has_permissions(manage_guild=True)
    async def eb_bl_remove_cmd(self,ctx,cmd,arg:Hybrid):
        cmd = self.bc.get_command(cmd)
        if not cmd:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Command does not exist!")
            return await ctx.send(embed=em)
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if cmd.qualified_name not in data["commands"]:
            data["commands"][cmd.qualified_name] = {}
            data["commands"][cmd.qualified_name]["roles_bl"] = []
            data["commands"][cmd.qualified_name]["roles_wl"] = []
            data["commands"][cmd.qualified_name]["channels_bl"] = []
            data["commands"][cmd.qualified_name]["channels_wl"] = []
        if type(arg) == discord.Role:
            if arg.id not in data["commands"][cmd.qualified_name]["roles_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role was never blacklisted!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["roles_bl"].remove(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer ignoring anyone with the {} role for this command".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id not in data["commands"][cmd.qualified_name]["channels_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel was never blacklisted!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["channels_bl"].remove(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer ignoring this command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @restrictions.group(invoke_without_command=True, aliases=["wl"], name="whitelist")
    async def eb_wl(self, ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="eb wl")

    @eb_wl.group(invoke_without_command=True, aliases=[], name="add")
    @commands.has_permissions(manage_guild=True)
    async def eb_wl_add(self,ctx,arg:Hybrid):
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if type(arg) == discord.Role:
            if arg.id in data["roles_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role is already whitelisted!")
                return await ctx.send(embed=em)
            if data["roles_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["roles_wl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now taking commands from anyone with the {} role".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id in data["channels_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel is already whitelisted!")
                return await ctx.send(embed=em)
            if data["channels_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["channels_wl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now taking any command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @eb_wl_add.group(invoke_without_command=True, aliases=["cmd"], name="command")
    @commands.has_permissions(manage_guild=True)
    async def eb_wl_add_cmd(self,ctx,cmd,arg:Hybrid):
        cmd = self.bc.get_command(cmd)
        if not cmd:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Command does not exist!")
            return await ctx.send(embed=em)
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if cmd.qualified_name not in data["commands"]:
            data["commands"][cmd.qualified_name] = {}
            data["commands"][cmd.qualified_name]["roles_bl"] = []
            data["commands"][cmd.qualified_name]["roles_wl"] = []
            data["commands"][cmd.qualified_name]["channels_bl"] = []
            data["commands"][cmd.qualified_name]["channels_wl"] = []
        if type(arg) == discord.Role:
            if arg.id in data["commands"][cmd.qualified_name]["roles_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role is already whitelisted!")
                return await ctx.send(embed=em)
            if data["commands"][cmd.qualified_name]["roles_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["roles_wl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now taking commands from anyone with the {} role for this command".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id in data["commands"][cmd.qualified_name]["channels_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel is already whitelisted!")
                return await ctx.send(embed=em)
            if data["commands"][cmd.qualified_name]["channels_bl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You cannot have a whitelist and a blacklist at the same time!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["channels_wl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Now taking this command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @eb_wl.group(invoke_without_command=True, aliases=[], name="remove")
    @commands.has_permissions(manage_guild=True)
    async def eb_wl_remove(self,ctx,arg:Hybrid):
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if type(arg) == discord.Role:
            if arg.id not in data["roles_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role was never whitelisted!")
                return await ctx.send(embed=em)
            data["roles_wl"].append(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer taking commands from anyone with the {} role".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id not in data["channels_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel was never whitelisted!")
                return await ctx.send(embed=em)
            data["channels_wl"].remove(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer taking any command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @eb_wl_remove.group(invoke_without_command=True, aliases=["cmd"], name="command")
    @commands.has_permissions(manage_guild=True)
    async def eb_wl_remove_cmd(self,ctx,cmd,arg:Hybrid):
        cmd = self.bc.get_command(cmd)
        if not cmd:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Command does not exist!")
            return await ctx.send(embed=em)
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "commands": {}, "categories_bl": [], "roles_bl": [], "channels_bl": [], "categories_wl": [], "roles_wl": [], "channels_wl": [], "modonly": False, "modonlyrole": None}
        if cmd.qualified_name not in data["commands"]:
            data["commands"][cmd.qualified_name] = {}
            data["commands"][cmd.qualified_name]["roles_bl"] = []
            data["commands"][cmd.qualified_name]["roles_wl"] = []
            data["commands"][cmd.qualified_name]["channels_bl"] = []
            data["commands"][cmd.qualified_name]["channels_wl"] = []
        if type(arg) == discord.Role:
            if arg.id not in data["commands"][cmd.qualified_name]["roles_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This role was never whitelisted!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["roles_wl"].remove(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer taking commands from anyone with the {} role for this command".format(arg.name))
            await ctx.send(embed=em)
        if type(arg) == discord.TextChannel:
            if arg.id not in data["commands"][cmd.qualified_name]["channels_wl"]:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="This channel was never whitelisted!")
                return await ctx.send(embed=em)
            data["commands"][cmd.qualified_name]["channels_wl"].remove(arg.id)
            await self.bc.botedit.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="No longer taking this command in the {} channel".format(arg.name))
            await ctx.send(embed=em)

    @commands.command(description="Toggle the rickroll detector")
    @commands.has_permissions(manage_guild=True)
    async def ricktoggle(self,ctx):
        data = await self.bc.rickroll.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "enabled": False}
        data["enabled"] = not data["enabled"]
        await self.bc.rickroll.upsert(data)
        ternary = "enabled" if data["enabled"] else "disabled"
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="The rickroll detector is now {}".format(ternary))
        await ctx.send(embed=em)

    @commands.command(description="Makes the bot leave the server")
    @commands.has_permissions(manage_guild=True)
    async def leaveserver(self,ctx):
        await ctx.send("Goodbye people of this server :(_ _")
        await ctx.guild.leave()

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):
        if not after.author.bot:
            data2 = await self.bc.modroles.find(after.guild.id)
            data3 = await self.bc.censor.find(after.guild.id)
            if data3:
                if data2 is not None:
                    for i in data2["roles"]:
                        role = discord.utils.get(after.guild.roles,id=i)
                        if role in after.author.roles:
                            return
                        else:
                            continue
                else:
                    pass
                new_message = after.content
                caught= False
                if data3["toggled"]:
                    for word in data3["words"]:
                        if re.search(r'(?i)(\b' + r'+\W*'.join(word) + f'|{word})',after.content):
                            caught = True
                            try:
                                await after.delete()
                            except:
                                pass
                            new_message = re.sub(r'(?i)(\b' + r'+\W*'.join(word) + f'|{word})',r'\*'*len(word),new_message)
                    if caught:
                        webhooks = await after.channel.webhooks()
                        try:
                            webhook = webhooks[0]
                        except:
                            try:
                                webhook = await after.channel.create_webhook(name='Breadbot filter')
                            except:
                                pass
                        if webhook:
                            await webhook.send(
                                content=new_message,
                                username=after.author.nick or after.author.name,
                                avatar_url=after.author.avatar,
                                allowed_mentions=discord.AllowedMentions.none()
                            )
            else:
                pass

    @commands.Cog.listener()
    async def on_message(self,message):
        if not message.guild:
            return
        if not message.author.bot:
            data2 = await self.bc.modroles.find(message.guild.id)
            data3 = await self.bc.censor.find(message.guild.id)
            if data3:
                if data2 is not None:
                    for i in data2["roles"]:
                        role = discord.utils.get(message.guild.roles,id=i)
                        if role in message.author.roles:
                            return
                        else:
                            continue
                else:
                    pass
                new_message = message.content
                caught= False
                if data3["toggled"]:
                    for word in data3["words"]:
                        if re.search(r'(?i)(\b' + r'+\W*'.join(word) + f'|{word})',message.content):
                            caught = True
                            try:
                                await message.delete()
                            except:
                                pass
                            new_message = re.sub(r'(?i)(\b' + r'+\W*'.join(word) + f'|{word})',r'\*'*len(word),new_message)
                    if caught:
                        webhooks = await message.channel.webhooks()
                        try:
                            webhook = webhooks[0]
                        except:
                            try:
                                webhook = await message.channel.create_webhook(name='Breadbot filter')
                            except:
                                pass
                        if webhook:
                            await webhook.send(
                                content=new_message,
                                username=message.author.nick or message.author.name,
                                avatar_url=message.author.avatar,
                                allowed_mentions=discord.AllowedMentions.none()
                            )
            else:
                pass
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        #"""
        data = await self.bc.starboard.find(payload.guild_id)
        if not data:
            return
        if payload.emoji.name == '⭐':
            channel = data["channel"]
            if not channel:
                return
            message = await self.bc.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if payload.member.id == message.author.id or message.author.bot or channel == payload.channel_id:
                return await message.remove_reaction(payload.emoji, payload.member)
            print(data["messages"])
            star_message = list(filter(lambda message: message["messageid"] == payload.message_id, data["messages"]))
            star_message = star_message[0] if len(star_message) != 0 else None
            star_limit = data["limit"]
            for reaction in message.reactions:
                if reaction.emoji == '⭐':
                    count = reaction.count
                    break
                
            if count < star_limit:
                count == 0
            star_channel = self.bc.get_channel(channel)
            embed, mes = create_embed(message, count,self.bc)
            if not star_message:
                try:
                    star_mes = await star_channel.send(content=mes, embed=embed)
                except discord.errors.HTTPException:
                    embed = discord.Embed(description='[Original Message]({})'.format(message.jump_url), colour=random.choice(self.bc.color_list)).set_author(icon_url=message.author.avatar, name=message.author)
                    embed.set_footer(text='Missing Content, Cannot Load Original Message!', icon_url=self.bc.user.avatar)
                    star_mes = await star_channel.send(embed=embed, content=mes)
                data["messages"].append({"messageid": payload.message_id,"starchannelid": star_mes.id})
            else:
                star_message = await star_channel.fetch_message(star_message['starchannelid'])
                if not star_message:
                    data["messages"].remove({"messageid": payload.message_id,"starchannelid": star_message['starchannelid']})
                try:
                    await star_message.edit(content=mes, embed=embed)
                except discord.errors.HTTPException:
                    embed = discord.Embed(description='[Original Message]({})'.format(message.jump_url), colour=random.choice(self.bc.color_list)).set_author(icon_url=message.author.avatar, name=message.author)
                    embed.set_footer(text='Missing Content, Cannot Load Original Message!', icon_url=self.bc.user.avatar)
                    await star_message.edit(embed=embed, content=mes)
            await self.bc.starboard.upsert(data)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        #"""
        data = await self.bc.starboard.find(payload.guild_id)
        if not data:
            return
        if payload.emoji.name == '⭐':
            channel = data["channel"]
            if not channel:
                return
            message = await self.bc.get_channel(payload.channel_id).fetch_message(payload.message_id)
            #if payload.member.id == message.author.id or message.author.bot or channel == payload.channel_id:
            #    return await message.remove_reaction(payload.emoji, payload.member)
            print(data["messages"])
            star_message = list(filter(lambda message: message["messageid"] == payload.message_id, data["messages"]))
            star_message = star_message[0] if len(star_message) != 0 else star_message[0]
            star_limit = data["limit"]
            for reaction in message.reactions:
                if reaction.emoji == '⭐':
                    count = reaction.count
                    break
                
            if count < star_limit:
                return
            star_channel = self.bc.get_channel(channel)
            embed, mes = create_embed(message, count,self.bc)
            if not star_message:
                return
            else:
                star_message = await star_channel.fetch_message(star_message['starchannelid'])
                if not star_message:
                    data["messages"].remove({"messageid": payload.message_id,"starchannelid": star_message['starchannelid']})
                try:
                    await star_message.edit(content=mes, embed=embed)
                except discord.errors.HTTPException:
                    embed = discord.Embed(description='[Original Message]({})'.format(message.jump_url), colour=random.choice(self.bc.color_list)).set_author(icon_url=message.author.avatar, name=message.author)
                    embed.set_footer(text='Missing Content, Cannot Load Original Message!', icon_url=self.bc.user.avatar)
                    await star_message.edit(embed=embed, content=mes)
            await self.bc.starboard.upsert(data)
        #"""

    @commands.group(invoke_without_command=True)
    async def automod(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="automod")

    @commands.group(invoke_without_command=True)  
    async def chatbot(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="chatbot")
    
    @chatbot.command(
        description="Set the channel for the chatbot to respond to messages!",
        name="channel"
    )
    @commands.has_permissions(manage_channels=True)
    async def chatbot_channel(self,ctx,channel:discord.TextChannel):
        data = await self.bc.chatbot.find(ctx.guild.id)
        if not data:
            data = {"_id":ctx.guild.id, "channel":channel.id, "isenabled": True}
        data["channel"] = channel.id
        await self.bc.chatbot.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have set the chatbot channel to #{0.name}".format(channel))
        await ctx.send(embed=em)

    @chatbot.command(
        description="Enable/Disable the chatbot!",
        name="toggle"
    )
    @commands.has_permissions(manage_channels=True)
    async def chatbot_toggle(self,ctx):
        data = await self.bc.chatbot.find(ctx.guild.id)
        if not data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="This server does not have a chatbot system set up")
            return await ctx.send(embed=em)
        data["isenabled"] = not data["isenabled"]
        ternary = "enabled" if data["isenabled"] else "disabled"
        await self.bc.chatbot.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have set the chatbot to {}".format(ternary))
        await ctx.send(embed=em)
    
    @chatbot.command(
        description="Delete your settings for your chatbot!",
        name="delete"
    )
    @commands.has_permissions(manage_channels=True)
    async def chatbot_delete(self,ctx):
        data = await self.bc.chatbot.find(ctx.guild.id)
        if not data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="This server does not have a chatbot system set!")
            return await ctx.send(embed=em)
        await self.bc.chatbot.delete(ctx.guild.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have deleted the settings for the chatbot")
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def lvlsettings(self,ctx):
        data = await self.bc.ranks.find(ctx.guild.id)
        prefixes = await self.bc.prefixes.find(ctx.guild.id)
        if prefixes is None or "prefix" not in prefixes:
            prefix = "="
        else:
            prefix = prefixes["prefix"]
        channel = ctx.guild.get_channel(data["channel"]) if data['channel'] is not None else "Not Set"
        em = discord.Embed(
            title = "Level Settings"
        )
        em.add_field(name="Multiplier",value=f"x{data['multi']}")
        em.add_field(name="Level Up Message",value=data["message"])
        em.add_field(name="Level Up Channel",value=channel.mention if channel != "Not Set" else "Not Set")
        em.add_field(name="Blacklisted Channels",value=f"do `{prefix}lvlsettings blchannels show` to see")
        em.add_field(name="Rewards",value=f"go `{prefix}lvlsettings rewards show` to see")
        await ctx.send(embed=em)
    
    @lvlsettings.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def blchannels(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="lvlsettings blchannels")
    
    @blchannels.command(name="show", description="Shows the list of channels you can't earn xp in")
    async def blchannels_show(self,ctx):
        data = await self.bc.ranks.find(ctx.guild.id)
        channels = [ctx.guild.get_channel(channel) for channel in data['blacklisted']]
        if not channels:
            channels = ["No Channels"]
        em = discord.Embed(
            title="Blacklisted Channels",
            description="\n".join([channel.mention for channel in channels if channel]) if channels[0] != "No Channels" else "No Channels"
        )
        await ctx.send(embed=em)
    
    @blchannels.command(name="add", description="Add a channel that does not give xp for messaging in that channel")
    @commands.has_permissions(manage_guild=True)
    async def blchannels_add(self,ctx,channel:discord.TextChannel):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            return
        data["blacklisted"].append(channel.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Added #{} to the blacklisted channels.".format(channel.name))
        await ctx.send(embed=em)
        await self.bc.ranks.upsert(data)
        
    @blchannels.command(name="remove", description="Removes a channel from the blacklist")
    @commands.has_permissions(manage_guild=True)
    async def blchannels_remove(self,ctx,channel:discord.TextChannel):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            return
        try:
            data["blacklisted"].remove(channel.id)
        except:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="That chanel isnt blaclisted!")
            return await ctx.send(embed=em)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Removed #{} from the blacklisted channels.".format(channel.name))
        await ctx.send(embed=em)
        await self.bc.ranks.upsert(data)
        
    @lvlsettings.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def rewards(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="lvlsettings rewards")
    
    @rewards.command(name="show", description="Shows what roles you can get for leveling up")
    async def rewards_show(self,ctx):
        data = await self.bc.ranks.find(ctx.guild.id)
        rewards = deepcopy(data["rewards"])
        roles = [[ctx.guild.get_role(value), key] for key, value in rewards.items()]
        if not rewards:
            roles = ["No Roles"]
        em = discord.Embed(
            title="Reward Roles",
            description="\n".join([f"Level {roles[1]}: {roles[0].mention}" for roles in roles if roles]) if roles[0] != "No Roles" else "No Roles"
        )
        await ctx.send(embed=em)
    
    @rewards.command(name="add", description="Add a leveling reward for a role")
    @commands.has_permissions(manage_guild=True)
    async def rewards_add(self,ctx,level,*,role:discord.Role):
        try:
            data = await self.bc.ranks.find(ctx.guild.id)
            if data is None:
                return
            try:
                test = int(level)
            except:
                em = discord.Embed(color=discord.Color.red())
                em.set_author(name="You must pass an integer as the level!")
                return await ctx.send(embed=em)
            data["rewards"][str(level)] = role.id
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Added `{}` to the rewards.".format(role.name))
            await ctx.send(embed=em)
            await self.bc.ranks.upsert(data)
        except Exception as e:
            print(e)
        
    @rewards.command(name="remove", description="Remove the reward of getting a role for the level given")
    @commands.has_permissions(manage_guild=True)
    async def rewards_remove(self,ctx,level):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            return
        try:
            test = int(level)
        except:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="The level must be an integer")
            return await ctx.send(embed=em)
        data["rewards"].pop(str(level))
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Removed all role rewards for that level to the rewards.")
        await ctx.send(embed=em)
        await self.bc.ranks.upsert(data)

    @lvlsettings.command(name="multi",description="Increase your xp multiplier")
    @commands.has_permissions(manage_guild=True)
    async def xp_multi(self,ctx,multi):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="This server does not have a system set!")
            return await ctx.send(embed=em)
        data["multi"] = int(multi)
        await self.bc.ranks.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have updated the multiplier!")
        await ctx.send(embed=em)

    @lvlsettings.command(name="channel",description="Change the announcements channel for when someone levels up.")
    @commands.has_permissions(manage_guild=True)
    async def lvl_channel(self,ctx,channel:discord.TextChannel=None):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="This server does not have a system set!")
            return await ctx.send(embed=em)
        if channel:
            data["channel"] = channel.id
        else:
            data["channel"] = channel
        await self.bc.ranks.upsert(data)
        if channel:
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="I have set the announce channel to {}".format(channel.name))
            return await ctx.send(embed=em)
        else:
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="I have unset the channel")
            return await ctx.send(embed=em)
    
    @lvlsettings.command(name="message", description="Change the level up message")
    @commands.has_permissions(manage_guild=True)
    async def lvl_message(self,ctx,*,message:str=None):
        data = await self.bc.ranks.find(ctx.guild.id)
        if message is None:
            return await ctx.send("""
**Arguments for level up message**

{member} - member who leveled up
{level} - the level they are now at
{pastlevel} - the level that they used to be at
{rank} - the place on the leaderboard they are on
        """)
        if data is None:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="Something went wrong! Try again later")
            return await ctx.send(embed=em)
        data["message"] = message
        await self.bc.ranks.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have updated the level up message")
        await ctx.send(embed=em)


    @commands.group(
        aliases=["sb"], invoke_without_command=True
    )
    async def starboard(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="starboard")

    @starboard.command(
        name="channel",
        description="set a channel for your starboard",
        usage="<channel>"
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_channel(self,ctx,channel:discord.TextChannel):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not data or "channel" not in data:
            data = {"_id": ctx.guild.id, "channel": None, "limit": 5, "toggled": True, "messages": []}
        data["channel"] = channel.id
        await self.bc.starboard.upsert(data)
        em = discord.Embed(color=discord.Color.red())
        em.set_author(name="Successfully set the starboard channel to {}".format(channel.name))
        await ctx.send(embed=em)

    @starboard.command(
        name="delchannel",
        description="delete a channel set for your starboard",
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_delchannel(self,ctx):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not data or "channel" not in data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You do not have a channel set!")
            return await ctx.send(embed=em)
        await self.bc.starboard.delete(ctx.guild.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have deleted the channel set for the starboard")
        return await ctx.send(embed=em)
    
    @starboard.command(
        name="toggle",
        description="Toggle the starboard channel on or off",
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_toggle(self,ctx):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not data or "channel" not in data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You don't have a channel set up")
            return await ctx.send(embed=em)
        data["toggled"] = not data["toggled"]
        ternary = "enabled" if data["toggled"] else "disabled"
        await self.bc.starboard.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have set the starboard to {}".format(ternary))
        return await ctx.send(embed=em)

    @starboard.command(
        name="limit",
        description="Change how many stars a message needs to appear on the starboard"
    )
    @commands.has_permissions(manage_guild=True)
    async def starboard_limit(self,ctx,limit:int=None):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not limit and data:
            return await ctx.send("The starboard limit is {}".format(data["limit"]))
        elif not data or "channel" not in data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You need to set up a starboard channel first")
            return await ctx.send(embed=em)
        elif not limit:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You need to specify a limit!")
            return await ctx.send(embed=em)
        data["limit"] = limit
        await self.bc.starboard.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have set the starboard limit to {}".format(limit))
        return await ctx.send(embed=em)

    @automod.group(
        aliases=['censor'], usage="", invoke_without_command=True
    )
    @commands.guild_only()
    async def profanity(self, ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="automod profanity")

    @profanity.command(name="add", description="Add a word that members cannot send")
    @commands.has_permissions(manage_guild=True)
    async def censor_add(self,ctx,word:str):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            data = {"_id": ctx.guild.id, "words": [], "toggled": True}
        data["words"].append(word)
        await self.bc.censor.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="{} has been added to the censor filter".format(word))
        return await ctx.send(embed=em,delete_after=5)
        await ctx.message.delete()

    @profanity.command(name="remove", description="Remove a word from the censor list")
    @commands.has_permissions(manage_guild=True)
    async def censor_remove(self,ctx,word:str):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You do not have a filter set up!")
            return await ctx.send(embed=em)
        if word not in data["words"]:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="That word isn't in the filter!")
            return await ctx.send(embed=em)
        data["words"].remove(word)
        await self.bc.censor.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Removed {} from the filter".format(word))
        return await ctx.send(embed=em)

    @profanity.command(name="toggle", description="Toggle the censor system off/on")
    @commands.has_permissions(manage_guild=True)
    async def censor_toggle(self,ctx):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            data = {"_id": ctx.guild.id, "words": [], "toggled": True}
        data["toggled"] = not data["toggled"]
        ternary = "enabled" if data["toggled"] else "disabled"
        await self.bc.censor.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Censor filter is now {}".format(ternary))
        return await ctx.send(embed=em)

    @profanity.command(name="list", description="List the words that are banned")
    @commands.has_permissions(manage_guild=True)
    async def censor_list(self,ctx):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You have no filter set up")
            return await ctx.send(embed=em)
        em = discord.Embed(
            title="Censor List",
            description="\n".join([word for word in data["words"]]),
            color=random.choice(self.bc.color_list)
        )
        await ctx.send(embed=em)


    @commands.command(description='change the prefix for your guild. (leave blank for default prefix)', usage='[prefix]')
    @commands.has_permissions(manage_guild=True)
    async def prefix(self,ctx, *, prefix=None):
        if prefix == None:
            prefix = self.bc.DEFAULTPREFIX
        await self.bc.prefixes.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix has been set to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )
    
    @commands.group(description='change the channel for your suggestion channel.', usage='<channel>', invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def suggestions(self,ctx):
        await ctx.invoke(self.bc.get_command('help'), entity="suggestions")

    @suggestions.command(name="channel",description='change the channel for your suggestion channel.', usage='<channel>', invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def suggestions_channel(self,ctx, channel:discord.TextChannel):
        await self.bc.suggestions.upsert({"_id": ctx.guild.id, "numbers": 0,"channel":channel.id,"suggestions":[]})
        await ctx.send(
            f"Suggestions channel is {channel.mention}"
        )

    @suggestions.command(name="reset",description='change the channel for your suggestion channel.')
    @commands.has_permissions(manage_channels=True)
    async def suggestions_reset(self,ctx):
        await self.bc.suggestions.delete(ctx.guild.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="I have reset the suggestion configurations")
        return await ctx.send(embed=em)

    @commands.command(
        name="deleteprefix", aliases=["dp"], description="Delete your guilds prefix!", usage=" "
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def deleteprefix(self, ctx):
        await self.bc.prefixes.unset({"_id": ctx.guild.id, "prefix": 1})
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Server prefix has been reset")
        return await ctx.send(embed=em)
    
    @commands.command(
        description="Change what channel you want the bot to post server actions in (leave blank to delete)",
        usage="<channel>"
    )
    @commands.has_permissions(manage_channels=True)
    async def modlogs(self,ctx,channel:discord.TextChannel):
        data = await self.bc.modlogs.find(ctx.guild.id)
        if not channel and data is not None:
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Deleted modlogs channel")
            await ctx.send(embed=em)
            await self.bc.modlogs.delete(ctx.guild.id)
            return
        if not data or "channel" not in data:
            data = {"_id": ctx.guild.id, "channel": channel.id}
        else:
            data["channel"] = channel.id
        await self.bc.modlogs.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Modlogs channel is {}".format(channel.name))
        return await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def welcome(self,ctx):
        await ctx.invoke(self.bc.get_command("help"),entity="welcome")
    
    @welcome.command(name="ping", description="Set a role to ping when a user joins (leave blank to disable)")
    @commands.has_permissions(manage_guild=True)
    async def ping(self,ctx, *, role:discord.Role=None):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="There is no welcoming system")
            return await ctx.send(embed=em)
        if not role:
            data["ping"] = None
        else:
            data["ping"] = role.id
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Ping role is now {}".format(role.name))
        await ctx.send(embed=em)
        await self.bc.welcomes.upsert(data)

    @welcome.command(name="message", description="Set a custom message that the bot will send when a user joins!")
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self,ctx, *, message=None):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You need to set up a welcome system before setting a welcome message")
            return await ctx.send(embed=em)
        if not message:
            return await ctx.send("**Arguments**\nYou can use these arguments and the bot will replace it with the corresponding things.\n\n{member} - Mention of the member\n{server} - Name of the server\n{place} - The place of the member joining\n{ending} - The ending of a number such as st, nd, rd, th")
        data["message"] = message
        await self.bc.welcomes.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Welcome message set successfully")
        return await ctx.send(embed=em)

    @welcome.command(name="channel",description='Set a welcome channel', usage='<channel>')
    @commands.has_permissions(manage_channels=True)
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data or "channel" not in data:
            data = {"_id": ctx.guild.id, "channel":channel.id,"role":None, "auth": False, "ping": None, "message": "Welcome {member} to **{server}**. You are our `{place}{ending}` member!"}
        data["channel"] = channel.id
        await self.bc.welcomes.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Welcome channel is now {}".format(channel.name))
        return await ctx.send(embed=em)
    
    @welcome.command(
        description="Set up a welcome role",
        name="role",
        usage="<role>"
    )
    @commands.has_permissions(manage_roles=True)
    async def wel_role(self,ctx,*,role:discord.Role):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "channel":None ,"role":None, "auth": False, "ping": None, "message": "Welcome {member} to **{server}**. You are our `{place}{ending}` member!"}
        data["role"] = role.id
        await self.bc.welcomes.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Welcome role is now {}".format(role.name))
        return await ctx.send(embed=em)

    @welcome.command(
        description="Adds a captcha for sus people upon joining",
        name="auth"
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_auth(self,ctx):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data or "role" not in data:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You need a welcome role for this to work")
            return await ctx.send(embed=em)
        data["auth"] = not data["auth"]
        ternary = "enabled" if data["auth"] else "disabled"
        await self.bc.welcomes.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Welcome auth is now {}".format(ternary))
        return await ctx.send(embed=em)
        
    @welcome.command(description="Delete your welcome settings", name="delete")
    @commands.has_permissions(manage_guild=True)
    async def welcome_delete(self,ctx):
        await self.bc.welcomes.delete(ctx.guild.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Welcome configurations deleted")
        return await ctx.send(embed=em)

    @commands.command(description='syncs your muterole with your channels(sets muteroles in all channels to no send messages)', usage=' ')
    @commands.has_permissions(manage_roles=True)
    async def sync(self, ctx):
        with open('utility/storage/json/muteroles.json', 'r') as f:
            channel = json.load(f)
        if channel[str(ctx.guild.id)] == 'Not Set':
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="You do not have a muterole set up")
            return await ctx.send(embed=em)
        else:
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
            for muterole in ctx.guild.text_channels:
                try:
                    await muterole.set_permissions(role, send_messages=False,add_reactions=False, send_messages_in_threads=False, create_public_threads=False, create_private_threads=False)
                except:
                    print("yes")
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
            for muterole in ctx.guild.voice_channels:
                try:
                    await muterole.set_permissions(role, speak=False)
                except:
                    print("yes")
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Muterole has been synced with all channels")
        return await ctx.send(embed=em)

    @commands.command(description='Set a muterole', usage='<role>')
    @commands.has_permissions(manage_channels=True)
    async def muterole(self, ctx, role: discord.Role):
        if role == None:
            em = discord.Embed(color=discord.Color.red())
            em.set_author(name="A valid role has not been given!")
            return await ctx.send(embed=em)
        else:
            with open('utility/storage/json/muteroles.json', 'r') as f:
                welcome_id = json.load(f)
            welcome_id[str(ctx.guild.id)] = f'{role.id}'
            with open('utility/storage/json/muteroles.json', 'w') as f:
                json.dump(welcome_id, f, indent=4)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Muterole has been set as {}".format(role.name))
            return await ctx.send(embed=em)

    @commands.command(description='Set a leave channel', usage='<channel>')
    @commands.has_permissions(manage_channels=True)
    async def leaves(self, ctx, channel: discord.TextChannel):
        data = await self.bc.leaves.find(ctx.guild.id)
        if data is None:
            data = {"_id": ctx.guild.id, "channel": None}
        data["channel"] = channel.id
        await self.bc.leaves.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Leaves channel has been set to {}".format(channel.name))
        return await ctx.send(embed=em)

    @commands.command(description='use this to set modroles for your server that ignore certain automod rules',usage='<add or remove> <role>')
    @commands.has_permissions(manage_roles=True)
    async def modrole(self,ctx,thingy,role:discord.Role):
        if thingy == "add" or thingy == "set":
            data = await self.bc.modroles.find(ctx.guild.id)
            if data is None or "roles" not in data:
                data = {"_id": ctx.guild.id, "roles": []}
            if role.id in data["roles"]:
                return await ctx.send("This role is already a modrole!")
            data["roles"].append(role.id)
            await self.bc.modroles.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Modrole {} added".format(role.name))
            return await ctx.send(embed=em)
        if thingy == "remove" or thingy == "take":
            data = await self.bc.modroles.find(ctx.guild.id)
            if role.id not in data["roles"]:
                return await ctx.send("This role was never a modrole!")
            data["roles"].remove(role.id)
            await self.bc.modroles.upsert(data)
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Modrole {} removed".format(role.name))
            return await ctx.send(embed=em)

    @automod.group(description='use this to add/remove a links only channel for your server',invoke_without_command=True)
    async def linksonly(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="automod linksonly")
            
    @linksonly.command(name="add", description="Add a channel where members can send links")
    @commands.has_permissions(manage_channels=True)
    async def linkslonyadd(self,ctx,channel:discord.TextChannel):
        data = await self.bc.linksonly.find(ctx.guild.id)
        if data is None or "channels" not in data:
            data = {"_id": ctx.guild.id, "channels": []}
        data["channels"].append(channel.id)
        await self.bc.linksonly.upsert(data)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Channel has now been whitelisted")
        return await ctx.send(embed=em)

    @linksonly.command(name="remove", description="Make a channel not able to contain links")
    @commands.has_permissions(manage_channels=True)
    async def linkslonyremove(self,ctx,channel:discord.TextChannel):
        data = await self.bc.linksonly.find(ctx.guild.id)
        data["channels"].remove(channel.id)
        await self.bc.linksonly.upsert(data)
        if len(data["channels"]) == 0:
            await self.bc.linksonly.delete(ctx.guild.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Channel has been removed from whitelist")
        return await ctx.send(embed=em)

def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file)

def setup(bc):
    bc.add_cog(Config(bc))
    