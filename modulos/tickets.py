import discord
from discord import app_commands
from discord.ext import commands
from modulos.database import get_config
import json
import os
import asyncio

fileMessage = "messageTicket.json"

def saveMessageID(message_id: int):
    with open(fileMessage, "w") as f:
        json.dump({"message_id": message_id}, f)

def loadMessageID():
    if not os.path.exists(fileMessage):
        return None
    with open(fileMessage, "r") as f:
        data = json.load(f)
        return data.get("message_id")

class TicketDenunciaStaff(discord.ui.Modal, title="Abrindo ticket.."):
    nome = discord.ui.TextInput(
        label="Informe seu nick",
        placeholder="Descreva o seu nick..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    nomeDenunciado = discord.ui.TextInput(
        label="Informe o nick denúnciado",
        placeholder="Descreva o nick do usuário denúnciado..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    motivoDenuncia = discord.ui.TextInput(
        label="Qual é o motivo para esta denúncia?",
        placeholder="Descreva o que ocorreu..",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=700
    )
    async def on_submit(self, interaction: discord.Interaction):
        motivoDenuncia = self.motivoDenuncia.value
        nomeDenunciado = self.nomeDenunciado.value
        nome = self.nome.value
        await interaction.response.send_message(f"🛒 Ticket aberto!\n**Motivo:** {motivoDenuncia}\n**Nick:** {nome}\n**Denunciado:**{nomeDenunciado}", ephemeral=True)

class TicketDenuncia(discord.ui.Modal, title="Abrindo ticket.."):
    nome = discord.ui.TextInput(
        label="Informe seu nick",
        placeholder="Descreva o seu nick..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    nomeDenunciado = discord.ui.TextInput(
        label="Informe o nick denúnciado",
        placeholder="Descreva o nick do usuário denúnciado..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    motivoDenuncia = discord.ui.TextInput(
        label="Qual é o motivo para esta denúncia?",
        placeholder="Descreva o que ocorreu..",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=700
    )
    async def on_submit(self, interaction: discord.Interaction):
        motivoDenuncia = self.motivoDenuncia.value
        nomeDenunciado = self.nomeDenunciado.value
        nome = self.nome.value
        await interaction.response.send_message(f"🛒 Ticket aberto!\n**Motivo:** {motivoDenuncia}\n**Nick:** {nome}\n**Denunciado:**{nomeDenunciado}", ephemeral=True)

class TicketSuporte(discord.ui.Modal, title="Abrindo ticket.."):
    nome = discord.ui.TextInput(
        label="Informe seu nick",
        placeholder="Descreva o seu nick..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )
    problema = discord.ui.TextInput(
        label="Qual é o problema que está enfrentando?",
        placeholder="Descreva brevemente seu problema/duvida..",
        style=discord.TextStyle.long,
        required=True,
        max_length=500
    )
    async def on_submit(self, interaction: discord.Interaction):
        problema = self.problema.value
        nome = self.nome.value
        await interaction.response.send_message(f"🛒 Ticket aberto!\n**Problema:** {problema}\n**Nick:** {nome}", ephemeral=True)

class TicketRevisao(discord.ui.Modal, title="Abrindo ticket.."):
    nome = discord.ui.TextInput(
        label="Informe seu nick",
        placeholder="Descreva o seu nick..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    nomeStaff = discord.ui.TextInput(
        label="Informe o nome de quem lhe puniu",
        placeholder="Descreva o nick do staff se souber..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    punicaoRecebida = discord.ui.TextInput(
        label="Qual foi sua punição?",
        placeholder="Informe sua punição, ex: exoneração, advertência..",
        style=discord.TextStyle.short,
        required=True,
        max_length=80
    )

    punidoInjusto = discord.ui.TextInput(
        label="Por que acha que a punição foi injusta?",
        placeholder="Descreva por que você acha que foi injusto..",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=700
    )
    async def on_submit(self, interaction: discord.Interaction):
        nome = self.nome.value
        nomeStaff = self.nomeStaff.value
        punicaoRecebida = self.punicaoRecebida.value
        punidoInjusto = self.punidoInjusto.value
        await interaction.response.send_message(f"🛒 Ticket aberto!\n**Problema:** {punidoInjusto}\n**Nick:** {nome}", ephemeral=True)

class TicketCompra(discord.ui.Modal, title="Abrindo ticket.."):
    produto = discord.ui.TextInput(
        label="Deseja adquirir",
        placeholder="Descreva o produto que deseja comprar..",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )

    nome = discord.ui.TextInput(
        label="Informe seu nick",
        placeholder="Descreva o seu nick..",
        style=discord.TextStyle.short,
        required=True,
        max_length=40
    )

    async def on_submit(self, interaction: discord.Interaction):

        produto = self.produto.value
        nome = self.nome.value
        configSQL = get_config(interaction.guild.id)
        canalId = configSQL[3]
        canal = interaction.guild.get_channel(canalId)
        if canal is None or canal.category is None:
            print("Canal ou categoria nao encontrada, botar isso numa embed com link pra desenvolvedor depois")
            return
        
        categoria = canal.category

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }

        # se tiver cargo de staff salvo no DB
        if configSQL[7]:  # supondo que role_respvenda
            staff_role = interaction.guild.get_role(configSQL[7])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        newCanal = await interaction.guild.create_text_channel(f"💰・{interaction.user.name}", category=categoria, overwrites=overwrites)
        await interaction.response.send_message(f"Canal criado {newCanal.mention}", ephemeral=True)

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Comprar", description="Compre ou tire sua dúvida antes.", emoji="<:carrinho:1411183042520678430>", value="Compras"),
            discord.SelectOption(label="Suporte", description="Caso tenha problemas e dúvidas.", emoji="<:membrogreen:1411183038267920565>", value="Suporte"),
            discord.SelectOption(label="Denúncias", description="Caso veja algo errado denúncie e tomaremos providências.", emoji="<:aviso:1411183032869847051>", value="Denuncia"),
            discord.SelectOption(label="Denúncias Staff", description="Caso tenha problema com um membro da nossa equipe.", emoji="<:aviso:1411183032869847051>", value="Denuncia-staff"),
            discord.SelectOption(label="Revisar Punição", description="Caso tenha sido advertido ou exonerado injustamente.", emoji="<:revisao:1411183040125861918>", value="Revisao"),
        ]
        super().__init__(placeholder="Selecione uma categoria", min_values=1, max_values=1, options=options, custom_id="ticket_select_v1")

    async def callback(self, interaction: discord.Interaction):
        escolha = self.values[0]

        if escolha == "Compras":
            await interaction.response.send_modal(TicketCompra())
            await interaction.message.edit(view=TicketSetupView())
        
        if escolha == "Suporte":
            await interaction.response.send_modal(TicketSuporte())
            await interaction.message.edit(view=TicketSetupView())
        
        if escolha == "Denuncia":
            await interaction.response.send_modal(TicketDenuncia())
            await interaction.message.edit(view=TicketSetupView())
        
        if escolha == "Denuncia-staff":
            await interaction.response.send_modal(TicketDenunciaStaff())
            await interaction.message.edit(view=TicketSetupView())
        
        if escolha == "Revisao":
            await interaction.response.send_modal(TicketRevisao())
            await interaction.message.edit(view=TicketSetupView())

        #await interaction.response.send_message(f"<:novoticket:1410436720423469239>・Ticket de **{self.values[0]}** criado com sucesso.", ephemeral=True)

class TicketSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

async def ensure_setup_message(bot: discord.Client, channel: discord.TextChannel) -> discord.Message:
    message_id = loadMessageID()

    # tenta buscar a mensagem
    if message_id:
        try:
            msg = await channel.fetch_message(message_id)
            return msg
        except discord.NotFound:
            message_id = None

    embed = discord.Embed(
        title="<:ticketha:1410743936204673054> Como abrir um ticket",
        description="Abra seu ticket para falar com nossa equipe de suporte.\nSiga as instruções abaixo para que possamos te ajudar rápido!",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="<:novoticket:1410436720423469239> Como abrir",
        value="- Clique no menu abaixo da mensagem de ticket.\n- Escolha a categoria que mais se encaixa no seu problema.\n- Aguarde nossa equipe responder no seu ticket.",
        inline=False
    )

    embed.add_field(
        name="<:ticketdelete:1410436727033696256> Evite",
        value="- Enviar spam ou mensagens repetidas.\n- Usar tickets para assuntos que não são do suporte.\n- Mencionar repetidas vezes a equipe.",
        inline=False
    )

    embed.set_footer(text="Se precisar de ajuda, entre em contato com um suporte.")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1405539658242195456/1411173469772845067/Support-PNG-HD.png")  # exemplo de ícone de envelope


    view = TicketSetupView()
    bot.add_view(TicketSetupView())
    sent = await channel.send(embed=embed, view=view)

    saveMessageID(sent.id)
    return sent

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reticket", description="Caso a mensagem de ticket for deletada.")
    async def reticket(self, interaction: discord.Interaction):
        await interaction.response.send_message("<a:load:1411166499468607510>・Verificando o banco de dados, aguarde um instante..", ephemeral=True)
        await asyncio.sleep(4)

        configSQL = get_config(interaction.guild.id)
        if not configSQL:
            await interaction.edit_original_response("<:bloqueio:1410436751427899563>・O canal não está configurado corretamente ou não existe no banco de dados.")
            return
        
        canalTicket = self.bot.get_channel(configSQL[3]) or await self.bot.fetch_channel(configSQL[3])
        if canalTicket is None:
            await interaction.edit_original_response(content="<:bloqueio:1410436751427899563>・O canal não existe ou não pode ser acessado.")
            return
        
        msgg = await ensure_setup_message(self.bot, canalTicket)
        await interaction.edit_original_response(content=f"<:verificado:1410436717445644399>・O sistema de ticket foi normalizado, a equipe agradece por isso!")

    @app_commands.command(name="ping", description="Latência do bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"⭐・Minha latência de ping está atualmente: **{self.bot.latency*1000:.0f}ms**", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))