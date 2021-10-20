import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
from copy import deepcopy
from dateutil.relativedelta import relativedelta
import random
import asyncio
import datetime
from utility import words
from utility import working

shop = [
    {
        "name": "Laptop", 
        "desc": "Used to post reddit memes and other stuff", 
        "cost": 5000,
        "id": "laptop",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Bread Coin", 
        "desc": "A flex item.", 
        "cost": 100000,
        "id": "breadcoin",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Bread Totem", 
        "desc": "A flex item.", 
        "cost": 1000000,
        "id": "breadtotem",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Bank Note", 
        "desc": "Used to expand your bank", 
        "cost": 20000,
        "id": "banknote",
        "hidden": False,
        "canbuy": False
    },
    {
        "name": "Phone", 
        "desc": "Will soon have a use", 
        "cost": 10000,
        "id": "phone",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Hunting Rifle", 
        "desc": "Go hunting for animals", 
        "cost": 10000,
        "id": "rifle",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Fishing Pole", 
        "desc": "Used to go fishing with your old man", 
        "cost": 10000,
        "id": "fishingpole",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Fishy", 
        "desc": "Sell this", 
        "cost": 500,
        "id": "fish",
        "hidden": True,
        "canbuy": False
    },
    {
        "name": "Skunk", 
        "desc": "Sell this", 
        "cost": 180,
        "id": "skunk",
        "hidden": True,
        "canbuy": False
    },
    {
        "name": "Rabbit", 
        "desc": "Sell this", 
        "cost": 120,
        "id": "rabbit",
        "hidden": True,
        "canbuy": False
    },
    {
        "name": "Cow", 
        "desc": "Sell this", 
        "cost": 240,
        "id": "cow",
        "hidden": True,
        "canbuy": False
    },
    {
        "name": "Bear", 
        "desc": "Sell this", 
        "cost": 300,
        "id": "bear",
        "hidden": True,
        "canbuy": False
    },
    {
        "name": "Basic Lootbox", 
        "desc": "Use this with lootbox command", 
        "cost": 0,
        "id": "lootbox",
        "hidden": False,
        "canbuy": False
    },
    {
        "name": "Premium Lootbox", 
        "desc": "Use this with premlootbox command", 
        "cost": 0,
        "id": "premlootbox",
        "hidden": False,
        "canbuy": False
    }
]

places = [
    {
        "name": "Pantry",
        "minimum": 600,
        "maximum": 1200,
        "deadly": False
    },
    {
        "name": "Bed",
        "minimum": 800,
        "maximum": 1100,
        "deadly": True,
        "deathmessage": "The monster under your bed ate you"
    },
    {
        "name": "Attic",
        "minimum": 700,
        "maximum": 1000,
        "deadly": False
    },
    {
        "name": "Dog",
        "minimum": 600,
        "maximum": 1000,
        "deadly": False
    },
    {
        "name": "Pocket",
        "minimum": 600,
        "maximum": 1000,
        "deadly": False
    },
    {
        "name": "Shoe",
        "minimum": 600,
        "maximum": 1000,
        "deadly": False
    },
    {
        "name": "Wardrobe",
        "minimum": 600,
        "maximum": 1000,
        "deadly": False
    },
    {
        "name": "Air",
        "minimum": 1000,
        "maximum": 1400,
        "deadly": True,
        "deathmessage": "You somehow died from the thing that you breath."
    },
    {
        "name": "Mailbox",
        "minimum": 600,
        "maximum": 800,
        "deadly": True,
        "deathmessage": "Your crazy neighbor caught you in his mailbox so he smashed your head with a bat."
    },
    {
        "name": "Dumpster",
        "minimum": 800,
        "maximum": 1200,
        "deadly": True,
        "deathmessage": "The mutant racoons in the dumpster ate you alive."
    },
    {
        "name": "Car",
        "minimum": 600,
        "maximum": 900,
        "deadly": True,
        "deathmessage": "You got caught by the police for breaking into someone's car and resisted so you got shot to death."
    }
]

class PlaceButton(discord.ui.Button):
    def __init__(self, bc, ctx, name, min, max, deadly, deathmessage=None):
        super().__init__(style=discord.ButtonStyle.primary, label=name)
        self.bc = bc
        self.name = name
        self.min = min
        self.max = max
        self.deadly = deadly
        self.deathmessage = deathmessage
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return
        view = self.view
        data = await self.bc.economy.find(self.ctx.author.id)
        if self.deadly:
            chance = random.randrange(1, 100)
            if chance in range(1,31):
                data["wallet"] = 0
                for child in view.children:
                    if child.label != self.label:
                        child.style = discord.ButtonStyle.secondary
                    child.disabled = True
                await interaction.message.edit(self.deathmessage, view=view)
                await self.bc.economy.upsert(data)
            else:
                earnings = random.randrange(self.min, self.max)
                data["wallet"] += earnings
                for child in view.children:
                    if child.label != self.label:
                        child.style = discord.ButtonStyle.secondary
                    child.disabled = True
                await interaction.message.edit("You searched the **{}** and earned **{}** coins".format(self.name, earnings), view=view)
                await self.bc.economy.upsert(data)
        else:
            earnings = random.randrange(self.min, self.max)
            data["wallet"] += earnings
            for child in view.children:
                if child.label != self.label:
                    child.style = discord.ButtonStyle.secondary
                child.disabled = True
            await interaction.message.edit("You searched the **{}** and earned **{}** coins".format(self.name, earnings), view=view)
            await self.bc.economy.upsert(data)

class Search(discord.ui.View):
    def __init__(self, bc, ctx):
        super().__init__()
        self.bc = bc
        self.ctx = ctx
        buttons = []
        for x in range(3):
            place = random.choice(places)
            if place in buttons:
                place = random.choice(places)
                if place in buttons:
                    place = random.choice(places)
                    if place in buttons:
                        place = random.choice(places)
                        if place in buttons:
                            place = random.choice(places)
                            if place in buttons:
                                place = random.choice(places)
                
            
            if not "deathmessage" in place:
                self.add_item(PlaceButton(self.bc, self.ctx, place["name"], place["minimum"], place["maximum"], place["deadly"]))
                buttons.append(place)
            else:
                self.add_item(PlaceButton(self.bc, self.ctx, place["name"], place["minimum"], place["maximum"], place["deadly"], place["deathmessage"]))
                buttons.append(place)

class Blackjack(discord.ui.View):
    def __init__(self, amount, bc, pcards, bcards, ctx):
        super().__init__()
        self.amount = amount
        self.bc = bc
        self.pcards = pcards
        self.bcards = bcards
        self.ctx = ctx
        self.data = None
        self.cardsDrawn = 0
    
    @discord.ui.button(label='Hit', style=discord.ButtonStyle.green)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.data = await self.bc.economy.find(self.ctx.author.id)
        if interaction.user.id != self.ctx.author.id:
            return
        self.cardsDrawn += 1
        self.pcards += random.randrange(1, 10)
        if self.pcards > 21:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You Busted!\n\nYou now have **{self.data["wallet"]:,d}** coins',
                color=0xff0000)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            for child in self.children:
                child.disabled = True
            self.stop()
            await interaction.message.edit(embed=em, view=self)
            return
        if self.pcards == 21:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You got to 21 before your opponent and won **{self.amount:,d}** coins\n\nYou now have **{self.data["wallet"]+self.amount*2:,d}** coins',
                color=0x00ff00)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            self.data["wallet"] += 2 * self.amount
            await self.bc.economy.upsert(self.data)
            for child in self.children:
                child.disabled = True
            self.stop()
            await interaction.message.edit(embed=em, view=self)
            return
        if self.cardsDrawn == 5:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You managed to draw 5 cards without busting and earned yourself **{self.amount:,d}** coins\n\nYou now have **{self.data["wallet"]+self.amount*2:,d}** coins',
                color=0x00ff00)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            self.data["wallet"] += 2 * self.amount
            await self.bc.economy.upsert(self.data)
            for child in self.children:
                child.disabled = True
            self.stop()
            await interaction.message.edit(embed=em, view=self)
            return
        em = discord.Embed(
            title=f"{self.ctx.author.name}'s blackjack game", color=random.choice(self.bc.color_list))
        em.add_field(name=self.ctx.author.name, value=self.pcards)
        em.add_field(name='BreadBot', value='N/A')
        await interaction.message.edit(embed=em, view=self)

    @discord.ui.button(label='Stand', style=discord.ButtonStyle.green)
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.data = await self.bc.economy.find(self.ctx.author.id)
        if interaction.user.id != self.ctx.author.id:
            return
        if self.pcards < self.bcards:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You Had Less Cards Than Your Opponent!\n\nYou now have **{self.data["wallet"]:,d}** coins',
                color=0xff0000)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            await self.bc.economy.upsert(self.data)
            for child in self.children:
                child.disabled = True
            self.stop()
            await interaction.message.edit(embed=em, view=self)
            return
        else:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You Had More Cards Than Your Opponent and won **{self.amount:,d}** coins\n\nYou now have **{self.data["wallet"]+self.amount*2:,d}** coins',
                color=0x00ff00)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            self.data["wallet"] += 2 * self.amount
            await self.bc.economy.upsert(self.data)
            for child in self.children:
                child.disabled = True
            self.stop()
            await interaction.message.edit(embed=em, view=self)
            return

def custom_cooldown(rate:int, per:int, newrate:int, newper:int, bucket: commands.BucketType):

    default_mapping = commands.CooldownMapping.from_cooldown(rate, per, bucket)
    new_mapping = commands.CooldownMapping.from_cooldown(newrate, newper, bucket)

    def inner(ctx: commands.Context):
        key = ctx.author.id
        if key in ctx.bot.premiums:
            bucket = new_mapping.get_bucket(ctx.message)
        
        else:
            bucket = default_mapping.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after, BucketType.user)
        return True
    
    return inner

class Economy(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.heists = self.checkHeist.start()

    def cog_unload(self):
        self.heists.cancel()

    async def cog_before_invoke(self, ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "xp" not in data:
            data["xp"] = 0
        if "level" not in data:
            data["level"] = 1
        if data["xp"] >= 100:
            data["banklimit"] += random.randint(2000,3000)
            data["level"] += 1
        data["xp"] += 1
        await self.bc.economy.upsert(data)

    @commands.command()
    @commands.check(custom_cooldown(1, 30, 1, 12, BucketType.user))
    async def work(self, ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        topic = words.randtopic
        buttons = []
        for x in range(5):
            _topic = random.choice(topic)
            if _topic in buttons:
                _topic = random.choice(topic)
                if _topic in buttons:
                    _topic = random.choice(topic)
                    if _topic in buttons:
                        _topic = random.choice(topic)
                        if _topic in buttons:
                            _topic = random.choice(topic)
                            if _topic in buttons:
                                _topic = random.choice(topic)
            buttons.append(_topic)

        msg = await ctx.send("\n".join([f"`{word}`" for word in buttons]))
        await asyncio.sleep(5)
        await msg.edit("Choose the items in order", view=working.Order(buttons, self.bc, ctx))

    @commands.command()
    async def weekly(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        currenttime = datetime.datetime.now()
        claimtime = data['claimedweekly'] + relativedelta(seconds=86400*7)
        if currenttime >= claimtime:
            premium = await self.bc.packs.find(ctx.author.id)
            if not premium:
                earnings = 75000
            elif premium["Supporter"]:
                earnings = 75000*1.2
            elif premium["1ServerRedeemed"]:
                earnings = 75000*1.5
            elif premium["2ServersRedeemed"]:
                earnings = 75000*2
            data["wallet"] += earnings
            await ctx.send("You have now claimed your {}k coins for this week!".format(earnings/1000))
            await self.bc.economy.upsert(data)
            data["claimedweekly"] = datetime.datetime.now()
        else:
            timeleft = claimtime - datetime.datetime.now()
            seconds = timeleft.total_seconds()
            m, s = divmod(seconds, 60)
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
            await ctx.send("Bro wait for {} to claim your weekly prize".format(duration))

    @commands.command()
    async def daily(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        currenttime = datetime.datetime.now()
        claimtime = data['claimeddaily'] + relativedelta(seconds=86400)
        if currenttime >= claimtime:
            premium = await self.bc.packs.find(ctx.author.id)
            if not premium:
                earnings = 25000
            elif premium["Supporter"]:
                earnings = 25000*1.2
            elif premium["1ServerRedeemed"]:
                earnings = 25000*1.5
            elif premium["2ServersRedeemed"]:
                earnings = 25000*2
            data["wallet"] += earnings
            await ctx.send("You have now claimed your {}k coins for today!".format(earnings/1000))
            await self.bc.economy.upsert(data)
            data["claimeddaily"] = datetime.datetime.now()
        else:
            timeleft = claimtime - datetime.datetime.now()
            seconds = timeleft.total_seconds()
            m, s = divmod(seconds, 60)
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
            await ctx.send("Bro wait for {} to claim your daily prize".format(duration))
            
    @commands.command(hidden=True)
    @commands.is_owner()
    async def handouts(self,ctx,which):
        if which == "weeklyvalue":
            eco = await self.bc.economy.get_all()
            for data in eco:
                check = await self.bc.packs.find(data["_id"])
                if not check:
                    pass
                else:
                    if check["2ServersRedeemed"]:
                        member = self.bc.get_user(data["_id"])
                        await self.add_item(member, "premlootbox", 2)
            await ctx.send("The lootboxes have been handed out!")
        elif which == "dailybasic":
            eco = await self.bc.economy.get_all()
            for data in eco:
                check = await self.bc.packs.find(data["_id"])
                if not check:
                    pass
                else:
                    if check["1ServerRedeemed"]:
                        member = self.bc.get_user(data["_id"])
                        await self.add_item(member, "lootbox", 1)
            await ctx.send("The lootboxes have been handed out!")
        elif which == "weeklybasic":
            eco = await self.bc.economy.get_all()
            for data in eco:
                check = await self.bc.packs.find(data["_id"])
                if not check:
                    pass
                else:
                    if check["1ServerRedeemed"]:
                        member = self.bc.get_user(data["_id"])
                        await self.add_item(member, "premlootbox", 1)
            await ctx.send("The lootboxes have been handed out!")
        elif which == "weeklysup":
            eco = await self.bc.economy.get_all()
            for data in eco:
                check = await self.bc.packs.find(data["_id"])
                if not check:
                    pass
                else:
                    if check["Supporter"]:
                        member = self.bc.get_user(data["_id"])
                        await self.add_item(member, "lootbox", 1)
            await ctx.send("The lootboxes have been handed out!")
        elif which == "dailyvalue":
            eco = await self.bc.economy.get_all()
            for data in eco:
                check = await self.bc.packs.find(data["_id"])
                if not check:
                    pass
                else:
                    if check["2ServersRedeemed"]:
                        member = self.bc.get_user(data["_id"])
                        await self.add_item(member, "lootbox", 3)
            await ctx.send("The lootboxes have been handed out!")

    @tasks.loop(seconds=15)
    async def checkHeist(self):
        heist = deepcopy(self.bc.heistdata)
        for key, value in heist.items():
            member = value["_id"]
            member = self.bc.get_user(member)
            msg = value["messageId"]
            author = value['author']
            author = self.bc.get_user(author)
            currentTime = datetime.datetime.now()
            guild = self.bc.get_guild(value['guildId'])
            channel = self.bc.get_channel(value['channelId'])
            ctx = discord.utils.get(guild.text_channels, id=value['channelId'])
            data1 = await self.bc.economy.find(member.id)
            new_msg = await channel.fetch_message(msg)
            lost = []
            win = []
            unmuteTime = value['started'] + relativedelta(
                seconds=value['duration'])
            data = await self.bc.economy.find(author.id)
            users = await new_msg.reactions[0].users().flatten()
            users.pop(users.index(self.bc.user))
            if currentTime >= unmuteTime:
                if len(users) < 2:
                    await ctx.send("Not enough users joined")
                    await self.bc.heists.delete(member.id)
                    try:
                        self.bc.heistdata.pop(member.id)
                    except KeyError:
                        pass
                    return
                for user in users:
                    await self.check_acc(user)
                    data = await self.bc.economy.find(user.id)
                    if data["wallet"] < 1000:
                        pass
                    else:
                        chance = random.randrange(100)
                        if chance > 75:
                            lost.append(user)
                        else:
                            win.append(user)
                winings = data1["bank"] / len(win)
                winings = int(winings)
                data1["bank"] -= data1["bank"]
                await self.bc.economy.upsert(data1)
                for user in win:
                    data = await self.bc.economy.find(user.id)
                    data["wallet"] += winings
                    await self.bc.economy.upsert(data)
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
        name='gamble',
        aliases=['bet'],
        description='gamble.',
        usage='bet <amount or all>')
    @commands.cooldown(1, 15, BucketType.user)
    async def gamble(self,ctx,amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if data["wallet"] > 5000000:
            return await ctx.send("You are too rich to gamble! Go and prestige or spend your coins.")

        if amount == 'all':
            amount = data["wallet"]
            if amount > 500000:
                amount = 500000
        if amount == 'half':
            amount = data["wallet"] / 2
            if amount > 500000:
                amount = 500000
        if amount > 500000:
            return await ctx.send("You can only gamble 500k coins")

        amount = int(amount)
        if amount > data["wallet"]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        data["wallet"] -= amount

        P1 = random.randrange(1, 10)
        P2 = random.randrange(1, 10)

        if int(P1) < int(P2):
            await asyncio.sleep(1)
            em = discord.Embed(
                title=f"{ctx.author.name}'s gambling game",
                color=0xff0000,
                description=
                f'You lost **{amount}** coins\n\nYou now have **{data["wallet"]}** coins'
            )
            em.add_field(name=f'{ctx.author.name}', value=f'Rolled `{P1}`')
            em.add_field(name='BreadBot', value=f'Rolled `{P2}`')
            await ctx.send(embed=em)

        elif int(P1) > int(P2):
            em = discord.Embed(
                title=f"{ctx.author.name}'s gambling game",
                color=0x00ff00,
                description=
                f'You won **{amount}** coins gg\n\nYou now have **{data["wallet"]+amount}** coins'
            )
            em.add_field(name=f'{ctx.author.name}', value=f'Rolled `{P1}`')
            em.add_field(name='BreadBot', value=f'Rolled `{P2}`')
            await ctx.send(embed=em)
            data["wallet"] += amount*2
        elif int(P1) == int(P2):
            em = discord.Embed(
                title=f"{ctx.author.name}'s gambling game",
                color=0xffff00,
                description='Tie, You didnt lose any cash')
            em.add_field(name=f'{ctx.author.name}', value=f'Rolled `{P1}`')
            em.add_field(name='BreadBot', value=f'Rolled `{P2}`')
            await ctx.send(embed=em)
            data["wallet"] += amount
        await self.bc.economy.upsert(data)
    
    @commands.command(description="expand your bank")
    async def expand(self, ctx, amount=1):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "banknote")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a banknote!")
        res = await self.remove_item(ctx.author, "banknote", amount)
        if not res[0]:
            if res[1] == 1:
                return await ctx.send("That item was not found!")
            if res[1] == 2:
                return await ctx.send("You don't have that many banknotes to use!")
        data = await self.bc.economy.find(ctx.author.id)
        expansion = random.randrange(20000, 25000)
        data["banklimit"] += expansion*amount
        await ctx.send("Your bank has been expanded by {} coins".format(expansion*amount))
        await self.bc.economy.upsert(data)

    @commands.command(description="Get something random from the shop")
    async def lootbox(self, ctx):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "lootbox")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a lootbox!")
        res = await self.remove_item(ctx.author, "lootbox", 1)
        if not res[0]:
            if res[1] == 1:
                return await ctx.send("That item was not found!")
            if res[1] == 2:
                return await ctx.send("You don't have that many lootboxes to use!")
        earnings = random.randint(3000,5000)
        chance = random.randint(0,100)
        possibleitems = ["laptop", "phone", "rifle", "fishingpole"]
        item = random.choice(possibleitems)
        if chance < 41:
            await self.add_item(ctx.author, item, 1)
            await ctx.send("You managed to get a crisp {} coins with a {}".format(earnings, item))
        else:
            await ctx.send("You managed to get a crisp {} coins".format(earnings))
        data = await self.bc.economy.find(ctx.author.id)
        data["wallet"] += earnings
        await self.bc.economy.upsert(data)

    @commands.command()
    async def gift(self, ctx, member:discord.Member, item, amount = 1):
        await self.check_acc(ctx.author)
        await self.check_acc(member)
        data = await self.bc.economy.find(ctx.author.id)
        data2 = await self.bc.economy.find(member.id)
        if data["passive"]:
            return await ctx.send("You are in passive mode you have to turn that off to share items!")
        if data2["passive"]:
            return await ctx.send("This person has passive mode on so you cannot share items to them!")
        res = await self.remove_item(ctx.author, item, amount)
        if not res[0]:
            if res[1] == 1:
                return await ctx.send("That item was not found!")
            if res[1] == 2:
                return await ctx.send("You don't have that many items to give!")
        await self.add_item(member, item, amount)
        await ctx.send("They have now recieved the items!")

    @commands.command(description="Get something random from the shop")
    async def premlootbox(self, ctx):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "premlootbox")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a lootbox!")
        res = await self.remove_item(ctx.author, "premlootbox", 1)
        if not res[0]:
            if res[1] == 1:
                return await ctx.send("That item was not found!")
            if res[1] == 2:
                return await ctx.send("You don't have that many lootboxes to use!")
        earnings = random.randint(8000,12000)
        possibleitems = ["laptop", "phone", "rifle", "fishingpole", "banknote"]
        item = random.choice(possibleitems)
        chance = random.randint(0,100)
        if chance < 51:
            await self.add_item(ctx.author, item, 2)
            await ctx.send("You managed to get a crisp {} coins with 2 {}s".format(earnings, item))
        else:
            await ctx.send("You managed to get a crisp {} coins".format(earnings))
        data = await self.bc.economy.find(ctx.author.id)
        data["wallet"] += earnings
        await self.bc.economy.upsert(data)


    @commands.command(
        description='b l a c k j a c k', usage='<amount>', aliases=["bj"])
    @commands.check(custom_cooldown(1,30,1,12,BucketType.user))
    async def blackjack(self, ctx, amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if data["wallet"] > 5000000:
            return await ctx.send("You are too rich to gamble! Go and prestige or spend your coins.")
        pcards = random.randrange(1, 20)
        bcards = random.randrange(1, 20)

        if amount == 'all':
            amount = data["wallet"]
            if amount > 500000:
                amount = 500000
        if amount == 'half':
            amount = data["wallet"] / 2
            if amount > 500000:
                amount = 500000
        if amount > 500000:
            return await ctx.send("You can only gamble 500k coins")

        amount = int(amount)
        if amount > data["wallet"]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        data["wallet"] -= amount
        await self.bc.economy.upsert(data)
        em = discord.Embed(
            title=f"{ctx.author.name}'s blackjack game", color=random.choice(self.bc.color_list))
        em.add_field(name=ctx.author.name, value=pcards)
        em.add_field(name='BreadBot', value='N/A')
        await ctx.send(
            'Push `Hit` to draw more cards and push `Stand` to end the game with the amount you have now.'
        )
        await ctx.send(embed=em, view=Blackjack(amount, self.bc, pcards, bcards, ctx))


    @commands.command(
        aliases=["bal"]
    )
    async def balance(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        await self.check_acc(member)
        data = await self.bc.economy.find(member.id)
        em = discord.Embed(
            title="{}'s Bank Account".format(member.name),
            description=f"**Wallet:** {data['wallet']:,d}\n**Bank:** {data['bank']:,d}/{data['banklimit']:,d}",
            color=random.choice(self.bc.color_list)
        )
        await ctx.send(embed=em)

    @commands.command()
    async def profile(self, ctx, member: discord.Member=None):
        member = member or ctx.author
        await self.check_acc(member)
        data = await self.bc.economy.find(member.id)
        embed = discord.Embed(
            title = "Profile Stats",
            description = f"**Wallet:** {data['wallet']:,d}\n**Bank:** {data['bank']:,d}/{data['banklimit']:,d}",
            color = random.choice(self.bc.color_list)
        )
        embed.add_field(name="Leveling", value="**Level** - {}\n**XP** - {}".format(data["level"], data["xp"]))

    @commands.command()
    async def shop(self,ctx,item=None):
        await self.check_acc(ctx.author)
        if not item:
            em = discord.Embed(
                title="Economy Shop",
                color=random.choice(self.bc.color_list)
            )
            for item in shop:
                if not item["hidden"]:
                    em.add_field(name=f'{item["name"]} — {item["cost"]:,d}',value="{}\nID: `{}`".format(item["desc"], item["id"]), inline=False)
            await ctx.send(embed=em)
        else:
            await self.check_acc(ctx.author)
            data = await self.bc.economy.find(ctx.author.id)
            name_ = None
            item_name = item.lower()
            for item in shop:
                if item_name == item["id"]:
                    name_ = item
                    break
            if not name_:
                for item in shop:
                    if item_name in item["id"]:
                        name_ = item
                        break
            if not name_:
                return await ctx.send("I could not find that item in the shop! Please check your spelling!")

            iteminbag = False
            baggeditem = {}
            for item in data["bag"]:
                if item["name"] == name_["name"]:
                    iteminbag = True
                    baggeditem = item
                    break
            if iteminbag:
                amount = baggeditem["amount"]
            else:
                amount = 0
            
            embed = discord.Embed(
                title=name_["name"] + " ({} Owned)".format(amount),
                description=name_["desc"] + "\n\n**BUY** - {} coins\n**SELL** - {} coins".format(name_["cost"], int(name_["cost"] / 3))
            )

            await ctx.send(embed = embed)


    @commands.command(aliases=["pm"])
    @commands.check(custom_cooldown(1,30,1,12,BucketType.user))
    async def postmeme(self, ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        choices = ["d", "a", "n", "k"]
        res = await self.check_for(ctx.author, "laptop")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a laptop!")
        await ctx.send("""
- `D` **Dank meme**
- `A` **A meme**
- `N` **Normie meme**
- `K` **Kool meme**
""")    
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        try:
            msg = await self.bc.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("Your choices have timed out")
        else:
            if msg.content.lower() in choices:
                earnings = random.randrange(0, 3000)
                data["wallet"] += earnings
                await ctx.send("You posted your meme and you got **{}** coins from it".format(earnings))
                await self.bc.economy.upsert(data)
            else:
                return await ctx.send("You did not enter the choices right")

    @commands.command()
    async def prestige(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "prestige" not in data:
            data["prestige"] = 0
        if data["wallet"] <= 5000000:
            return await ctx.send("You do not have 5 million coins to prestige!")
        data["prestige"] += 1
        embed = discord.Embed(
            title = "Prestige Rewards",
            description = "**You have now reached prestige {}**\nYour inventory and coins have been reset but you get the following things:".format(data["prestige"]),
            color = random.choice(self.bc.color_list)
        )
        if data["prestige"] in range(0, 6):
            data["bag"] = [{'name': 'Laptop', 'id': 'laptop', 'amount': 1}, {'name': 'Fishing Pole', 'id': 'fishingpole', 'amount': 1}, {'name': 'Basic Lootbox', 'id': 'lootbox', 'amount': 1}]
            data["wallet"] = 0
            data["bank"] = 0
            data["banklimit"] = 75000
            embed.add_field(name="Rewards", value="Laptop x1\nFishing Pole x1\nBasic Lootbox x1\n\nStarter Bank Space: 75k")
        elif data["prestige"] in range(5, 11):
            data["bag"] = [{'name': 'Laptop', 'id': 'laptop', 'amount': 1}, {'name': 'Fishing Pole', 'id': 'fishingpole', 'amount': 1}, {'name': 'Hunting Rifle', 'id': 'rifle', 'amount': 1}, {'name': 'Basic Lootbox', 'id': 'lootbox', 'amount': 2}]
            data["wallet"] = 0
            data["bank"] = 0
            data["banklimit"] = 100000
            embed.add_field(name="Rewards", value="Laptop x1\nFishing Pole x1\nRifle x1\nBasic Lootbox x2\n\nStarter Bank Space: 100k")
        elif data["prestige"] > 15:
            data["bag"] = [{'name': 'Laptop', 'id': 'laptop', 'amount': 1}, {'name': 'Fishing Pole', 'id': 'fishingpole', 'amount': 1}, {'name': 'Hunting Rifle', 'id': 'rifle', 'amount': 1}, {'name': 'Phone', 'id': 'phone', 'amount': 1}, {'name': 'Basic Lootbox', 'id': 'lootbox', 'amount': 2}]
            data["wallet"] = 0
            data["bank"] = 0
            data["banklimit"] = 150000
            embed.add_field(name="Rewards", value="Laptop x1\nFishing Pole x1\nRifle x1\nPhone x1\nBasic Lootbox x2\n\nStarter Bank Space: 150k")
        await ctx.send(embed=embed)
        await self.bc.economy.upsert(data)

    @commands.command()
    @commands.check(custom_cooldown(1,45,1,20,BucketType.user))
    async def hunt(self, ctx):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "rifle")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a hunting rifle!")
        animals = ["skunk", "cow", "rabbit", "bear"]
        randanimal = random.choice(animals)
        chance = random.randrange(0,100)
        if chance < 71:
            await self.add_item(ctx.author, randanimal, 1)
            await ctx.send("You fired your rifle and caught a {}".format(randanimal))
        else:
            await ctx.send("You fired your rifle and the animal got away.")

    @commands.command()
    @commands.check(custom_cooldown(1,45,1,20,BucketType.user))
    async def fish(self, ctx):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "fishingpole")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a fishing pole!")
        fish = random.randrange(1,3)
        await self.add_item(ctx.author, "fish", fish)
        await ctx.send("You have caught {} fish".format(fish))

    @commands.command(aliases=["scout"])
    @commands.check(custom_cooldown(1,30,1,12,BucketType.user))
    async def search(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        await ctx.send("**Where do you want to search?**\nPick one of the options below to search", view=Search(self.bc, ctx))

    @commands.command()
    @commands.check(custom_cooldown(1,30,1,12,BucketType.user))
    async def beg(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        earnings = random.randint(0, 800)
        if earnings in range(0, 200):
            await ctx.send("**Some guy** donated {}".format(earnings))
        if earnings in range(201, 400):
            await ctx.send("**Elon Musk** donated {}".format(earnings))
        if earnings in range(401, 600):
            await ctx.send("**Bill Gates** donated {}".format(earnings))
        if earnings in range(601, 800):
            await ctx.send("**BongoPlayzYT** donated {}".format(earnings))
        data["wallet"] += earnings
        await self.bc.economy.upsert(data)

    @commands.command(aliases=["with"])
    async def withdraw(self,ctx,amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if amount == "all":
            amount = data["bank"]
        if amount == "half":
            amount = data["bank"] / 2
        amount = int(amount)
        
        if amount > data["bank"]:
            return await ctx.send("You dont have that much money in your bank!")

        data["wallet"] += amount
        data["bank"] -= amount
        await self.bc.economy.upsert(data)
        await ctx.send("Successfully withdrew **{}** coins from your bank!".format(amount))

    @commands.command(aliases=["dep"])
    async def deposit(self,ctx,amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if amount == "all":
            amount = data["wallet"]
            if amount + data["bank"] > data["banklimit"]:
                maths = data["wallet"] - data["banklimit"]
                amount = data["wallet"] - maths - data["bank"]
        if amount == "half":
            amount = data["wallet"] / 2

        amount = int(amount)
        if amount > data["wallet"]:
            await ctx.send("You dont have that much money!")
            return
        if amount < 0:
            await ctx.send("Amount must be positive")
            return
        if amount + data["bank"] > data["banklimit"]:
            await ctx.send("You dont have enough space in your bank!")
            return
        
        data["bank"] += amount
        data["wallet"] -= amount
        
        await self.bc.economy.upsert(data)
        await ctx.send("Successfully deposited **{}** coins!".format(amount))


    @commands.command()
    async def rich(self,ctx):
        data = await self.bc.economy.get_all()
        lb = sorted(data, key=lambda x: x["wallet"], reverse=True)
        em = discord.Embed(
            title="Top 10 Global Users With the most amount of money in their wallet"
        )
        index = 0
        for user in lb:
            if index == 10 or index == len(lb):
                break
            else:
                index += 1
                em.add_field(name=f"{index}. {self.bc.get_user(user['_id'])}", value=f"{user['wallet']}", inline=False)
        await ctx.send(embed=em)

    @commands.command()
    async def buy(self,ctx,item,amount=1):
        await self.check_acc(ctx.author)
        res = await self.buy_item(ctx.author, item, amount)
        if not res[0]:
            if res[1] == 1:
                return await ctx.send("That item was not found!")
            if res[1] == 2:
                return await ctx.send("This item cannot be bought!")
            if res[1] == 3:
                return await ctx.send("You don't have enough money in your wallet for this!")
        await ctx.send("Item Bought Successfully!")

    @commands.command()
    async def sell(self,ctx,item,amount=1):
        await self.check_acc(ctx.author)
        res = await self.sell_item(ctx.author, item, amount)
        if not res[0]:
            if res[1] == 1:
                return await ctx.send("That item was not found!")
            if res[1] == 2:
                return await ctx.send("You don't have that much of that item to sell!")
        name_ = None
        item_name = item.lower()
        for item in shop:
            if item_name == item["id"]:
                name_ = item
                break
        if not name_:
            for item in shop:
                if item_name in item["id"]:
                    name_ = item
                    break
        if not name_:
            return await ctx.send("I could not find that item in the shop! Please check your spelling!")
        await ctx.send("Item Sold Successfully for {} coins!".format(int(name_["cost"] / 3)))

    @commands.command(aliases=["inv"])
    async def inventory(self,ctx, member:discord.Member=None):
        member = member or ctx.author
        await self.check_acc(member)
        data = await self.bc.economy.find(member.id)
        embed = discord.Embed(
            title="{}'s inventory".format(member.name),
            color = random.choice(self.bc.color_list)
        )
        if len(data["bag"]) == 0:
            embed.add_field(name="This inventory is empty!", value="Use the shop command to get some items!")
        else:
            for item in data["bag"]:
                embed.add_field(name=f"{item['name']} ─ {item['amount']:,d}", value="ID: `{}`".format(item["id"]), inline=False)
        await ctx.send(embed=embed)

    @commands.command(description="Turn this on so no one can rob you")
    @commands.check(custom_cooldown(1,45,1,20,BucketType.user))
    async def passive(self, ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        data["passive"] = not data["passive"]
        ternary = "enabled" if data["passive"] else "disabled"
        await ctx.send(f"Your passive mode is now {ternary}")
        await self.bc.economy.upsert(data)

    @commands.command(description="rob a person")
    @commands.check(custom_cooldown(1,45,1,20,BucketType.user))
    async def rob(self,ctx,member:discord.Member):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        await self.check_acc(member)
        data2 = await self.bc.economy.find(member.id)
        earnings = random.randint(0,data2["wallet"])
        if data2["passive"]:
            await ctx.send(
                "This person is in passive mode leave him alone :(_ _")
            return
        if data["passive"]:
            await ctx.send(
                "Mate you are in passive mode so you cant rob someone"
            )
            return
        data["wallet"] += earnings
        data2["wallet"] -= earnings
        await ctx.send("You robbed this person and got {}".format(earnings))
        await self.bc.economy.upsert(data)
        await self.bc.economy.upsert(data2)

    @commands.command()
    async def share(self,ctx,member:discord.Member, amount:int):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        await self.check_acc(member)
        data2 = await self.bc.economy.find(member.id)
        if amount > data["wallet"]:
            return await ctx.send("You dont have that much money!")
        if data["passive"]:
            return await ctx.send("You are in passive mode you have to turn that off to share coins!")
        if data2["passive"]:
            return await ctx.send("This person has passive mode on so you cannot share coins to them!")
        data["wallet"] -= amount
        data2["wallet"] += amount
        await ctx.send("You have now shared **{}** to `{}`".format(amount, member))
        await self.bc.economy.upsert(data)
        await self.bc.economy.upsert(data2)

    @commands.command(description="rob a person", usage="<user>")
    async def heist(self, ctx, member: discord.Member):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        await self.check_acc(member)
        data2 = await self.bc.economy.find(member.id)
        if data["wallet"] < 1000:
            await ctx.send("You need atleast 1000 coins to start a heist!")
            return
        if data2["bank"] < 1000:
            await ctx.send("this person doesnt have enough for a good heist")
            return
        if data2["passive"]:
            await ctx.send(
                "This person is in passive mode leave him alone :(_ _")
            return
        if data["passive"]:
            await ctx.send(
                "Mate you are in passive mode so you cant heist against someone"
            )
            return
        msg = await ctx.send(
            "aight everyone looks like we gonna bust open a bank. React to this message within 120 seconds to join. Must have 1000 coins to join. Must have atleast 2 people to start."
        )

        await msg.add_reaction("👍")

        data = {
            '_id': member.id,
            'started': datetime.datetime.now(),
            'duration': 120,
            'channelId': ctx.channel.id,
            'messageId': msg.id,
            'guildId': ctx.guild.id,
            'author': ctx.author.id,
        }
        await self.bc.heists.upsert(data)
        self.bc.heistdata[member.id] = data

    async def check_acc(self, member):
        data = await self.bc.economy.find(member.id)
        if data:
            return True
        else:
            data = {
                "_id": member.id,
                "wallet": 0,
                "bank": 0,
                "banklimit": 50000,
                "claimeddaily": datetime.datetime.now(),
                "claimedweekly": datetime.datetime.now(),
                "prestige": 0,
                "passive": False,
                "xp": 0,
                "level": 1,
                "bag": []
            }
            await self.bc.economy.upsert(data)

    async def check_for(self,member,item_name):
        data = await self.bc.economy.find(member.id)
        name_ = None
        item_name = item_name.lower()
        for item in shop:
            if item_name in item["id"]:
                name_ = item
                break

        if not name_:
            return [False, 1]

        iteminbag = False
        for item in data["bag"]:
            if item["name"] == name_["name"]:
                iteminbag = True
                break
        if not iteminbag:
            return [False, 2]
        
        return [True]

    async def add_item(self, member, item_name, amount):
        data = await self.bc.economy.find(member.id)
        name_ = None
        item_name = item_name.lower()
        for item in shop:
            if item_name == item["id"]:
                name_ = item
                break
        if not name_:
            for item in shop:
                if item_name in item["id"]:
                    name_ = item
                    break
        
        if not name_:
            return [False, 1]
        
        iteminbag = False
        for item in data["bag"]:
            if item["name"] == name_["name"]:
                item["amount"] += amount
                iteminbag = True
                break
        if not iteminbag:
            data["bag"].append({"name": name_["name"], "id": name_["id"], "amount": amount})
        await self.bc.economy.upsert(data)
        return [True]

    async def buy_item(self, member, item_name, amount):
        data = await self.bc.economy.find(member.id)
        name_ = None
        item_name = item_name.lower()
        for item in shop:
            if item_name == item["id"]:
                name_ = item
                break
        if not name_:
            for item in shop:
                if item_name in item["id"]:
                    name_ = item
                    break
        if not name_:
            return [False, 1]

        if not name_["canbuy"]:
            return [False, 2]
        
        amount = int(amount)
        if data["wallet"] < name_["cost"] * amount:
            return [False, 3]
        
        
        iteminbag = False
        for item in data["bag"]:
            if item["name"] == name_["name"]:
                item["amount"] += amount
                data["wallet"] -= name_["cost"] * amount
                iteminbag = True
                break
        if not iteminbag:
            data["bag"].append({"name": name_["name"], "id": name_["id"], "amount": amount})
            data["wallet"] -= name_["cost"] * amount
        await self.bc.economy.upsert(data)
        return [True]
    
    async def remove_item(self, member, item_name, amount):
        data = await self.bc.economy.find(member.id)
        name_ = None
        for item in data["bag"]:
            if item_name in item["id"]:
                name_ = item
                break
        
        if not name_:
            return [False, 1]

        amount = int(amount)
        if amount > name_["amount"]:
            return [False, 2]

        for item in data["bag"]:
            if item == name_:
                item["amount"] -= amount
                if item["amount"] == 0:
                    data["bag"].remove(item)
                break
        await self.bc.economy.upsert(data)
        return [True]

    async def sell_item(self, member, item_name, amount):
        data = await self.bc.economy.find(member.id)
        name_ = None
        for item in data["bag"]:
            if item_name in item["id"]:
                name_ = item
                break
        
        if not name_:
            return [False, 1]

        amount = int(amount)
        if amount > name_["amount"]:
            return [False, 2]

        worth = 0
        for item in shop:
            if item["id"] == name_["id"]:
                worth = round((item["cost"] / 3) * amount)
                break

        for item in data["bag"]:
            if item == name_:
                item["amount"] -= amount
                data["wallet"] += worth
                if item["amount"] == 0:
                    data["bag"].remove(item)
                break
        await self.bc.economy.upsert(data)
        return [True]

def setup(bc):
    bc.add_cog(Economy(bc))