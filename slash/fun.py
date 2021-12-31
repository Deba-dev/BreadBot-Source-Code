import discord
import re
from discord import commands as slash
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

class MemeView(discord.ui.View):
    def __init__(self,ctx,memes):
        self.ctx = ctx
        self.bc = ctx.bot
        self.memes = memes
        super().__init__()

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stopmeme(self,button,interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot interact with this!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        self.stop()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Next Meme", style=discord.ButtonStyle.success)
    async def nextmeme(self,button,interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot interact with this!", ephemeral=True)
        meme = random.choice(self.memes)

        name=meme.title
        url=meme.url
        em = discord.Embed(
            color=random.choice(self.bc.color_list),
            description=f"**[{name}]({url})**"
        )
        em.set_image(url=url)
        await interaction.response.edit_message(embed=em)

class FunSlash(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.subs = []
        self.meme_task = self.refresh_memes.start()

    def cog_unload(self):
        self.meme_task.cancel()

    @slash.command(
        description="Mutes you for an amount of time!",
        usage='[time]'
    )
    async def selfmute(self, ctx,*, time: TimeConverter=None):
        with open('utility/storage/json/muteroles.json', 'r') as f:
            channel = json.load(f)
        member = ctx.author
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(channel[str(ctx.guild.id)]))
        except KeyError:
            await ctx.respond("No muted role was found! Please set one with the muterole command")
            return


        try:
            if self.bc.muted_users[member.id]:
                await ctx.respond("This user is already muted")
                return
        except KeyError:
            pass


        await ctx.respond("Are you sure you want to mute yourself?\nThis action is irreversable unless a mod decides to unmute you\n\nThis message will time out in 30 seconds. Reply with yes or no")
        def check(z):
            return z.author == ctx.author and z.channel == ctx.channel
        msg = await self.bc.wait_for('message', check=check, timeout = 30)
        if msg.content.lower() == "yes":
            data = {
                '_id': member.id,
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
                await ctx.respond(
                    f"Muted {member.display_name} for {hours} hours, {minutes} minutes and {seconds} seconds"
                )
                await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=f"{hours} hours, {minutes} minutes and {seconds} seconds")
            elif int(minutes):
                await ctx.respond(
                    f"Muted {member.display_name} for {minutes} minutes and {seconds} seconds"
                )
                await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=f"{minutes} minutes and {seconds} seconds")
            elif int(seconds):
                await ctx.respond(f"Muted {member.display_name} for {seconds} seconds")
                await self.postmodlog(ctx.guild,"Mute",ctx.author,ctx.channel,member=member,duration=f"{seconds} seconds")
        else:
            await ctx.respond("Aborting...")
            return

    @tasks.loop(minutes=60)
    async def refresh_memes(self):
        subreddit = await reddit.subreddit("memes")
        top = subreddit.top(limit=500)
        self.subs.clear()
        async for submission in top:
            self.subs.append(submission)
        self.bc.gettingmemes = False

    @refresh_memes.before_loop
    async def before_refresh_memes(self):
        await self.bc.wait_until_ready()

    @slash.command(hidden=True)
    async def mock(self,ctx,*,words):
        formated = [letters for letters in words]
        final = ""
        for i in formated:
            mock = random.randrange(0,50)
            if mock < 25:
                final += i.lower()
            else:
                final += i.upper()
        await ctx.respond(final)
            
    @slash.command(description="Let's see how fast you can get the cookie")
    async def cookie(self,ctx):
        embed=discord.Embed(
            title="Catch The Cookie!",
            description="In 5 seconds I will react to this message with a cookie and you have to react as fast as you can!"
        )
        msg = await ctx.respond(embed=embed)
        await asyncio.sleep(5)
        await msg.add_reaction("🍪")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "🍪"
        try:
            start = time.perf_counter()
            reaction, user = await self.bc.wait_for('reaction_add', timeout=30, check=check)
        except asyncio.TimeoutError:
            return await ctx.respond("This message has timed out!")
        else:
            end = time.perf_counter()
            await ctx.respond("**{}** has caught the cookie in {} seconds!".format(ctx.author, (round((end - start) * 100)) / 100))


    @slash.command(description="Test how fast you can type")
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
        font = ImageFont.truetype("utility/fonts/abel-regular.ttf", 45)
        im = Image.new("RGB", (720, 420), (0, 0, 0))
        text = "{} {} {} {} {}{}".format(Adjective, Subject3, Adverby, Verb, Object1, Punctuation)
        draw = ImageDraw.Draw(im)
        textwrapped = textwrap.wrap(text, width=35)
        draw.text((offset,margin), "\n".join(textwrapped), font=font, fill="#ffffff")
        im.save("utility/storage/images/words.png")
        await ctx.respond(file=discord.File("utility/storage/images/words.png"))
        await ctx.respond("**You must type exactly as it is said on the image. You have 60 seconds**")
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
                return await ctx.respond("You have completed the sentence correctly!", embed=embed)
            else:
                return await ctx.respond("You did not enter the right sentence!")
        except asyncio.TimeoutError:
            return await ctx.respond("You have run out of time!")

    @slash.command(
        name="8ball",
        aliases=['eightball'],
        description="ask the bread gods anything with your magik 8ball",
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
        await ctx.respond(
            f'Question: {question}\nAnswer: {random.choice(responses)}')

    @slash.command(
        description='fake ban people and prank',
        usage='<person>')
    async def fban(self, ctx, person):
      await ctx.respond(f'{person} was banned by <@{ctx.author.id}>')
          
    @slash.command(
        description="get some fresh memes",
        usage=" "
    )
    async def meme(self,ctx):
        if self.bc.gettingmemes:
            return await ctx.respond("Sorry but the memes are still loading! Try again later!")
        meme = random.choice(self.subs)

        name=meme.title
        url=meme.url
        em = discord.Embed(
            color=random.choice(self.bc.color_list),
            description=f"**[{name}]({url})**"
        )
        em.set_image(url=url)
        await ctx.respond(embed=em, view=MemeView(ctx,self.subs))


    @slash.command(
      description='make an embed', usage=' '
    )
    async def embed(self, ctx):
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        embed = discord.Embed()
        _ = await ctx.respond("What do you want your embed title to be?")
        _ = await _.original_message()
        try:
            msg = await self.bc.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("You didnt respond in time!")
        else:
            embed.title = msg.content
        await _.delete()

        _ = await ctx.send("What do you want your embed description to be?")
        try:
            msg = await self.bc.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("You didnt respond in time!")
        else:
            embed.description = msg.content
        await _.delete()

        _ = await ctx.send("What do you want your embed footer to be?")
        try:
            msg = await self.bc.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("You didnt respond in time!")
        else:
            await _.delete()
            _ = await ctx.send("What do you want your footer image to be? Respond with `none` to set no image")
            try:
                _msg = await self.bc.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("You didnt respond in time!")
            else:
                if _msg.content.lower() != "none":
                    pass
                else:
                    embed.set_footer(text=msg.content, icon_url=_msg.content)
            await _.delete()
            embed.set_footer(text=msg.content)

        _ = await ctx.send("What do you want your embed fields to be? Use this format: Title//Value//Inline or Title//Value. For the inline either put true or false. And then respond with `done` when you want to finish")
        while True:
            try:
                msg = await self.bc.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("You didnt respond in time!")
            else:
                if msg.content == "done":
                    break
                formatted = msg.content.split("//")
                if len(formatted) > 2:
                    embed.add_field(name=formatted[0], value=formatted[1], inline=True if formatted[2].lower() == "true" else False) 
                embed.add_field(name=formatted[0], value=formatted[1])
        await _.delete()

        _ = await ctx.send("What do you want your embed color to be? Use hex code format or say `none` to not set a color")
        try:
            msg = await self.bc.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("You didnt respond in time!")
        else:
            embed.color = int(msg.content.replace("#", "0x"), 16) if not msg.content.lower() == "none" else discord.Embed.Empty
        await _.delete()

        await ctx.send(embed=embed)

def setup(bc):
    bc.add_cog(FunSlash(bc))
