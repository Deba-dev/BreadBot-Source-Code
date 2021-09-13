import discord
from discord.ext import commands
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

class Config(commands.Cog):
    def __init__(self, bc):
      self.bc = bc

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def ricktoggle(self,ctx):
        data = await self.bc.rickroll.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "enabled": False}
        data["enabled"] = not data["enabled"]
        await self.bc.rickroll.upsert(data)
        ternary = "enabled" if data["enabled"] else "disabled"
        await ctx.send("The rickroll detector is now {}".format(ternary))
 
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command()
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
            return await ctx.send("You didn't set up the chatbot yet!")
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
            return await ctx.send("You didn't set up the chatbot yet!")
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
    
    @blchannels.command(name="show")
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
    
    @blchannels.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def blchannels_add(self,ctx,channel:discord.TextChannel=None):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            return
        if not channel:
            return await ctx.send("Please specify a channel!")
        data["blacklisted"].append(channel.id)
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Added #{} to the blacklisted channels.".format(channel.name))
        await ctx.send(embed=em)
        await self.bc.ranks.upsert(data)
        
    @blchannels.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def blchannels_remove(self,ctx,channel:discord.TextChannel=None):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            return
        if not channel:
            return await ctx.send("Please specify a channel!")
        try:
            data["blacklisted"].remove(channel.id)
        except:
            return await ctx.send("That channel isnt blacklisted!")
        em = discord.Embed(color=discord.Color.green())
        em.set_author(name="Removed #{} from the blacklisted channels.".format(channel.name))
        await ctx.send(embed=em)
        await self.bc.ranks.upsert(data)
        
    @lvlsettings.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def rewards(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="lvlsettings rewards")
    
    @rewards.command(name="show")
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
    
    @rewards.command(name="add",pass_context=True)
    @commands.has_permissions(manage_guild=True)
    async def rewards_add(self,ctx,level,*,role:discord.Role):
        try:
            data = await self.bc.ranks.find(ctx.guild.id)
            if data is None:
                return
            try:
                test = int(level)
            except:
                return await ctx.send("The level must be an integer!")
            data["rewards"][str(level)] = role.id
            em = discord.Embed(color=discord.Color.green())
            em.set_author(name="Added `{}` to the rewards.".format(role.name))
            await ctx.send(embed=em)
            await self.bc.ranks.upsert(data)
        except Exception as e:
            print(e)
        
    @rewards.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def rewards_remove(self,ctx,level):
        data = await self.bc.ranks.find(ctx.guild.id)
        if data is None:
            return
        try:
            test = int(level)
        except:
            return await ctx.send("The level must be an integer!")
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
            return await ctx.send("There is no db for this server! Try again")
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
            return await ctx.send("There is no db for this server! Try again")
        if channel:
            data["channel"] = channel.id
        else:
            data["channel"] = channel
        await self.bc.ranks.upsert(data)
        if channel:
            await ctx.send(f"I have updated the level up channel to {channel.mention}!")
        else:
            await ctx.send("The level channel is now unset")
    
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
            await ctx.send("Something went wrong! Try again later")
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
    @commands.is_owner()
    async def starboard_channel(self,ctx,channel:discord.TextChannel=None):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not channel:
            return await ctx.send("Specify a channel!")
        elif not data or "channel" not in data:
            data = {"_id": ctx.guild.id, "channel": None, "limit": 5, "toggled": True, "messages": []}
        data["channel"] = channel.id
        await self.bc.starboard.upsert(data)
        await ctx.send(f"The starboard channel is now {channel.mention}")

    @starboard.command(
        name="delchannel",
        description="delete a channel set for your starboard",
    )
    @commands.is_owner()
    async def starboard_delchannel(self,ctx):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not data or "channel" not in data:
            return await ctx.send("You dont have a channel set up!")
        await self.bc.starboard.delete(ctx.guild.id)
        await ctx.send("The starboard channel is now deleted")
    
    @starboard.command(
        name="toggle",
        description="Toggle the starboard channel on or off",
    )
    @commands.is_owner()
    async def starboard_toggle(self,ctx):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not data or "channel" not in data:
            return await ctx.send("You dont have a channel set up!")
        data["toggled"] = not data["toggled"]
        ternary = "enabled" if data["toggled"] else "disabled"
        await self.bc.starboard.upsert(data)
        await ctx.send(f"The starboard channel is now {ternary}")

    @starboard.command(
        name="limit",
        description="Change how many stars a message needs to appear on the starboard"
    )
    @commands.is_owner()
    async def starboard_limit(self,ctx,limit:int=None):
        data = await self.bc.starboard.find(ctx.guild.id)
        if not limit and data:
            return await ctx.send("The starboard limit is {}".format(data["limit"]))
        elif not data or "channel" not in data:
            return await ctx.send("You need to set up a starboard channel first")
        elif not limit:
            return await ctx.send("Specify a number!")
        data["limit"] = limit
        await self.bc.starboard.upsert(data)
        await ctx.send(f"The starboard limit is now {limit}")

    @automod.group(
        aliases=['censor'], usage="", invoke_without_command=True
    )
    @commands.guild_only()
    async def profanity(self, ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="automod profanity")

    @profanity.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def censor_add(self,ctx,word:str):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            data = {"_id": ctx.guild.id, "words": [], "toggled": True}
        data["words"].append(word)
        await self.bc.censor.upsert(data)
        await ctx.send(f"{word} has been added to the censor filter", delete_after=5)
        await ctx.message.delete()

    @profanity.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def censor_remove(self,ctx,word:str):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            await ctx.send("You have no filter set up!")
            return
        if word not in data["words"]:
            await ctx.send("That word isn't in the filter!")
            return
        data["words"].remove(word)
        await self.bc.censor.upsert(data)
        await ctx.send(f"{word} has been removed from the censor filter")

    @profanity.command(name="toggle")
    @commands.has_permissions(manage_guild=True)
    async def censor_toggle(self,ctx):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            data = {"_id": ctx.guild.id, "words": [], "toggled": True}
        data["toggled"] = not data["toggled"]
        ternary = "enabled" if data["toggled"] else "disabled"
        await self.bc.censor.upsert(data)
        await ctx.send(f"The censor filter is now {ternary}")

    @profanity.command(name="list")
    async def censor_list(self,ctx):
        data = await self.bc.censor.find(ctx.guild.id)
        if not data or "words" not in data:
            await ctx.send("You have no filter set up!")
            return
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
        await ctx.send("I have reset the suggestion settings")

    @commands.command(
        name="deleteprefix", aliases=["dp"], description="Delete your guilds prefix!", usage=" "
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def deleteprefix(self, ctx):
        await self.bc.prefixes.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("This guilds prefix has been set back to the default")
    
    @commands.command(
        description="Change what channel you want the bot to post server actions in (leave blank to delete)",
        usage="<channel>"
    )
    @commands.has_permissions(manage_channels=True)
    async def modlogs(self,ctx,channel:discord.TextChannel=None):
        data = await self.bc.modlogs.find(ctx.guild.id)
        if not channel and data is not None:
            await ctx.send("Modlogs channel has been deleted")
            await self.bc.modlogs.delete(ctx.guild.id)
            return
        elif not channel:
            await ctx.send("Please set up a modlogs channel!")
            return
        if not data or "channel" not in data:
            data = {"_id": ctx.guild.id, "channel": channel.id}
        else:
            data["channel"] = channel.id
        await self.bc.modlogs.upsert(data)
        await ctx.send("Modlogs channel is now {}".format(channel.mention))

    @commands.group(invoke_without_command=True)
    async def welcome(self,ctx):
        await ctx.invoke(self.bc.get_command("help"),entity="welcome")
    
    @welcome.command(name="ping", description="Set a role to ping when a user joins (leave blank to disable)")
    @commands.has_permissions(manage_guild=True)
    async def ping(self,ctx, *, role:discord.Role=None):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data:
            return await ctx.send("You did not set up a welcome system! Please set one up before making a ping role!")
        if not role:
            data["ping"] = None
        else:
            data["ping"] = role.id
        await ctx.send("Success! I have set the ping role!")
        await self.bc.welcomes.upsert(data)

    @welcome.command(name="message", description="Set a custom message that the bot will send when a user joins!")
    @commands.has_permissions(manage_guild=True)
    async def welcome_message(self,ctx, *, message=None):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data:
            return await ctx.send("You did not set up a welcome system! Please set one up before making a welcome message!")
        if not message:
            return await ctx.send("**Arguments**\nYou can use these arguments and the bot will replace it with the corresponding things.\n\n{member} - Mention of the member\n{server} - Name of the server\n{place} - The place of the member joining\n{ending} - The ending of a number such as st, nd, rd, th")
        data["message"] = message
        await ctx.send("I have now set the welcome message!")

    @welcome.command(name="channel",description='Set a welcome channel', usage='<channel>')
    @commands.has_permissions(manage_channels=True)
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data or "channel" not in data:
            data = {"_id": ctx.guild.id, "channel":channel.id,"role":None, "auth": False, "ping": None, "message": "Welcome {member} to **{server}**. You are our `{place}{ending}` member!"}
        data["channel"] = channel.id
        await self.bc.welcomes.upsert(data)
        await ctx.send("The welcome channel is now {}".format(channel.mention))
    
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
        await ctx.send("The welcome role is now {}".format(role.name))

    @welcome.command(
        description="Adds a captcha for sus people upon joining",
        name="auth"
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome_auth(self,ctx):
        data = await self.bc.welcomes.find(ctx.guild.id)
        if not data or "role" not in data:
            return await ctx.send("You must have a welcome role for this to work!")
        data["auth"] = not data["auth"]
        ternary = "enabled" if data["auth"] else "disabled"
        await self.bc.welcomes.upsert(data)
        await ctx.send(f"The captcha is now {ternary}")
        
    @welcome.command(description="Delete your welcome settings", name="delete")
    async def welcome_delete(self,ctx):
        await self.bc.welcomes.delete(ctx.guild.id)
        await ctx.send("I have deleted the settings for the welcome system")

    @commands.command(description='syncs your muterole with your channels(sets muteroles in all channels to no send messages)', usage=' ')
    @commands.has_permissions(manage_roles=True)
    async def sync(self, ctx):
        with open('muteroles.json', 'r') as f:
            channel = json.load(f)
        if channel[str(ctx.guild.id)] == 'Not Set':
            await ctx.send("You dont have a muterole set up")
            return
        else:
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
            for muterole in ctx.guild.text_channels:
                try:
                    await muterole.set_permissions(role, send_messages=False,add_reactions=False)
                except:
                    print("yes")
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
            for muterole in ctx.guild.voice_channels:
                try:
                    await muterole.set_permissions(role, speak=False)
                except:
                    print("yes")
        await ctx.send("I have synced the muterole with all channels")

    @commands.command(description='Set a muterole', usage='<role>')
    @commands.has_permissions(manage_channels=True)
    async def muterole(self, ctx, role: discord.Role):
        if role == None:
            await ctx.send('You havent provided a valid role!')
        else:
            with open('muteroles.json', 'r') as f:
                welcome_id = json.load(f)
            welcome_id[str(ctx.guild.id)] = f'{role.id}'
            with open('muteroles.json', 'w') as f:
                json.dump(welcome_id, f, indent=4)
            await ctx.send(f'The muterole has been set as `{role.name}`.')

    @commands.command(description='Set a leave channel', usage='<channel>')
    @commands.has_permissions(manage_channels=True)
    async def leaves(self, ctx, channel: discord.TextChannel=None):
        if channel == None:
            await ctx.send('You havent provided a valid channel!')
            return
        data = await self.bc.leaves.find(ctx.guild.id)
        if data is None:
            data = {"_id": ctx.guild.id, "channel": None}
        data["channel"] = channel.id
        await self.bc.leaves.upsert(data)
        await ctx.send(f"Leaves channel is now set to {channel.mention}")

    @commands.command(description='use this to set a modrole for your server',usage='<add or remove>')
    @commands.has_permissions(manage_roles=True)
    async def modrole(self,ctx,thingy,role:discord.Role):
        if thingy == "add" or thingy == "set":
            data = await self.bc.modroles.find(ctx.guild.id)
            if data is None or "roles" not in data:
                data = {"_id": ctx.guild.id, "roles": []}
            data["roles"].append(role.id)
            await self.bc.modroles.upsert(data)
            await ctx.send(f"Modrole `{role.name}` added")
        if thingy == "remove" or thingy == "take":
            data = await self.bc.modroles.find(ctx.guild.id)
            data["roles"].remove(role.id)
            await self.bc.modroles.upsert(data)
            await ctx.send("Modrole successfully removed")

    @automod.group(description='use this to add/remove a links only channel for your server',invoke_without_command=True)
    async def linksonly(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="automod linksonly")
            
    @linksonly.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def linkslonyadd(self,ctx,channel:discord.TextChannel):
        data = await self.bc.linksonly.find(ctx.guild.id)
        if data is None or "channels" not in data:
            data = {"_id": ctx.guild.id, "channels": []}
        data["channels"].append(channel.id)
        await self.bc.linksonly.upsert(data)
        await ctx.send(f"channel `{channel.name}` added")

    @linksonly.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def linkslonyremove(self,ctx,channel:discord.TextChannel):
        data = await self.bc.linksonly.find(ctx.guild.id)
        data["channels"].remove(channel.id)
        await self.bc.linksonly.upsert(data)
        if len(data["channels"]) == 0:
            await self.bc.linksonly.delete(ctx.guild.id)
        await ctx.send("channel successfully removed")

def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file)

def setup(bc):
    bc.add_cog(Config(bc))
    