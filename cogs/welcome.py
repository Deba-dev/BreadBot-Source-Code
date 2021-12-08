import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps, ImageFont
import io
import datetime
import json
import random
from captcha.image import ImageCaptcha
import asyncio
image = ImageCaptcha()


class Invites(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'{member} has joined a server')
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
        data = await self.bc.welcomes.find(member.guild.id)
        sus = False
        if year != 0 and month == 0:
            sus = False
        elif year != 0 and month != 0:
            sus = False
        elif year == 0 and month > 1:
            sus = False
        else:
            sus = True
        if not data:
            return
        if not data["channel"]:
            if data["role"]:
                if data["auth"]:
                    if sus:
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
                            image.write(real,"utility/storage/images/captcha.png")
                            await member.send(file=discord.File('utility/storage/images/captcha.png'), content="Complete the captcha below. This server uses Breadbot's captchas to make sure you are not a bot.")
                            def check(z):
                                return z.author == member and z.channel == member.dm_channel
                            try:
                                msg2 = await self.bc.wait_for('message', check=check, timeout=30)
                                if msg2.content.lower() == str(real):
                                    role = discord.utils.get(member.guild.roles, id=data["role"])
                                    await member.add_roles(role)
                                    await member.send("Captcha correct. Access Granted")
                                    break

                                else:
                                    await member.send("Wrong! Try Again")
                            except asyncio.TimeoutError:
                                await member.send("Out of time! Try again")
                    else:
                        role = discord.utils.get(member.guild.roles, id=data["role"])
                        await member.add_roles(role)
                else:
                    role = discord.utils.get(member.guild.roles, id=data["role"])
                    await member.add_roles(role)
        else:
            if data["role"]:
                if data["auth"]:
                    if sus:
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
                            image.write(real,"utility/storage/images/captcha.png")
                            await member.send(file=discord.File('utility/storage/images/captcha.png'), content="Complete the captcha below. This server uses Breadbot's captchas to make sure you are not a bot.")
                            def check(z):
                                return z.author == member and z.channel == member.dm_channel
                            try:
                                msg2 = await self.bc.wait_for('message', check=check, timeout=30)
                                if msg2.content.lower() == str(real):
                                    role = discord.utils.get(member.guild.roles, id=data["role"])
                                    await member.add_roles(role)
                                    await member.send("Captcha correct. Access Granted")
                                    break

                                else:
                                    await member.send("Wrong! Try Again")
                            except asyncio.TimeoutError:
                                await member.send("Out of time! Try again")
                    else:
                        role = discord.utils.get(member.guild.roles, id=data["role"])
                        await member.add_roles(role)
                else:
                    role = discord.utils.get(member.guild.roles, id=data["role"])
                    await member.add_roles(role)

            a = list(str(len(member.guild.members)))
            if '1' in a[-1]:
                ending = 'ˢᵗ'
            elif '2' in a[-1]:
                ending = 'ⁿᵈ'
            elif '3' in a[-1]:
                ending = 'ʳᵈ'
            else:
                ending = 'ᵗʰ'
            channel = self.bc.get_channel(data["channel"])
            bots = len([bot for bot in member.guild.members if bot.bot])

            message = data["message"].replace("{member}", member.mention).replace("{server}", member.guild.name).replace("{place}", str(len(member.guild.members))).replace("{ending}", ending)
            if data["ping"]:
                pingrole = discord.utils.get(member.guild.roles, id=data["ping"])
            avatar = member.avatar
            await avatar.save('utility/storage/images/Avatar.png')
            im = Image.open('utility/storage/images/Avatar.png').convert("RGB")
            im = im.resize((680, 680))
            bigsize = (im.size[0] * 3, im.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)
            output = ImageOps.fit(im, mask.size, centering=(10, 10))
            output.putalpha(mask)
            output.save('utility/storage/images/output.png')

            background = Image.open('utility/storage/images/welcome.png').convert("RGB")
            background.paste(im, (149, 0), im)
            draw2 = ImageDraw.Draw(background)
            txt = f"Welcome {member.name}"
            def fittext(txt,imgfraction):
                fontsize = 1
                img_fraction = imgfraction

                font = ImageFont.truetype("utility/fonts/abel-regular.ttf", fontsize)
                while font.getsize(txt)[0] < img_fraction*background.size[0]:
                    # iterate until the text size is just larger than the criteria
                    fontsize += 1
                    font = ImageFont.truetype("utility/fonts/abel-regular.ttf", fontsize)

                # optionally de-increment to be sure it is less than criteria
                fontsize -= 1
                return ImageFont.truetype("utility/fonts/abel-regular.ttf", fontsize)

            draw2.text((50, 780), txt, fill=(0,0,0,255), font=fittext(f"Welcome {member.name}", 0.60))

            sidebar = Image.new("RGBA", background.size, (0,0,0,0))
            draw = ImageDraw.Draw(sidebar)
            txt = f"ID: {member.id}"
            place = len(member.guild.members)
            draw.rectangle((1280, 0, 1920, 1080), fill=(0,0,0,178))
            draw.text((1325, 120), txt, fill=(255,255,255,255), font=fittext(f"ID: {member.id}",0.30))
            txt = f"Place in server: {place}"
            draw.text((1325, 200), txt, fill=(255,255,255,255), font=fittext(f"Place in server: {place}",0.30))
            background.paste(sidebar,(0,0),sidebar)
            background.save('utility/storage/images/overlap.png')
            if data["ping"]:
                await channel.send(pingrole.mention)
                
            em = discord.Embed(
                title="Welcome {}".format(member),
                description=message
            )
            em.add_field(name="Suspicious? {}".format(sus),value="Account made {} years, {} months, {} days {} hours {} minutes ago".format(int(year), int(month), int(day), int(hour),int(minute)))
            
            file = discord.File('utility/storage/images/overlap.png')
            await channel.send(file=file,embed=em)



def setup(bot):
    bot.add_cog(Invites(bot))