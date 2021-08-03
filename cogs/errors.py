import discord
import asyncio
import traceback
import json
import string, random
from random import choice
from discord.ext import commands

errors = ('ArithmeticError', 'AssertionError', 'BaseException', 'BlockingIOError',
          'BrokenPipeError', 'BufferError', 'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError',
          'ConnectionError', 'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning', 'EOFError',
          'EnvironmentError', 'FileExistsError', 'FileNotFoundError','FloatingPointError', 'FutureWarning',
          'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning', 'UnexpectedQuoteError',
          'IndentationError', 'IndexError', 'InterruptedError', 'IsADirectoryError', 'KeyError',
          'KeyboardInterrupt', 'LookupError', 'MemoryError', 'ModuleNotFoundError', 'NameError',
          'NotADirectoryError', 'NotImplemented', 'NotImplementedError', 'OSError', 'OverflowError',
          'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError', 'RecursionError',
          'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning', 'StopAsyncIteration',
          'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError',
          'TimeoutError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError',
          'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning',
          'WindowsError', 'ZeroDivisionError')

def gen_code():
    chars = list(string.hexdigits) + list(string.octdigits)
    num = list(string.digits) + list(string.hexdigits) + list(string.octdigits)
    former = []
    for i in range(random.randint(5, 8)):
        x = ('y', 'n')
        if random.choice(x) == 'y':
            if random.choice(x) == 'y':
                former.append(random.choice(chars).lower())
            else:
                former.append(random.choice(chars).upper())
        else:
            former.append(random.choice(num))
    return ''.join(map(str, former))

class Errors(commands.Cog):
    def __init__(self, bc):
        self.bc = bc

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        #Ignore these errors
        ignored = (commands.CommandNotFound)
        if isinstance(error, ignored):
            return

        #Begin actual error handling
        if isinstance(error, commands.errors.NotOwner):
            if ctx.command.name == "invite":
                return
            msg = await ctx.message.reply('Only **{}** can use this command.'.format(await self.bc.fetch_user(self.bc.owner)))
            await asyncio.sleep(3)
            await msg.delete()
        elif isinstance(error, commands.errors.DisabledCommand):
            msg = await ctx.message.reply("This command is disabled for mantinance!")
            await asyncio.sleep(3)
            await msg.delete()
        elif isinstance(error, commands.MissingPermissions):
            msg = await ctx.message.reply('You need **{}** perms to complete this action.'.format(error.missing_perms[0]))
            await asyncio.sleep(3)
            await msg.delete()
        elif isinstance(error, commands.errors.NoPrivateMessage):
            msg = await ctx.message.reply("The user has blocked me or has the DM's closed.")
            await asyncio.sleep(3)
            await msg.delete()
        elif isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            w, d = divmod(d, 7)
            if int(d) == 0 and int(h) == 0 and int(m) == 0:
                em = discord.Embed(color=0xff0000)
                em.set_author(
                    name=f' You must wait {int(s)} seconds to use this command!'
                )
                await ctx.message.reply(embed=em)
            elif int(d) == 0 and int(h) == 0 and int(m) != 0:
                em = discord.Embed(color=0xff0000)
                em.set_author(
                    name=
                    f' You must wait {int(m)} minutes and {int(s)} seconds to use this command!'
                )
                await ctx.message.reply(embed=em)
            elif int(d) == 0 and int(h) != 0 and int(m) != 0:
                em = discord.Embed(color=0xff0000)
                em.set_author(
                    name=
                    f' You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!'
                )
                await ctx.message.reply(embed=em)
            elif int(d) != 0 and int(h) != 0 and int(m) != 0:
                em = discord.Embed(color=0xff0000)
                em.set_author(
                    name=
                    f' You must wait {int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!'
                )
                await ctx.message.reply(embed=em)
            else:
                em = discord.Embed(color=0xff0000)
                em.set_author(
                    name=
                    f' You must wait {int(w)} weeks, {int(d)} days, {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!'
                )
                await ctx.message.reply(embed=em)
        elif isinstance(error, commands.BotMissingPermissions):
            msg = await ctx.message.reply('I am missing permissions.')
            await asyncio.sleep(3)
            await msg.delete()
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            msg = await ctx.message.reply('The cog {} is already loaded.'.format(error.args[0]))
            await asyncio.sleep(3)
            await msg.delete()
        elif isinstance(error, commands.MissingRequiredArgument):
            data = await self.bc.prefixes.find(ctx.guild.id)
            if data is None:
                data = {}
                data["prefix"] = "="
            aliases = "|".join(ctx.command.aliases)
            cmd_invoke = f"[{ctx.command.name}|{aliases}]" if ctx.command.aliases else ctx.command.name

            full_invoke = ctx.command.qualified_name.replace(ctx.command.name, "")
            params = ctx.command.usage if ctx.command.usage else ctx.command.signature
            em = discord.Embed(
                title="Missing Required Argument",
                color = discord.Color.red(),
                description="```{}{}{} {}```\n\n**{}**".format(data["prefix"],full_invoke,cmd_invoke,params,error.args[0])
            )
            await ctx.send(embed=em)
        elif isinstance(error, discord.errors.Forbidden):
            msg = await ctx.message.reply('I do not have permissions for this command!')
            await asyncio.sleep(3)
            await msg.delete()
        else:
            code = gen_code()
            error = traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)
            error_type = 'Unspecified'
            for i in range(len(error)):
                for j in errors:
                    if j in error[i]:
                        error_type = j
                        break
            with open("errors.json", "r") as f:
                data = json.load(f)
            data[str(code)] = {}
            data[str(code)]['Command'] = ctx.command.qualified_name.title()
            data[str(code)]['Error Type'] = error_type
            data[str(code)]['Error'] = error
            with open("errors.json", "w") as f:
                json.dump(data,f,indent=4)
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.__class__.__name__} Cog has been loaded\n-----")
        
    
def setup(bc):
    bc.add_cog(Errors(bc))