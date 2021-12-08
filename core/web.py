from flask import Flask, request, abort, jsonify
import os
import googletrans
import sys
import discord
from discord import SyncWebhook, Embed, Color
from threading import Thread
import random
import re
import datetime
import requests
import time
import urllib
import json

app = Flask('')

webhook_password = os.environ.get("webhook_password")
discord_webhook = os.environ.get("webhook")
webhook_id = int(re.search(r"\d+", discord_webhook).group())
webhook_token = re.search(r"(?!.*\/)+(.*)", discord_webhook).group()

@app.route('/')
def home():
    return 'BreadBot is now connected to discord'

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

@app.route("/getdocs", methods=["GET"])
def getdocs():
    with open("utility/storage/json/docs.json", "r") as f:
        data = json.load(f)
    return data

def run():
    app.run(host='0.0.0.0', port=random.randint(2000,9000))

def stay_alive():
    while True:
        start = time.time()
        
        while True:
            end = time.time()
            
            if ((end - start) >= (15 * 60)):
                urllib.request.urlopen("https://Bot.breadbotsucks.repl.co")
                break