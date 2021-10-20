import discord
import random
import copy

class OrderButton(discord.ui.Button):
    def __init__(self, label, order, bc, ctx):
        self.bc = bc
        self.order = order
        self.ctx = ctx
        super().__init__(label=label)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return
        view = self.view
        data = await self.bc.economy.find(self.ctx.author.id)
        if self.order.index(self.label) == view.button:
            self.disabled = True
            view.button += 1
            if view.button == 5:
                data["wallet"] += 5000
                await self.bc.economy.upsert(data)
                view.stop()
                await interaction.message.edit("Congrats! You earned 5k coins for your hard work", view=view)
            else:
                await interaction.message.edit("Choose the items in order", view=view)
        else:
            self.style = discord.ButtonStyle.danger
            for child in view.children:
                if child.label != self.label:
                    child.style = discord.ButtonStyle.secondary
                child.disabled = True
            view.stop()
            await interaction.message.edit("You earned no money for working because you failed!", view=view)
            

class Order(discord.ui.View):
    def __init__(self, topic, bc, ctx):
        self.button = 0
        super().__init__()
        originaltopic = copy.copy(topic)
        random.shuffle(topic)
        for item in topic:
            self.add_item(OrderButton(item, originaltopic, bc, ctx))