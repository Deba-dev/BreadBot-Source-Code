"""
   Copyright [2021] [BongoPlayzYT]

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
import keep_alive
import time
from random import choice
from discord.ext import commands
import motor.motor_asyncio
import datetime
import tools.errors
from tools import commands2
import discordmongo


async def get_prefix(bc, message):
    # If dm's
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

class BreadBot(commands.AutoShardedBot):
    def __init__(self):
        owner=485513915548041239
        DEFAULTPREFIX = "="
        intents=discord.Intents.all()

        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True, 
            owner_id=owner,
            intents=intents)
        
        self.owner = owner
        self.remove_command("help")
        self.muted_users = {}
        self.heistdata = {}
        self.GAWdata = {}
        self.connection_url = os.environ.get("mongo")
        with open("changelogs.txt", "r") as f:
            lines = f.readlines()
        self.version = lines[1].replace("**Version:** ", "")
        self.DEFAULTPREFIX = DEFAULTPREFIX
        self.dbltoken = os.environ.get("DBLTOKEN")
        self.gettingmemes = True
        self.colors = {
            "WHITE": 0xFFFFFF,
            "AQUA": 0x1Abc9C,
            "GREEN": 0x2ECC71,
            "BLUE": 0x3498DB,
            "PURPLE": 0x9B59B6,
            "LUMINOUS_VIVID_PINK": 0xE91E63,
            "GOLD": 0xF1C40F,
            "ORANGE": 0xE67E22,
            "RED": 0xE74C3C,
            "NAVY": 0x34495E,
            "DARK_AQUA": 0x11806A,
            "DARK_GREEN": 0x1F8B4C,
            "DARK_BLUE": 0x206694,
            "DARK_PURPLE": 0x71368A,
            "DARK_VIVID_PINK": 0xAD1457,
            "DARK_GOLD": 0xC27C0E,
            "DARK_ORANGE": 0xA84300,
            "DARK_RED": 0x992D22,
            "DARK_NAVY": 0x2C3E50,
        }
        self.color_list = [c for c in self.colors.values()]
        self.main_perms = ["administrator", "manage_channels", "manage_guild", "kick_members", "ban_members","view_audit_log", "send_messages", "read_messages", "send_tts_messages", "attach_files", "embed_links", "mention_everyone", "connect", "speak", "mute_members", "deafen_members", "change_nicknames", "manage_roles", ""]

        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(self.connection_url))
        self.db = self.mongo["bread"]
        self.prefixes = discordmongo.Mongo(connection_url=self.db, dbname="prefixes")
        self.mutes = discordmongo.Mongo(connection_url=self.db, dbname="mutes")
        self.modroles = discordmongo.Mongo(connection_url=self.db, dbname="modroles")
        self.heists = discordmongo.Mongo(connection_url=self.db, dbname="heists")
        self.cmd_usage = discordmongo.Mongo(connection_url=self.db, dbname="usage")
        self.linksonly = discordmongo.Mongo(connection_url=self.db, dbname="linkonly")
        self.premium = discordmongo.Mongo(connection_url=self.db, dbname="premium")
        self.warns = discordmongo.Mongo(connection_url=self.db, dbname="warnings")
        self.invites = discordmongo.Mongo(connection_url=self.db, dbname="invites")
        self.config = discordmongo.Mongo(connection_url=self.db, dbname="config")
        self.reaction_roles = discordmongo.Mongo(connection_url=self.db, dbname="reactionroles")
        self.modlogs = discordmongo.Mongo(connection_url=self.db, dbname="modlogs")
        self.giveaways = discordmongo.Mongo(connection_url=self.db, dbname="giveaways")
        self.suggestions = discordmongo.Mongo(connection_url=self.db, dbname="suggestions")
        self.censor = discordmongo.Mongo(connection_url=self.db, dbname="censor")
        self.welcomes = discordmongo.Mongo(connection_url=self.db, dbname="welcomes")
        self.leaves = discordmongo.Mongo(connection_url=self.db, dbname="leaves")
        self.starboard = discordmongo.Mongo(connection_url=self.db, dbname="starboard")
        self.ranks = discordmongo.Mongo(connection_url=self.db, dbname="levels")
        self.tags = discordmongo.Mongo(connection_url=self.db, dbname="tags")
        self.chatbot = discordmongo.Mongo(connection_url=self.db, dbname="chatbot")
        self.locked = discordmongo.Mongo(connection_url=self.db, dbname="locked")
        self.logs = discordmongo.Mongo(connection_url=self.db, dbname="cmdlogs")
        self.economy = discordmongo.Mongo(connection_url=self.db, dbname="economy")
        self.rickroll = discordmongo.Mongo(connection_url=self.db, dbname="rickroll")
        self.afk = discordmongo.Mongo(connection_url=self.db, dbname="afk")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith("_"):
                self.load_extension(f'cogs.{filename[:-3]}')
                
        @self.before_invoke
        async def before_any_command(ctx):
            data = read_json("blacklist")
            self.blacklisted_users = data["blacklistedUsers"]
            if ctx.author.id in self.blacklisted_users:
                error = tools.errors.Blacklisted(ctx)
                raise await error.send()
            
            data = await self.premium.find(ctx.guild.id)
            if data is None and ctx.command.qualified_name.lower() in commands2.premium:
                error = tools.errors.Premium(ctx)
                raise await error.send()

            try:
                await ctx.trigger_typing()
            except discord.errors.Forbidden:
                pass

    async def on_ready(self):
        data = read_json("blacklist")
        self.blacklisted_users = data["blacklistedUsers"]
        currentMutes = await self.mutes.get_all()
        currentHeists = await self.heists.get_all()
        currentGAWs = await self.giveaways.get_all()
        
        for mute in currentMutes:
            self.muted_users[mute["_id"]] = mute
        for heist in currentHeists:
            self.heistdata[heist["_id"]] = heist
        for GAW in currentGAWs:
            self.GAWdata[GAW["_id"]] = GAW
        print(self.user.id)
        self.launch_time = datetime.datetime.utcnow()

    async def on_message(self,message):
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

        #If a person is using a premium command the bot will ignore if the command is being used in a non premium server


    
    def run(self, a):
        token = os.environ.get("token")
        keep_alive.keep_alive()
        
        super().run(token, reconnect=True)

def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file, indent=4)



