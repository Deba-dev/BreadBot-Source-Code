import discord
from discord.ext import commands
import json
import random
from random import choice



class Ranks(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    mainshop = [{
        "name": "DaneEssence",
        "price": 100000,
        "description": "essence of dane"
    },
                {
                    "name": "Laptop",
                    "price": 5000,
                    "description": "Use this for the internet command"
                },
                {
                    "name": "DaneCoin",
                    "price": 1000000,
                    "description": "flex money"
                },
                {
                    "name": "fishingpole",
                    "price": 5000,
                    "description":
                    "get a chance to get a fish and sell it"
                },
                {
                    "name": "fishy",
                    "price": 200,
                    "description": "sell this"
                },
                {
                    "name": "rifle",
                    "price": 10000,
                    "description": "use this to hunt animals for a good price"                    
                },
                {
                    "name": "dead_animal",
                    "price": 500,
                    "description": "sell this"                    
                },
                {
                    "name": "LootBox",
                    "price": None,
                    "description": "Get this from each 10 levels you level up with cool stuff inside"                    
                }]
    """
    @commands.Cog.listener()
    async def on_command_completion(self,ctx):

        await self.open_account(ctx.author)
        data = await self.bc.prefixes.get_by_id(ctx.guild.id)
        if not data or "prefix" not in data:
            prefix = self.bc.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        bal = await self.update_bank(ctx.author)
        maths = bal[4] % 5
        maths = int(maths)
        await self.update_bank(ctx.author, 1, "xp")
        if bal[3] > 100 or bal[3] == 100:
            await self.update_bank(ctx.author, 20000, "bnklmt")
            await self.update_bank(ctx.author, 1, "level")
            await self.update_bank(ctx.author, -1 * bal[3], "xp")
        if maths == 0 and bal[3] == 1:
            await self.give1(ctx.author, "LootBox", 1)
        else:
            pass
    """
    @commands.Cog.listener()
    async def on_message(self,msg):
        data = await self.bc.ranks.find(msg.guild.id)
        if isinstance(msg.channel, discord.DMChannel):
            return
        if msg.author.bot:
            return
        if data is None:
            data = {"id":msg.guild.id, "multi":1, "message":"{member} you just leveled up to level {level} GG!","channel": None, "members": [], "blacklisted": [], "rewards": {}}
            data["members"].append({"userid": msg.author.id, "level":1, "xp": 0, "maxXp": 35})
        isindata = False    
        for member in data["members"]:
            if member["userid"] == msg.author.id:
                isindata = True
        if not isindata:
            data["members"].append({"userid": msg.author.id, "level":1, "xp": 0, "maxXp": 35})
        user = next((user for user in data["members"] if user['userid'] == msg.author.id), None)
        user["xp"] += 1*data["multi"]
        rank = data["members"].index(user) 
        if user["xp"] >= user["maxXp"]:
            user["level"] += 1
            newxp = user["maxXp"] + 40 * user["level"]
            newxp = int(newxp)
            user["maxXp"] = newxp
            user["xp"] = 0
            if data["channel"] is not None:
                channel = self.bc.get_channel(int(data["channel"]))
                setmessage = data["message"].replace("{member}", f"<@{msg.author.id}>")
                setmessage = setmessage.replace("{level}", str(user["level"]))
                setmessage = setmessage.replace("{pastlevel}", str(user["level"]-1))
                setmessage = setmessage.replace("{rank}", str(rank + 1))
                await channel.send(setmessage)
        if data["members"][rank-1]["level"] < user["level"] and rank != 0:
            saveddict = user
            data["members"].remove(user)
            data["members"].insert(rank-1, saveddict) 
            await self.bc.ranks.upsert(data)
        elif data["members"][rank-1]["level"] == user["level"] and data["members"][rank-1]["xp"] < user["xp"]and rank != 0:
            saveddict = user
            data["members"].remove(user)
            data["members"].insert(rank-1, saveddict)
        if str(user["level"]) in data["rewards"].keys():
            role = discord.utils.get(msg.guild.roles, id=int(data["rewards"][str(user["level"])]))
            await msg.author.add_roles(role)
        

        await self.bc.ranks.upsert(data)


    
    
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
            users[str(user.id)]["passive"] = 'false'

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)
        return True

    async def get_bank_data(self):
        with open("mainbank.json", "r") as f:
            users = json.load(f)

        return users

    async def update_bank(self, user, change=0, mode="wallet"):
        users = await self.get_bank_data()

        users[str(user.id)][mode] += int(change)

        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

        bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"], users[str(user.id)]["bnklmt"], users[str(user.id)]["xp"], users[str(user.id)]["level"]]
        return bal

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

def setup(bc):
    bc.add_cog(Ranks(bc))