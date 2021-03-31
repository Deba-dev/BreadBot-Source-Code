import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import random
from random import choice
import asyncio
from tools import words

class Games(commands.Cog):
    def __init__(self,bc):
        self.bc = bc


    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def decipher(self, ctx, opt='Easy'):
        options = ['easy', 'medium', 'hard', 'impossible']
        if not opt.lower() in options:
            await ctx.send('Give a valid difficulty.\n**Current Difficulties:**\n> `Easy` `Medium` `Hard` `Impossible`')
            return
        choice = opt.lower()
        if choice == 'easy':
            choice = random.choice(words.easy)
        elif choice == 'medium':
            choice = random.choice(words.medium)
        elif choice == 'hard':
            choice = random.choice(words.hard)
        elif choice == 'impossible':
            choice = random.choice(words.impossible)
        x = list(choice)
        random.shuffle(x)
        await ctx.send('**⬇ The word you must decipher is ⬇**')
        await ctx.send(' '.join(map(str, x)))
        def check(m):
            user = ctx.author
            if m.author.id == user.id and m.content.lower() == choice.lower():
                return True
            return False
        try:
            await self.bc.wait_for('message',timeout=30.0,check=check)
            await ctx.send(f'**Congratulations {ctx.author}! You got the correct word.**')
        except asyncio.TimeoutError:
            await ctx.send('Your answer is **INCORRECT!**')
            await ctx.send(f'**The correct word was {choice}**')

def setup(bc):
    bc.add_cog(Games(bc))