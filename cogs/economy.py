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
from utility import Pag

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
        "name": "Gaming PC", 
        "desc": "Used to start the Cryptocurrency known as Dough", 
        "cost": 30000,
        "id": "gamingpc",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "GPU", 
        "desc": "Main Component with your gaming pc", 
        "cost": 35000,
        "id": "gpu",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Water Cooler", 
        "desc": "Must have in order to not overheat your pc", 
        "cost": 25000,
        "id": "watercooler",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Power Supply", 
        "desc": "Needed for your gaming pc", 
        "cost": 40000,
        "id": "powersupply",
        "hidden": False,
        "canbuy": True
    },
    {
        "name": "Bread Coin", 
        "desc": "A flex item.", 
        "cost": 100000,
        "id": "Dough",
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
        "hidden": True,
        "canbuy": False
    },
    {
        "name": "Premium Lootbox", 
        "desc": "Use this with premlootbox command", 
        "cost": 0,
        "id": "premlootbox",
        "hidden": True,
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

class NFTBuy(discord.ui.View):
    def __init__(self, ctx, nft_id:int, offer:int):
        self.bc = ctx.bot
        self.nft_id = nft_id
        self.offer = offer
        self.ctx = ctx
        super().__init__(timeout=300)

    async def on_timeout(self):
        return await self.ctx.send("{} Seems like your offer expired for this person".format(self.ctx.author.mention))

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def buy_confirm(self,button,interaction):
        data = await self.bc.nfts.find(self.nft_id) 
        eco = await self.bc.economy.find(self.ctx.author.id)

        em = discord.Embed(
            title="Offer on {} (ID: {})".format(data["name"], data["_id"]),
            description="{} wants to buy your NFT: {} for {} Dough".format(self.ctx.author, data["name"], self.offer),
            color=random.choice(self.bc.color_list)
        )
        
        if eco["Dough"] < self.offer:
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(embed=em, view=self)
            return await interaction.response.send_message("Seems like this person does not have enough dough to cover their offer!", ephemeral=True)
        eco["Dough"] -= self.offer
        await self.bc.economy.upsert(eco)
        eco = await self.bc.economy.find(interaction.user.id)
        eco["Dough"] += self.offer
        await self.bc.economy.upsert(eco)
        data["owner"] = self.ctx.author.id
        await self.bc.nfts.upsert(data)
        for child in self.children:
            child.disabled = True
        self.stop()
        await interaction.message.edit(embed=em, view=self)
        await self.ctx.send("{} Seems like {} has accepted your offer!".format(self.ctx.author.mention, interaction.user))
        return await interaction.response.send_message("You have sold this NFT and you aquired {} Dough".format(self.offer), ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def nft_decline(self,button,interaction):
        data = await self.bc.nfts.find(self.nft_id)
        em = discord.Embed(
            title="Offer on {} (ID: {})".format(data["name"], data["_id"]),
            description="{} wants to buy your NFT: {} for {} Dough".format(self.ctx.author, data["name"], self.offer),
            color=random.choice(self.bc.color_list)
        )
        
        for child in self.children:
            child.disabled = True
        self.stop()
        await interaction.message.edit(embed=em, view=self)
        await self.ctx.send("{} Seems like {} has declined your offer!".format(self.ctx.author.mention, interaction.user))

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
        self.mons = self.give_mons.start()
        self._running = {}

    def cog_unload(self):
        self.heists.cancel()
        self.mons.cancel()

    @tasks.loop(seconds=5)
    async def give_mons(self):
        await self.bc.rewind.wait()
        data = await self.bc.economy.get_all()
        for data in data:
            if "Dough" not in data:
                continue
            self._running[str(data["_id"])] = True
            if data["gpu"] - data["cooling"] > 20:
                user = self.bc.get_user(data["_id"])
                try:
                    await user.send("Your GPU Overheated and exploded your setup!")
                except:
                    pass
                data["gpu"] = 1
                data["cooling"] = 1
                data["power"] = 1
                await self.bc.economy.upsert(data)
                self._running[str(data["_id"])] = False
                continue
            if data["gpu"] - data["power"] > 15:
                level_multi = int(data["gpu"] / 5) + 1
                decreased_by = 1 - (((data["gpu"] - data["power"]) - 15) / 15)
                if decreased_by < 0.001:
                    self._running[str(data["_id"])] = False
                    continue
                data["Dough"] += ((round((0.005 * data["gpu"]) * 1000) / 1000) * level_multi) * decreased_by

                data["Dough"] = round(data["Dough"] * 1000) / 1000
                self._running[str(data["_id"])] = False
                await self.bc.economy.upsert(data)
                continue
            level_multi = int(data["gpu"] / 5) + 1
            data["Dough"] += (round((0.005 * data["gpu"]) * 1000) / 1000) * level_multi

            data["Dough"] = round(data["Dough"] * 1000) / 1000
            self._running[str(data["_id"])] = False
            await self.bc.economy.upsert(data)

    @commands.group(invoke_without_command=True,aliases=["up"])
    async def upgrade(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="upgrade")
    
    @upgrade.command(description="Upgrade your GPU", aliases=["g"], name="gpu")
    async def up_gpu(self,ctx,amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "Dough" not in data:
            return await ctx.send("You need Dough before you can upgrade your gpu!")
        if amount == "all" or amount == "a":
            _ = 1
            cost = 0
            while True:
                cost += int(35000 + (500 * data["gpu"]) * data["gpu"])
                if data["wallet"] < cost:
                    cost -= int(35000 + (500 * data["gpu"]) * data["gpu"])
                    _ -= 1
                    amount = _ - 1
                    data["gpu"] -= 1
                    if amount <= 0:
                        return await ctx.send("You do not have enough money to upgrade atleast once")
                    break
                data["gpu"] += 1
                _ += 1
        else:
            cost = 0
            _amount = int(amount)
            _ = 1
            for i in range(_amount):
                data["gpu"] += 1
                cost += int(35000 + (500 * data["gpu"]) * data["gpu"])
                if data["wallet"] < cost:
                    cost -= int(35000 + (500 * data["gpu"]) * data["gpu"])
                    _ -= 1
                    amount = _
                    data["gpu"] -= 1
                    if amount <= 0:
                        return await ctx.send("You do not have enough money to upgrade atleast once")
                    return await ctx.send("You do not have enough coins to upgrade that many times! It would cost {} to upgrade {} times".format(int(40000 + (2000 * (_ + 1)) * data["gpu"]), amount))
                    break
                amount = _
                _ += 1
        data["wallet"] -= cost
        await ctx.send("Successfully upgraded your gpu for: {} coins\n\n**[Level {} >> Level {}]**".format(cost, data["gpu"] - amount, data["gpu"]))
        await self.bc.economy.upsert(data)

    @upgrade.command(description="Upgrade your cooling", aliases=["c"], name="cooling")
    async def up_cooling(self,ctx,amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "Dough" not in data:
            return await ctx.send("You need Dough before you can upgrade your cooling!")
        if amount == "all" or amount == "a":
            _ = 1
            cost = 0
            while True:
                cost += int(25000 + (500 * data["cooling"]) * data["cooling"])
                if data["wallet"] < cost:
                    cost -= int(25000 + (500 * data["cooling"]) * data["cooling"])
                    _ -= 1
                    amount = _ - 1
                    data["cooling"] -= 1
                    if amount <= 0:
                        return await ctx.send("You do not have enough money to upgrade atleast once")
                    break
                data["cooling"] += 1
                _ += 1
        else:
            _amount = int(amount)
            _ = 1
            cost = 0
            for i in range(_amount):
                data["cooling"] += 1
                cost += int(25000 + (500 * data["cooling"]) * data["cooling"])
                if data["wallet"] < cost:
                    cost -= int(25000 + (500 * data["cooling"]) * data["cooling"])
                    _ -= 1
                    amount = _
                    data["cooling"] -= 1
                    if amount <= 0:
                        return await ctx.send("You do not have enough money to upgrade atleast once")
                    return await ctx.send("You do not have enough coins to upgrade that many times! It would cost {} to upgrade {} times".format(int(25000 + (2000 * (_ + 1)) * data["cooling"]), amount))
                    break
                amount = _
                _ += 1
        data["wallet"] -= cost
        await ctx.send("Successfully upgraded your cooling for: {} coins\n\n**[Level {} >> Level {}]**".format(cost, data["cooling"] - amount, data["cooling"]))
        await self.bc.economy.upsert(data)

    @upgrade.command(description="Upgrade your power", aliases=["p"], name="power")
    async def up_power(self,ctx,amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "Dough" not in data:
            return await ctx.send("You need Dough before you can upgrade your power!")
        if amount == "all" or amount == "a":
            _ = 1
            cost = 0
            while True:
                cost += int(40000 + (500 * data["power"]) * data["power"])
                if data["wallet"] < cost:
                    cost -= int(40000 + (500 * data["power"]) * data["power"])
                    _ -= 1
                    amount = _ - 1
                    data["power"] -= 1
                    if amount <= 0:
                        return await ctx.send("You do not have enough money to upgrade atleast once")
                    break
                data["power"] += 1
                _ += 1
        else:
            _amount = int(amount)
            _ = 1
            cost = 0
            for i in range(_amount):
                data["power"] += 1
                cost += int(40000 + (500 * data["power"]) * data["power"])
                if data["wallet"] < cost:
                    cost -= int(40000 + (500 * data["power"]) * data["power"])
                    _ -= 1
                    amount = _
                    data["power"] -= 1
                    if amount <= 0:
                        return await ctx.send("You do not have enough money to upgrade atleast once")
                    return await ctx.send("You do not have enough coins to upgrade that many times! It would cost {} to upgrade {} times".format(int(40000 + (2000 * (_ + 1)) * data["power"]), amount))
                    break
                amount = _
                _ += 1
        data["wallet"] -= cost
        await ctx.send("Successfully upgraded your power for: {} coins\n\n**[Level {} >> Level {}]**".format(cost, data["power"] - amount, data["power"]))
        await self.bc.economy.upsert(data)

    async def cog_before_invoke(self, ctx):
        await self.bc.rewind.wait()
        self._running[str(ctx.author.id)] = False if str(ctx.author.id) not in self._running else self._running[str(ctx.author.id)]
        if self._running[str(ctx.author.id)]:
            while True:
                if not self._running[str(ctx.author.id)]:
                    break
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "xp" not in data:
            data["xp"] = 0
        if "level" not in data:
            data["level"] = 1
        if data["xp"] >= 100:
            data["banklimit"] += random.randint(2000,3000)
            data["level"] += 1
            data["xp"] = 0
        data["xp"] += 1
        await self.bc.economy.upsert(data)

    @commands.command(description="Start your journy for Dough")
    async def Dough(self,ctx):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "gamingpc")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You need a gaming pc!")
        res = await self.check_for(ctx.author, "powersupply")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You need a power supply!")
        res = await self.check_for(ctx.author, "gpu")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You need a gpu!")
        res = await self.check_for(ctx.author, "watercooler")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You need a water cooler!")
        data = await self.bc.economy.find(ctx.author.id)
        if "Dough" in data:
            level_multi = int(data["gpu"] / 5) + 1
            estimate = (round((0.005 * data["gpu"]) * 1000) / 1000) * level_multi
            if data["gpu"] - data["power"] > 15:
                estimate *= 1 - (((data["gpu"] - data["power"]) - 15) / 15)
                estimate = round(estimate * 1000) / 1000
            em = discord.Embed(
                title="Dough Mining Stats"
            )
            em.add_field(name="Power Stats", value="Level: {}\nEnergy Consumption: {}%".format(data["power"], (((data["gpu"] - data["power"]) - 15) / 15) * 100 if (((data["gpu"] - data["power"]) - 15) / 15) * 100 > 0 else 0))
            em.add_field(name="GPU Stats", value="Level: {}\nEstimated Dough per 5 seconds: {}".format(data["gpu"], estimate))
            em.add_field(name="Cooling Stats", value = "Level: {}\nOverheat Progress: {}%".format(data["cooling"], ((data["gpu"] - data["cooling"]) / 20) * 100 if ((data["gpu"] - data["cooling"]) / 20) * 100 > 0 else 0))
            return await ctx.send(embed=em)
        data["Dough"] = 0
        data["gpu"] = 1
        data["power"] = 1
        data["cooling"] = 1
        await ctx.send("You can now begin your journy on getting Dough! I will DM you if there is an issue with the power supply or anything!")
        await self.bc.economy.upsert(data)

    @commands.group(invoke_without_command=True, description="Check out or make some cool NFTs")
    async def nft(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="nft")

    @nft.command(name="lookup", aliases=["view"], description="Look at an NFT by its ID")
    async def nft_lookup(self,ctx,nft_id:int):
        data = await self.bc.nfts.find(nft_id)
        if not data:
            return await ctx.send("That NFT does not exist!")
        total = 0
        for offer in data["offers"]:
            total += offer
        owner = self.bc.get_user(data["owner"])
        em = discord.Embed(
            title = data["name"],
            description = "**Estimated Value:** {} Dough\n**Owner:** {}".format(total / len(data["offers"]), owner.mention),
            color = random.choice(self.bc.color_list)
        )
        em.set_image(url=data["image"])
        await ctx.send(embed=em)

    @nft.command(name="create", aliases=["make"], description="Create your own NFT!") 
    async def nft_create(self,ctx,image, *, name):
        if not image.startswith("https://"):
            return await ctx.send("Image must be https!")
        if not image.endswith((".png", ".jpg", ".jpeg", ".gif")):
            return await ctx.send("Image must be .png, .jpg, .jpeg, or .gif")
        eco = await self.bc.economy.find(ctx.author.id)
        if not eco or "Dough" not in eco:
            return await ctx.send("You need to mine some dough before you can make an NFT!")
        latest_nft = 0
        nfts = await self.bc.nfts.get_all()
        for nft in nfts:
            if nft["_id"] > latest_nft:
                latest_nft = nft["_id"]
        data = {"_id": latest_nft + 1, "owner": ctx.author.id, "offers": [10], "name": name, "image": image}
        if eco["Dough"] < 10:
            return await ctx.send("You need 10 Dough to make an NFT")
        eco["Dough"] -= 10
        await self.bc.economy.upsert(eco)
        await self.bc.nfts.upsert(data)
        await ctx.send("Successfully made your NFT for 10 dough")

    @nft.command(name="buy", aliases=["offer"], description="Make an offer for an NFT", hidden=True)
    async def nft_buy(self,ctx,nft_id:int,offer:int):
        data = await self.bc.nfts.find(nft_id)
        if not data:
            return await ctx.send("That NFT does not exist!")
        if data["owner"] == ctx.author.id:
            return await ctx.send("You cannot buy your own NFT")
        eco = await self.bc.economy.find(ctx.author.id)
        if "Dough" not in eco:
            return await ctx.send("You need some dough first!")
        if eco["Dough"] < offer:
            return await ctx.send("You do not have enough dough for this offer!")
        if offer <= 0:
            return await ctx.send("Offer must be a positive number!")
        user = self.bc.get_user(data["owner"])
        em = discord.Embed(
            title="Offer on {} (ID: {})".format(data["name"], data["_id"]),
            description="{} wants to buy your NFT: {} for {} Dough".format(ctx.author, data["name"], offer),
            color=random.choice(self.bc.color_list)
        )
        await user.send(embed=em,view=NFTBuy(ctx,nft_id,offer))
        data["offers"].append(offer)
        await self.bc.nfts.upsert(data)
        await ctx.send("Offer sent! I will mention you when something happens!")

    @nft.group(invoke_without_command=True, description="Browse NFTs that were created")
    async def browse(self,ctx):
        await ctx.invoke(self.bc.get_command("help"), entity="nft browse")

    @browse.command(name="hightolow",aliases=["htl"],description="Search NFTs from high values to low values")
    async def browse_htl(self,ctx):
        data = await self.bc.nfts.get_all()
        for _data in data:
            total = 0
            for offer in _data["offers"]:
                total += offer
            _data["offers"] = int(total / len(_data["offers"]))
        data = sorted(data, key=lambda x: x["offers"], reverse=True)
        pages = []
        for nft in data:
            pages.append({"content": "**{} (ID: {})**\n\n**Average Value:** {}\n**Owner:** {}".format(nft["name"], nft["_id"], nft["offers"], self.bc.get_user(nft["owner"])), "image": nft["image"]})
        await Pag(title="NFTs from High to Low", color=random.choice(self.bc.color_list), entries=pages, length=1).start(ctx)
        
    @commands.command(description="Exchange Dough for Coins")
    async def exchange(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        if "Dough" not in data:
            return await ctx.send("You need some Dough before you can exchange")
        data["wallet"] += int(4500 * data["Dough"])
        await ctx.send("Exchanged your {} Dough into {} Coins".format(data["Dough"], int(4500 * data["Dough"])))
        data["Dough"] = 0
        await self.bc.economy.upsert(data)

    @commands.command(description="Get some money by doing some tasks")
    @commands.check(custom_cooldown(1, 30, 1, 12, BucketType.user))
    async def work(self, ctx):
        await self.check_acc(ctx.author)
        res = await self.check_for(ctx.author, "phone")
        if not res[0]:
            if res[1] == 2:
                return await ctx.send("You do not have a phone to work on!")
        data = await self.bc.economy.find(ctx.author.id)
        topic = words.randtopic()
        work = ["match", "order"]
        chosen = random.choice(work)
        if chosen == "order":
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
        elif chosen == "match":
            colors = ["blue", "yellow", "red", "green"]
            buttons = []
            for x in range(4):
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
            choices = {}
            print(choices)
            choice = 0
            for color in colors:
                choices[color] = buttons[choice]
                choice += 1
            randcolor = random.choice(colors)
            msg = await ctx.send("\n".join([f"`{color}` {word}" for color, word in choices.items()]))
            await asyncio.sleep(5)
            await msg.edit(f"Choose the item that was next to the color {randcolor}", view=working.Match(choices, self.bc, ctx, randcolor))

    @commands.command(description="Collect your weekly coins")
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
            data["claimedweekly"] = datetime.datetime.now()
            await self.bc.economy.upsert(data)
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

    @commands.command(description="Collect your daily coins")
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
            data["claimeddaily"] = datetime.datetime.now()
            await self.bc.economy.upsert(data)
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
        amount = int(amount)
        if amount > 500000:
            return await ctx.send("You can only gamble 500k coins")

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

    @commands.command(description="Gift an item to a user")
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
        amount = int(amount)
        if amount > 500000:
            return await ctx.send("You can only gamble 500k coins")
            
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
        aliases=["bal"],
        description="Look at how much money you have in the bank"
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
        if "Dough" in data:
            em.description += f"\n**Dough:** {data['Dough']}"
        await ctx.send(embed=em)

    @commands.command(description="Look at a more detailed menu of your stats")
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

    @commands.command(description="Check out the cool items in the shop")
    async def shop(self,ctx,item=None):
        await self.check_acc(ctx.author)
        if not item:
            pages = []
            for i in range(0, len(shop), 5):
                shop_items = shop[i : i + 5]
                items_entry = ""

                for item in shop_items:
                    if item["hidden"]:
                        continue
                    desc = item["desc"]
                    _id = item["id"]

                    items_entry += f'**{item["name"]} — {item["cost"]:,d}**\n{desc}\nID: `{_id}`\n\n'
                pages.append(items_entry)
            await Pag(title="Economy Shop", color=random.choice(self.bc.color_list), entries=pages, length=1).start(ctx)
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
                description=name_["desc"] + "\n\n**BUY** - {}\n**SELL** - {} coins".format(str(name_["cost"]) + " coins" if name_["canbuy"] else "NOT FOR SALE", int(name_["cost"] / 3))
            )

            await ctx.send(embed = embed)


    @commands.command(aliases=["pm"], description="Use your laptop to post some reddit memes")
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
            msg = await self.bc.wait_for("message", check=check, timeout=10)
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

    @commands.command(description="Start all over again with a few buffs")
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

    @commands.command(description="Go hunting for some wild animals")
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

    @commands.command(description="Go fishing with your old man")
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

    @commands.command(aliases=["scout"], description="Look for coins around the world")
    @commands.check(custom_cooldown(1,30,1,12,BucketType.user))
    async def search(self,ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        await ctx.send("**Where do you want to search?**\nPick one of the options below to search", view=Search(self.bc, ctx))

    @commands.command(description="Beg for coins.")
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

    @commands.command(aliases=["with"], description="Take some money out of your bank")
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

    @commands.command(aliases=["dep"], description="Put some money into your bank")
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


    @commands.command(description="Check out the top 10 global richest people using this bot")
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

    @commands.command(description="Buy an item from the shop")
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

    @commands.command(description="Sell an item for 1/3 of its price")
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

    @commands.command(aliases=["inv"], description="Check out what items you have in your inventory")
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

    @commands.command(description="Share some coins and bring some joy :)")
    async def share(self,ctx,member:discord.Member, amount:int):
        if amount < 0:
            return await ctx.send("Amount must be a positive number")
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

    @commands.command(description="rob a person's bank", usage="<user>")
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