import discord
from discord.ext import commands, tasks
import json
import re
import datetime
from copy import deepcopy
import asyncio
import random
from random import choice
import sys
import time
from dateutil.relativedelta import relativedelta

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d||))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400,"":1}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)

class Moderation(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @staticmethod
    def _overwrites_to_json(overwrites):
        try:
            return {str(target.id): overwrite._values for target, overwrite in overwrites.items()}
        except Exception:
            return {}



    @tasks.loop(seconds=1)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.bc.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                with open('muteroles.json', 'r') as f:
                    channel = json.load(f)
                guild = self.bc.get_guild(value['guildId'])
                member = guild.get_member(value["_id"])

                role = discord.utils.get(guild.roles, id=int(channel[str(guild.id)]))
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Unmuted: {member.display_name}")

                await self.bc.mutes.delete(member.id)
                try:
                    self.bc.muted_users.pop(member.id)
                except KeyError:
                    pass
    
    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bc.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        description="Mutes a given user for an amount of time!",
        usage='<user> [time]'
    )
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter=None):
        with open('muteroles.json', 'r') as f:
            channel = json.load(f)
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
        except KeyError:
            await ctx.send("No muted role was found! Please set one with the muterole command")
            return
        pos1 = ctx.guild.roles.index(ctx.author.top_role)
        pos2 = ctx.guild.roles.index(member.top_role)
        if pos1 == pos2:
            await ctx.send("Both of you have the same power so i can not mute this person!")
            return
        elif pos1 < pos2:
            await ctx.send("This person has more power than you so i can not mute him for you!")
            return


        try:
            if self.bc.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass

        data = {
            "_id": member.id,
            'mutedAt': datetime.datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bc.mutes.upsert(data)
        self.bc.muted_users[member.id] = data

        await member.add_roles(role)

        if not time:
            await ctx.send(f"Muted {member.display_name} infinitely")
            await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=time)
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            if int(hours):
                await ctx.send(
                    f"Muted {member.display_name} for {hours} hours, {minutes} minutes and {seconds} seconds"
                )
                await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=f"{hours} hours, {minutes} minutes and {seconds} seconds")
            elif int(minutes):
                await ctx.send(
                    f"Muted {member.display_name} for {minutes} minutes and {seconds} seconds"
                )
                await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=f"{minutes} minutes and {seconds} seconds")
            elif int(seconds):
                await ctx.send(f"Muted {member.display_name} for {seconds} seconds")
                await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=f"{seconds} seconds")

    @commands.command(
        name='unmute',
        description="Unmuted a member!",
        usage='<user>'
    )
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        with open('muteroles.json', 'r') as f:
            channel = json.load(f)
        role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return



        await self.bc.mutes.delete(member.id)
        try:
            self.bc.muted_users.pop(member.id)
        except KeyError:
            pass

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await member.remove_roles(role)
        await self.postmodlog(ctx.guild,"Unmute",ctx.author,ctx.channel,member=member)
        await ctx.send(f"Unmuted `{member.display_name}`")

    @commands.command(
        pass_context=True,
        name='addrole',
        description='add a role to someone ',
        usage='<member> <role>')
    @commands.has_permissions(manage_roles=True)
    async def addrole(self,
                      ctx,
                      member: discord.Member,
                      *,
                      role: discord.Role):
        await member.add_roles(role)
        await ctx.message.delete()
        await ctx.send(f'{member} Was Given {role}')

    @commands.command(description='Massnick everyone anythin', usage='<name>')
    @commands.has_permissions(manage_nicknames=True)
    async def massnick(self, ctx, *args):
        Nick = ' '.join(map(str, args))
        for member in ctx.guild.members:
            if member == ctx.guild.owner:
                pass
            else:
                try:
                    await member.edit(nick=f'{Nick}')
                    await asyncio.sleep(0.5)
                except:
                    pass
        await ctx.send(f'The entire guild user name was set to `{Nick}`')

    @commands.command(description='revert all nicknames to regular', usage=' ')
    @commands.has_permissions(manage_nicknames=True)
    async def revert(self, ctx):
        for member in ctx.guild.members:
            if member == ctx.guild.owner:
                pass
            else:
                try:
                    await member.edit(nick=f'{member.name}')
                    await asyncio.sleep(0.5)
                except:
                  pass
        await ctx.send('All usernames have returned to normal!')

    @commands.command(
        pass_context=True,
        name='takerole',
        description='takes a role from someone ',
        usage='<member> <role>')
    @commands.has_permissions(manage_roles=True)
    async def takerole(self,
                       ctx,
                       member: discord.Member,
                       *,
                       role: discord.Role):
        pos1 = ctx.guild.roles.index(ctx.author.top_role)
        pos2 = ctx.guild.roles.index(member.top_role)
        if pos1 == pos2:
            await ctx.send("Both of you have the same power so i can not take a role from this person!")
            return
        elif pos1 < pos2:
            await ctx.send("This person has more power than you so i can not take a role from him for you!")
            return
        await ctx.message.delete()
        await member.remove_roles(role)
        await ctx.send(f'{role} was taken from {member}')

    @commands.command(
        name='kick',
        description='kick people',
        usage='<user> [reason]')
    @commands.has_permissions(kick_members=True)
    async def kick(self,
                   ctx,
                   member: discord.Member,
                   *,
                   reason="No Reason Specified"):
        user = member
        pos1 = ctx.guild.roles.index(ctx.author.top_role)
        pos2 = ctx.guild.roles.index(member.top_role)
        if pos1 == pos2:
            await ctx.send("Both of you have the same power so i can not kick this person!")
            return
        elif pos1 < pos2:
            await ctx.send("This person has more power than you so i can not kick him for you!")
            return
        await ctx.message.delete()
        try:
            await user.send(
                f"you were kicked from {ctx.guild.name} for the following reason:\n\n{reason}"
            )
        except:
            await ctx.send("member has been kicked but i could not send a dm to them")
            await self.postmodlog(ctx.guild,"Kick",ctx.author,ctx.channel,reason)
            return
        try:
            await member.kick(reason=reason)
        except:
            await ctx.send("Could Not Kick This Member because I am missing permissions")
            return
        await ctx.send(f'successfully kicked {user}')
        await self.postmodlog(ctx.guild,"Kick",ctx.author,ctx.channel,member,reason)

    @commands.command()
    async def channelsync(self,ctx):
        await ctx.channel.edit(sync_permissions=True)
        await ctx.send("Channel perms synced with category!")

    @commands.command(
        name='ban',
        description='ban people',
        usage='<user> [reason]')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Specified"):
        user = member
        pos1 = ctx.guild.roles.index(ctx.author.top_role)
        pos2 = ctx.guild.roles.index(member.top_role)
        if pos1 == pos2:
            await ctx.send("Both of you have the same power so i can not ban this person!")
            return
        elif pos1 < pos2:
            await ctx.send("This person has more power than you so i can not ban him for you!")
            return
        await ctx.message.delete()
        try:
            await member.ban(reason=reason)
        except:
            await ctx.send("Could Not Ban This Member because I am missing permissions")
            return
        try:
            await user.send(
                f"you were banned from {ctx.guild.name} for the following reason:\n\n{reason}"
            )
        except:
            await ctx.send("member has been banned but i could not send a dm to them")
            await self.postmodlog(ctx.guild,"Ban",ctx.author,ctx.channel,member,reason)
            return
        await ctx.send(f'successfully banned {user}')
        await self.postmodlog(ctx.guild,"Ban",ctx.author,ctx.channel,member=member,reason=reason)
    @commands.command(
        description='Unban someone by their id',
        usage='<userid>'
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member):
        member = await self.bc.fetch_user(int(member))
        await ctx.guild.unban(member)
        await ctx.send(f"unbanned {member.name}")
        await self.postmodlog(ctx.guild,"Unban",ctx.author,ctx.channel)
    @commands.command(
        name='purge',
        description=
        'clear messages with no limit incase you wanna clear your entire chat',
        usage='<amount>')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=1 + amount)
        await self.postmodlog(ctx.guild,"Channel Purge",ctx.author,ctx.channel)

    @commands.command(description='lock the channel ', usage=' ')
    @commands.has_permissions(manage_channels=True)
    async def lock(self,ctx):
        data = await self.bc.modroles.find(ctx.guild.id)
        data2 = await self.bc.locked.find(ctx.channel.id)
        if data2:
            return await ctx.send("This channel is already locked!")
        else:
            data2 = {"_id": ctx.channel.id, "perms": {}}
        #Before channel locks the perms are saved into db
        data2["perms"] = self._overwrites_to_json(ctx.channel.overwrites)
        for role in ctx.guild.roles:
            if role.name == self.bc.user.name:
                continue
            perms = ctx.channel.overwrites_for(role)
            perms.send_messages = False
            perms.add_reactions = False
            await ctx.channel.set_permissions(role, overwrite=perms)
            await asyncio.sleep(0.5)
        try:
            for role in data["roles"]:
                role = discord.utils.get(ctx.guild.roles, id=role)
                perms = ctx.channel.overwrites_for(role)
                perms.send_messages = True
                perms.add_reactions = True
                await ctx.channel.set_permissions(role, overwrite=perms)
                await asyncio.sleep(0.5)
        except Exception as e:
            print(e)
        
        await self.bc.locked.upsert(data2)
        await ctx.send(f"Locked {ctx.channel.mention}. Eveyone that doesnt have a modrole set with me cant chat here.")
        await self.postmodlog(ctx.guild,"Channel Lock",ctx.author,ctx.channel)

    @commands.command(description='unlock a channel you locked', usage='unlock')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self,ctx):
        with open('muteroles.json', 'r') as f:
            channel = json.load(f)
        muterole = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
        if not muterole:
            pass
        data = await self.bc.locked.find(ctx.channel.id)
        if data is None:
            return await ctx.send("This channel is not locked!")
        for role, permissions in data["perms"].items():
            if role == muterole.id:
                continue
            guildrole = discord.utils.get(ctx.guild.roles, id=int(role))
            await ctx.channel.set_permissions(guildrole, overwrite=discord.PermissionOverwrite(**permissions))
            await asyncio.sleep(0.5)
        await ctx.send(f"Unlocked {ctx.channel.mention} all roles can talk here now")
        await self.postmodlog(ctx.guild,"Channel Unlock",ctx.author,ctx.channel)

    @commands.command(description='set a slowmode to a channel. leave blank to reset. max is 21600 seconds', usage='[seconds]')
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self,ctx,*, time: TimeConverter=None):
        if time > 21600:
            await ctx.send("That is over 6 hours i cant do that.")
            return
        if time == None:
            time = 0
        else:
            m, s = divmod(time, 60)
            h, m = divmod(m, 60)
            await ctx.channel.edit(slowmode_delay=time)
            if int(h) == 0 and int(m) == 0:
                em=discord.Embed(
                    color=0xff0000)
                em.set_author(name=f'Slowmode is now {int(s)} seconds')
                await ctx.send(embed=em)
            elif int(h) == 0 and int(m) != 0:
                em=discord.Embed(
                    color=0xff0000
                )
                em.set_author(name=f' Slowmode is now {int(m)} minutes and {int(s)} seconds')
                await ctx.send(embed=em)
            else:
                em=discord.Embed(
                    color=0xff0000
                )
                em.set_author(name=f' Slowmode is now {int(h)} hours, {int(m)} minutes and {int(s)} seconds')
                await ctx.send(embed=em)
            await self.postmodlog(ctx.guild,"Slowmode Change",ctx.author,ctx.channel)

    @commands.command(
        description="Warn someone",
        usage="<user> [reason]"
    )
    @commands.has_permissions(manage_messages=True)
    async def warn(self,ctx,member:discord.Member,*,reason="No Reason Given"):
        data = await self.bc.warns.find(ctx.guild.id)
        if not data:
            data = {
                "_id": ctx.guild.id,
                "cases": 0,
                str(member.id): [],
            }            
        if str(member.id) not in data:
            data = {
                "_id": ctx.guild.id,
                "cases": data["cases"],
                str(member.id): [],
            }
            data[str(member.id)].append({"warning": len(data[str(member.id)]) + 1, "reason": reason,"moderator":ctx.author.id, "case": data["cases"] + 1})
            data["cases"] += 1
        else:
            data[str(member.id)].append({"warning": len(data[str(member.id)]) + 1, "reason": reason,"moderator":ctx.author.id, "case": data["cases"] + 1})
            data["cases"] += 1
        await self.bc.warns.upsert(data)
        await ctx.send("Warned **{}** for the reason:\n`{}`".format(member,reason))
        await self.postmodlog(ctx.guild,"Warn",ctx.author,ctx.channel,member=member,reason=reason,case=data["cases"])

    @commands.command(
        description="Check a person's warns",
        usage="[user]"
    )
    async def warns(self,ctx,member:discord.Member=None):
        data = await self.bc.warns.find(ctx.guild.id)
        if not member:
            member = ctx.author
        if str(member.id) not in data or len(data[str(member.id)]) == 0:
            await ctx.send("This person has no warns")
            return
        else:
            em = discord.Embed(
                title="{}'s warnings".format(member.name),
                color = random.choice(self.bc.color_list)
            )
            warns = data[str(member.id)]
            for thing in warns:
                warnno = thing["warning"]
                reason = thing["reason"]
                mod = await self.bc.fetch_user(thing["moderator"])
                case = thing["case"]
                em.add_field(name=f"Warning {warnno}",value=f"Reason: {reason}\nModerator: {mod}\nCase: {case}",inline=False)
            await ctx.send(embed=em)

    @commands.command(
      aliases=["delwarn"],
      description="delete a warn",
      usage="<user> <case #>"
    )
    @commands.has_permissions(manage_messages=True)
    async def deletewarn(self,ctx,member:discord.Member,case:int):
        data = await self.bc.warns.find(ctx.guild.id)
        if not data:
            await ctx.send("Your server has no warns")
            return
        if str(member.id) not in data:
            await ctx.send("This person has no warns")
            return
        else:
            warns = data[str(member.id)]
            for thing in warns:
                if case == thing["case"]:
                    warns.remove({"warning":thing["warning"], "reason":thing["reason"],"moderator":thing["moderator"],"case":case})
                    await self.bc.warns.upsert(data)
                    await ctx.send("Succesfully deleted warn")
                    await self.postmodlog(ctx.guild,"Warn Deleted",ctx.author,ctx.channel,reason=None,case=case)
                    break
                else:
                    continue

    async def postmodlog(self,guild,action,moderator,channelexec,member=None,reason=None,case=None,duration=None):
        data = await self.bc.modlogs.find(guild.id)
        if not data or "channel" not in data:
            return
        channel = discord.utils.get(guild.text_channels,id=data["channel"])
        em = discord.Embed(
            title="Moderation Command Action",
            color=random.choice(self.bc.color_list)
        )
        em.add_field(name="Action:",value=action,inline=False)
        em.add_field(name="Responsible Moderator:",value=moderator.name,inline=False)
        em.add_field(name="Channel Executed:",value=channelexec.mention,inline=False)
        if reason is not None:
            em.add_field(name="Reason:",value=reason,inline=False)
        if case is not None:
            em.add_field(name="Case:",value=case,inline=False)
        if duration is not None:
            em.add_field(name="Duration:",value=duration)
        if member is not None:
            em.add_field(name="User affected:",value=member,inline=False)
        await channel.send(embed=em)

def setup(bc):
    bc.add_cog(Moderation(bc))
