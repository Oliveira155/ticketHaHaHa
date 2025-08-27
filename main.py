import discord
from discord.ext import commands
import os

# ------------------ /  T  /  -------------------

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

for filename in os.listdir("./modulos"):
    if filename.endswith(".py"):
        client.load_extension(f"modulos.{filename[:-3]}")

@client.event
async def on_ready():
    print(f"Conectando como {client.user}..")

client.run(TOKEN)