import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN

TOKEN = DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)


async def load_extensions():
    for filename in os.listdir("./modulos"):
        if filename.endswith(".py"):
            await bot.load_extension(f"modulos.{filename[:-3]}")
            print("Carregando Módulos..")

@bot.event
async def on_ready():
    await load_extensions()
    await bot.tree.sync()  # <- ESSENCIAL
    print(f"Carregando Slash commands..")
    print(f"Conectando como {bot.user}..")

bot.run(TOKEN)