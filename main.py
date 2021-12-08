from core import bot
from core.web import run, stay_alive
from threading import Thread

site_thread = Thread(target=run)
ping_thread = Thread(target=stay_alive)
self = bot.BreadBot()

site_thread.start()
ping_thread.start()
self.run()