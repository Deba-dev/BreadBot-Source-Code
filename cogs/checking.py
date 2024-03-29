import discord
from discord.ext import commands
import random
from discord.ext.commands import cooldown, BucketType
from random import choice
from PIL import *
import inspect,os
import math
import datetime
import utility

utility.hypixel.setkey("e411c189-0633-4ad0-9493-f4f902353bd3")

def convert_size(bytes):
    if bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def format_num(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'Qd'][magnitude])

class Checking(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @commands.command(name="source",aliases=["github"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def source(self, ctx, *, command: str = None):
        """Source code command by BobDotCom
        """
        source_url = 'https://github.com/RealBongoChongo/BreadBot-Source-Code'
        branch = 'master'
        if command is None:
            return await ctx.send(source_url)
        obj = self.bc.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'

        final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url + " <- Source")
        
    @commands.command(description="Diagnose a command to see why it may not be working!")
    async def diagnose(self,ctx,cmd):
        cmd = self.bc.get_command(cmd)
        if not cmd:
            return await ctx.send("This is not a valid command!")
        
        data = await self.bc.botedit.find(ctx.guild.id)
        if not data:
            return await ctx.send("There is nothing set that could possibly interfere with this command")
        em = discord.Embed(title="Diagnosis")
        data["roles_bl"] = [await commands.RoleConverter().convert(ctx, str(role)) for role in data["roles_bl"]]
        em.add_field(name="Server Blacklisted Roles", value=", ".join([role.mention for role in data["roles_bl"]]) if data["roles_bl"] else "None")
        data["roles_wl"] = [await commands.RoleConverter().convert(ctx, str(role)) for role in data["roles_wl"]]
        em.add_field(name="Server Whitelisted Roles", value=", ".join([role.mention for role in data["roles_wl"]]) if data["roles_wl"] else "None")
        data["channels_bl"] = [await commands.TextChannelConverter().convert(ctx, str(channel)) for channel in data["channels_bl"]]
        em.add_field(name="Server Blacklisted Channels", value=", ".join([channel.mention for channel in data["channels_bl"]]) if data["channels_bl"] else "None")
        data["channels_wl"] = [await commands.TextChannelConverter().convert(ctx, str(channel)) for channel in data["channels_wl"]]
        em.add_field(name="Server Whitelisted Channels", value=", ".join([channel.mention for channel in data["channels_wl"]]) if data["channels_wl"] else "None")

        if cmd.qualified_name not in data["commands"]:
            em.add_field(name="Command Blacklisted Roles", value="None")
            em.add_field(name="Command Whitelisted Roles", value="None")
            em.add_field(name="Command Blacklisted Channels", value="None")
            em.add_field(name="Command Whitelisted Channels", value="None")
        else:
            data = data["commands"][cmd.qualified_name]
            data["roles_bl"] = [await commands.RoleConverter().convert(ctx, str(role)) for role in data["roles_bl"]]
            em.add_field(name="Command Blacklisted Roles", value=", ".join([role.mention for role in data["roles_bl"]]) if data["roles_bl"] else "None")
            data["roles_wl"] = [await commands.RoleConverter().convert(ctx, str(role)) for role in data["roles_wl"]]
            em.add_field(name="Command Whitelisted Roles", value=", ".join([role.mention for role in data["roles_wl"]]) if data["roles_wl"] else "None")
            data["channels_bl"] = [await commands.TextChannelConverter().convert(ctx, str(channel)) for channel in data["channels_bl"]]
            em.add_field(name="Command Blacklisted Channels", value=", ".join([channel.mention for channel in data["channels_bl"]]) if data["channels_bl"] else "None")
            data["channels_wl"] = [await commands.TextChannelConverter().convert(ctx, str(channel)) for channel in data["channels_wl"]]
            em.add_field(name="Command Whitelisted Channels", value=", ".join([channel.mention for channel in data["channels_wl"]]) if data["channels_wl"] else "None")
        await ctx.send(embed=em)

    @commands.command(description="Check out the hypixel stats of a user")
    async def hypixel(self,ctx,user):
        player = utility.hypixel.Player(user)
        data = player.getdata()
        if data:
            em = discord.Embed(
                title = "Hypixel Stats for {}".format(data["name"]),
                color = random.choice(self.bc.color_list)
            )
            em.add_field(name="Rank",value=data["rank"])
            em.add_field(name="Network Level", value=data["level"])
            if data["guild"] is not None:
                em.add_field(name="Guild", value=data["guild"]["name"])
            else:
                em.add_field(name="Guild",value="No Guild")
            if not data["recentgames"]:
                em.add_field(name="Recent Game", value="None")
            else:
                mode = data["recentgames"][0]["mode"].replace("FOUR_FOUR","4x4x4x4").replace("FOUR_THREE","3x3x3x3").replace("EIGHT_TWO", "Doubles").replace("EIGHT_ONE", "Solos")
                em.add_field(name="Recent Game", value="""
```yaml
Name: {}
Mode: {}
Map: {}
```
""".format(data["recentgames"][0]["gameType"],mode,data["recentgames"][0]["map"]))
            await ctx.send(embed=em)
        else:
            await ctx.send("This user has been recently searched!")

    @commands.group(invoke_without_command=True)
    async def skyblock(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="skyblock")
        
    @skyblock.command(name="player", description="Check out a player's general profile stats")
    async def skyblock_player(self,ctx,user):
        player = utility.SkyblockPlayer(user)
        stats1 = player.getprofile()
        if stats1 is None:
            return await ctx.send("This player does not exist!")
        stats = stats1["members"][stats1["profile_id"]]["stats"]
        objectives = stats1["members"][stats1["profile_id"]]["objectives"]
        em = discord.Embed(
            title=f"Hypixel Profile Stats for {user}"
        )
        em.add_field(name="Kills", value=stats["kills"])
        em.add_field(name="Deaths", value=stats["deaths"])
        em.add_field(name="Best Crit Damage", value=stats["highest_critical_damage"])
        em.add_field(name="Total Auction Bids", value=stats["auctions_bids"])
        em.add_field(name="Highest Auction Bid", value=stats["auctions_highest_bid"])
        em.add_field(name="Complete Objectives",value=len({key: value for key, value in objectives.items() if value["status"] == "COMPLETE"}))
        await ctx.send(embed=em)

    @skyblock.group(invoke_without_command=True)
    async def bazaar(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="skyblock bazaar")
    
    @bazaar.command(name="item", description="Lookup any item in the bazaar")
    async def bazaar_item(self,ctx,*,item):
        sb = utility.Skyblock()
        item = sb.getbazaar(item)
        if item is None:
            return await ctx.send("That item doesn't exist or it is not sold on the bazaar!")
        item = item["quick_status"]
        em = discord.Embed(
            title="Bazaar stats for {}".format(item["productId"].lower().capitalize())
        )
        em.add_field(name="Buy Price",value=item["buyPrice"])
        em.add_field(name="Sell Price", value=item["sellPrice"])
        em.add_field(name="Buy Orders",value=item["buyOrders"])
        em.add_field(name="Sell Orders", value = item["sellOrders"])
        await ctx.send(embed=em)

    @commands.command(
        description="Check your level in your server!"
    )
    async def rank(self,ctx,member:discord.Member=None):
        if not member:
            member = ctx.author
        if member.bot:
            return await ctx.send("Bots cant earn levels!")
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            data = {"id":ctx.guild.id, "multi":1, "message":"{member} you just leveled up to level {level} GG!","channel": None, "members": [], "blacklisted": [], "rewards": {}}
            data["members"].append({"userid": member.id, "level":1, "xp": 0, "maxXp": 35})
        if next((user for user in data["members"] if user['userid'] == member.id), None) is None:
            data["members"].append({"userid": member.id, "level":1, "xp": 0, "maxXp": 35})
        user = next((user for user in data["members"] if user['userid'] == member.id), None)
        member = self.bc.get_user(user["userid"])    
        avatar = member.avatar
        if not avatar:
            avatar = member.default_avatar
        await avatar.save('utility/storage/images/Avatar.png')
        im = Image.open('utility/storage/images/Avatar.png').convert("RGB")
        im = im.resize((120, 120))
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        output = ImageOps.fit(im, mask.size, centering=(10, 10))
        output.putalpha(mask)
        output.save('utility/storage/images/output.png')

        im2 = Image.open('utility/storage/images/level.png').convert('RGBA')
        im2.paste(im, (5, 5), im)
        draw = ImageDraw.Draw(im2)
        incriments = 416 / user["maxXp"]
        if "color" not in user:
            color=(98,211,245,255)
        else:
            color=(user["color"][0],user["color"][1],user["color"][2],255)

        if user["xp"] != 0:
            x, y, diam = incriments*user["xp"], 178, 24
            draw.ellipse([x,y,x+diam,y+diam], fill=color)
            ImageDraw.floodfill(im2, xy=(9,190), value=color, thresh=40)
        else:
            pass
        rank = data["members"].index(user)
        font = ImageFont.truetype("utility/fonts/abel-regular.ttf", 20)
        draw.text((35, 145), "Level: {}".format(user["level"]), fill=(255, 255, 255),font=font)
        draw.text((125, 145), "XP: {}/{}".format(format_num(user["xp"]),format_num(user["maxXp"])), fill=(255, 255, 255),font=font)
        draw.text((330, 145), "Rank: #{}".format(rank+1), fill=(255, 255, 255),font=font)
        draw.text((132, 30), f"{member.name}#{member.discriminator}", fill=(255, 255, 255,255),font=font)
        draw.rectangle((132, 67, 374, 70), fill=color, outline=color)
        draw.rectangle((456, 0, 520, 210), fill=color, outline=color)

        
        
        # Save result
        im2.save('utility/storage/images/result.png')
        await ctx.send(file=discord.File("utility/storage/images/result.png"))
        await self.bc.ranks.upsert(data)

    @commands.command(
        description="Check the top 10 people with the most levels"
    )
    async def lb(self,ctx):
        data = await self.bc.ranks.find(ctx.guild.id)
        em = discord.Embed(
            title = "Level Leaderboard",
            color = random.choice(self.bc.color_list)
        )
        em.set_thumbnail(url=ctx.guild.icon)
        for member in data["members"]:
            if data["members"].index(member) == 10:
                break
            _member = ctx.guild.get_member(member["userid"])
            rank = data["members"].index(member) + 1
            em.add_field(name=f"{rank}. {_member}",value="Level: {}\nXP: {}/{}".format(member["level"],format_num(member["xp"]),format_num(member["maxXp"])),inline=False)
        await ctx.send(embed=em)

    @commands.command(
      name='memberinfo', aliases=['userinfo','whois'], description='check out some facts about another user or yourself', usage='[user]'
    )
    async def memberinfo(self, ctx, member:discord.Member = None):
        user = user = ctx.author if not member else member
        roles = [role for role in user.roles]
        roles.remove(ctx.guild.default_role)
        nick = user.nick if user.nick else "No Nickname"
        activity = user.activity.name if user.activity else "No Activity"
        perm_list = [perm[0] for perm in user.guild_permissions if perm[1]]
        booster = "<a:tick:816709602384937031>" if ctx.guild.premium_subscriber_role in user.roles else "<a:no:816709772342591498>"
        if user.status == discord.Status.online:
            new_status = "🟢 | Online"
        if user.status == discord.Status.idle:
            new_status = "🟡 | Idle"
        if user.status == discord.Status.dnd:
            new_status = "🔴 | Do Not Disturb"
        else:
            new_status = "⚫ | Offline"
            
        em = discord.Embed(
            title=user.name + "#" + user.discriminator,
            color=random.choice(self.bc.color_list),
            timestamp = datetime.datetime.utcnow()
        )
        em.add_field(name="General:",value="""
Nickname: {}
Activity: {}
Status: {}
Bot: {}
Booster: {}
Registered: {}
Joined: {}
""".format(f"**{nick}**",f"```{activity}```",f"**{new_status}**",f"**{user.bot}**",booster,f"**{user.created_at.strftime('%a, %#d %B %Y, %I:%M %p')}**",f"**{user.joined_at.strftime('%a, %#d %B %Y, %I:%M %p')}**"))
        em.add_field(name="Top Role", value=f"{user.top_role.mention}",inline=False)
        if len(roles) == 0:
            em.add_field(name="Member Roles (0)", value="This user has no roles", inline=False)
        else:
            if len(str([role.mention for role in roles])) < 1025:
                em.add_field(name=f"Member Roles ({len(roles)})", value=", ".join([role.mention for role in roles]), inline=False)
            else:
                em.add_field(name=f"Member Roles ({len(roles)})", value="Too many roles to send", inline=False)
        em.add_field(name="General Permissions",value=", ".join([f"{perm[0].replace('_', ' ')}" for perm in user.guild_permissions if perm[1] and perm[0] in self.bc.main_perms])  if [f"{perm[0].replace('_', ' ').title()}" for perm in user.guild_permissions if perm[1] and perm[0] in self.bc.main_perms] else "No Permissions",inline=False)
        em.set_footer(text=f'Member ID: {user.id}')
        em.set_thumbnail(url=user.avatar)
        await ctx.send(embed=em)

    @commands.command(
        aliases=['avatar'], description="get the avatar of someone else", usage="[user]"
    )
    @cooldown(1, 10, BucketType.user)
    async def av(self, ctx, member: discord.Member=None):
        if member == None:
            member = ctx.author
        else:
            pass
        user = ctx.author
        embed = discord.Embed(
            title=f"{member}'s avatar",
            color=random.choice(self.bc.color_list), timestamp=datetime.datetime.utcnow(),
        )
        embed.set_image(url=member.avatar)
        embed.set_footer(text=f'Requested by: {user}')
        await ctx.send(embed=embed)

    @commands.command(description="See what modroles are set in your server")
    async def modroles(self,ctx):
        data = await self.bc.modroles.find(ctx.guild.id)
        roles = []
        for i in data["roles"]:
            role = discord.utils.get(ctx.guild.roles, id=i)
            roles.append(role)
        em=discord.Embed(
            title="Modroles",
            description="\n".join([role.mention for role in roles]),
            color=random.choice(self.bc.color_list)
        )
        await ctx.send(embed=em)

    @commands.command(
        description="check out some facts about ya server",
        aliases=['server'],
        usage=" "
    )
    @commands.cooldown(1, 5, BucketType.guild)
    async def serverinfo(self, ctx):
        embed = discord.Embed(
            title="Server Overview",
            color = random.choice(self.bc.color_list)
        )
        embed.add_field(name="General", value="Server Region: {}\nName: {}\nOwner: {}\nOwner ID: {}\nMembers: {}\nBots: {}".format(ctx.guild.region[0].title(), ctx.guild.name, ctx.guild.owner, ctx.guild.owner.id, len(ctx.guild.members), len([bot for bot in ctx.guild.members if bot.bot])))
        embed.add_field(name="Channels/Roles/Categories", value="Categories: {}\nVoice Channels: {}\nText Channels: {}\nRoles: {}".format(len(ctx.guild.categories), len(ctx.guild.voice_channels), len(ctx.guild.text_channels), len(ctx.guild.roles)))
        embed.add_field(name="Boost Info", value="Boosts: {}\nServer Level: {}".format(ctx.guild.premium_subscription_count, ctx.guild.premium_tier))
        true = ctx.guild.mfa_level
        if true == 1:
            true = '<a:tick:816709602384937031>'
        else:
            true = '<a:no:816709772342591498>'
        embed.add_field(name="Misc", value="Admin 2FA: {}\nVerification Level: {}".format(true, ctx.guild.verification_level[0].title()))
        embed.set_footer(text=f'Prompted by {ctx.author}', icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.command(
        name="channelstats",
        aliases=["cs"],
        description="Sends a nice fancy embed with some channel stats",
        usage=' '
    )
    async def channelstats(self, ctx):
        channel = ctx.channel

        embed = discord.Embed(
            title=f"Stats for **{channel.name}**",
            description=f"{'Category: {}'.format(channel.category.name) if channel.category else 'This channel is not in a category'}",
            color=random.choice(self.bc.color_list),
        )
        embed.add_field(name="Channel Guild", value=ctx.guild.name)
        embed.add_field(name="Channel Id", value=channel.id)
        embed.add_field(
            name="Channel Topic",
            value=f"{channel.topic if channel.topic else 'No topic.'}",
            inline=False,
        )
        embed.add_field(name="Channel Position", value=channel.position)
        embed.add_field(
            name="Channel Slowmode Delay", value=channel.slowmode_delay
        )
        embed.add_field(name="Channel is nsfw?", value=channel.is_nsfw())
        embed.add_field(name="Channel is news?", value=channel.is_news())
        embed.add_field(
            name="Channel Creation Time", value=channel.created_at
        )
        embed.add_field(
            name="Channel Permissions Synced",
            value=channel.permissions_synced,
            inline=False,
        )
        embed.add_field(name="Channel Hash", value=hash(channel))

        await ctx.send(embed=embed)

def setup(bc):
    bc.add_cog(Checking(bc))