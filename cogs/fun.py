import discord
import re
from discord.ext import commands, tasks
import random
from random import choice
from discord.ext.commands import cooldown, BucketType
import json
import sys
import time
import praw
from PIL import *
import datetime
#praw = ""
reddit = praw.Reddit(client_id="Ip5v-geI7BuIUw",
                     client_secret="5nWhsfqSFtjsMIEW5uf71WQO79DRUw",
                     user_agent="i just get memes",
                     check_for_async=False)

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

class Fun(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.subs = []
        self.meme_task = self.refresh_memes.start()

    def cog_unload(self):
        self.meme_task.cancel()

    @commands.command(
        description="Mutes you for an amount of time!",
        usage='[time]'
    )
    async def selfmute(self, ctx,*, time: TimeConverter=None):
        with open('muteroles.json', 'r') as f:
            channel = json.load(f)
        member = ctx.author
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
        except KeyError:
            await ctx.send("No muted role was found! Please set one with the muterole command")
            return


        try:
            if self.bc.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass


        await ctx.send("Are you sure you want to mute yourself?\nThis action is irreversable unless a mod decides to unmute you\n\nThis message will time out in 30 seconds. Reply with yes or no")
        def check(z):
            return z.author == ctx.author and z.channel == ctx.channel
        msg = await self.bc.wait_for('message', check=check, timeout = 30)
        if msg.content.lower() == "yes":
            data = {
                'id': member.id,
                'mutedAt': datetime.datetime.now(),
                'muteDuration': time or None,
                'mutedBy': ctx.author.id,
                'guildId': ctx.guild.id,
            }
            await self.bc.mutes.upsert(data)
            self.bc.muted_users[member.id] = data

            await member.add_roles(role)
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
        else:
            await ctx.send("Aborting...")
            return

    @tasks.loop(minutes=60)
    async def refresh_memes(self):
        subreddit = reddit.subreddit("crappydesign")
        top = subreddit.top(limit=500)
        self.subs.clear()
        for submission in top:
            self.subs.append(submission)

    @refresh_memes.before_loop
    async def before_refresh_memes(self):
        await self.bc.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(hidden=True)
    async def mock(self,ctx,*,words):
        formated = [letters for letters in words]
        final = ""
        for i in formated:
            mock = random.randrange(0,50)
            if mock < 25:
                final += i.lower()
            else:
                final += i.upper()
        await ctx.send(final)
            




    @commands.command(
        aliases=['eightball', '8ball'],
        description="ask the danepai gods anything with your magik 8ball",
        usage='<question>')
    @cooldown(1, 15, BucketType.user)
    async def _8ball_(self, ctx, *, question):
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "As I see it, yes.", "Most likely.",
            "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.",
            "Better not tell you now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        await ctx.send(
            f'Question: {question}\nAnswer: {random.choice(responses)}')

    @commands.command(
        description='Accidentally looked at something distrubing? use this command for the bot to give holy water',
        usage=' ')
    async def holywater(self,ctx):
      await ctx.send(file=discord.File('holy-water.png'))

    @commands.command(
        description='fake ban people and prank',
        usage='<person>')
    async def fban(self, ctx, person):
      await ctx.send(f'{person} was banned by <@{ctx.author.id}>')
      await ctx.message.delete()


    @commands.command(hidden=True)
    @cooldown(1, 10, BucketType.user)
    async def pp(self, ctx, user : discord.Member=None):
        if user == None:
            user = ctx.author
        else:
            pass
        pen = ['8D',
               '8=D',
               '8==D',
               '8===D',
               '8====D',
               '8=====D',
               '8======D',
               '8=======D',
               '8========D',
               '8=========D',
               '8==========D',
               '8===========D',
               '8============D',
               '8=============D',
               '8==============D',
               '8===============D']
        e = discord.Embed(title="", description="", color=0x50C878)
        e.add_field(name='**PP machine 5000**',
                    value=f'{user.display_name} pp size is:\n{random.choice(pen)}\n**Even my angel has a bigger one**', )
        await ctx.send(embed=e)
          
    @commands.command(
        description="get some fresh memes",
        usage=" "
    )
    async def meme(self,ctx):

        meme = random.choice(self.subs)

        name=meme.title
        url=meme.url
        em = discord.Embed(
            color=random.choice(self.bc.color_list),
            description=f"**[{name}]({url})**"
        )
        em.set_image(url=url)
        await ctx.send(embed=em)


    @commands.command(
      description='make an embed', usage=' '
    )
    async def embed(self, ctx):
        await ctx.send("what do you want the title to be")

        def check(x):
            return x.author == ctx.author

        msg1 = await self.bc.wait_for('message', check=check, timeout=30)

        await ctx.send("what do you want the desc to be")

        def check(z):
            return z.author == ctx.author

        msg2 = await self.bc.wait_for('message', check=check, timeout=30)

        await ctx.send("what do you want the field title to be")

        def check(z):
            return z.author == ctx.author

        msg3 = await self.bc.wait_for('message', check=check, timeout=30)

        await ctx.send("what do you want the desc of the field to be")

        def check(z):
            return z.author == ctx.author

        msg4 = await self.bc.wait_for('message', check=check, timeout=30)

        await ctx.send("what do you want the footer to have?")

        def check(z):
            return z.author == ctx.author

        msg5 = await self.bc.wait_for('message', check=check, timeout=30)

        await ctx.send("what do you want the color to be? just make sure you replace the # of the hex code with a 0x like 0xff0000")
        
        def check(z):
            return z.author == ctx.author

        msg6 = await self.bc.wait_for('message', check=check, timeout=30)
        em = discord.Embed(
          title=msg1.content, 
          description=msg2.content,
          color=int(msg6.content,16)
          )
        em.add_field(name=msg3.content, value=msg4.content)
        em.set_footer(text=msg5.content)
        await ctx.send(embed=em)
        

def setup(bc):
    bc.add_cog(Fun(bc))
