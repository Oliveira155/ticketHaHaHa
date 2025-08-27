import os
import discord

# ------------------ /  T  /  -------------------

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Conectando como {client.user}..")

client.run(TOKEN)