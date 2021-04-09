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
from io import BytesIO
import time
import datetime
from tools import commands2
from tools import hypixel
from tools.hypixel import Player, Skyblock,SkyblockPlayer

hypixel.setkey("e411c189-0633-4ad0-9493-f4f902353bd3")

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

    @commands.group(invoke_without_command=True)
    async def changelogs(self,ctx):
        with open("changelogs.txt","r") as f:
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
        await save_audit_logs(ctx.guild)
        await ctx.send("Saved audit logs in a text file")
    
    @changelogs.command()
    async def add(self,ctx,version,*,notes):
        with open("changelogs.txt","w+") as f:
            f.write("""
**Version:** {}
**Notes:**
{}            
""".format(version,notes))
        self.bc.version = version
        await ctx.send("I have updated the changelogs!")

    @commands.command()
    async def hypixel(self,ctx,user):
        player = hypixel.Player(user)
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
        
    @skyblock.command(name="player")
    async def skyblock_player(self,ctx,user):
        player = SkyblockPlayer(user)
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
    
    @skyblock.command(name="banking")
    async def skyblock_banking(self,ctx,user):
        player = SkyblockPlayer(user)
        stats1 = player.getprofile()
        if stats1 is None:
            return await ctx.send("This player does not exist!")
        print(stats1.keys())

    @skyblock.group(invoke_without_command=True)
    async def bazaar(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="skyblock bazaar")
    
    @bazaar.command(name="item")
    async def bazaar_item(self,ctx,*,item):
        sb = Skyblock()
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
    async def toggle(self,ctx,command=None):
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
            'assprogram': "ass "*69,
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
        link = await channel.create_invite(max_age = 300)
        await ctx.author.send(str(link))
        await ctx.send("Getting invites...")

    @commands.command(aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self,ctx, user: discord.Member, *,
                        reason='No Reason Specified'):

        self.bc.blacklisted_users.append(user.id)
        data = read_json("blacklist")
        data["blacklistedUsers"].append(user.id)
        write_json(data, "blacklist")
        await ctx.send(f"{user.name} is now blacklisted")

    @commands.command(aliases=["pr"])
    @commands.is_owner()
    async def premium(self,ctx):
        data = await self.bc.premium.find(ctx.guild.id)
        if not data:
            data = {"id": ctx.guild.id}
            await self.bc.premium.upsert(data)
            await ctx.send("server is now premium")
        else:
            await ctx.send("this server is already premium")
            return

    @commands.command(aliases=["unpr"])
    @commands.is_owner()
    async def unpremium(self,ctx):
        data = await self.bc.premium.find(ctx.guild.id)
        if not data:
            await ctx.send("this server was never premium lol")
            return
        else:
            await self.bc.premium.delete_by_id(ctx.guild.id)
            await ctx.send("took premium from server")



    @commands.command(aliases=["unbl"])
    async def unblacklist(self,ctx, user: discord.Member):

        self.bc.blacklisted_users.remove(user.id)
        data = read_json("blacklist")
        data["blacklistedUsers"].remove(user.id)
        write_json(data, "blacklist")
        await ctx.send(f"{user.name} is now unblacklisted")



    @commands.command()
    async def nukebl(self, ctx):

        for user in self.bc.get_all_members():
            try:
                self.bc.blacklisted_users.append(user.id)
                data = read_json("blacklist")
                data["blacklistedUsers"].append(user.id)
                write_json(data, "blacklist")
                self.bc.blacklisted_users.remove(ctx.author.id)
                data = read_json("blacklist")
                data["blacklistedUsers"].remove(ctx.author.id)
                write_json(data, "blacklist")
            except:
                print("yes")
        await ctx.send("stuffed everyone in blacklist")



    @commands.command()
    async def unnukebl(self, ctx):

        for user in self.bc.get_all_members():
            try:
                self.bc.blacklisted_users.remove(user.id)
                data = read_json("blacklist")
                data["blacklistedUsers"].remove(user.id)
                write_json(data, "blacklist")
            except:
                print("a")
        await ctx.send("removed all ppl from blacklist get ready for crime")



    @commands.command()
    async def bls(self, ctx, x=10):
        data = read_json("blacklist")
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
            member = self.bc.fetch_user(id_)
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


    @commands.Cog.listener()
    async def on_message(self, message):
        data = await self.bc.prefixes.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = self.bc.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        if message.author.id == self.bc.user.id:
            return
        if message.author.id in self.bc.blacklisted_users:
            return
        if message.author != message.author.bot and not message.author.bot:
            if not message.guild and not message.content.startswith(prefix):
                await self.bc.get_guild(760950684849537124).get_channel(
                    760950866701320193
                ).send(
                    f'User `{message.author}` has sent a report saying: **{message.content}**'
                )
                await self.bc.process_commands(message)

        await self.bc.process_commands(message)
        if not message.guild:
            return

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

    @commands.command(description='lock the channel (manage channel perms needed)', usage=' ')
    @commands.is_owner()
    async def overridelock(self,ctx):
        data = await self.bc.modroles.find(ctx.guild.id)
        for role in ctx.guild.roles:
            await ctx.channel.set_permissions(role, send_messages=False)
        try:
            for role in data["roles"]:
                role = discord.utils.get(ctx.guild.roles, id=role)
                await ctx.channel.set_permissions(role, send_messages=True)
        except Exception as e:
            print(e)
        await ctx.send(f"Locked {ctx.channel.mention}. Eveyone that doesnt have a modrole set with me cant chat here.")

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
                


def read_json(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
    return data


def write_json(data, filename):
    with open(f"{filename}.json", "w") as file:
        json.dump(data, file, indent=4)

def setup(bc):
    bc.add_cog(Owner(bc))