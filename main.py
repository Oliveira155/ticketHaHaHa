import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN
from modulos.database import init_db

init_db()

TOKEN = DISCORD_TOKEN

#-------------
# mudar pra false quando não estiver em dev
emDesenvolvimento = True
serverDev = 1033558614117453904

#-------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

async def load_extensions():
    print("\n\n\n\n\n\n\n")
    print("Carregando Módulos..")
    for filename in os.listdir("./modulos"):
        if filename.endswith(".py"):
            await bot.load_extension(f"modulos.{filename[:-3]}")
            print(f"Módulo '{filename[:-3]}' carregado")

@bot.event
async def on_ready():
    await load_extensions()
    if emDesenvolvimento:
        guildSync = discord.Object(id=serverDev)
        await bot.tree.sync(guild=guildSync)
    else:
        await bot.tree.sync()

    print(f"Carregando Slash commands..")
    print(f"Conectando como {bot.user}..")

bot.run(TOKEN)