from discord.ext import commands

class Blacklisted(commands.CommandError):
    def __init__(self):
        super().__init__("Seems like Bungo blacklisted you from using BreadBot!")

class Premium(commands.CommandError):
    def __init__(self):
        super().__init__("Seems like you need premium to use this command. You can buy premium at <https://patreon.com/breadbot_>!")

class EditError(commands.CommandError):
    pass