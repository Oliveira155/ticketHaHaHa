import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN
from modulos.database import init_db
from modulos.botdata import init_bot_db
from imagens import get_image

init_db()
init_bot_db()

TOKEN = DISCORD_TOKEN

#-------------
# mudar pra false quando não estiver em dev
emDesenvolvimento = False
serverDev = 1033558614117453904

#-------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

async def load_extensions():
    print("\n" * 15)
    print("------------------------------------------")
    print("Carregando Módulos..\n")
    for filename in os.listdir("./modulos"):
        if filename.endswith(".py"):
            await bot.load_extension(f"modulos.{filename[:-3]}")
            print(f"Módulo '{filename[:-3]}' carregado!")

@bot.event
async def on_ready():
    await load_extensions()
    if emDesenvolvimento == True:
        guildSync = discord.Object(id=serverDev)
        await bot.tree.sync(guild=guildSync)
    else:
        await bot.tree.sync()

    print(f"Banco de dados carregado!")
    print(f"Carregado Slash commands!")
    print("------------------------------------------")
    print(f"Conectado como {bot.user}!")

bot.run(TOKEN)