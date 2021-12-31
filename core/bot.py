"""
   Copyright [2021] [BungoChungo]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""
import discord
import random
import os
import json
import time
from random import choice
from discord.ext import commands, tasks
import motor.motor_asyncio
import datetime
import utility
import asyncio
import discordmongo
import googletrans
import sys
from .base import BaseBot

async def get_prefix(bc, message):
    if not message.guild:
        return commands.when_mentioned_or(bc.DEFAULTPREFIX)(bc, message)

    try:
        data = await bc.prefixes.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bc.DEFAULTPREFIX)(bc, message)
        return commands.when_mentioned_or(data["prefix"])(bc, message)
    except:
        return commands.when_mentioned_or(bc.DEFAULTPREFIX)(bc, message)

class BreadBot(BaseBot):
    def __init__(self):

        # Important things
        owner=485513915548041239
        DEFAULTPREFIX = "="
        intents=discord.Intents.all()
        self.owner = owner
        self.DEFAULTPREFIX = DEFAULTPREFIX
        self.premiums = []

        # Initialize the bot
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True, 
            owner_id=owner,
            intents=intents,
            
            allowed_mentions=discord.AllowedMentions(everyone=False))

        # Task data
        self.muted_users = {}
        self.heistdata = {}
        self.GAWdata = {}
        self.remindData = {}

        # Get version from changelogs
        with open("utility/storage/changelogs.txt", "r") as f:
            lines = f.readlines()
        self.version = lines[1].replace("**Version:** ", "")

        # Random shit
        self.remove_command("help")
        self.dbltoken = os.environ.get("DBLTOKEN")
        self.gettingmemes = True
        self.rewind = asyncio.Event(loop=self.loop)
        self.rewind.set()

        # Load cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith("_"):
                self.load_extension(f'cogs.{filename[:-3]}')
                print(filename[:-3].capitalize() + " Cog has been loaded\n" + "-"*len(filename[:-3] + " Cog has been loaded") + "\n")
        self.load_extension("slashtest.test")
        self.load_extension("slash.fun")

        @self.before_invoke
        async def before_any_command(ctx):
            if not isinstance(ctx.command, commands.Command):
                return
            data = read_json("utility/storage/json/blacklist")
            self.blacklisted_users = data["blacklistedUsers"]
            if ctx.author.id in self.blacklisted_users:
                raise utility.Blacklisted()
            
            data = await self.premium.find(ctx.guild.id)
            if data is None and ctx.command.qualified_name.lower() in utility.commands2.premium:
                raise utility.Premium()

            data = await self.botedit.find(ctx.guild.id)
            if data:
                # Check Role Blacklist
                for role in data["roles_bl"]:
                    role = await commands.RoleConverter().convert(ctx, str(role))
                    if role in ctx.author.roles:
                        raise utility.EditError

                # Check Role Whitelist
                found = False
                for role in data["roles_wl"]:
                    role = await commands.RoleConverter().convert(ctx, role)
                    if role in ctx.author.roles:
                        found = True
                        break
                
                if not found and data["roles_wl"]:
                    raise utility.EditError

                # Check Channel Blacklist
                for channel in data["channels_bl"]:
                    if ctx.channel.id == channel:
                        raise utility.EditError

                # Check Channel Whitelist
                found = False
                for channel in data["channels_wl"]:
                    if channel == ctx.channel.id:
                        found = True
                        break
                
                if not found and data["channels_wl"]:
                    raise utility.EditError
                # Check Command Settings
                if ctx.command.qualified_name in data["commands"]:
                    cmd_data = data["commands"][ctx.command.qualified_name]

                    # Check Role Blacklist
                    for role in cmd_data["roles_bl"]:
                        role = await commands.RoleConverter().convert(ctx, str(role))
                        if role in ctx.author.roles:
                            raise utility.EditError

                    # Check Role Whitelist
                    found = False
                    for role in cmd_data["roles_wl"]:
                        role = await commands.RoleConverter().convert(ctx, role)
                        if role in ctx.author.roles:
                            found = True
                            break
                    
                    if not found and cmd_data["roles_wl"]:
                        raise utility.EditError

                    # Check Channel Blacklist
                    for channel in cmd_data["channels_bl"]:
                        if ctx.channel.id == channel:
                            raise utility.EditError

                    # Check Channel Whitelist
                    found = False
                    for channel in cmd_data["channels_wl"]:
                        if channel == ctx.channel.id:
                            found = True
                            break
                    
                    if not found and cmd_data["channels_wl"]:
                        raise utility.EditError
            try:
                await ctx.trigger_typing()
            except discord.errors.Forbidden:
                pass

    def __repr__(self):
        return "**BreadBot Core** Version {}".format(self.version)
    
    @tasks.loop(minutes = 90)
    async def create_backup(self):
        
        # Backup Economy

        all = await self.economy.get_all()
        with open("utility/storage/json/backups.json", "r") as f:
            data = json.load(f)
        
        
        if len(data["economy"]) == 10:
            oldest = sorted(data["economy"], key=lambda x: eval(x)["timestamp"])[0]
            data["economy"].remove(oldest)
        data["economy"].append(str({"timestamp": datetime.datetime.now().timestamp(), "data": all}))

        all = await self.nfts.get_all()
        if len(data["nfts"]) == 10:
            oldest = sorted(data["nfts"], key=lambda x: eval(x)["timestamp"])[0]
            data["nfts"].remove(oldest)
        data["nfts"].append(str({"timestamp": datetime.datetime.now().timestamp(), "data": all}))

        with open("utility/storage/json/backups.json", "w") as f:
            data = json.dump(data, f, indent=4)

    async def on_ready(self):
        self.create_backup.start()
        for guild in self.guilds:
            botcount = len([member for member in guild.members if member.bot])
            if botcount >= 100:
                await guild.leave()

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{self.DEFAULTPREFIX}help | https://dashboard.breadbot.me"))
        await self.register_commands()
        data = read_json("utility/storage/json/blacklist")
        self.blacklisted_users = data["blacklistedUsers"]
        currentMutes = await self.mutes.get_all()
        currentHeists = await self.heists.get_all()
        currentGAWs = await self.giveaways.get_all()
        currentReminders = await self.reminders.get_all()
        
        for mute in currentMutes:
            self.muted_users[mute["_id"]] = mute
        for heist in currentHeists:
            self.heistdata[heist["_id"]] = heist
        for GAW in currentGAWs:
            self.GAWdata[GAW["_id"]] = GAW
        for reminder in currentReminders:
            self.remindData[reminder["_id"]] = reminder

        users = await self.packs.get_all()
        guilds = await self.premium.get_all()
        for data in users:
            self.premiums.append(data["_id"])
        for data in guilds:
            self.premiums.append(data["_id"])
        self.launch_time = datetime.datetime.utcnow()

    async def on_message(self,message):
        if message.author != message.author.bot and not message.author.bot:
            if not message.guild and not message.content.startswith(prefix):
                await self.get_guild(760950684849537124).get_channel(
                    760950866701320193
                ).send(
                    f'User `{message.author}` has sent a report saying: **{message.content}**'
                )
        if not message.guild:
            return
        data = await self.prefixes.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = self.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        #Checks if the author is itself
        if message.author.id == self.user.id:
            return

        #checks if a blacklisted user is using a command if so, it sends a message


        #When the bot is tagged it responds with the guild's prefix
        if message.content.startswith(f"<@!{self.user.id}>") and len(message.content) == len(f"<@!{self.user.id}>"):
            data = await self.prefixes.get_by_id(message.guild.id)
            if not data or "prefix" not in data:
                prefix = self.DEFAULTPREFIX
            else:
                prefix = data["prefix"]
            await message.channel.send(
                f"My prefix here is `{prefix}`", delete_after=15)

        await self.process_commands(message)
        #If a person is using a premium command the bot will ignore if the command is being used in a non premium server


    
    def run(self):
        token = os.environ.get("token")
        try:
            super().run(token, reconnect=True)
        except:
            os.system("kill 1")

def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file, indent=4)



