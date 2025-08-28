import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import threading
from imagens import get_image

DB_PATH = "guilds.db"
db_lock = threading.Lock()

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
    conn.commit()
    conn.close()

def set_config(guild_id, log=None, bemvindo=None, ticket=None, autorole=None, sugestao=None):
    with db_lock:  # bloqueia para evitar concorrência
        with sqlite3.connect(DB_PATH, timeout=5) as conn:
            c = conn.cursor()

            c.execute("SELECT * FROM guild_config WHERE guild_id=?", (guild_id,))
            current = c.fetchone()

            if current:
                log = log if log is not None else current[1]
                bemvindo = bemvindo if bemvindo is not None else current[2]
                ticket = ticket if ticket is not None else current[3]
                autorole = autorole if autorole is not None else current[4]
                sugestao = sugestao if sugestao is not None else current[5]

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

    @app_commands.command(name="canalticket", description="Definir o canal onde vão clicar para abrir os tickets")
    async def ticket(self, interaction: discord.Interaction, channel: discord.TextChannel):
        set_config(interaction.guild.id, ticket=channel.id)
        await interaction.response.send_message(f"✅・Canal de ticket configurado com sucesso.", ephemeral=True)

    @app_commands.command(name="configs", description="Ver as configurações setadas neste servidor.")
    async def configs(self, interaction: discord.Interaction):
        config = get_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message("❌ Nenhuma configuração encontrada.", ephemeral=True)
            return


        guild_id, log_id, bemvindo_id, ticket_id, autorole_id, sugestao_id = config

        # converte IDs de canal para menção, se existirem
        log_mention = f"<#{log_id}>" if log_id else "Não configurado"
        bemvindo_mention = f"<#{bemvindo_id}>" if bemvindo_id else "Não configurado"
        ticket_mention = f"<#{ticket_id}>" if ticket_id else "Não configurado"
        autorole_mention = f"<#{autorole_id}>" if autorole_id else "Não configurado"
        sugestao_mention = f"<#{sugestao_id}>" if sugestao_id else "Não configurado"

        #convertidos - colocar isso em embed depois
        mensagem = (
            f"# 📋 Configurações do servidor:\n"
            f"> 🔹 ID do Servidor: {guild_id}\n"
            f"> 🔹 Canal de log: {log_mention}\n"
            f"> 🔹 Canal de boas-vindas: {bemvindo_mention}\n"
            f"> 🔹 Canal de tickets: {ticket_mention}\n"
            f"> 🔹 Canal de sugestões: {sugestao_mention}\n"
            f"> 🔹 Cargo de autorole: {autorole_mention}"
        )

        await interaction.response.send_message(mensagem, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DatabaseConfig(bot))