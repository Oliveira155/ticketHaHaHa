import discord
from discord import app_commands
from discord.ext import commands
from modulos.database import get_config
import json
import os
import asyncio
from datetime import datetime
import pytz
import re
import aiohttp

brasilia = datetime.now(pytz.timezone("America/Sao_Paulo"))

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

# Converte emojis personalizados <:nome:id> para <img>
def converter_emoji_para_img(texto):
    def repl(match):
        nome, eid = match.groups()
        return f'<img src="https://cdn.discordapp.com/emojis/{eid}.png" alt=":{nome}:" style="width:20px;height:20px;vertical-align:middle;">'
    return re.sub(r'<:([a-zA-Z0-9_]+):([0-9]+)>', repl, texto)

def markdown_to_html(texto):
    texto = re.sub(r'```(.*?)```', r'<pre>\1</pre>', texto, flags=re.DOTALL)
    texto = re.sub(r'`(.*?)`', r'<code>\1</code>', texto)
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', texto)
    return texto

async def converter_mencoes_azul(texto, guild: discord.Guild):
    pattern = re.compile(r'<@!?(\d+)>')
    parts = []
    last_index = 0

    for match in pattern.finditer(texto):
        start, end = match.span()
        parts.append(texto[last_index:start])
        user_id = int(match.group(1))
        member = guild.get_member(user_id)
        if not member:
            try:
                member = await guild.fetch_member(user_id)
            except discord.NotFound:
                member = None
        if member:
            parts.append(f'<span style="color:#00AFF4;">@{member.name}</span>')
        else:
            parts.append(f'<span style="color:#00AFF4;">@{user_id}</span>')
        last_index = end

    parts.append(texto[last_index:])
    return ''.join(parts)

async def criar_transcript_html(canal: discord.TextChannel, arquivo_nome: str, pasta_temp="attachments_temp"):
    brasilia_tz = pytz.timezone("America/Sao_Paulo")
    membros_ativos = {}

    # Cria pasta temporária para anexos
    os.makedirs(pasta_temp, exist_ok=True)

    async for msg in canal.history(limit=None, oldest_first=True):
        membros_ativos[msg.author.id] = msg.author

    with open(arquivo_nome, "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Transcript do Canal #{canal.name}</title>
<style>
body {{
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    background-color: #36393F;
    color: #DCDDDE;
    display: flex;
    margin: 0;
    padding: 0;
}}
.sidebar {{
    width: 250px;
    background-color: #2F3136;
    padding: 10px;
    overflow-y: auto;
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
}}
.main-content {{
    margin-right: 250px;
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    height: 100vh;
}}
.member {{
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}}
.member img {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 8px;
}}
.member span {{
    color: #FFFFFF;
    font-weight: bold;
}}
.bot-tag {{
    background-color: #7289DA;
    color: white;
    font-weight: bold;
    font-size: 0.7em;
    padding: 1px 4px;
    border-radius: 3px;
    margin-left: 5px;
}}
.embed {{
    display: flex;
    max-width: 600px;
    background-color: #292B2F;
    border-left: 4px solid #00AFF4;
    border-radius: 4px;
    padding: 10px;
    margin: 5px 0;
}}

.embed-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
}}

.embed-thumb {{
    flex: 0 0 auto;
    margin-left: 10px;
}}

.embed-thumb img {{
    max-width: 80px;
    max-height: 80px;
    border-radius: 4px;
}}

.embed-title {{
    font-weight: bold;
    color: #00AFF4;
    margin-bottom: 5px;
}}

.embed-description {{
    color: #DCDDDE;
    margin-bottom: 5px;
}}

.embed-field {{
    margin-top: 2px;           /* reduz espaço entre os campos */
}}

.embed-field pre {{
    background-color: #1E1F22;
    padding: 4px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 2px 0;
    font-family: "Consolas", "Courier New", monospace;
    color: #DCDDDE;
}}

.embed-field code {{
    background-color: #1E1F22;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: "Consolas", "Courier New", monospace;
    color: #DCDDDE;
}}

.embed-field b {{
    color: #FFFFFF;
}}

.embed img {{
    max-width: 80px;
    max-height: 80px;
    margin-top: 5px;
    border-radius: 4px;
}}
.msg {{
    display: flex;
    align-items: flex-start;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 8px;
    background-color: #2F3136;
}}
.avatar {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}}
.content {{
    flex: 1;
}}
.author {{
    font-weight: bold;
    color: #FFFFFF;
}}
.timestamp {{
    color: #72767D;
    font-size: 0.75em;
    margin-left: 5px;
}}
a {{
    color: #00AFF4;
    text-decoration: none;
}}
</style>
</head>
<body>
<div class="main-content">
<h2>Transcript do Canal #{canal.name}</h2>
""")

        async with aiohttp.ClientSession() as session:
            async for msg in canal.history(limit=None, oldest_first=True):
                timestamp = msg.created_at.replace(tzinfo=pytz.UTC).astimezone(brasilia_tz)
                timestamp_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")
                author_name = msg.author.name
                avatar_url = msg.author.avatar.url if msg.author.avatar else msg.author.default_avatar.url
                bot_tag = '<span class="bot-tag">OWNER</span>' if msg.author.bot else ""

                content = converter_emoji_para_img(msg.content)
                content = markdown_to_html(content)
                content = await converter_mencoes_azul(content, canal.guild)
                content = content.replace("\n", "<br>")

                f.write(f"""
<div class="msg">
    <img class="avatar" src="{avatar_url}" alt="avatar">
    <div class="content">
        <span class="author">{author_name}{bot_tag}</span>
        <span class="timestamp">[{timestamp_str}]</span><br>
        {content}<br>
""")

                # Baixar anexos e referenciar localmente
                for attach in msg.attachments:
                    try:
                        filename = f"{pasta_temp}/{attach.filename}"
                        async with session.get(attach.url) as resp:
                            if resp.status == 200:
                                with open(filename, "wb") as out_file:
                                    out_file.write(await resp.read())
                                f.write(f'<img src="{filename}" style="max-width:300px; display:block; margin:5px 0;"><br>')
                    except Exception as e:
                        f.write(f'<a href="{attach.url}">[Anexo: {attach.filename}]</a><br>')

                for embed in msg.embeds:
                    f.write('<div class="embed">')
                    
                    # Conteúdo da embed
                    f.write('<div class="embed-content">')
                    if embed.title:
                        title_html = markdown_to_html(converter_emoji_para_img(embed.title))
                        title_html = await converter_mencoes_azul(title_html, canal.guild)
                        f.write(f'<div class="embed-title">{title_html}</div>')
                    if embed.description:
                        desc_html = markdown_to_html(converter_emoji_para_img(embed.description))
                        desc_html = await converter_mencoes_azul(desc_html, canal.guild)
                        desc_html = desc_html.replace("\n", "<br>")
                        f.write(f'<div class="embed-description">{desc_html}</div>')
                    for field in embed.fields:
                        name_html = markdown_to_html(converter_emoji_para_img(field.name))
                        name_html = await converter_mencoes_azul(name_html, canal.guild)
                        value_html = markdown_to_html(converter_emoji_para_img(field.value))
                        value_html = await converter_mencoes_azul(value_html, canal.guild)
                        value_html = value_html.replace("\n", "<br>")
                        f.write(f'<div class="embed-field"><b>{name_html}</b>:<br>{value_html}</div>')
                    f.write('</div>')  # fecha embed-content

                    # Thumbnail (agora dentro do embed)
                    if embed.thumbnail and embed.thumbnail.url:
                        f.write(f'<div class="embed-thumb"><img src="{embed.thumbnail.url}"></div>')

                    f.write('</div>')  # fecha embed

                f.write("</div></div>\n")

        # Sidebar fixa
        f.write("</div>")  # fecha main-content
        f.write('<div class="sidebar"><h3>Disponivel</h3>')
        for member in membros_ativos.values():
            bot_tag = '<span class="bot-tag">OWNER</span>' if member.bot else ""
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            f.write(f"""
<div class="member">
    <img src="{avatar_url}" alt="avatar">
    <span>{member.name}{bot_tag}</span>
</div>
""")
        f.write("</div></body></html>")

    return arquivo_nome

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
        if configSQL[6]:  # atendente
            staff_role = interaction.guild.get_role(configSQL[6])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        newCanal = await interaction.guild.create_text_channel(f"👨‍⚖️┃denúncia-staff・{interaction.user.name}", category=categoria, overwrites=overwrites)

        linkTicket = f"https://discord.com/channels/{interaction.guild.id}/{newCanal.id}"

        botaoLink1 = discord.ui.Button(label="Ir para o canal", url=linkTicket, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

        viewBotaoLinks = discord.ui.View()
        viewBotaoLinks.add_item(botaoLink1)

        await interaction.response.send_message(f"<:verificado:1410436717445644399>・Canal criado com sucesso!", view=viewBotaoLinks, ephemeral=True)

        embedTicket=discord.Embed(title="<:casa:1410743952243429406> Ticket criado!", description="Caro usuário, ao abrir **este ticket** seja breve e faça **sua parte ajudando** os atendentes dizendo o que você precisa, ou o que deseja adquirir, para um suporte eficiente e rápido.\n\n> Caso fique mencionando muitas vezes será punido.\n> Caso este ticket tenha sido aberto indevidamente será punido.", color=0x32CD3A)
        embedTicket.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        embedTicket.add_field(name="👤 Nick", value=f"```{nome}```", inline=True)
        embedTicket.add_field(name="👤 Denúnciado", value=f"```{nomeDenunciado}```", inline=True)
        embedTicket.add_field(name="📝 Motivo", value=f"```{motivoDenuncia}```", inline=True)

        embedTicket.set_footer(text=f"{interaction.guild.name}")
        embedTicket.timestamp = brasilia
        viewCreateTicket = TicketBotao(newCanal.id, interaction.user.id)
        await newCanal.send(f"{interaction.user.mention}", embed=embedTicket, view=viewCreateTicket)

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
        if configSQL[6]:  # atendente
            staff_role = interaction.guild.get_role(configSQL[6])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        newCanal = await interaction.guild.create_text_channel(f"👨‍⚖️┃denúncia・{interaction.user.name}", category=categoria, overwrites=overwrites)

        linkTicket = f"https://discord.com/channels/{interaction.guild.id}/{newCanal.id}"

        botaoLink1 = discord.ui.Button(label="Ir para o canal", url=linkTicket, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

        viewBotaoLinks = discord.ui.View()
        viewBotaoLinks.add_item(botaoLink1)

        await interaction.response.send_message(f"<:verificado:1410436717445644399>・Canal criado com sucesso!", view=viewBotaoLinks, ephemeral=True)

        embedTicket=discord.Embed(title="<:casa:1410743952243429406> Ticket criado!", description="Caro usuário, ao abrir **este ticket** seja breve e faça **sua parte ajudando** os atendentes dizendo o que você precisa, ou o que deseja adquirir, para um suporte eficiente e rápido.\n\n> Caso fique mencionando muitas vezes será punido.\n> Caso este ticket tenha sido aberto indevidamente será punido.", color=0x32CD3A)
        embedTicket.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        embedTicket.add_field(name="👤 Nick", value=f"```{nome}```", inline=True)
        embedTicket.add_field(name="👤 Denúnciado", value=f"```{nomeDenunciado}```", inline=True)
        embedTicket.add_field(name="📝 Motivo", value=f"```{motivoDenuncia}```", inline=True)

        embedTicket.set_footer(text=f"{interaction.guild.name}")
        embedTicket.timestamp = brasilia
        viewCreateTicket = TicketBotao(newCanal.id, interaction.user.id)
        await newCanal.send(f"{interaction.user.mention}", embed=embedTicket, view=viewCreateTicket)

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
        if configSQL[6]:  # atendente
            staff_role = interaction.guild.get_role(configSQL[6])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        newCanal = await interaction.guild.create_text_channel(f"📦┃suporte・{interaction.user.name}", category=categoria, overwrites=overwrites)

        linkTicket = f"https://discord.com/channels/{interaction.guild.id}/{newCanal.id}"

        botaoLink1 = discord.ui.Button(label="Ir para o canal", url=linkTicket, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

        viewBotaoLinks = discord.ui.View()
        viewBotaoLinks.add_item(botaoLink1)

        await interaction.response.send_message(f"<:verificado:1410436717445644399>・Canal criado com sucesso!", view=viewBotaoLinks, ephemeral=True)

        embedTicket=discord.Embed(title="<:casa:1410743952243429406> Ticket criado!", description="Caro usuário, ao abrir **este ticket** seja breve e faça **sua parte ajudando** os atendentes dizendo o que você precisa, ou o que deseja adquirir, para um suporte eficiente e rápido.\n\n> Caso fique mencionando muitas vezes será punido.\n> Caso este ticket tenha sido aberto indevidamente será punido.", color=0x32CD3A)
        embedTicket.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        embedTicket.add_field(name="👤 Nick", value=f"```{nome}```", inline=True)
        embedTicket.add_field(name="📋 Assunto", value=f"```{problema}```", inline=True)

        embedTicket.set_footer(text=f"{interaction.guild.name}")
        embedTicket.timestamp = brasilia
        viewCreateTicket = TicketBotao(newCanal.id, interaction.user.id)
        await newCanal.send(f"{interaction.user.mention}", embed=embedTicket, view=viewCreateTicket)

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
        if configSQL[6]:  # atendente
            staff_role = interaction.guild.get_role(configSQL[6])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        newCanal = await interaction.guild.create_text_channel(f"📝┃revisão・{interaction.user.name}", category=categoria, overwrites=overwrites)

        linkTicket = f"https://discord.com/channels/{interaction.guild.id}/{newCanal.id}"

        botaoLink1 = discord.ui.Button(label="Ir para o canal", url=linkTicket, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

        viewBotaoLinks = discord.ui.View()
        viewBotaoLinks.add_item(botaoLink1)

        await interaction.response.send_message(f"<:verificado:1410436717445644399>・Canal criado com sucesso!", view=viewBotaoLinks, ephemeral=True)

        embedTicket=discord.Embed(title="<:casa:1410743952243429406> Ticket criado!", description="Caro usuário, ao abrir **este ticket** seja breve e faça **sua parte ajudando** os atendentes dizendo o que você precisa, ou o que deseja adquirir, para um suporte eficiente e rápido.\n\n> Caso fique mencionando muitas vezes será punido.\n> Caso este ticket tenha sido aberto indevidamente será punido.", color=0x32CD3A)
        embedTicket.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        embedTicket.add_field(name="👤 Nick", value=f"```{nome}```", inline=True)
        embedTicket.add_field(name="👤 Nick Staff", value=f"```{nomeStaff}```", inline=True)
        embedTicket.add_field(name="📋 Punição Recebida", value=f"```{punicaoRecebida}```", inline=True)
        embedTicket.add_field(name="📝 Contestação", value=f"```{punidoInjusto}```", inline=True)

        embedTicket.set_footer(text=f"{interaction.guild.name}")
        embedTicket.timestamp = brasilia
        viewCreateTicket = TicketBotao(newCanal.id, interaction.user.id)
        await newCanal.send(f"{interaction.user.mention}", embed=embedTicket, view=viewCreateTicket)

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

        newCanal = await interaction.guild.create_text_channel(f"💰┃compra・{interaction.user.name}", category=categoria, overwrites=overwrites)

        linkTicket = f"https://discord.com/channels/{interaction.guild.id}/{newCanal.id}"

        botaoLink1 = discord.ui.Button(label="Ir para o canal", url=linkTicket, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

        viewBotaoLinks = discord.ui.View()
        viewBotaoLinks.add_item(botaoLink1)

        await interaction.response.send_message(f"<:verificado:1410436717445644399>・Canal criado com sucesso!", view=viewBotaoLinks, ephemeral=True)

        embedTicket=discord.Embed(title="<:casa:1410743952243429406> Ticket criado!", description="Caro usuário, ao abrir **este ticket** seja breve e faça **sua parte ajudando** os atendentes dizendo o que você precisa, ou o que deseja adquirir, para um suporte eficiente e rápido.\n\n> Caso fique mencionando muitas vezes será punido.\n> Caso este ticket tenha sido aberto indevidamente será punido.", color=0x32CD3A)
        embedTicket.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embedTicket.add_field(name="👤 Nick", value=f"```{nome}```", inline=True)
        embedTicket.add_field(name="<:presenteroxo:1410436738928873502> Produto desejado", value=f"```{produto}```", inline=True)
        embedTicket.set_footer(text=f"{interaction.guild.name}")
        embedTicket.timestamp = brasilia
        viewCreateTicket = TicketBotao(newCanal.id, interaction.user.id)
        await newCanal.send(f"{interaction.user.mention}", embed=embedTicket, view=viewCreateTicket)

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

class TicketBotao(discord.ui.View):
    def __init__(self, canal_id: int, id_user: int):
        super().__init__(timeout=None)
        self.canal_id = canal_id
        self.id_user = id_user

    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.danger, emoji="<:cadeadoclosedred:1410436710323716126>")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal = interaction.guild.get_channel(self.canal_id)
        user = await interaction.guild.fetch_member(self.id_user)
        if canal and user:
            configSQL = get_config(interaction.guild.id)
            cargoatendente = configSQL[6]
            cargoAt = interaction.guild.get_role(cargoatendente)
            if not cargoAt in interaction.user.roles:
                EmbedConfirmacao=discord.Embed(title="", description=f"Você não tem permissão para fechar este ticket!", color=0xff0000)
                EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=True)
                return
            
            if not canal.permissions_for(user).view_channel:
                EmbedConfirmacao=discord.Embed(title="", description=f"Este ticket já está fechado!", color=0xff0000)
                EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=True)
                return
            
            EmbedConfirmacao=discord.Embed(title="", description=f"O canal foi fechado por {interaction.user.mention}, agora só o suporte consegue ver este canal.", color=0xff0000)
            EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            await canal.set_permissions(user, view_channel=False, send_messages=False)
            viewBotaoConfirm = TicketBotaoConfirm(canal.id, user.id)
            await interaction.response.send_message(embed=EmbedConfirmacao, view=viewBotaoConfirm, ephemeral=False)

class TicketBotaoConfirm(discord.ui.View):
    def __init__(self, canal_id: int, id_user: int):
        super().__init__(timeout=None)
        self.canal_id = canal_id
        self.id_user = id_user

    @discord.ui.button(label="Deletar", style=discord.ButtonStyle.danger, emoji="<:ticketdelete:1410436727033696256>")
    async def apagar(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal = interaction.guild.get_channel(self.canal_id)
        #user = interaction.guild.get_member(self.id_user)
        if canal:
            configSQL = get_config(interaction.guild.id)
            cargoatendente = configSQL[6]
            cargoAt = interaction.guild.get_role(cargoatendente)
            if not cargoAt in interaction.user.roles:
                EmbedConfirmacao=discord.Embed(title="", description=f"Você não tem permissão para deletar este ticket!", color=0xff0000)
                EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=True)
                return
            EmbedConfirmacao=discord.Embed(title="", description=f"Este ticket foi deletado por {interaction.user.mention} e será apagado em 5 segundos..", color=0xff0000)
            EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            EmbedConfirmacao.timestamp = brasilia
            await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=False)
            await asyncio.sleep(5)
            await canal.delete()

    @discord.ui.button(label="Deletar e Salvar", style=discord.ButtonStyle.danger, emoji="<:ticketdelete:1410436727033696256>")
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal = interaction.guild.get_channel(self.canal_id)
        #user = interaction.guild.get_member(self.id_user)
        if canal:
            configSQL = get_config(interaction.guild.id)
            cargoatendente = configSQL[6]
            cargoAt = interaction.guild.get_role(cargoatendente)
            if not cargoAt in interaction.user.roles:
                EmbedConfirmacao=discord.Embed(title="", description=f"Você não tem permissão para deletar este ticket!", color=0xff0000)
                EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=True)
                return
            
            configSQL = get_config(interaction.guild.id)
            if not configSQL:
                await interaction.edit_original_response("<:bloqueio:1410436751427899563>・O canal de logs não está configurado corretamente ou não existe no banco de dados.")
                return
            
            EmbedConfirmacao=discord.Embed(title="", description=f"Este ticket foi deletado e salvo por {interaction.user.mention} e será apagado em 5 segundos..", color=0xff0000)
            EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            EmbedConfirmacao.timestamp = brasilia

            await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=False)

            canalLogzada = interaction.guild.get_channel(configSQL[1]) or await interaction.guild.fetch_channel(configSQL[1])
            arquivo = await criar_transcript_html(canal, f"transcript-{canal.id}.html")
            await canalLogzada.send(f"{interaction.user.mention}", file=discord.File(arquivo))

            await asyncio.sleep(5)
            await canal.delete()


    @discord.ui.button(label="Abrir", style=discord.ButtonStyle.success, emoji="<:unlock:1410743954147905556>")
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal = interaction.guild.get_channel(self.canal_id)
        user = await interaction.guild.fetch_member(self.id_user)
        if canal and user:
            configSQL = get_config(interaction.guild.id)
            cargoatendente = configSQL[6]
            cargoAt = interaction.guild.get_role(cargoatendente)
            if not cargoAt in interaction.user.roles:
                EmbedConfirmacao=discord.Embed(title="", description=f"Você não tem permissão para abrir este ticket!", color=0xff0000)
                EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=True)
                return
            
            if canal.permissions_for(user).view_channel:
                EmbedConfirmacao=discord.Embed(title="", description=f"Este ticket já está aberto!", color=0xff0000)
                EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=True)
                return

            EmbedConfirmacao=discord.Embed(title="", description=f"Este ticket foi aberto novamente por {interaction.user.mention}.", color=0x32CD3A)
            EmbedConfirmacao.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            EmbedConfirmacao.timestamp = brasilia
            await canal.set_permissions(user, view_channel=True, send_messages=True)
            await interaction.response.send_message(embed=EmbedConfirmacao, ephemeral=False)

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