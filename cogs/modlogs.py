import discord
import asyncio
import datetime
import random
from random import choice
from discord.ext import commands

class ModLogs(commands.Cog):
    def __init__(self,bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        data = await self.bc.modlogs.find(after.guild.id)
        if data is None:
            return
        channel = self.bc.get_channel(data["channel"])
        if before.nick != after.nick:
            em = discord.Embed(
                title="Nickname Change",
                color=random.choice(self.bc.color_list),
                timestamp=datetime.datetime.utcnow()
            )
            em.add_field(name="Before:", value=before.nick)
            em.add_field(name="After:", value=after.nick)
            em.set_thumbnail(url=after.avatar_url)
            em.set_footer(text="User ID: "+str(after.id))
            await channel.send(embed=em)
        if before.roles != after.roles:
            beforeroles = [role.mention for role in before.roles]
            beforeroles.remove(before.guild.default_role)
            if len(beforeroles) == 0:
                beforeroles = ["No Roles"]
            afterroles = [role for role in after.roles]
            afterroles.remove(before.guild.default_role)
            em = discord.Embed(
                title="Roles Change",
                color=random.choice(self.bc.color_list),
                timestamp=datetime.datetime.utcnow()
            )
            em.add_field(name="Before:", value=", ".join([role for role in beforeroles]))
            em.add_field(name="After:", value=", ".join([role.mention for role in afterroles]))
            em.set_thumbnail(url=after.avatar_url)
            em.set_footer(text="User ID: "+str(after.id))
            await channel.send(embed=em)
        else:
            return
    
    @commands.Cog.listener()
    async def on_message_delete(self,msg):
        data = await self.bc.modlogs.find(msg.guild.id)
        if data is None:
            return
        channel = self.bc.get_channel(data["channel"])
        em = discord.Embed(
            title="Deleted Message",
            color=random.choice(self.bc.color_list),
            timestamp=datetime.datetime.utcnow()
        )
        em.add_field(name="Message Content:",value=msg.content,inline=False)
        em.add_field(name="Channel:",value=msg.channel.mention,inline=False)            
        em.set_thumbnail(url=msg.author.avatar_url)
        em.set_footer(text="User ID: "+str(msg.author.id))
        await channel.send(embed=em)
    
    @commands.Cog.listener()
    async def on_guild_role_create(self,role):
        data = await self.bc.modlogs.find(role.guild.id)
        if data is None:
            return
        channel = self.bc.get_channel(data["channel"])
        em = discord.Embed(
            title="Role Created",
            color=random.choice(self.bc.color_list),
            timestamp=datetime.datetime.utcnow()
        )
        em.add_field(name="Role Name:",value=role,inline=False)
        em.add_field(name="Mentionable:",value=role.mentionable,inline=False)
        em.add_field(name="Hoisted:",value=role.hoist,inline=False)
        em.set_footer(text="Role ID: "+str(role.id))
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_role_delete(self,role):
        data = await self.bc.modlogs.find(role.guild.id)
        if data is None:
            return
        channel = self.bc.get_channel(data["channel"])
        em = discord.Embed(
            title="Role Deleted",
            color=random.choice(self.bc.color_list),
            timestamp=datetime.datetime.utcnow()
        )
        em.add_field(name="Role Name:",value=role,inline=False)
        em.add_field(name="Mentionable:",value=role.mentionable,inline=False)
        em.add_field(name="Hoisted:",value=role.hoist,inline=False)
        em.set_footer(text="Role ID: "+str(role.id))
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_ban(self,guild,user):
        data = await self.bc.modlogs.find(guild.id)
        if data is None:
            return
        channel = self.bc.get_channel(data["channel"])
        em=discord.Embed(
            title="Member Ban",
            color=random.choice(self.bc.color_list)
        )
        em.add_field(name="User:",value=user,inline=False)         
        em.set_thumbnail(url=user.avatar_url)
        em.set_footer(text="User ID: "+str(user.id))
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_member_unban(self,guild,user):
        data = await self.bc.modlogs.find(guild.id)
        if data is None:
            return
        channel = self.bc.get_channel(data["channel"])
        em=discord.Embed(
            title="Member Unban",
            color=random.choice(self.bc.color_list)
        )
        em.add_field(name="User:",value=user,inline=False)         
        em.set_thumbnail(url=user.avatar_url)
        em.set_footer(text="User ID: "+str(user.id))
        await channel.send(embed=em)

def setup(bc):
    bc.add_cog(ModLogs(bc))