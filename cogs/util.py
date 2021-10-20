import discord
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType
import json
import datetime
import time
import sys
import random
import traceback
import io
import re
import contextlib
import textwrap
from traceback import format_exception
import math
from random import choice
from captcha.image import ImageCaptcha
import asyncio
from googletrans import Translator
from copy import deepcopy
from dateutil.relativedelta import relativedelta
image = ImageCaptcha()
translator = Translator()

def convert_size(bytes):
    if bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

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

class Utility(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.RemindTask = self.checkReminders.start()

    def cog_unload(self):
        self.RemindTask.cancel()

    @tasks.loop(seconds=1)
    async def checkReminders(self):
        heist = deepcopy(self.bc.remindData)
        for key, value in heist.items():
            try:
                member = value["_id"]
                member = self.bc.get_user(member)
                message = value["reminder"]
                remindTime = value['startedat'] + relativedelta(seconds=value['duration'])
                currentTime = datetime.datetime.now()
                if currentTime >= remindTime:
                    try:
                        await member.send("I am reminding you: **{}**".format(message))
                    except:
                        await self.bc.reminders.delete(member.id)
                        try:
                            self.bc.remindData.pop(member.id)
                        except KeyError:
                            pass
                    else:
                        await self.bc.reminders.delete(member.id)
                        try:
                            self.bc.remindData.pop(member.id)
                        except KeyError:
                            pass
            except:
                continue

    @commands.command()
    async def remind(self,ctx,time: TimeConverter, *, reminder):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if int(d) == 0 and int(h) == 0 and int(m) == 0:
            duration = f"{int(s)} seconds"
        elif int(d) == 0 and int(h) == 0 and int(m) != 0:
            duration = f"{int(m)} minutes {int(s)} seconds"
        elif int(d) == 0 and int(h) != 0 and int(m) != 0:
            duration = f"{int(h)} hours, {int(m)} minutes and {int(s)} seconds"
        elif int(d) != 0 and int(h) != 0 and int(m) != 0:
            duration = f"{int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds"
        else:
            duration = f"{int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds"
        data = {
            "_id": ctx.author.id,
            'duration': time,
            'startedat': datetime.datetime.now(),
            'reminder': reminder
        }
        await self.bc.reminders.upsert(data)
        remindTime = data['startedat'] + relativedelta(seconds=data['duration'])
        await ctx.send("Ok! I shall remind you <t:{}:R>".format(int(remindTime.timestamp())))
        self.bc.remindData[ctx.author.id] = data

    @commands.command(description="Translate words")
    async def translate(self, ctx, *, word):
        result = translator.translate(word, dest="en")
        em = discord.Embed(
            title="Translator Results",
            description="**Result:** {}\n**Source Language:** {}".format(result.text, result.src)
        )
        await ctx.send(embed=em)

    @commands.command(description="Redo a command instead of typing it out again by replying to the message you want to redo")
    async def re(self,ctx):
        await self.bc.process_commands(ctx.message.reference.cached_message)

    @commands.command(hidden=True)
    async def cap(self,ctx):
        characters = "abcdefghijklmnopqrstuvwxyz1234567890"
        filtered = []
        final = []
        real = ""
        for x in characters:
            filtered.append(x)
        for i in range(5):
            letter = random.randrange(0,len(filtered))
            final.append(filtered[letter])
        for z in final:
            real += str(z)
        data = image.generate(real)
        image.write(real,"captcha.png")
        await ctx.send(file=discord.File('captcha.png'))
        def check(z):
            return z.author == ctx.author and z.channel == ctx.channel
        try:
            msg2 = await self.bc.wait_for('message', check=check, timeout=30)
            if msg2.content.lower() == str(real):
                await ctx.send("Captcha correct")
            else:
                await ctx.send("wrong")
        except asyncio.TimeoutError:
            await ctx.send("out of time")

    @commands.group(name="tag", description="Make custom commands for your server",invoke_without_command=True)
    async def tag(self,ctx,tag=None):
        if not tag:
            return await ctx.invoke(self.bc.get_command("help"), entity="tag")
        data = await self.bc.tags.find(ctx.guild.id)
        if not data:
            return await ctx.send("There are no tags for this server!")
        try:
            await ctx.send(data["tags"][tag]["content"])
        except:
            return await ctx.send("That tag doesnt exist!")
        
    
    @tag.command(name="create",description="create a tag")
    async def tag_create(self,ctx,name,*,content:commands.clean_content):
        data = await self.bc.tags.find(ctx.guild.id)
        if data is None:
            data = {"_id": ctx.guild.id, "tags":{}}
        if name in data["tags"].keys():
            return await ctx.send("That tag already exists!")
        data["tags"][name] = {}
        data["tags"][name]["content"] = content
        data["tags"][name]["author"] = str(ctx.author.id)
        await self.bc.tags.upsert(data)
        await ctx.send("Tag Created")

    @tag.command(name="edit",description="edit a tag")
    async def tag_edit(self,ctx,name,*,content:commands.clean_content):
        data = await self.bc.tags.find(ctx.guild.id)
        if data is None:
            data = {"_id": ctx.guild.id, "tags":{}}
        try:
            tag = data["tags"][name]
        except KeyError:
            return await ctx.send("That tag doesnt exist!")
        if tag["author"] != str(ctx.author.id):
            return await ctx.send("You dont own this tag!")
        data["tags"][name]["content"] = content
        await self.bc.tags.upsert(data)
        await ctx.send("Tag Edited")

    @tag.command(name="delete",description="delete a tag")
    async def tag_delete(self,ctx,name=None):
        if not name:
            return await ctx.send("Specify a tag!")
        data = await self.bc.tags.find(ctx.guild.id)
        if not data:
            return await ctx.send("There are no tags for this server!")
        try:
            tag = data["tags"][name]
        except KeyError:
            return await ctx.send("That tag doesnt exist!")
        if tag["author"] != str(ctx.author.id):
            return await ctx.send("You dont own this tag!")
        data["tags"].pop(name)
        await self.bc.tags.upsert(data)
        await ctx.send("Tag Deleted")

    @tag.command(name="owner", description="find the owner of a tag")
    async def tag_owner(self,ctx,name=None):
        if not name:
            return await ctx.send("Specify a tag!")
        data = await self.bc.tags.find(ctx.guild.id)
        if not data:
            return await ctx.send("There are no tags for this server!")
        try:
            member = await self.bc.fetch_user(data["tags"][name]["author"])
            em = discord.Embed(
                title = f"Tag owner of {name}",
                color = random.choice(self.bc.color_list)
            )
            em.set_thumbnail(url=member.avatar)
            em.add_field(name="Owner",value=member.mention)
            await ctx.send(embed=em)
        except:
            return await ctx.send("That tag doesnt exist!")

    @commands.command(description="Look at the tags your server")
    async def tags(self,ctx):
        data = await self.bc.tags.find(ctx.guild.id)
        if not data:
            return await ctx.send("There are no tags for this server!")
        tags = [f"**{tag}**" for tag in data["tags"]]
        await ctx.send("\n".join(tags))

    @commands.command(name="calc", aliases=["calculator", "calculate"],usage="<equation>")
    async def _calc(self,ctx, *, equation=None):
        if not equation:
            return await ctx.send("Specify an equation!")
        local_variables = {}

        stdout = io.StringIO()

        try:
            calc = equation
            calc = calc.replace("^","**")
            calc = calc.replace("x", "*")
            calc = clean_code(calc)
            filtcode = f"print({calc})"
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"from math import sin, cos, tan, pi\nfrom fractions import Fraction as f2d\nasync def func():\n{textwrap.indent(filtcode, '    ')}", local_variables,
                )
                
                await local_variables["func"]()
                result = f"{stdout.getvalue()}"
        except Exception as e:
            result = "An Error Occurred! Make sure you entered numbers correctly"
            #await ctx.send(format_exception(e, e, e.__traceback__))
        em = discord.Embed(
            title=f"Calculating {equation}...",
            description=f"Answer:\n```{result}```",
            color = random.choice(self.bc.color_list)
        )
        em.set_footer(text="Calculator 2.0")
        await ctx.send(embed=em)


    @commands.command(
        description="count characters in a message you give the bot",
        usage="<words>"
    )
    async def countchars(self,ctx,*,args):
        chars = 0
        charsnospace = 0
        spaces = 0
        for x in args:
            chars += 1
            if x != " ":
                charsnospace += 1
            elif x == " ":
                spaces += 1
        em=discord.Embed(
            title="Character Counter",
            description="Characters: {}\nCharacters without spaces: {}\nSpaces: {}".format(chars,charsnospace,spaces),
            color=random.choice(self.bc.color_list),
            timestamp=datetime.datetime.utcnow()
        )
        await ctx.send(embed=em)

    @commands.command(description="Go afk", usage="[reason]")
    async def afk(self,ctx,*,reason=None):
        try:
            await ctx.author.edit(nick='[AFK] '+ ctx.author.display_name)
        except:
            await ctx.send("I have set your afk but could not change your nickname")
        await ctx.send(ctx.author.mention + " I have set your afk: "+ str(reason), allowed_mentions=discord.AllowedMentions.none())
        data = await self.bc.afk.find(ctx.guild.id)
        if not data:
            data = {"_id": ctx.guild.id, "members": {}}
        if str(ctx.author.id) not in data["members"].keys():
            data["members"][str(ctx.author.id)] = {}
            data["members"][str(ctx.author.id)]["reason"] = str(reason)
        await self.bc.afk.upsert(data)
    
    @commands.Cog.listener()
    async def on_message(self,msg):
        if not msg.guild:
            return
        data = await self.bc.afk.find(msg.guild.id)
        if not data:
            return
        if msg.author.bot:
            return
        for user in msg.mentions:
            if str(user.id) in data["members"].keys():
                await msg.channel.send("This user is afk: {}".format(data["members"][str(user.id)]["reason"]), allowed_mentions=discord.AllowedMentions.none())
                break
        if str(msg.author.id) in data["members"].keys():
            await msg.channel.send("Welcome Back! I have taken your afk from you!")
            data["members"].pop(str(msg.author.id))
            try:
                await msg.author.edit(nick=msg.author.display_name.replace("[AFK] ", ""))
            except:
                pass
            await self.bc.afk.upsert(data)

    @commands.command(
        description="make the bot generate a password for u in dms",
        usage="[amt of letters]"
    )
    async def password(self,ctx,amt=5):
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-_=+[{]}|;:,<.>/?`~"
        formated = []
        final = ""
        for x in characters:
            formated.append(x)
        for i in range(amt):
            rand = random.randint(0,len(formated) - 1)
            final += formated[rand]
        em=discord.Embed(
            title="Generated Password",
            description=f"```{final}```"
        )
        await ctx.author.send(embed=em)
        await ctx.send("I have dmed you your generated password")

    @commands.command(
        description="get the last deleted message in your server",
        usage=""
    )
    async def snipe(self,ctx):
        with open('utility/storage/json/snipe.json', 'r') as f:
            snipe = json.load(f)
        message = snipe[str(ctx.guild.id)]["content"]
        author = snipe[str(ctx.guild.id)]["author"]
        avatar = snipe[str(ctx.guild.id)]["avatar"]
        timedel = snipe[str(ctx.guild.id)]["timedelete"]
        timedel = datetime.datetime.strptime(timedel, '%Y-%m-%d %H:%M:%S.%f')
        em = discord.Embed(
            description=f"{message}",
            color=random.choice(self.bc.color_list),
            timestamp=timedel
        )
        em.set_author(name=author, icon_url=avatar)
        await ctx.send(embed=em)

    @commands.command(
      name='ping', description='shows bot latency', usage=' '
    )
    @cooldown(1, 5, BucketType.user)
    async def ping(self, ctx):
        counter = 0 
        msg = await ctx.send("Getting Bot Ping...")
        em = discord.Embed(
            title="Bot Latency",
            color = random.choice(self.bc.color_list)
        )
        speeds = []
        for i in range(3):
            counter += 1
            start = time.perf_counter()
            await msg.edit(content="Testing how long it gets from here to discord hq {}/3".format(counter))
            end = time.perf_counter()
            speed = round((end - start) * 1000)
            speeds.append(speed)
            if speed < 150:
                em.add_field(name="Ping {}".format(counter), value=f"{speed}ms | Good")
            elif speed in range(150, 250):
                em.add_field(name="Ping {}".format(counter), value=f"{speed}ms | Medium")
            elif speed > 250:
                em.add_field(name="Ping {}".format(counter), value=f"{speed}ms | Bad")
        await msg.edit(content=f"`{speed}ms` Ping")
        em.add_field(name="Websocket Ping:",value=f"{round(self.bc.latency * 1000)}ms")
        sum = 0
        for speed in speeds:
            sum += speed
        average = sum / 3
        newaverage = int(average * 100)
        roundedavg = newaverage / 100
        em.add_field(name="Average Ping:", value=f"{roundedavg}ms")
        await msg.edit(embed=em)

def setup(bc):
  bc.add_cog(Utility(bc))