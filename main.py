from threading import Thread
import bot

self = bot.BreadBot()
_thread = Thread(target=self.run("a"))
_thread.start() #Starts the bot