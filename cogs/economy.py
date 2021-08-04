import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
from copy import deepcopy
from dateutil.relativedelta import relativedelta
import random
import asyncio
import datetime

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
        "id": "fishy",
        "hidden": True,
        "canbuy": False
    }
]

class Blackjack(discord.ui.View):
    def __init__(self, amount, bc, pcards, bcards, ctx, data):
        self.amount = amount
        self.bc = bc
        self.pcards = pcards
        self.bcards = bcards
        self.ctx = ctx
        self.data = data
        self.cardsDrawn = 1
    
    @discord.ui.button(label='Hit', style=discord.ButtonStyle.green)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
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
            await self.ctx.send(embed=em)
            return
        if self.pcards == 21:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You got to 21 before your opponent and won **{self.amount:,d}** coins\n\nYou now have **{self.data["wallet"]+self.amount*2:,d}** coins',
                color=0x00ff00)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            await interaction.message.edit(embed=em)
            self.data["wallet"] += 2 * self.amount
            await self.bc.economy.upsert(self.data)
            return
        if self.cardsDrawn == 5:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You managed to draw 5 cards without busting and earned yourself **{self.amount:,d}** coins\n\nYou now have **{self.data["wallet"]+self.amount*2:,d}** coins',
                color=0x00ff00)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            await interaction.message.edit(embed=em)
            self.data["wallet"] += 2 * self.amount
            await self.bc.economy.upsert(self.data)
            return
        em = discord.Embed(
            title=f"{self.ctx.author.name}'s blackjack game", color=random.choice(self.bc.color_list))
        em.add_field(name=self.ctx.author.name, value=self.pcards)
        em.add_field(name='BreadBot', value='N/A')
        await interaction.message.edit(embed=em)

    @discord.ui.button(label='Stand', style=discord.ButtonStyle.green)
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.pcards < self.bcards:
            em = discord.Embed(
                title=f"{self.ctx.author.name}'s blackjack game",
                description=
                f'You Had Less Cards Than Your Opponent!\n\nYou now have **{self.data["wallet"]:,d}** coins',
                color=0xff0000)
            em.add_field(name=self.ctx.author.name, value=self.pcards)
            em.add_field(name='BreadBot', value=self.bcards)
            await self.bc.economy.upsert(self.data)
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
            return

class Economy(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        self.heists = self.checkHeist.start()

    def cog_unload(self):
        self.heists.cancel()

    @tasks.loop(seconds=15)
    async def checkHeist(self):
        heist = deepcopy(self.bc.heistdata)
        for key, value in heist.items():
            member = value["_id"]
            member = await self.bc.get_user(member)
            msg = value["messageId"]
            author = value['author']
            author = await self.bc.get_user(author)
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
        description='b l a c k j a c k', usage='<amount>', aliases=["bj"])
    async def blackjack(self, ctx, amount):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        pcards = random.randrange(1, 20)
        bcards = random.randrange(1, 20)

        if amount == 'all':
            amount = data["wallet"]
        if amount == 'half':
            amount = data["wallet"] / 2

        amount = int(amount)
        if amount > data["wallet"]:
            await ctx.send("you dont have that much money!")
            return
        if amount < 0:
            await ctx.send("amount must be positive")
            return

        data["wallet"] -= amount

        em = discord.Embed(
            title=f"{ctx.author.name}'s blackjack game", color=random.choice(self.bc.color_list))
        em.add_field(name=ctx.author.name, value=pcards)
        em.add_field(name='BreadBot', value='N/A')
        await ctx.send(
            'Push `Hit` to draw more cards and push `Stand` to end the game with the amount you have now.'
        )
        #await ctx.send(embed=em, view=Blackjack(amount, self.bc, pcards, bcards, ctx, data))
        await ctx.send(embed=em, view=Blackjack())


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
    async def shop(self,ctx):
        await self.check_acc(ctx.author)
        em = discord.Embed(
            title="Economy Shop",
            color=random.choice(self.bc.color_list)
        )
        for item in shop:
            if not item["hidden"]:
                em.add_field(name=f'{item["name"]} — {item["cost"]:,d}',value="{}\nID: `{}`".format(item["desc"], item["id"]), inline=False)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 30, BucketType.user)
    async def postmeme(self, ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        choices = ["d", "a", "n", "k"]
        res = await self.check_for(ctx.author, "laptop")
        if not res[0]:
            if res[0][1] == 2:
                return await ctx.send("You do not have this item!")
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
    @commands.cooldown(1, 45, BucketType.user)
    async def fish(self, ctx):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        res = await self.check_for(ctx.author, "fishingpole")
        if not res[0]:
            if res[0][1] == 2:
                return await ctx.send("You do not have this item!")
        fish = random.randrange(1,3)
        await self.add_item(ctx.author, "fishy", fish)
        await ctx.send("You have caught {} fish".format(fish))

    @commands.command()
    @commands.cooldown(1, 30, BucketType.user)
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
        await ctx.send("Item Sold Successfully!")

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

    @commands.command(description="rob a person")
    async def rob(self,ctx,member:discord.Member):
        await self.check_acc(ctx.author)
        data = await self.bc.economy.find(ctx.author.id)
        await self.check_acc(member)
        data2 = await self.bc.economy.find(member.id)
        earnings = random.randint(0,data2["wallet"])
        if data2["passive"] == "true":
            await ctx.send(
                "This person is in passive mode leave him alone :(_ _")
            return
        if data["passive"] == "true":
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
        if data2["passive"] == "true":
            await ctx.send(
                "This person is in passive mode leave him alone :(_ _")
            return
        if data["passive"] == "true":
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
                "nextdaily": None,
                "nextweekly": None,
                "passive": False,
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
        print(data["bag"])
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