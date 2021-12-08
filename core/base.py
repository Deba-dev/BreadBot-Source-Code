import os
from discord.ext import commands
import discordmongo
import motor.motor_asyncio

class BaseBot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        self.main_perms = ["administrator", "manage_channels", "manage_guild", "kick_members", "ban_members","view_audit_log", "send_messages", "read_messages", "send_tts_messages", "attach_files", "embed_links", "mention_everyone", "connect", "speak", "mute_members", "deafen_members", "change_nicknames", "manage_roles", "manage_messages"]

        self.connection_url = os.environ.get("mongo")
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(self.connection_url))
        self.db = self.mongo["bread"]
        self.prefixes = discordmongo.Mongo(connection_url=self.db, dbname="prefixes")
        self.mutes = discordmongo.Mongo(connection_url=self.db, dbname="mutes")
        self.modroles = discordmongo.Mongo(connection_url=self.db, dbname="modroles")
        self.heists = discordmongo.Mongo(connection_url=self.db, dbname="heists")
        self.cmd_usage = discordmongo.Mongo(connection_url=self.db, dbname="usage")
        self.linksonly = discordmongo.Mongo(connection_url=self.db, dbname="linkonly")
        self.premium = discordmongo.Mongo(connection_url=self.db, dbname="premium")
        self.packs = discordmongo.Mongo(connection_url=self.db, dbname="packs")
        self.warns = discordmongo.Mongo(connection_url=self.db, dbname="warnings")
        self.invites = discordmongo.Mongo(connection_url=self.db, dbname="invites")
        self.config = discordmongo.Mongo(connection_url=self.db, dbname="config")
        self.reactions = discordmongo.Mongo(connection_url=self.db, dbname="reactionroles")
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
        self.reminders = discordmongo.Mongo(connection_url=self.db, dbname="reminders")
        self.botedit = discordmongo.Mongo(connection_url=self.db, dbname="botedit")
        self.nfts = discordmongo.Mongo(connection_url=self.db, dbname="nfts")