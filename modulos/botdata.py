import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from functools import wraps
from imagens import get_image

founderID = 773266869574434836
BOT_DB_PATH = "botdata.db"

def db_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with sqlite3.connect(BOT_DB_PATH) as conn:
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
    return wrapper

@db_query
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

@db_query
def add_owner(cursor, owner_id: int, senha: str):
    cursor.execute("INSERT OR IGNORE INTO botCfg (owner_id, key_senha) VALUES (?, ?)", (owner_id, senha))

@db_query
def get_owner(cursor, owner_id: int):
    cursor.execute("SELECT * FROM botCfg WHERE owner_id=?", (owner_id,))
    return cursor.fetchone()

@db_query
def update_senha(cursor, owner_id: int, senha: str):
    cursor.execute("UPDATE botCfg SET key_senha=? WHERE owner_id=?", (senha, owner_id))

class botdatabase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="permitir", description="Comando restrito aos desenvolvedores.")
    async def permitir(self, interaction: discord.Interaction, usuario: discord.Member):
        add_owner(owner_id=usuario.id, senha="mudesuasenha")
        await interaction.response.send_message(f"> ⭐・Permissão cedida ao ID (**{usuario.id}**)", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(botdatabase(bot))