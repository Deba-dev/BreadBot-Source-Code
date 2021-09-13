from flask import Flask, request, abort, jsonify
import googletrans
import discord
import os
import sys

update = False
if googletrans.__version__ != "3.1.0-alpha":
    os.system("pip install googletrans==3.1.0a")
    update = True
if discord.__version__ != "2.0.0a":
    os.system("pip install git+https://github.com/Rapptz/discord.py")
    update = True
if update:
    os.execv(sys.executable, ['python'] + sys.argv)

from discord import SyncWebhook, Embed, Color
from threading import Thread
import random
import re
import datetime
import requests
import bot
import time
import urllib

app = Flask('')

webhook_password = os.environ.get("webhook_password")
discord_webhook = os.environ.get("webhook")
webhook_id = int(re.search(r"\d+", discord_webhook).group())
webhook_token = re.search(r"(?!.*\/)+(.*)", discord_webhook).group()

@app.route('/')
def home():
    return 'Bot is now connected to discord'

@app.route('/dblwebhook', methods=['POST'])
def webhook():
    sys.stdout.flush()
    if request.headers.get('Authorization') == webhook_password:
        user_id = request.json.get('user')
        bot_id = request.json.get('bot') # ID of the bot that was upvoted 
        request_type = request.json.get('type')
        weekend_status = request.json.get('isWeekend')
        now = datetime.datetime.utcnow()
        if discord_webhook != "":
            embed_title = "Test" if request_type == 'test' else 'New upvote!'
            embed = Embed(title=embed_title, description=f"**Upvoter: <@{user_id}>** ({user_id})\n**Upvoted bot:** <@{bot_id}> ({bot_id})", timestamp=datetime.datetime.utcnow(), color=Color.green())
            webhook = SyncWebhook.from_url(discord_webhook)
            webhook.send(embed=embed)
        return '', 200
    else:
        abort(400)

def run():
    app.run(host='0.0.0.0', port=random.randint(2000,9000))

def stay_alive():
	while True:
		start = time.time()
		
		while True:
			end = time.time()

			# This 15 is for the amount of minutes you change it and take it upto 30 minutes at most
			if ((end - start) >= (20 * 60)):
				urllib.requests.urlopen("https://Bot.breadbotsucks.repl.co")
				break

site_thread = Thread(target=run)
ping_thread = Thread(target=stay_alive)
self = bot.BreadBot()

site_thread.start()
ping_thread.start()
self.run()