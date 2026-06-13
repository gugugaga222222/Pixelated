import os
import discord
import requests
from discord.ext import commands
from flask import Flask, request, jsonify
from threading import Thread

# SETUP
app = Flask(__name__)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Pulling secrets from Render Environment Variables (Do not write keys here!)
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
JNKIE_API_KEY = os.environ.get('JNKIE_API_KEY')

# WEBHOOK LISTENER (This is what your shop/adwall talks to)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    hwid = data.get('hwid') # The user's HWID
    
    if not hwid:
        return jsonify({"status": "error", "message": "No HWID"}), 400

    # Call Jnkie API
    headers = {"Authorization": f"Bearer {JNKIE_API_KEY}"}
    response = requests.post("https://api.jnkie.com/v1/generate", 
                             json={"hwid": hwid}, headers=headers)

    if response.status_code == 200:
        key = response.json().get('key')
        return jsonify({"status": "success", "key": key}), 200
    
    return jsonify({"status": "error", "message": "API call failed"}), 500

# DISCORD COMMAND
@bot.command()
async def buy(ctx):
    await ctx.author.send("Go to your shop link here to complete your purchase!")

# THREADING (Required to run Flask and Discord at the same time)
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(DISCORD_TOKEN)