import discord
import typing
from discord.ext import commands
from PIL import Image, ImageDraw, ImageOps, ImageFont
from io import BytesIO
import datetime
import glitchart
import random
from utility import image_convert as im_cv
from utility.imager import IMAGEOPS

class Images(commands.Cog):
    def __init__(self,bc):
        self.bc = bc

    @commands.command(name='Invert', usage="[image]")
    async def invert(self, ctx, argument: str = None, animate: str = '--true', *size) -> typing.Union[discord.MessageReference, discord.Embed]:
        stream = await im_cv.get_stream(ctx, query=argument)

        if not stream:
            return await ctx.message.reply(content='Invalid image url passed')

        file = await self.bc.loop.run_in_executor(None, IMAGEOPS, ImageOps.invert, stream, animate, *size)
        embed = discord.Embed(title='Inverted!', color=random.choice(self.bc.color_list)).set_image(
            url='attachment://{}'.format(file.filename))

        try:
            await ctx.message.reply(file=file, embed=embed)
        except Exception:
            return await ctx.message.reply(content='File is too large to send')


    @commands.command(
        description="Add a glitch effect to your images"
    )
    async def glitch(self,ctx,member:discord.Member=None):
        if not member:
            member = ctx.author
        avatar = member.avatar
        await avatar.save("utility/storage/images/avatar.png")
        
        glitchart.png('utility/storage/images/avatar.png', max_amount=10)
        await ctx.send(file=discord.File("avatar_glitch.png"))

    @commands.command(
        description = "Pixelate an image"
    )
    async def pixelate(self, ctx, member:discord.Member=None):
        if not member:
            member = ctx.author
        avatar = member.avatar
        data = BytesIO(await avatar.read())
        img = Image.open(data)
        imgSmall = img.resize((16,16),resample=Image.BILINEAR)
        
        result = imgSmall.resize(img.size,Image.NEAREST)
        result.save('utility/storage/images/result.png')
        await ctx.send(file=discord.File("utility/storage/images/result.png"))

    @commands.command(
        description="kick someone in the nuts",
        usage="[user]"
    )
    async def nuts(self,ctx,member:discord.Member=None):
        if not member:
            member = ctx.author
            ctx.author = self.bc.user
        im = Image.open("utility/storage/images/download.jpg")
        im1 = member.avatar
        im2 = ctx.author.avatar
        data = BytesIO(await im1.read())
        pfp = Image.open(data)
        pfp = pfp.resize((40,40))
        im.paste(pfp, (130,0))
        data2 = BytesIO(await im2.read())
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((40,40))
        im.paste(pfp2, (10,0))
        im.save("utility/storage/images/completenuts.jpg")
        await ctx.send(file=discord.File("utility/storage/images/completenuts.jpg"))
    
    @commands.command(
        description="slap someone",
        usage="[user]"
    )
    async def slap(self,ctx,member:discord.Member):
        if not member:
            member = ctx.author
            ctx.author = self.bc.user
        im = Image.open("utility/storage/images/slap.jpg")
        im2 = member.avatar
        im1 = ctx.author.avatar
        data = BytesIO(await im1.read())
        pfp = Image.open(data)
        pfp = pfp.resize((200,200))
        im.paste(pfp, (650,0))
        data2 = BytesIO(await im2.read())
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((200,200))
        im.paste(pfp2, (130,0))
        im.save("utility/storage/images/slap2.jpg")
        await ctx.send(file=discord.File("utility/storage/images/slap2.jpg"))

    @commands.command(hidden=True)
    async def testing(self,ctx, member:discord.Member=None):
        member = member or ctx.author
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
        background.save('utility/storage/images/overlap.png')
        await ctx.send(file=discord.File('utility/storage/images/overlap.png'))

def setup(bc):
    bc.add_cog(Images(bc))