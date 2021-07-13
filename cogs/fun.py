import discord
import re
from discord.ext import commands, tasks
import asyncio
import random
from random import choice
from discord.ext.commands import cooldown, BucketType
from PIL import Image, ImageDraw, ImageOps, ImageFont
import textwrap
import json
import sys
import time
import asyncpraw
import datetime
#praw = ""
reddit = asyncpraw.Reddit(client_id="Ip5v-geI7BuIUw",
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
        subreddit = await reddit.subreddit("kidsarefuckingstupid")
        top = subreddit.top(limit=500)
        self.subs.clear()
        async for submission in top:
            self.subs.append(submission)
        self.bc.gettingmemes = False

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
            
    @commands.command(description="Let's see how fast you can get the cookie")
    async def cookie(self,ctx):
        embed=discord.Embed(
            title="Catch The Cookie!",
            description="In 5 seconds I will react to this message with a cookie and you have to react as fast as you can!"
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await msg.add_reaction("🍪")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "🍪"
        try:
            start = time.perf_counter()
            reaction, user = await self.bc.wait_for('reaction_add', timeout=30, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("This message has timed out!")
        else:
            end = time.perf_counter()
            await ctx.send("**{}** has caught the cookie in {} seconds!".format(ctx.author, (round((end - start) * 100)) / 100))


    @commands.command(description="Test how fast you can type")
    async def wpm(self,ctx):
        All_Adjectives = ["The fierce", "The obedient", "The skinny", "The delicious", "The damaged", "The heavy", "The aquatic", "The ancient", "The chivalrous", "The cowardly", "The anxious", "The deranged", "The draconian", "The evanescent", "The quick", "The scaled", "The furry", "The wet", "The dry", "The dark blue", "The French", "The illegal", "The suspicious", "The fresh", "The German", "An arctic", "An ordinary", "The salty", "A dirty", "The loud", "The young", "The colossal", "The fat", "The mysterious", "The silly", "The powerful", "The rich", "The oily", "The poisonous", "The venomous", "The chocolate", "The cold", "The chaotic", "The lawful", "The good", "The evil", "The motivated", "The undead"]
        All_Subjects = ["kitten", "salmon", "knight", "teacher", "bear", "doctor", "fox", "tapir", "phoenix", "lawyer", "warlock", "dragon", "sheep", "judge", "barrel", "demon", "orc","inspector", "detective", "attorney", "prosecutor", "man", "teenager", "woman", "boy", "girl", "jackal", "ghost", "moth", "pancake", "pan cake", "paladin", "policeman", "samurai", "explorer", "traitor", "king", "queen", "animal", "goldfish", "zombie", "mummy", "witch", "cheerleader", "conductor", "priest", "alien", "god", "deity", "chicken", "butler", "monk"]
        All_Adverbs = ["quickly", "slowly", "angrily", "gracefully", "hungrily", "fortunately", "cautiously", "foolishly", "stealthily", "weakly", "silently", ]
        All_Verbs = ["ate", "stole", "bit into", "walked into", "left", "jumped over", "pet", "jumped into", "bought", "remembered", "followed", "talked to", "punched", "kissed", "threw", "drank out of", "voted for", "discovered", "watched", "created", "healed", "was eaten by",]
        All_Objects = ["the volcano", "the mall", "the apartment", "the jail cell", "the burger", "the pizza", "the capybara", "the candlestick", "the airplane", "the mansion", "the dungeon", "the scythe", "the baguette", "the ghost", "the cupcake", "the bowl of peas", "the snake", "the pearl", "the priest"]
        All_Punctuation = [".", "!", ]

        Adjective = random.choice(All_Adjectives)
        Subject3 = random.choice(All_Subjects)
        Adverby = random.choice(All_Adverbs)
        Verb = random.choice(All_Verbs)
        Object1 = random.choice(All_Objects)
        Punctuation = random.choice(All_Punctuation)
        offset = margin = 60
        font = ImageFont.truetype("abel-regular.ttf", 45)
        im = Image.new("RGB", (720, 420), (0, 0, 0))
        text = "{} {} {} {} {}{}".format(Adjective, Subject3, Adverby, Verb, Object1, Punctuation)
        draw = ImageDraw.Draw(im)
        textwrapped = textwrap.wrap(text, width=35)
        draw.text((offset,margin), "\n".join(textwrapped), font=font, fill="#ffffff")
        im.save("images/words.png")
        await ctx.send(file=discord.File("images/words.png"))
        await ctx.send("**You must type exactly as it is said on the image. You have 60 seconds**")
        def check(msg):
            return msg.author == ctx.author
        try:
            start = time.perf_counter()
            msg = await self.bc.wait_for("message", check=check, timeout=60)
            if msg.content == text:
                end = time.perf_counter()
                embed = discord.Embed(
                    title="Stats",
                    description=f"**Time upon completion:** {end - start}\n**Words Per Minute:** {5 / (end - start) * 60}"
                )
                return await ctx.send("You have completed the sentence correctly!", embed=embed)
            else:
                return await ctx.send("You did not enter the right sentence!")
        except asyncio.TimeoutError:
            return await ctx.send("You have run out of time!")

    @commands.command(
        name="8ball",
        aliases=['eightball'],
        description="ask the danepai gods anything with your magik 8ball",
        usage='<question>')
    @cooldown(1, 5, BucketType.user)
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
        if self.bc.gettingmemes:
            return await ctx.send("Sorry but the memes are still loading! Try again later!")
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
