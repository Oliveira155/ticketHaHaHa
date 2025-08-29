import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import threading
from imagens import get_image
from datetime import datetime

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
    with db_lock:  # bloqueia para evitar concorrência ..
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

    @app_commands.command(name="configurar", description="Definir as configurações do bot no servidor")
    @app_commands.checks.has_permissions(administrator=True)
    async def configurar(self, interaction: discord.Interaction,
        cargodebemvindo: discord.Role=None,
        canalticket: discord.TextChannel=None,
        canalregistro: discord.TextChannel=None,
        canalbemvindo: discord.TextChannel=None,
        canalsugestao: discord.TextChannel=None):
        if not any([cargodebemvindo, canalticket, canalregistro, canalbemvindo, canalsugestao]):
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・Insira os argumentos para mudar as configurações.", ephemeral=True)
            return
        
        set_config(interaction.guild.id,
            autorole=cargodebemvindo.id if cargodebemvindo else None,
            ticket=canalticket.id if canalticket else None,
            log=canalregistro.id if canalregistro else None,
            bemvindo=canalbemvindo.id if canalbemvindo else None,
            sugestao=canalsugestao.id if canalsugestao else None)
        await interaction.response.send_message(f"<:verificado:1410436717445644399>・Configuração atualizada com sucesso.", ephemeral=True)

    @app_commands.command(name="configs", description="Ver as configurações setadas neste servidor.")
    async def configs(self, interaction: discord.Interaction):
        config = get_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・Nenhuma configuração encontrada.", ephemeral=True)
            return


        guild_id, log_id, bemvindo_id, ticket_id, autorole_id, sugestao_id = config

        logLink = f"https://discord.com/channels/{interaction.guild.id}/{log_id}"
        bemvindoLink = f"https://discord.com/channels/{interaction.guild.id}/{bemvindo_id}"
        ticketLink = f"https://discord.com/channels/{interaction.guild.id}/{ticket_id}"
        sugestaoLink = f"https://discord.com/channels/{interaction.guild.id}/{sugestao_id}"

        botaoLink1 = discord.ui.Button(label="Canal LOG", url=logLink, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")
        botaoLink2 = discord.ui.Button(label="Canal Bem-vindo", url=bemvindoLink, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")
        botaoLink3 = discord.ui.Button(label="Canal Ticket", url=ticketLink, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")
        botaoLink4 = discord.ui.Button(label="Canal Sugestão", url=sugestaoLink, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

        viewBotaoLinks = discord.ui.View()
        viewBotaoLinks.add_item(botaoLink1)
        viewBotaoLinks.add_item(botaoLink2)
        viewBotaoLinks.add_item(botaoLink3)
        viewBotaoLinks.add_item(botaoLink4)

        # converte IDs de canal para menção, se existirem
        log_mention = f"<:verificado:1410436717445644399> <#{log_id}>" if log_id else "<:alert:1410743945063043255> ``N/C``"
        bemvindo_mention = f"<:verificado:1410436717445644399> <#{bemvindo_id}>" if bemvindo_id else "<:alert:1410743945063043255> ``N/C``"
        ticket_mention = f"<:verificado:1410436717445644399> <#{ticket_id}>" if ticket_id else "<:alert:1410743945063043255> ``N/C``"
        autorole_mention = f"<:verificado:1410436717445644399> <@{autorole_id}>" if autorole_id else "<:alert:1410743945063043255> ``N/C``"
        sugestao_mention = f"<:verificado:1410436717445644399> <#{sugestao_id}>" if sugestao_id else "<:alert:1410743945063043255> ``N/C``"

        embedConfigs=discord.Embed(title=f"<:admin:1410436795178553464> {interaction.guild.name}", description="", color=0xFFFFFF)
        #embedConfigs.add_field(name="<:adminazul:1410436787452510260> ID do Servidor", value=guild_id, inline=True)
        embedConfigs.add_field(name="<:membro:1410744041506869278> Dono do Servidor", value=f"<:verificado:1410436717445644399> <@{interaction.guild.owner_id}>", inline=False)
        embedConfigs.add_field(name="<:canaldiscord:1410436772231385169> Canal Bem-vindo", value=bemvindo_mention, inline=False)
        embedConfigs.add_field(name="<:canaldiscord:1410436772231385169> Cargo Bem-vindo", value=autorole_mention, inline=False)
        embedConfigs.add_field(name="<:canaldiscord:1410436772231385169> Canal Tickets", value=ticket_mention, inline=False)
        embedConfigs.add_field(name="<:canaldiscord:1410436772231385169> Canal Sugestões", value=sugestao_mention, inline=False)
        embedConfigs.add_field(name="<:canaldiscord:1410436772231385169> Canal Registros", value=log_mention, inline=False)
        embedConfigs.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embedConfigs.set_footer(text="Todos os direitos reservados", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embedConfigs.timestamp = datetime.utcnow()

        await interaction.response.send_message(embed=embedConfigs, view=viewBotaoLinks, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(DatabaseConfig(bot))