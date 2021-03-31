import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps, ImageFont
from io import BytesIO
import datetime

class Images(commands.Cog):
    def __init__(self,bc):
        self.bc = bc

    @commands.command(description="Invert the color on ur pfp")
    async def invert(self,ctx,member:discord.Member=None):
        member = ctx.author if not member else member
        avatar = member.avatar_url_as(format=None,static_format='png',size=1024)
        await avatar.save('images/Avatar.png')
        im = Image.open('images/Avatar.png').convert("RGB")
        inverted = ImageOps.invert(im)
        inverted.save("images/inverted.png")
        await ctx.send(file=discord.File("images/inverted.png"))

    @commands.command(
        description="kick someone in the nuts",
        usage="[user]"
    )
    async def nuts(self,ctx,member:discord.Member=None):
        if not member:
            member = ctx.author
            ctx.author = self.bc.user
        im = Image.open("images/download.jpg")
        im1 = member.avatar_url_as(size=128)
        im2 = ctx.author.avatar_url_as(size=128)
        data = BytesIO(await im1.read())
        pfp = Image.open(data)
        pfp = pfp.resize((40,40))
        im.paste(pfp, (130,0))
        data2 = BytesIO(await im2.read())
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((40,40))
        im.paste(pfp2, (10,0))
        im.save("images/completenuts.jpg")
        await ctx.send(file=discord.File("images/completenuts.jpg"))

    @commands.command(
        description="make a gun point at someone",
        usage="<user>"
    )
    async def gun(self,ctx,member:discord.Member):
        im = Image.open("images/gun.jpg")
        im1 = member.avatar_url_as(size=128)
        data = BytesIO(await im1.read())
        pfp = Image.open(data)
        pfp = pfp.resize((120,120))
        im.paste(pfp, (21,15))
        im.save("images/completegun.jpg")
        await ctx.send(file=discord.File("images/completegun.jpg"))
    
    @commands.command(
        description="slap someone",
        usage="[user]"
    )
    async def slap(self,ctx,member:discord.Member):
        if not member:
            member = ctx.author
            ctx.author = self.bc.user
        im = Image.open("images/slap.jpg")
        im2 = member.avatar_url_as(size=128)
        im1 = ctx.author.avatar_url_as(size=128)
        data = BytesIO(await im1.read())
        pfp = Image.open(data)
        pfp = pfp.resize((200,200))
        im.paste(pfp, (650,0))
        data2 = BytesIO(await im2.read())
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((200,200))
        im.paste(pfp2, (130,0))
        im.save("images/slap2.jpg")
        await ctx.send(file=discord.File("images/slap2.jpg"))

    @commands.command(hidden=True)
    async def testing(self,ctx, member:discord.Member=None):
        member = member or ctx.author
        avatar = member.avatar_url_as(format=None,static_format='png',size=1024)
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
        background.paste(sidebar,(0,0),sidebar)
        background.save('images/overlap.png')
        await ctx.send(file=discord.File('images/overlap.png'))

def setup(bc):
    bc.add_cog(Images(bc))