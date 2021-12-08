import discord
from discord import commands as slash
from discord.ext import commands
import random
import time

class test(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @slash.slash_command()
    async def ping(self, ctx):
        counter = 0 
        msg = await ctx.respond("Getting Bot Ping...")
        msg = await msg.original_message()
        await msg.edit("Testing how long it gets from here to discord hq 0/3")
        em = discord.Embed(
            title="Bot Latency",
            color = random.choice(self.bc.color_list)
        )
        speeds = []
        for i in range(3):
            counter += 1
            start = time.perf_counter()
            await msg.edit(content="Testing how long it gets from here to discord hq {}/3".format(counter))
            end = time.perf_counter()
            speed = round((end - start) * 1000)
            speeds.append(speed)
            if speed < 150:
                em.add_field(name="Ping {}".format(counter), value=f"{speed}ms | Good")
            elif speed in range(150, 250):
                em.add_field(name="Ping {}".format(counter), value=f"{speed}ms | Medium")
            elif speed > 250:
                em.add_field(name="Ping {}".format(counter), value=f"{speed}ms | Bad")
        await msg.edit(content=f"`{speed}ms` Ping")
        em.add_field(name="Websocket Ping:",value=f"{round(self.bc.latency * 1000)}ms")
        sum = 0
        for speed in speeds:
            sum += speed
        average = sum / 3
        newaverage = int(average * 100)
        roundedavg = newaverage / 100
        em.add_field(name="Average Ping:", value=f"{roundedavg}ms")
        await msg.edit(embed=em)

def setup(bc):
    bc.add_cog(test(bc))