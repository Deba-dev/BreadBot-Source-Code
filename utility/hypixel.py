import requests
import math
apikey = [None]
BASE = 10_000
GROWTH = 2_500
REVERSE_PQ_PREFIX = -(BASE - 0.5 * GROWTH) / GROWTH
REVERSE_CONST = REVERSE_PQ_PREFIX
GROWTH_DIVIDES_2 = 2 / GROWTH


def setkey(key):
    apikey[0] = key


class Player:
    def __init__(self,name):
        self.playername = name
        self.uuid = self.getuuid(self.playername)
        self.apikey = self.getkey()
        self.playerdata = None

    def getkey(self):
        return apikey[0]

    def getuuid(self,name):
        res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}").json()
        return res["id"]

    def getdata(self):
        response = requests.get('https://api.hypixel.net/player?key='+self.apikey+'&uuid='+self.uuid).json()
        guild = requests.get('https://api.hypixel.net/guild?key='+self.apikey+'&player='+self.uuid).json()
        recentgames = requests.get('https://api.hypixel.net/recentgames?key='+self.apikey+'&uuid='+self.uuid).json()
        if response["success"] == False and response["cause"] == "Invalid API key":
            return None
        player = response.get("player")
        guild = guild.get("guild")
        recentgames = recentgames.get("games")
        rank = player["packageRank"] if "packageRank" in player.keys() else player["newPackageRank"]
        if rank == "VIP":
            rank = "VIP"
        elif rank == "VIP_PLUS":
            rank = "VIP+"
        elif rank == "MVP":
            rank = "MVP"
        elif rank == "MVP_PLUS":
            rank = "MVP+"
        else:
            rank = None
        data = {
            "name": player["displayname"],
            "rank": rank,
            "level": math.floor(1 + REVERSE_PQ_PREFIX + math.sqrt(REVERSE_CONST + GROWTH_DIVIDES_2 * player["networkExp"])),
            "recentgames": (recentgames 
                            if len(recentgames) > 0 
                            else None),
            "guild": ({
                        "name": guild["name"],
                        "members": guild["members"],
                        "ranks": guild["ranks"]
                     }
                     if guild is not None
                     else None)
        }
        return data
        
class SkyblockPlayer:
    def __init__(self,user):
        self.playername = user
        self.uuid = self.getuuid(self.playername)
        self.apikey = self.getkey()

    def getkey(self):
        return apikey[0]

    def getuuid(self,name):
        res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}").json()
        return res["id"]
    
    def getauctions(self):
        res = requests.get(f"https://api.hypixel.net/skyblock/auction?key={self.apikey}&uuid={self.uuid}").json()
        return res["auctions"]

    def getprofile(self):
        res = requests.get(f"https://api.hypixel.net/skyblock/profile?key={self.apikey}&profile={self.uuid}").json()
        return res["profile"] if res["success"] else None
    
class Skyblock:
    def allauctions(self, page=0):
        res = requests.get("https://api.hypixel.net/skyblock/auctions").json()
        return res
    
    def getbazaar(self,item):
        item = item.upper().replace(" ", "_")
        res = requests.get(f"https://api.hypixel.net/skyblock/bazaar").json()
        products = res["products"][item] if item in res["products"].keys() else None
        return products