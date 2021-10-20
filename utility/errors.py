class Blacklisted(Exception):
    def __init__(self,ctx):
        self.ctx = ctx
    
    async def send(self):
        await self.ctx.send("You are blacklisted from this bot!")

class Premium(Exception):
    def __init__(self,ctx):
        self.ctx = ctx

    async def send(self):
        await self.ctx.send("You can only use this command in premium servers!")