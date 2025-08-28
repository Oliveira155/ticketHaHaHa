import discord
from discord import app_commands
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

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        missingPerms = error.missing_permissions # lista

        if 'administrator' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ser administrador para usar esse comando.**", ephemeral=True)

        elif 'ban_members' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ter permissão de 'Banir membros'.**", ephemeral=True)

        elif 'kick_members' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ter permissão de 'Expulsar membros'.**", ephemeral=True)

        elif 'manage_guild' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ter a permissão de 'Gerenciar Servidor'.**", ephemeral=True)

        elif 'manage_roles' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ter a permissão de 'Gerenciar Cargos'.**", ephemeral=True)

        elif 'manage_channels' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ter a permissão de 'Gerenciar Canais'.**", ephemeral=True)

        elif 'manage_messages' in missingPerms:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa ter a permissão de 'Gerenciar Mensagens'.**", ephemeral=True)
            
        else:
            await interaction.response.send_message(f"<:bloqueio:1410436751427899563>・**Você não tem as permissões necessárias:** ``{', '.join(missingPerms)}``", ephemeral=True)

    elif isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Você precisa de um cargo especifico para usar esse comando.**", ephemeral=True)

    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Não tenho permissões suficientes para isso.**", ephemeral=True)

    else:
        botaoLink = discord.ui.Button(label="Reportar", url="https://discord.gg/enQ693fw72", style=discord.ButtonStyle.link, emoji="<:atendente:1410743948124753950>")

        viewBotaoLink = discord.ui.View()
        viewBotaoLink.add_item(botaoLink)
        await interaction.response.send_message("<:bloqueio:1410436751427899563>・**Ocorreu um erro, comunique aos desenvolvedores se possivel.**", view=viewBotaoLink, ephemeral=True)

bot.run(TOKEN)