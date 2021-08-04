import discord
import DiscordUtils
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps, ImageFont
import io
import datetime
import json
import random
from captcha.image import ImageCaptcha
import asyncio
image = ImageCaptcha()
# Requires: pip install DiscordUtils


class Invites(commands.Cog):
    def __init__(self, bc):
        self.bc = bc
        bc.tracker = DiscordUtils.InviteTracker(bc)
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bc.tracker.cache_invites()
    
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.bc.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        botcount = len([member for member in guild.members if member.bot])
        if botcount >= 50:
            await guild.leave()
            return
        await self.bc.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.bc.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bc.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'{member} has joined a server')
        try:
            inviter = await self.bc.tracker.fetch_inviter(member)
            if inviter is None:
                class NotFoundInvite:
                    def something(self):
                        return None
                inviter = NotFoundInvite
                inviter.mention = "I could not find who invited!"
            data = await self.bc.invites.find(inviter.id)
            if data is None:
                data = {"_id": inviter.id, "count": 0, "usersInvited": []}
        except Exception as e:
            #print(e)
            class NotFoundInvite:
                def something(self):
                    return None
            inviter = NotFoundInvite
            inviter.mention = "I could not find who invited!"
        if inviter.mention != "I could not find who invited!":
            data["count"] += 1
            data["usersInvited"].append(member.id)
            await self.bc.invites.upsert(data)
        else:
            data = {}
            data["count"] = None
        year = int(datetime.datetime.now().strftime("%Y")) - int(
            member.created_at.strftime("%Y"))

        month = int(datetime.datetime.now().strftime("%m")) - int(
            member.created_at.strftime("%m"))
        if month < 0:
            month = month + 12
        day = int(datetime.datetime.now().strftime("%d")) - int(
            member.created_at.strftime("%d"))
        if day < 0:
            day = day + 30
        hour = int(datetime.datetime.utcnow().strftime("%H")) - int(
            member.created_at.strftime("%H"))
        if hour < 0:
            hour = hour + 24
        minute = int(datetime.datetime.now().strftime("%M")) - int(
            member.created_at.strftime("%M"))
        if minute < 0:
            minute = minute + 60
        bots = 0
        for member in member.guild.members:
            if member.bot == True:
                bots += 1
            else:
                pass
        data2 = await self.bc.welcomes.find(member.guild.id)
        if data2 is None:
            return
        sus = True
        a = list(str(len(member.guild.members)))
        if '1' in a[-1]:
            ending = 'ˢᵗ'
        elif '2' in a[-1]:
            ending = 'ⁿᵈ'
        elif '3' in a[-1]:
            ending = 'ʳᵈ'
        else:
            ending = 'ᵗʰ'
        try:
            if data2["channel"] is not None:
                channel = self.bc.get_channel(data2["channel"])
            if channel.name not in member.guild.channels and member not in channel.guild.members:
                pass
            else:
                message = data2["message"].replace("{member}", member.mention).replace("{server}", member.guild.name).replace("{place}", str(len(member.guild.members))).replace("{ending}", ending)
                if data2["ping"]:
                    pingrole = discord.utils.get(member.guild.roles, id=data2["ping"])
                avatar = member.avatar
                await avatar.save('images/Avatar.png')
                im = Image.open('images/Avatar.png').convert("RGB")
                im = im.resize((680, 680))
                bigsize = (im.size[0] * 3, im.size[1] * 3)
                mask = Image.new('L', bigsize, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + bigsize, fill=255)
                mask = mask.resize(im.size, Image.ANTIALIAS)
                im.putalpha(mask)
                output = ImageOps.fit(im, mask.size, centering=(10, 10))
                output.putalpha(mask)
                output.save('images/output.png')

                background = Image.open('images/welcome.png').convert("RGB")
                background.paste(im, (149, 0), im)
                draw2 = ImageDraw.Draw(background)
                txt = f"Welcome {member.name}"
                def fittext(txt,imgfraction):
                    fontsize = 1
                    img_fraction = imgfraction

                    font = ImageFont.truetype("abel-regular.ttf", fontsize)
                    while font.getsize(txt)[0] < img_fraction*background.size[0]:
                        # iterate until the text size is just larger than the criteria
                        fontsize += 1
                        font = ImageFont.truetype("abel-regular.ttf", fontsize)

                    # optionally de-increment to be sure it is less than criteria
                    fontsize -= 1
                    return ImageFont.truetype("abel-regular.ttf", fontsize)

                draw2.text((50, 780), txt, fill=(0,0,0,255), font=fittext(f"Welcome {member.name}", 0.60))

                sidebar = Image.new("RGBA", background.size, (0,0,0,0))
                draw = ImageDraw.Draw(sidebar)
                txt = f"ID: {member.id}"
                place = len(member.guild.members)
                draw.rectangle((1280, 0, 1920, 1080), fill=(0,0,0,178))
                draw.text((1325, 120), txt, fill=(255,255,255,255), font=fittext(f"ID: {member.id}",0.30))
                txt = f"Place in server: {place}"
                draw.text((1325, 200), txt, fill=(255,255,255,255), font=fittext(f"Place in server: {place}",0.30))
                txt = f"Invited By: {inviter}"
                draw.text((1325, 320), txt, fill=(255,255,255,255), font=fittext(txt,0.30))
                background.paste(sidebar,(0,0),sidebar)
                background.save('images/overlap.png')
                if data2["ping"]:
                    await channel.send(pingrole.mention)
                if int(year) != 0 and int(month) == 0:
                    em = discord.Embed(
                        title="Welcome {}".format(member),
                        description=message
                    )
                    em.add_field(name="Suspicious? No",value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
                    em.add_field(name="Who Invited?",value=f"Invited by: {inviter.mention}\nTotal Invites in some servers: {data['count']}")
                    file = discord.File('images/overlap.png')
                    await channel.send(file=file,embed=em)
                    sus = False
                elif int(year) != 0 and int(month) != 0:
                    em = discord.Embed(
                        title="Welcome {}".format(member),
                        description=message
                    )
                    em.add_field(name="Suspicious? No",value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
                    em.add_field(name="Who Invited?",value=f"Invited by: {inviter.mention}\nTotal Invites in some servers: {data['count']}")
                    file = discord.File('images/overlap.png')
                    await channel.send(file=file,embed=em)
                    sus = False
                elif int(year) == 0 and int(month) > 3:
                    em = discord.Embed(
                        title="Welcome {}".format(member),
                        description=message
                    )
                    em.add_field(name="Suspicious? No",value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
                    em.add_field(name="Who Invited?",value=f"Invited by: {inviter.mention}\nTotal Invites in some servers: {data['count']}")
                    file = discord.File('images/overlap.png')
                    await channel.send(file=file,embed=em)
                    sus = False
                elif int(year) == 0 and int(month) not in range(0, 2):
                    em = discord.Embed(
                        title="Welcome {}".format(member),
                        description=message
                    )
                    em.add_field(name="Suspicious? A bit sus if you ask me",value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
                    em.add_field(name="Who Invited?",value=f"Invited by: {inviter.mention}\nTotal Invites in some servers: {data['count']}")
                    file = discord.File('images/overlap.png')
                    await channel.send(file=file,embed=em)
                    sus = False
                elif int(year) == 0 and int(month) < 1:
                    em = discord.Embed(
                        title="Welcome {}".format(member),
                        description=message
                    )
                    em.add_field(name="Suspicious? VERY SUS CALL EMERGENCY MEETING",value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
                    em.add_field(name="Who Invited?",value=f"Invited by: {inviter.mention}\nTotal Invites in some servers: {data['count']}")
                    file = discord.File('images/overlap.png')
                    await channel.send(file=file,embed=em)
                    sus = True
                else:
                    em = discord.Embed(
                        title="Welcome {}".format(member),
                        description=message
                    )
                    em.add_field(name="Suspicious? VERY SUS CALL EMERGENCY MEETING",value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
                    em.add_field(name="Who Invited?",value=f"Invited by: {inviter.mention}\nTotal Invites in some servers: {data['count']}")
                    file = discord.File('images/overlap.png')
                    await channel.send(file=file,embed=em)
                    sus = True
                if sus == True and data2["auth"]:
                    await channel.send("Sending user captcha...")
                    while True:
                        characters = "abcdefghijklmnopqrstuvwxyz1234567890"
                        filtered = []
                        final = []
                        real = ""
                        for x in characters:
                            filtered.append(x)
                        for i in range(5):
                            letter = random.randrange(0,len(filtered))
                            final.append(filtered[letter])
                        for z in final:
                            real += str(z)
                        data = image.generate(real)
                        image.write(real,"captcha.png")
                        await member.send(file=discord.File('captcha.png'), content="Complete the captcha below. The reason you have to complete the captcha is to avoid bots from raiding.")
                        def check(z):
                            return z.author == member and z.channel == member.dm_channel
                        try:
                            msg2 = await self.bc.wait_for('message', check=check, timeout=30)
                            if msg2.content.lower() == str(real):
                                if data2["role"] is not None:
                                    role = discord.utils.get(member.guild.roles,id=data2["role"])
                                    await member.add_roles(role)
                                await member.send("Captcha correct")
                                break

                            else:
                                await member.send("Wrong! Try Again")
                        except asyncio.TimeoutError:
                            await member.send("Out of time! Try again")
                else:
                    if data2["role"] is not None:
                        role = discord.utils.get(member.guild.roles,id=data2["role"])
                        await member.add_roles(role)
        except KeyError:
            pass


def setup(bot):
    bot.add_cog(Invites(bot))