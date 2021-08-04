from flask import Flask, request, abort, jsonify
from discord import Webhook, Embed, Color
from threading import Thread
import random
import re
import os
import datetime
import sys

app = Flask('')

webhook_password = os.environ.get("webhook_password")
discord_webhook = os.environ.get("webhook")
webhook_id = int(re.search(r"\d+", discord_webhook).group())
webhook_token = re.search(r"(?!.*\/)+(.*)", discord_webhook).group()

@app.route('/')
def home():
    return 'Im in!'

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
            webhook = Webhook.partial(webhook_id, webhook_token)
            webhook.send(embed=embed)
        return '', 200
    else:
        abort(400)

def run():
    app.run(host='0.0.0.0', port=random.randint(2000,9000))


def keep_alive():
    '''
	Creates and starts new thread that runs the function run.
	'''
    t = Thread(target=run)
    t.start()
