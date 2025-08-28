import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from functools import wraps
from imagens import get_image
import threading


founderID = 773266869574434836
BOT_DB_PATH = "botdata.db"
db_lock = threading.Lock()

def safe_db_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_lock:
            with sqlite3.connect(BOT_DB_PATH, timeout=5) as conn:
                cursor = conn.cursor()
                result = func(cursor, *args, **kwargs)
                conn.commit()
                return result
    return wrapper

@safe_db_query
def init_bot_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS botCfg (
            owner_id INTEGER PRIMARY KEY,
            key_senha TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT 1 FROM botCfg WHERE owner_id=?", (founderID,))
    if not cursor.fetchone():
        cursor.execute("INSERT OR IGNORE INTO botCfg (owner_id, key_senha) VALUES (?, ?)", (founderID, "mudesuasenha"))

@safe_db_query
def add_owner(cursor, owner_id: int, senha: str):
    cursor.execute("INSERT OR IGNORE INTO botCfg (owner_id, key_senha) VALUES (?, ?)", (owner_id, senha))

@safe_db_query
def get_owner(cursor, owner_id: int):
    cursor.execute("SELECT * FROM botCfg WHERE owner_id=?", (owner_id,))
    return cursor.fetchone()

@safe_db_query
def update_senha(cursor, owner_id: int, senha: str):
    cursor.execute("UPDATE botCfg SET key_senha=? WHERE owner_id=?", (senha, owner_id))

def get_senha(owner_id: int):
    user = get_owner(owner_id)
    return user[1] if user else None

class botdatabase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setperm", description="Comando restrito aos desenvolvedores.")
    async def permitir(self, interaction: discord.Interaction, usuario: discord.Member):
        if interaction.user.id == founderID:
            add_owner(owner_id=usuario.id, senha="mudesuasenha")
            await interaction.response.send_message(f"> ⭐・Permissão cedida ao usuário **{usuario.mention}**(**{usuario.id}**)", ephemeral=True)
        else:
            await interaction.response.send_message(f"> ⭐・Suas permissões são insuficientes para este comando.", ephemeral=True)

    @app_commands.command(name="mudarkey", description="Comando restrito aos desenvolvedores.")
    async def minhakey(self, interaction: discord.Interaction, senhalogin: str, usuario: discord.Member=None):
        if usuario is None:
            usuario = interaction.user
        if get_owner(owner_id=interaction.user.id) is not None:
            if usuario.id == interaction.user.id:
                update_senha(owner_id=interaction.user.id, senha=senhalogin)
                await interaction.response.send_message(f"> ⭐・Sua senha foi alterada com sucesso.", ephemeral=True)
            elif interaction.user.id == founderID:
                update_senha(owner_id=usuario.id, senha=senhalogin)
                await usuario.send(f"> ⭐・Sua senha foi alterada por {interaction.user.mention}, agora sua senha é: ||{senhalogin}||")
                await interaction.response.send_message(f"> ⭐・Você alterou a senha do usuário {usuario.mention} (**{usuario.id}**).", ephemeral=True)
        else:
            await interaction.response.send_message(f"> ⭐・Suas permissões são insuficientes para este comando.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(botdatabase(bot))