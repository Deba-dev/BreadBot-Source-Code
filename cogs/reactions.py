import discord
import asyncio
import emojis
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = str(payload.emoji)
        data = await self.bc.reactions.find(payload.channel_id)
        if not data or not payload.guild_id:
            return
        print(emoji)
        if str(payload.message_id) not in data["menus"].keys():
            return
        menu = data["menus"][str(payload.message_id)]
        if emoji in menu.keys():
            guild = self.bc.get_guild(payload.guild_id)
            role = guild.get_role(menu[emoji])
            await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        emoji = str(payload.emoji)
        data = await self.bc.reactions.find(payload.channel_id)
        if not data or not payload.guild_id:
            return
        print(emoji)
        if str(payload.message_id) not in data["menus"].keys():
            return
        menu = data["menus"][str(payload.message_id)]
        if emoji in menu.keys():
            guild = self.bc.get_guild(payload.guild_id)
            role = guild.get_role(menu[emoji])

            member = guild.get_member(payload.user_id)
            await member.remove_roles(role)
    
    @commands.group(description="Make a reaction role menu", invoke_without_command=True, aliases=["rr"])
    @commands.cooldown(1,5,commands.BucketType.guild)
    async def reactionrole(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="reactionrole")

    @reactionrole.command(description="Quick setup for a reaction role")
    @commands.is_owner()
    @commands.cooldown(1,5,commands.BucketType.guild)
    async def make(self,ctx):
        embed = discord.Embed()
        roles = []
        channel = None
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        await ctx.send("What channel should the menu be in?")
        try:
            msg = await self.bc.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out!")
        else:
            try:
                _ = await commands.TextChannelConverter().convert(ctx, msg.content)
            except:
                return await ctx.send("Channel is invalid")
            else:
                channel = _
        await ctx.send("What do you want the title and description to be of the reaction role menu? You can also use {roles} to already display the roles!\n\nFormat: `Title||Description`\nExample: `Color Roles||Come get your color roles here:\n{roles}`")
        try:
            msg = await self.bc.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out!")
        else:
            if not "||" in msg.content:
                return await ctx.send("You need to have a title and a description!")
            format = msg.content.split("||")
            if len(format) > 2:
                return await ctx.send("You cant have more titles or descriptions!")
            embed.title = format[0]
            embed.description = format[1]
            await ctx.send("This is what your menu will look like!", embed=embed)
        await ctx.send("What color do you want the embed to be? **Use hex code format**\n\nExample: `#ff0000`")
        try:
            msg = await self.bc.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out!")
        else:
            if "#" not in msg.content:
                return await ctx.send("You must use hex code format")
            try:
                color = int(msg.content.replace("#", "0x"), 16)
            except:
                return await ctx.send("An error occured whilst converting this to a number!")
            else:
                embed.color = color
            await ctx.send("Your menu will now look like this!", embed=embed)
        await ctx.send("Now here comes the fun part. Put down your emoji and a role! Say `done` when you are finished!\n\nExample: `:kek: @\everyone`")
        while True:
            try:
                msg = await self.bc.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Timed out!")
            else:
                if msg.content == "done":
                    break
                format = msg.content.split(" ")
                if len(format) != 2:
                    return await ctx.send("You need an emoji and a role seperated by a space!")
                try:
                    role = await commands.RoleConverter().convert(ctx, format[1])
                except:
                    return await ctx.send("Role is invalid!")
                try:
                    await commands.EmojiConverter().convert(ctx, format[0])
                except:
                    emoji = emojis.get(format[0])
                    try:
                        emoji = emoji.pop()
                    except:
                        return await ctx.send("Invalid emoji")
                else:
                    emoji = format[0]

                emoji = str(emoji)

                roles.append({"emoji": emoji, "role": role.id})
                await msg.add_reaction("<a:tick:816709602384937031>")
        role_desc = ""
        for data in roles:
            role = await commands.RoleConverter().convert(ctx, str(data["role"]))
            role_desc += "{} - {}\n".format(data["emoji"], role.mention)
        embed.description = embed.description.replace("{roles}", role_desc)
        data = await self.bc.reactions.find(channel.id)
        try:
            msg = await channel.send(embed=embed)
        except:
            return await ctx.send("I cannot send messages in this channel!")
        for reaction in roles:
            await msg.add_reaction(reaction["emoji"])
        if not data:
            data = {"_id": channel.id, "disabled": False, "menus": {}}
        data["menus"][str(msg.id)] = {}
        for reaction in roles:
            data["menus"][str(msg.id)][reaction["emoji"]] = reaction["role"]
        await self.bc.reactions.upsert(data)
        
def setup(bc):
    bc.add_cog(ReactionRoles(bc))