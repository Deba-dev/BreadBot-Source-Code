import discord
from discord.ext import commands
import random
from PIL import Image, ImageDraw, ImageFont,ImageOps
from random import choice
import contextlib
import ast
import io
import sys
from copy import deepcopy
import json
import os
import asyncio
import traceback
import requests
from io import BytesIO
import time
import datetime
from utility import util

def format_num(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T', 'Qd'][magnitude])

async def save_audit_logs(guild):
    with open(f'audit_logs_{guild.name}', 'w+') as f:
        async for entry in guild.audit_logs(limit=100):
            f.write('{0.user} did {0.action} to {0.target}\n\n'.format(entry))

class Owner(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @staticmethod
    def _overwrites_to_json(overwrites):
        try:
            return {str(target.id): overwrite._values for target, overwrite in overwrites.items()}
        except Exception:
            return {}

    def insert_returns(self,body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)
    
    async def get_members(self,guild):
        member = []
        guild = self.bc.get_guild(int(guild))
        for members in guild.members:
            member.append(members.name + "#" + members.discriminator)
        return member

    @commands.command()
    @commands.is_owner()
    async def updatedocs(self,ctx):
        await util.docs("premium", "config", self.bc, ctx)
        await util.docs("daily", "economy", self.bc, ctx)
        await util.docs("meme", "fun", self.bc, ctx)
        await util.docs("lock", "moderation", self.bc, ctx)
        await util.docs("calc", "utility", self.bc, ctx)
        await util.docs("serverinfo", "checking", self.bc, ctx)
        await util.docs("pixelate", "images", self.bc, ctx)
        await util.docs("gaw", "serverevents", self.bc, ctx)

    @commands.command()
    @commands.is_owner()
    async def botfarms(self, ctx):
        for guild in self.bc.guilds:
            botcount = len([member for member in guild.members if member.bot])
            if botcount >= 100:
                await guild.leave()

    @commands.command()
    @commands.is_owner()
    async def thumbnail(self, ctx, episode, desc):
        im = Image.open("images/thumbnail.png").convert("RGB")
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("LondrinaSolid-Regular.ttf", 60)
        draw.text((290,240), f"( Episode {episode} )", fill = (160, 160, 160), font = font)
        def fittext(txt,imgfraction):
            fontsize = 1
            img_fraction = imgfraction

            font = ImageFont.truetype("LondrinaSolid-Regular.ttf", fontsize)
            while font.getsize(txt)[0] < img_fraction*im.size[0]:
                # iterate until the text size is just larger than the criteria
                fontsize += 1
                font = ImageFont.truetype("LondrinaSolid-Regular.ttf", fontsize)

            # optionally de-increment to be sure it is less than criteria
            fontsize -= 1
            return ImageFont.truetype("LondrinaSolid-Regular.ttf", fontsize)
        draw.text((260,320), f"{desc}", fill = (160, 160, 160), font = fittext(desc, 0.60))
        im.save("images/output.png")
        await ctx.send(file=discord.File("images/output.png"))

    @commands.group(invoke_without_command=True)
    async def changelogs(self,ctx):
        with open("utility/storage/changelogs.txt","r") as f:
            lines = f.readlines()
        notes = "".join(line for line in lines)
        em = discord.Embed(
            title="Changelogs for Latest Version",
            description=notes
        )
        await ctx.send(embed=em)
    
    @commands.command()
    @commands.is_owner()
    async def audit(self,ctx):
        data = await self.bc.logs.find(ctx.guild.id)
        if data is None:
            return await ctx.send("There are no logs!")
        await ctx.send(data["logs"])
    
    @changelogs.command()
    @commands.is_owner()
    async def add(self,ctx,version,*,notes):
        with open("utility/storage/changelogs.txt","w+") as f:
            f.write("""
**Version:** {}
**Notes:**
{}            
""".format(version,notes))
        self.bc.version = version
        await ctx.send("I have updated the changelogs!")

    @commands.command()
    async def rankcolor(self,ctx,*,rgb):
        data = await self.bc.ranks.find(ctx.guild.id)
        user = next((user for user in data["members"] if user['userid'] == ctx.author.id), None)
        rgb = rgb.split(",")
        if len(rgb) != 3:
            return await ctx.send("You must put rgb like 'R, G, B'")
        try:
            r = int(rgb[0])
            g = int(rgb[1])
            b = int(rgb[2])
        except:
            return await ctx.send("You must put in numbers!")
            
        if r in range(0,256) and g in range(0,256) and b in range(0,256):
            user["color"] = [r,g,b]
            await ctx.send("I have updated your rank card color!")
            await self.bc.ranks.upsert(data)
        else:
            return await ctx.send("The rgb numbers must be in range of 0-255")


    @commands.command()
    @commands.is_owner()
    async def restart(self,ctx):
        await ctx.send("Restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command()
    @commands.is_owner()
    async def toggle(self,ctx,*, command=None):
        if command == None:
            await ctx.send("Specify a command dummy")

        command = self.bc.get_command(command)

        if command is None:
            await ctx.send("That command doesn't exist")
        
        elif ctx.command == command:
            await ctx.send("Don't try to disable this command")
        
        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.send("I have toggled {} to {}".format(command,ternary))

    @commands.command()
    async def shortcmd(self,ctx,member:discord.Member,member2:discord.Member):
        pos1 = ctx.guild.roles.index(member2.top_role)
        pos2 = ctx.guild.roles.index(member.top_role)
        if pos1 == pos2:
            await ctx.send("Both of you have same power")
        elif pos1 > pos2:
            await ctx.send(member2.name + " has more power")
        else:
            await ctx.send(member.name + " has more power")
            
    @commands.command()
    @commands.is_owner()
    async def responsetime(self,ctx,*,command):
        start = time.perf_counter()
        await ctx.invoke(self.bc.get_command(command))
        end = time.perf_counter()
        speed = round((end - start) * 1000)
        await ctx.send("It took **{}ms** to run `{}`".format(speed,command))


    @commands.command()
    @commands.is_owner()
    async def run(self,ctx, *, cmd):
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        self.insert_returns(body)
        env = {
            'bc': self.bc,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__,
            'py': None,
            'assprogram': ctx.send("ass "*69),
            'getmembers': await self.get_members(ctx.guild.id),
            'format_num': format_num
        }
        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
            result = list(result)
            await ctx.send(result)
        except Exception:
            await ctx.send(traceback.format_exc(),delete_after=10)
    @commands.command()
    async def uptime(self,ctx):
        delta_uptime = datetime.datetime.utcnow() - self.bc.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed = discord.Embed(title = "Uptime:",description = f"{days}d, {hours}h, {minutes}m", color = random.choice(self.bc.color_list))
        await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx, serverid:int):
        """Create instant invite"""
        servers = [guild for guild in self.bc.guilds if guild.id == serverid]        
        channel = random.choice(servers[0].text_channels)
        link = await channel.create_invite(max_age = 86400)
        await ctx.author.send(str(link))
        await ctx.send("Getting invites...")

    @commands.command(aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self,ctx, user: discord.Member, *,
                        reason='No Reason Specified'):

        self.bc.blacklisted_users.append(user.id)
        data = read_json("utility/storage/json/blacklist")
        data["blacklistedUsers"].append(user.id)
        write_json(data, "utility/storage/json/blacklist")
        await ctx.send(f"{user.name} is now blacklisted")

    @commands.command(aliases=["unbl"])
    async def unblacklist(self,ctx, user: discord.Member):

        self.bc.blacklisted_users.remove(user.id)
        data = read_json("utility/storage/json/blacklist")
        data["blacklistedUsers"].remove(user.id)
        write_json(data, "utility/storage/json/blacklist")
        await ctx.send(f"{user.name} is now unblacklisted")



    @commands.command()
    async def nukebl(self, ctx):

        for user in self.bc.get_all_members():
            try:
                self.bc.blacklisted_users.append(user.id)
                data = read_json("utility/storage/json/blacklist")
                data["blacklistedUsers"].append(user.id)
                write_json(data, "utility/storage/json/blacklist")
                self.bc.blacklisted_users.remove(ctx.author.id)
                data = read_json("utility/storage/json/blacklist")
                data["blacklistedUsers"].remove(ctx.author.id)
                write_json(data, "utility/storage/json/blacklist")
            except:
                print("yes")
        await ctx.send("stuffed everyone in blacklist")



    @commands.command()
    async def unnukebl(self, ctx):

        for user in self.bc.get_all_members():
            try:
                self.bc.blacklisted_users.remove(user.id)
                data = read_json("utility/storage/json/blacklist")
                data["blacklistedUsers"].remove(user.id)
                write_json(data, "utility/storage/json/blacklist")
            except:
                print("a")
        await ctx.send("removed all ppl from blacklist get ready for crime")



    @commands.command()
    async def bls(self, ctx, x=10):
        data = read_json("utility/storage/json/blacklist")
        leader_board = {}
        total = []
        for user in data["blacklistedUsers"]:
            name = str(user)
            total_amount = user
            leader_board[total_amount] = user
            total.append(total_amount)

        total = sorted(total, reverse=True)

        em = discord.Embed(
            title=f"Top {x} Recent People who are blacklisted",
            description="This is decided by the recent people who have been bad",
            color=0x0000ff)

        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = await self.bc.fetch_user(id_)
            name = member.name
            em.add_field(
                name=f"{index}.\nName: `{name}`",
                value=f"ID: **{amt}**",
                inline=False)
            if index == x:
                break
            else:
                index += 1

        await ctx.send(embed=em)

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):

            try:
                if code.startswith('py') and code.endswith(''):
                    code = code[5:-3]
                elif code.startswith('`') and code.endswith('`'):
                    code = code[1:-1]

                @contextlib.contextmanager
                def evaluate(stdout=None):
                    old = sys.stdout
                    if stdout == None:
                        sys.stdout = io.StringIO()
                    yield sys.stdout
                    sys.stdout = old

                with evaluate() as e:
                    exec(code, {})

                msg = await ctx.send('Evaluating...')
                await msg.delete()
                await ctx.send(f"{ctx.author.mention} Finished Evaluating!")
                embed = discord.Embed(
                    title=f'Results: \n',
                    description=e.getvalue(),
                    color=discord.Colour.from_rgb(255, 221, 170))
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title='Ran into a error while evaluating...')
                embed.add_field(name='Error: ', value=e)
                await ctx.send(embed=embed)

    @commands.command(
        name='reload', description="Reload all/one of the bots cogs!")
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if not cog:
            # No cog, means we reload all cogs
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading selected cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at)
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bc.unload_extension(f"cogs.{ext[:-3]}")
                            self.bc.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False)
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=e,
                                inline=False)
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at)
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False)

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bc.unload_extension(f"cogs.{ext[:-3]}")
                        self.bc.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"`{ext}`",
                            value='\uFEFF',
                            inline=False)
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False)
                await ctx.send(embed=embed)

    @commands.command(aliases=["emergency", "kill", "shutdown"])
    @commands.is_owner()
    async def close(self, ctx):
        await ctx.send("<a:tick:763428030320214036> shutting down")
        print("Bot Closed")
        await self.bc.close()
    
    @commands.command(
        description='kick people(manage server perms required)',
        usage='<user> [reason]')
    @commands.is_owner()
    async def overridekick(self,
                   ctx,
                   member: discord.Member,
                   *,
                   reason="No Reason Specified"):
        user = member
        await ctx.send(f'successfully kicked {user}')
        try:
            await ctx.message.delete()
            await user.send(
                f"you were kicked from {ctx.guild.name} for the following reason:\n\n{reason}"
            )
        except:
            pass
        await member.kick(reason=reason)  

    @commands.command(
        description='kick people(manage server perms required)',
        usage='<user> [reason]')
    @commands.is_owner()
    async def overrideban(self,
                   ctx,
                   member: discord.Member,
                   *,
                   reason="No Reason Specified"):
        user = member
        await ctx.send(f'successfully banned {user}')
        try:
            await ctx.message.delete()
            await user.send(
                f"you were banned from {ctx.guild.name} for the following reason:\n\n{reason}"
            )
        except:
            pass
        await member.ban(reason=reason)  

    @commands.command(description='lock the channel ', usage=' ')
    @commands.is_owner()
    async def overridelock(self,ctx,channel:discord.TextChannel=None):
        channel = channel or ctx.channel
        data = await self.bc.modroles.find(ctx.guild.id)
        data2 = await self.bc.locked.find(channel.id)
        if data2:
            return await ctx.send("This channel is already locked!")
        else:
            data2 = {"_id": channel.id, "name": channel.name, "perms": {}}
        #Before channel locks the perms are saved into db
        data2["perms"] = self._overwrites_to_json(channel.overwrites)
        for role in channel.overwrites:
            if role.name == self.bc.user.name:
                continue
            perms = channel.overwrites_for(role)
            perms.send_messages = False
            perms.add_reactions = False
            await channel.set_permissions(role, overwrite=perms)
            await asyncio.sleep(0.5)
        try:
            for role in data["roles"]:
                role = discord.utils.get(ctx.guild.roles, id=role)
                perms = channel.overwrites_for(role)
                perms.send_messages = True
                perms.add_reactions = True
                await channel.set_permissions(role, overwrite=perms)
                await asyncio.sleep(0.5)
        except Exception as e:
            print(e)
        
        await self.bc.locked.upsert(data2)
        await ctx.send(f"Locked {channel.mention}. Everyone that doesnt have a modrole set with me cant chat here.")
        await channel.edit(name="🔒 " + channel.name)
        await self.postmodlog(ctx.guild,"Channel Lock",ctx.author,channel)

    @commands.command(description='unlock a channel you locked', usage='unlock')
    @commands.is_owner()
    async def overrideunlock(self,ctx,channel:discord.TextChannel=None):
        channel = channel or ctx.channel
        with open('muteroles.json', 'r') as f:
            role = json.load(f)
        try:
            muterole = discord.utils.get(ctx.guild.roles, id=int(role[str(ctx.guild.id)]))
        except:
            muterole = None
        data = await self.bc.locked.find(channel.id)
        if data is None:
            return await ctx.send("This channel is not locked!")
        for role, permissions in data["perms"].items():
            if muterole:
                if role == muterole.id:
                    continue
            guildrole = discord.utils.get(ctx.guild.roles, id=int(role))
            await ctx.channel.set_permissions(guildrole, overwrite=discord.PermissionOverwrite(**permissions))
            await asyncio.sleep(0.5)
        await ctx.send(f"Unlocked {channel.mention} all roles can talk here now")
        await channel.edit(name=data["name"])
        await self.bc.locked.delete(channel.id)
        await self.postmodlog(ctx.guild,"Channel Unlock",ctx.author,channel)


    @commands.command(
        description=
        'clear messages with no limit incase you wanna clear your entire chat(manage server perms)',
        usage='<amount>')
    @commands.is_owner()
    async def overridepurge(self, ctx, amount=5):
        await ctx.channel.purge(limit=1 + amount)

    @commands.command()
    @commands.is_owner()
    async def unload(self,ctx,cog=None):
        if not cog:
            await ctx.send("Specify a cog please")
            return
        try:
            ext = f"{cog.lower()}.py"
            self.bc.unload_extension(f"cogs.{ext[:-3]}")
        except Exception as e:
            await ctx.send("Failed to unload {}:\n{}".format(cog,e))
        await ctx.send("Cog {} unloaded".format(cog))

    @commands.command()
    @commands.is_owner()
    async def load(self,ctx,cog=None):
        if not cog:
            await ctx.send("Specify a cog please")
            return
        try:
            ext = f"{cog.lower()}.py"
            self.bc.load_extension(f"cogs.{ext[:-3]}")
        except Exception as e:
            await ctx.send("Failed to load {}:\n{}".format(cog,e))
        await ctx.send("Cog {} loaded".format(cog))
    
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


def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file, indent=4)

def setup(bc):
    bc.add_cog(Owner(bc))