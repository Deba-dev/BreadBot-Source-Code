import discord
import json
from discord.ext import commands, tasks
from copy import deepcopy
import datetime
from dateutil.relativedelta import relativedelta
import asyncio
import random
from random import choice
from discord.ext.commands import cooldown, BucketType
import sqlite3
import sys
import time


class Economy(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.heists = self.checkHeist.start()
        self.mainshop = [{"name": "DaneEssence","price": 100000,"description": "essence of dane"},
        {"name": "Laptop","price": 5000,"description": "Use this for the postmeme command"},
        {"name": "DaneCoin","price": 1000000,"description": "flex money"},
        {"name": "fishingpole","price": 5000,"description": "get a chance to get a fish and sell it"}, 
        {"name": "fishy","price": 200,"description": "sell this"},
        {"name": "rifle","price": 10000,"description": "use this to hunt animals for a good price"}, 
        {"name": "dead_animal","price": 500,"description": "sell this"},
        {"name":"LootBox","price":None,"description":"Get this from each 10 levels you level up with cool stuff inside"}]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} Cog has been loaded\n-----")

    def cog_unload(self):
        self.heists.cancel()

    @tasks.loop(minutes=1)
    async def checkHeist(self):
        heist = deepcopy(self.bc.heistdata)
        for key, value in heist.items():
            member = value["id"]
            member = await self.bc.fetch_user(member)
            msg = value["messageId"]
            author = value['author']
            author = await self.bc.fetch_user(author)
            currentTime = datetime.datetime.now()
            guild = self.bc.get_guild(value['guildId'])
            channel = self.bc.get_channel(value['channelId'])
            ctx = discord.utils.get(guild.text_channels, id=value['channelId'])
            bal1 = await self.update_bank(member)
            new_msg = await channel.fetch_message(msg)
            lost = []
            win = []
            unmuteTime = value['started'] + relativedelta(
                seconds=value['duration'])
            bal = await self.update_bank(author)
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.bc.user))
            if currentTime >= unmuteTime:
                if len(users) < 10:
                    await ctx.send("Not enough users joined")
                    await self.bc.heists.delete(member.id)
                    try:
                        self.bc.heistdata.pop(member.id)
                    except KeyError:
                        pass
                    return
                for user in users:
                    bal = await self.update_bank(user)
                    if bal[0] < 1000:
                        pass
                    else:
                        chance = random.randrange(100)
                        if chance > 75:
                            lost.append(user)
                        else:
                            win.append(user)
                winings = bal1[1] / len(win)
                winings = int(winings)
                await self.update_bank(member, -1 * bal1[1], "bank")
                for user in win:
                    await self.update_bank(user, winings)
                wins = ""
                for user in win:
                    wins += f"{user} won {winings} from the heist\n"
                loses = ""
                for user in lost:
                    wins += f"{user} lost the heist :(\n"
                em = discord.Embed(
                    title="Heist results on {}'s bank".format(member.name),
                    color=random.choice(self.bc.color_list),
                    description=wins)
                if len(loses) == 0:
                    pass
                else:
                    em.add_field(name="People who lost :(", value=loses)
                await self.bc.heists.delete(member.id)
                try:
                    self.bc.heistdata.pop(member.id)
                except KeyError:
                    pass
                await ctx.send(embed=em)

    @checkHeist.before_loop
    async def before_check_current_mutes(self):
        await self.bc.wait_until_ready()

    @commands.command(
        description='b l a c k j a c k', usage='<amount>', aliases=["bj"])
    async def blackjack(self, ctx, amount=None):
        await self.open_account(ctx.author)
        pcards = random.randrange(1, 20)
        bcards = random.randrange(1, 20)

        if amount == None:
            await ctx.send("please specify an amount")
            return

        bal = await self.update_bank(ctx.author)
        if amount == 'all':
            amount = bal[0]
        if amount == 'half':
            amount = bal[0] / 2

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        await self.update_bank(ctx.author, -1 * amount)

        em = discord.Embed(
            title=f"{ctx.author.name}'s blackjack game", color=0x0000ff)
        em.add_field(name=ctx.author.name, value=pcards)
        em.add_field(name='BreadBot', value='N/A')
        await ctx.send(
            'say `hit` to draw more cards and `stand` to end the game with your stack'
        )
        await ctx.send(embed=em)

        def check(z):
            return z.author == ctx.author and z.content == 'hit' or z.content == 'stand' or z.content == 'Hit' or z.content == 'Stand'

        msg2 = await self.bc.wait_for('message', check=check, timeout=30)
        if msg2.content == 'hit' or msg2.content == 'Hit':
            pcards2 = pcards + random.randrange(1, 10)
            if pcards2 > 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Busted!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards2)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            if pcards2 == 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You got to 21 before your opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards2)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return
            em = discord.Embed(
                title=f"{ctx.author.name}'s blackjack game", color=0x0000ff)
            em.add_field(name=ctx.author.name, value=pcards2)
            em.add_field(name='BreadBot', value='N/A')
            await ctx.send(
                'say `hit` to draw more cards and `stand` to end the game with your stack'
            )
            await ctx.send(embed=em)
        elif msg2.content == 'stand' or msg2.content == 'Stand':
            if pcards < bcards:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had Less Cards Than Your Opponent!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            else:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had More Cards Than Your Opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return

        def check(z):
            return z.author == ctx.author and z.content == 'hit' or z.content == 'stand' or z.content == 'Hit' or z.content == 'Stand'

        msg2 = await self.bc.wait_for('message', check=check, timeout=30)
        if msg2.content == 'hit' or msg2.content == 'Hit':
            pcards3 = pcards2 + random.randrange(1, 10)
            if pcards3 > 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Busted!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards3)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            if pcards3 == 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You got to 21 before your opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards3)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return
            em = discord.Embed(
                title=f"{ctx.author.name}'s blackjack game", color=0x0000ff)
            em.add_field(name=ctx.author.name, value=pcards3)
            em.add_field(name='BreadBot', value='N/A')
            await ctx.send(
                'say `hit` to draw more cards and `stand` to end the game with your stack'
            )
            await ctx.send(embed=em)
        elif msg2.content == 'stand' or msg2.content == 'Stand':
            if pcards2 < bcards:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had Less Cards Than Your Opponent!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards2)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            else:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had More Cards Than Your Opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards2)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return

        def check(z):
            return z.author == ctx.author and z.content == 'hit' or z.content == 'stand' or z.content == 'Hit' or z.content == 'Stand'

        msg2 = await self.bc.wait_for('message', check=check, timeout=30)
        if msg2.content == 'hit' or msg2.content == 'Hit':
            pcards4 = pcards3 + random.randrange(1, 10)
            if pcards4 > 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Busted!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards4)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            if pcards4 == 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You got to 21 before your opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards4)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return
            em = discord.Embed(
                title=f"{ctx.author.name}'s blackjack game", color=0x0000ff)
            em.add_field(name=ctx.author.name, value=pcards4)
            em.add_field(name='BreadBot', value='N/A')
            await ctx.send(
                'say `hit` to draw more cards and `stand` to end the game with your stack'
            )
            await ctx.send(embed=em)
        elif msg2.content == 'stand' or msg2.content == 'Stand':
            if pcards3 < bcards:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had Less Cards Than Your Opponent\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards3)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            else:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had More Cards Than Your Opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards3)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return

        def check(z):
            return z.author == ctx.author and z.content == 'hit' or z.content == 'stand' or z.content == 'Hit' or z.content == 'Stand'

        msg2 = await self.bc.wait_for('message', check=check, timeout=30)
        if msg2.content == 'hit' or msg2.content == 'Hit':
            pcards5 = pcards4 + random.randrange(1, 10)
            if pcards5 > 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Busted!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards5)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            if pcards5 == 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You got to 21 before your opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards5)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return
            em = discord.Embed(
                title=f"{ctx.author.name}'s blackjack game", color=0x0000ff)
            em.add_field(name=ctx.author.name, value=pcards5)
            em.add_field(name='BreadBot', value='N/A')
            await ctx.send(
                'say `hit` to draw more cards and `stand` to end the game with your stack'
            )
            await ctx.send(embed=em)
        elif msg2.content == 'stand' or msg2.content == 'Stand':
            if pcards4 < bcards:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had Less Cards Than Your Opponent\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards4)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            else:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had More Cards Than Your Opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards4)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return

        def check(z):
            return z.author == ctx.author and z.content == 'hit' or z.content == 'stand' or z.content == 'Hit' or z.content == 'Stand'

        msg2 = await self.bc.wait_for('message', check=check, timeout=30)
        if msg2.content == 'hit' or msg2.content == 'Hit':
            pcards6 = pcards5 + random.randrange(1, 10)
            if pcards6 > 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Busted!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards6)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            if pcards6 == 21:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You got to 21 before your opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards6)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return
            em = discord.Embed(
                title=f"{ctx.author.name}'s blackjack game",
                description=
                f'You drew 5 cards without busting and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                color=0x00ff00)
            em.add_field(name=ctx.author.name, value=pcards6)
            em.add_field(name='BreadBot', value=bcards)
            await ctx.send(embed=em)
            await self.update_bank(ctx.author, 2 * amount)
        elif msg2.content == 'stand' or msg2.content == 'Stand':
            if pcards5 < bcards:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had Less Cards Than Your Opponent!\n\nYou now have **{bal[0]-amount:,d}** coins',
                    color=0xff0000)
                em.add_field(name=ctx.author.name, value=pcards5)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                return
            else:
                em = discord.Embed(
                    title=f"{ctx.author.name}'s blackjack game",
                    description=
                    f'You Had More Cards Than Your Opponent and won **{amount:,d}** coins\n\nYou now have **{bal[0]+amount:,d}** coins',
                    color=0x00ff00)
                em.add_field(name=ctx.author.name, value=pcards5)
                em.add_field(name='BreadBot', value=bcards)
                await ctx.send(embed=em)
                await self.update_bank(ctx.author, 2 * amount)
                return

    @commands.command(
        name='shop',
        description=f'check out the shop to see whats in store',
        usage=' ')
    async def shop(self, ctx):
        em = discord.Embed(title="Shop", color=random.choice(self.bc.color_list))

        for item in self.mainshop:
            if item["price"] == None:
                continue
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            em.add_field(name=name, value=f"${price:,d} | {desc}")

        await ctx.send(embed=em)

    @commands.command(
        name='buy',
        description=f'buy something in the shop',
        usage='<item> [amount]')
    async def buy(self, ctx, item, amount=1):
        await self.open_account(ctx.author)

        res = await self.buy_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(
                    f"You don't have enough money in your wallet to buy {amount:,d} {item}"
                )
                return
        item = item.lower()
        for thing in self.mainshop:
            name = thing["name"].lower()
            if item in name:
                name_ = name.split(item)
                name_ = item + name_[1]
                break

        await ctx.send(f"You purchased {amount:,d} {name_}")

    @commands.command(
        description='only owner can use', usage='<user> <amount>')
    @commands.is_owner()
    async def award(self, ctx, member: discord.Member, amount):
        await self.open_account(member)

        amount = int(amount)
        await self.update_bank(member, amount)

        await ctx.send(f"you awarded {amount:,d} coins to {member}")

    @commands.command(
        aliases=["inv", "bag"],
        name='inventory',
        description=f'look whats inside your inventory',
        usage=' ')
    async def inventory(self, ctx):
        await self.open_account(ctx.author)
        user = ctx.author
        users = await self.get_bank_data()
        em = discord.Embed(title='Inventory', color=0x0000ff)
        try:
            bag = users[str(user.id)]['bag']
            for item in bag:
                item_name = item['item']
                item_amount = item['amount']
                em.add_field(name=item_name, value=item_amount, inline=False)
        except KeyError:
            bag = []
            em.add_field(name='Empty', value='Earn some items.')
        await ctx.send(embed=em)

    @commands.command(
        name='sell',
        description=f'sell an item for 50% its price',
        usage='<item> [amount]')
    async def sell(self, ctx, item, amount=1):
        await self.open_account(ctx.author)

        res = await self.sell_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(
                    f"You don't have {amount:,d} {item} in your bag.")
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your bag.")
                return

        await ctx.send(f"You just sold {amount:,d} {item}.")

    @commands.command(
        name='rich',
        description=f'look at the global richest members using the bot',
        usage='[amount of ppl]')
    async def rich(self, ctx, x=10):
        users = await self.get_bank_data()
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            total_amount = users[user]["wallet"] + users[user]["bank"]
            leader_board[total_amount] = name
            if total_amount != 0:
                total.append(total_amount)
            else:
                pass

        total = sorted(total, reverse=True)

        em = discord.Embed(
            title=f"Top {x} Richest People",
            description=
            "This is decided on the basis of raw money in the bank and wallet",
            color=0x0000ff)

        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = await self.bc.fetch_user(id_)
            name = member.name
            em.add_field(
                name=f"{index}. {name}", value=f"{amt:,d}", inline=False)
            if index == x or index == total:
                break
            else:
                index += 1

        await ctx.send(embed=em)

    @commands.command(name='work', description=f'work', usage=' ')
    @cooldown(1, 90, BucketType.user)
    async def work(self, ctx):
        await self.open_account(ctx.author)
        channel = ctx.channel
        responses = [
            "i like to clickbait people",
            "hello welcome to my youtube channel", 
            "danepai is cool",
            "omg free robux",
            "omg i found herobrine in minecraft", 
            "i am very cringe"
        ]
        doit = random.choice(responses)
        await channel.send('repeat what i say')
        await asyncio.sleep(1)
        await channel.send(doit)

        users = await self.get_bank_data()

        user = ctx.author

        earnings = random.randrange(200, 400)

        def check(m):
            return m.content.lower(
            ) == doit and m.channel == channel and m.author == ctx.author

        try:
            msg = await self.bc.wait_for('message', timeout=15, check=check)

        except asyncio.TimeoutError:
            await channel.send(
                "You didnt send it in time!")
        else:
            if msg.content.lower() == doit:
                await channel.send(
                    f'you just got {earnings:,d} coins from working'.format(
                        msg))
            elif msg.content.lower() != doit:
                await ctx.send(
                    'You didnt respond correctly.')
                return

        users[str(user.id)]["wallet"] += earnings
        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command(
        name='daily', description=f'get your daily coins', usage=' ')
    @cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        await self.open_account(ctx.author)
        users = await self.get_bank_data()

        user = ctx.author

        earnings = 5000

        em = discord.Embed(
            title="Daily Coins",
            color=0x0000ff,
            description=f"You collected {earnings:,d} coins as your daily coins"
        )
        users[str(user.id)]["wallet"] += earnings
        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)
        await ctx.send(embed=em)

    @commands.command(
        name='weekly', description=f'get your weekly coins', usage=' ')
    @cooldown(1, 604800, BucketType.user)
    async def weekly(self, ctx):
        await self.open_account(ctx.author)
        users = await self.get_bank_data()

        user = ctx.author

        earnings = 25000

        em = discord.Embed(
            title="Weekly Coins",
            color=0x0000ff,
            description=
            f"You collected {earnings:,d} coins as your Weekly coins")
        users[str(user.id)]["wallet"] += earnings
        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)
        await ctx.send(embed=em)

    @commands.command(aliases=["pm"])
    @cooldown(1, 35, BucketType.user)
    async def postmeme(self, ctx):
        item = "laptop"
        amount = 1
        breaklaptop = random.randrange(1, 100)
        if breaklaptop > 89:
            await self.sell_this(ctx.author, item, 1, 0)
            await ctx.send("Your laptop broke because you rage lmao")
        else:
            res = await self.check_for(ctx.author, item, amount)
            if not res[0]:
                if res[1] == 1:
                    await ctx.send("That Object isn't there!")
                    return
                if res[1] == 2:
                    await ctx.send(
                        f"You don't have {amount} {item} in your bag.")
                    return
                if res[1] == 3:
                    await ctx.send(f"You don't have a {item} in your bag.")
                    return
            await ctx.send("""**What type of meme do you want to post?**
`n` **■  Normie Meme**
`e` **■  Edgy meme**
`r` **■  Repost meme**
`d` **■  Dank meme**""")
            choices = ["n", "e", "r", "d"]

            def check(z):
                return z.author == ctx.author and z.channel == ctx.channel

            msg = await self.bc.wait_for('message', check=check, timeout=20)
            if msg.content.lower() in choices:
                karma = random.randrange(5000)
                if karma in range(0, 500):
                    earnings = random.randrange(100)
                    await ctx.send(
                        "Your meme is a bit dead with {} karma. You get {} coins from it"
                        .format(karma, earnings))
                elif karma in range(500, 1000):
                    earnings = random.randrange(200, 500)
                    await ctx.send(
                        "Your meme is **__decent__** with {} karma. You get {} coins from it"
                        .format(karma, earnings))
                elif karma in range(1000, 2000):
                    earnings = random.randrange(500, 750)
                    await ctx.send(
                        "Your meme is **__very decent__** with {} karma. You get {} coins from it"
                        .format(karma, earnings))
                elif karma in range(2000, 5000):
                    earnings = random.randrange(750, 1000)
                    await ctx.send(
                        "Your meme is **__TRENDING__** with {} karma. You get {} coins from it"
                        .format(karma, earnings))
                await self.update_bank(ctx.author, earnings)
            else:
                await ctx.send("choose a meme from the list bruh")
                return

    @commands.command(description=f'use your fishing pole and fish', usage=' ')
    @cooldown(1, 45, BucketType.user)
    async def fish(self, ctx, amount=1, item="fishingpole", fish="fishy"):
        await self.open_account(ctx.author)
        fishamt = random.randrange(4)
        res = await self.check_for(ctx.author, item, amount)
        fishing = await self.give1(ctx.author, fish, fishamt)

        users = await self.get_bank_data()

        user = ctx.author

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(
                    f"You don't have {amount:,d} {item} in your bag.")
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your bag.")
                return
        if not fishing[0]:
            if fishing[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if fishing[1] == 2:
                await ctx.send(
                    f"You don't have enough money in your wallet to buy {amount:,d} {item}"
                )
                return
        await ctx.send(f'You caught {fishamt} common fish')

    @commands.command(
        description=f'use your hunting rifle and hunt', usage=' ')
    @cooldown(1, 45, BucketType.user)
    async def hunt(self, ctx, amount=1, item="rifle", fish="dead_animal"):
        await self.open_account(ctx.author)
        fishamt = 1
        res = await self.check_for(ctx.author, item, amount)
        fishing = await self.give1(ctx.author, fish, fishamt)

        users = await self.get_bank_data()

        user = ctx.author

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(
                    f"You don't have {amount:,d} {item} in your bag.")
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your bag.")
                return
        if not fishing[0]:
            if fishing[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if fishing[1] == 2:
                await ctx.send(
                    f"You don't have enough money in your wallet to buy {amount:,d} {item}"
                )
                return
        await ctx.send(f'You caught {fishamt} dead animal')

    @commands.command(
        aliases=['steal'],
        name='rob',
        description=f'rob some money from your friends',
        usage='<member>')
    @cooldown(1, 120, BucketType.user)
    async def rob(self, ctx, member: discord.Member):
        await self.open_account(ctx.author)
        await self.open_account(member)
        users = await self.get_bank_data()

        bal = await self.update_bank(member)
        ownbal = await self.update_bank(ctx.author)

        if users[str(ctx.author.id)]["passive"] == "true":
            await ctx.send("You Cant rob this person's money in passive mode!")
            return
        elif users[str(member.id)]["passive"] == "true":
            await ctx.send(
                "You can't rob this person money because they are in passive mode!"
            )
            return
        else:

            if bal[0] < 500:
                await ctx.send(
                    "That person doesnt have atleast 500 coins in their wallet. It isnt worth it"
                )
                return
            if ownbal[0] < 500:
                await ctx.send("You need atleast 500 coins to rob someone")
                return
            earnings = random.randrange(0, bal[0])

            await self.update_bank(ctx.author, earnings)
            await self.update_bank(member, -1 * earnings)

            await ctx.send(f"you robbed {member} and got {earnings:,d} coins")

    @commands.command(description="rob a person", usage="<user>")
    async def heist(self, ctx, member: discord.Member):
        await self.open_account(ctx.author)
        users = await self.get_bank_data()
        bal = await self.update_bank(ctx.author)
        otherbal = await self.update_bank(member)
        if bal[0] < 1000:
            await ctx.send("You need atleast 1000 coins to start a heist!")
            return
        if otherbal[1] < 1000:
            await ctx.send("this person doesnt have enough for a good heist")
            return
        if users[str(member.id)]["passive"] == "true":
            await ctx.send(
                "This person is in passive mode leave him alone :(_ _")
            return
        if users[str(ctx.author.id)]["passive"] == "true":
            await ctx.send(
                "Mate you are in passive mode so you cant heist against someone"
            )
            return
        msg = await ctx.send(
            "aight everyone looks like we gonna bust open a bank. React to this message within 120 seconds to join. Must have 1000 coins to join. Must have atleast 10 people to start."
        )

        await msg.add_reaction("👍")

        data = {
            'id': member.id,
            'started': datetime.datetime.now(),
            'duration': 120,
            'channelId': ctx.channel.id,
            'messageId': msg.id,
            'guildId': ctx.guild.id,
            'author': ctx.author.id,
        }
        await self.bc.heists.upsert(data)
        self.bc.heistdata[member.id] = data

    @commands.command(
        description='Open a loot box (if you have one)', usage=' ')
    async def lootbox(self, ctx):
        amount = random.randrange(1, 2)
        item = "LootBox"
        loots = []
        for x in self.mainshop:
            loots.append(x["name"].lower())
        loots.remove("dead_animal")
        loots.remove("fishy")
        loots.remove("lootbox")
        randitem = random.randrange(len(loots))
        earnings = random.randrange(5000, 10000)
        items = loots[randitem]

        users = await self.get_bank_data()

        user = ctx.author
        res = await self.sell_this(ctx.author, item, amount, 0)
        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"You don't have {amount} {item} in your bag.")
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your bag.")
                return
        res = await self.give1(ctx.author, items, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(
                    f"You don't have enough money in your wallet to buy {amount} {item}"
                )
                return
        await self.update_bank(ctx.author, earnings)
        await ctx.send(
            "From your lootbox you got a crisp **{}** coins. You also got {} {}(s)"
            .format(earnings, amount, items))

    @commands.command(
        description="turn this on and no one will rob u",
        usage="<True or False>")
    async def passive(self, ctx, toggle):
        await self.open_account(ctx.author)
        users = await self.get_bank_data()
        user = ctx.author
        if toggle.lower() == "true":
            users[str(user.id)]["passive"] = 'true'
            with open("mainbank.json", "w") as f:
                json.dump(users, f, indent=4)
            await ctx.send(
                "Passive mode is now on. No one can rob you and give u money and u cant rob and give money"
            )
        if toggle.lower() == "false":
            users[str(user.id)]["passive"] = 'false'
            with open("mainbank.json", "w") as f:
                json.dump(users, f, indent=4)
            await ctx.send("Passive mode is now turned off")

    @commands.command(
        name='balance',
        aliases=['bal'],
        description='check your balance or someone elses balance',
        usage='[user]')
    async def balance(self, ctx, member: discord.Member = None):
        await self.open_account(ctx.author)

        if member == None:

            user = ctx.author

            users = await self.get_bank_data()

            wallet_amt = users[str(user.id)]["wallet"]
            bank_amt = users[str(user.id)]["bank"]
            banklimit = users[str(user.id)]["bnklmt"]

            em = discord.Embed(
                title=f"{ctx.author.name}'s bank balance",
                description=
                f"Wallet: {wallet_amt:,d}\nBank: {bank_amt:,d}/{banklimit:,d}",
                color=0x0000ff)

            await ctx.send(embed=em)
        else:
            user = member

            users = await self.get_bank_data()

            wallet_amt = users[str(user.id)]["wallet"]
            bank_amt = users[str(user.id)]["bank"]

            em = discord.Embed(
                title=f"{member.name}'s bank balance",
                description=f"Wallet: {wallet_amt:,d}\nBank: {bank_amt:,d}",
                color=0x0000ff)

            await ctx.send(embed=em)

    @commands.command(description="check out ya stats", usage=" ")
    async def profile(self, ctx, member: discord.Member = None):
        await self.open_account(ctx.author)
        if member == None:
            member = ctx.author
        bal = await self.update_bank(member)
        em = discord.Embed(
            title=f"{member.name}'s Profile",
            color=random.choice(self.bc.color_list))
        em.set_thumbnail(url=member.avatar_url)
        em.add_field(name="XP", value=f"{bal[3]}/100")
        em.add_field(name="Level", value=f"{bal[4]}")
        em.add_field(name="Wallet", value=f"{bal[0]:,d}")
        em.add_field(name="Bank", value=f"{bal[1]:,d}/{bal[2]:,d}")
        await ctx.send(embed=em)

    @commands.command(name='beg', description='beg for money', usage=' ')
    @cooldown(1, 30, BucketType.user)
    async def beg(self, ctx):

        await self.open_account(ctx.author)

        users = await self.get_bank_data()

        user = ctx.author

        earnings = random.randrange(200)

        await ctx.send(f"Someone gave you {earnings} coins!")

        users[str(user.id)]["wallet"] += earnings

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command(
        name='withdraw',
        aliases=['with'],
        description='withdraw money out of your bank',
        usage='<amount or all>')
    async def withdraw(self, ctx, amount=None):
        await self.open_account(ctx.author)

        if amount == None:
            await ctx.send("please specify an amount")
            return

        bal = await self.update_bank(ctx.author)
        if amount == 'all':
            amount = bal[1]
        if amount == "half":
            amount = bal[1] / 2
        amount = int(amount)
        if amount > bal[1]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        await self.update_bank(ctx.author, amount)
        await self.update_bank(ctx.author, -1 * amount, "bank")

        await ctx.send(f"you withdrew {amount:,d} coins")

    @commands.command(
        name='deposit',
        aliases=['dep'],
        description='deposit some cash into your bank',
        usage='<amount or all>')
    async def deposit(self, ctx, amount=None):
        await self.open_account(ctx.author)

        if amount == None:
            await ctx.send("please specify an amount")
            return

        bal = await self.update_bank(ctx.author)
        if amount == "all":
            amount = bal[0]
            if amount + bal[1] > bal[2]:
                maths = bal[0] - bal[2]
                amount = bal[0] - maths - bal[1]
        if amount == "half":
            amount = bal[0] / 2

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return
        if amount + bal[1] > bal[2]:
            await ctx.send("you dont have enough space in your bank!")
            return

        await self.update_bank(ctx.author, -1 * amount)
        await self.update_bank(ctx.author, amount, "bank")

        await ctx.send(f"you deposited {amount:,d} coins")

    @commands.command(
        aliases=['give'],
        name='share',
        description='share some money with your friends',
        usage='<member> <amount or all>')
    async def share(self, ctx, member: discord.Member, amount=None):
        await self.open_account(ctx.author)
        await self.open_account(member)
        users = await self.get_bank_data()

        if amount == None:
            await ctx.send("please specify an amount")
            return

        if users[str(ctx.author.id)]["passive"] == "true":
            await ctx.send("You Cant share money in pasive mode!")
            return
        elif users[str(member.id)]["passive"] == "true":
            await ctx.send(
                "You can't give this person money because they are passive!")
            return
        else:

            bal = await self.update_bank(ctx.author)
            if amount == 'all':
                amount = bal[0]

            amount = int(amount)
            if amount > bal[0]:
                await ctx.send("you dont have that much money!")
                return
            if amount < 0:
                await ctx.send("amount must be positive")
                return

            await self.update_bank(ctx.author, -1 * amount)
            await self.update_bank(member, amount)

            await ctx.send(f"you gave {amount:,d} coins to {member}")

    @commands.command(
        name='slots',
        description='use the slot machine to gamble your life away',
        usage='<amount or all>')
    @cooldown(1, 15, BucketType.user)
    async def slots(self, ctx, amount=None):
        await self.open_account(ctx.author)

        if amount == None:
            await ctx.send("please specify an amount")
            return

        bal = await self.update_bank(ctx.author)
        if amount == 'all':
            amount = bal[0]

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        await self.update_bank(ctx.author, -1 * amount)

        await ctx.send(f"you bet {amount:,d} coins")

        final = []
        for i in range(3):
            a = random.choice(["X", "O", "Q"])

            final.append(a)

        await ctx.send(str(final))

        if final[0] == final[1] or final[0] == final[2] or final[1] == final[2]:

            await self.update_bank(ctx.author, 2 * amount)
            await ctx.send("you won")
        else:
            await self.update_bank(ctx.author, amount - amount)
            await ctx.send("you lost hah")

    @commands.command(
        name='gamble',
        aliases=['bet'],
        description='gamble.',
        usage='<amount or all>')
    @cooldown(1, 15, BucketType.user)
    async def gamble(self, ctx, amount=None):

        if amount == None:
            await ctx.send("Please Specify a Number")
            return

        bal = await self.update_bank(ctx.author)
        if amount == 'all':
            amount = bal[0]
        if amount == 'half':
            amount = bal[0] / 2

        amount = int(amount)
        if amount > bal[0]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        await self.update_bank(ctx.author, -1 * amount)

        P1 = random.randrange(1, 10)
        P2 = random.randrange(1, 10)

        if int(P1) < int(P2):
            await asyncio.sleep(1)
            em = discord.Embed(
                title=f"{ctx.author.name}'s gambling game",
                color=0xff0000,
                description=
                f'You lost **{amount:,d}** coins\n\nYou now have **{bal[0]-amount:,d}** coins'
            )
            em.add_field(name=f'{ctx.author.name}', value=f'Rolled `{P1}`')
            em.add_field(name='BreadBot', value=f'Rolled `{P2}`')
            await ctx.send(embed=em)

        elif int(P1) > int(P2):
            em = discord.Embed(
                title=f"{ctx.author.name}'s gambling game",
                color=0x00ff00,
                description=
                f'You won **{amount:,d}** coins gg\n\nYou now have **{bal[0]+amount:,d}** coins'
            )
            em.add_field(name=f'{ctx.author.name}', value=f'Rolled `{P1}`')
            em.add_field(name='BreadBot', value=f'Rolled `{P2}`')
            await ctx.send(embed=em)
            await self.update_bank(ctx.author, 2 * amount)
        elif int(P1) == int(P2):
            em = discord.Embed(
                title=f"{ctx.author.name}'s gambling game",
                color=0xffff00,
                description='Tie, You didnt lose any cash')
            em.add_field(name=f'{ctx.author.name}', value=f'Rolled `{P1}`')
            em.add_field(name='BreadBot', value=f'Rolled `{P2}`')
            await ctx.send(embed=em)
            await self.update_bank(ctx.author, amount)

    async def open_account(self, user):

        users = await self.get_bank_data()

        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["wallet"] = 0
            users[str(user.id)]["bank"] = 0
            users[str(user.id)]["bnklmt"] = 50000
            users[str(user.id)]["xp"] = 0
            users[str(user.id)]["level"] = 0
            users[str(user.id)]["passive"] = "false"

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)
        return True

    async def get_bank_data(self):
        with open("mainbank.json", "r") as f:
            users = json.load(f)

        return users

    async def sell_this(self, user, item_name, amount, price=None):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                if price == None:
                    price = 0.5 * item["price"]
                break

        if name_ == None:
            return [False, 1]

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False, 2]
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    if new_amt == 0:
                        users[str(user.id)]["bag"].remove({
                            "item": item_name,
                            "amount": new_amt
                        })
                    t = 1
                    break
                index += 1
            if t == None:
                return [False, 3]
        except:
            return [False, 3]

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

        await self.update_bank(user, cost, "wallet")

        return [True, "Worked"]

    async def update_bank(self, user, change=0, mode="wallet"):
        users = await self.get_bank_data()

        users[str(user.id)][mode] += int(change)

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

        bal = [
            users[str(user.id)]["wallet"], users[str(user.id)]["bank"],
            users[str(user.id)]["bnklmt"], users[str(user.id)]["xp"],
            users[str(user.id)]["level"]
        ]
        return bal

    async def buy_this(self, user, item_name, amount):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                price = item["price"]
                break
            elif item_name in item["name"].lower():
                name_ = item["name"].lower()
                price = item["price"]
                break

        if name_ == None:
            return [False, 1]

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        if bal[0] < cost:
            return [False, 2]

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == name_:
                    old_amt = thing["amount"]
                    new_amt = old_amt + amount
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1
            if t == None:
                obj = {"item": name_, "amount": amount}
                users[str(user.id)]["bag"].append(obj)
        except:
            obj = {"item": name_, "amount": amount}
            users[str(user.id)]["bag"] = [obj]

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

        await self.update_bank(user, cost * -1, "wallet")

        return [True, "Worked"]

    async def give1(self, user, item_name, amount):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                break

        if name_ == None:
            return [False, 1]

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt + amount
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index += 1
            if t == None:
                obj = {"item": item_name, "amount": amount}
                users[str(user.id)]["bag"].append(obj)
        except:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["bag"] = [obj]

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

        return [True, "Worked"]

    async def check_for(self, user, item_name, amount=1, price=None):
        item_name = item_name.lower()
        name_ = None
        for item in self.mainshop:
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                if price == None:
                    price = 0 * item["price"]
                break

        if name_ == None:
            return [False, 1]

        cost = price * amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False, 2]
                    users[str(user.id)]["bag"][index]["amount"] = old_amt
                    t = 1
                    break
                index += 1
            if t == None:
                return [False, 3]
        except:
            return [False, 3]

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

        await self.update_bank(user, cost, "wallet")

        return [True, "Worked"]


def setup(bc):
    bc.add_cog(Economy(bc))
