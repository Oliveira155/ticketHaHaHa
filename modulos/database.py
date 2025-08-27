import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

DB_PATH = "guilds.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            log_channel INTEGER,
            bemvindo_channel INTEGER,
            ticket_channel INTEGER,
            autorole_id INTEGER,
            suggestion_channel INTEGER
        )
    """)
    print("Banco de dados carregados.")
    conn.commit()
    conn.close()

def set_config(guild_id, log=None, bemvindo=None, ticket=None, autorole=None, sugestao=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()


    c.execute("SELECT * FROM guild_config WHERE guild_id=?", (guild_id,))
    if c.fetchone():
        log = log if log is not None else c.fetchone[1]
        bemvindo = bemvindo if bemvindo is not None else c.fetchone[2]
        ticket = ticket if ticket is not None else c.fetchone[3]
        autorole = autorole if autorole is not None else c.fetchone[4]
        sugestao = sugestao if sugestao is not None else c.fetchone[5]

        c.execute("""
        UPDATE guild_config
        SET log_channel=?, bemvindo_channel=?, ticket_channel=?, autorole_id=?, suggestion_channel=?
        WHERE guild_id=?
        """, (log, bemvindo, ticket, autorole, sugestao, guild_id))
    else:
        c.execute("""
        INSERT INTO guild_config (guild_id, log_channel, bemvindo_channel, ticket_channel, autorole_id, suggestion_channel)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (guild_id, log, bemvindo, ticket, autorole, sugestao))
    conn.commit()
    conn.close()

def get_config(guild_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM guild_config WHERE guild_id=?", (guild_id,))
    result = c.fetchone()
    conn.close()
    return result

class DatabaseConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@app_commands.command(name="ping", description="Latência do bot")
    #async def test(self, interaction: discord.Interaction):
        #await interaction.response.send_message(f"⭐・Minha latência de ping está atualmente: **{self.bot.latency*1000:.0f}ms**", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DatabaseConfig(bot))