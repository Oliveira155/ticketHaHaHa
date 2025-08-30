import discord
from discord import app_commands
from discord.ext import commands
from modulos.database import get_config
from datetime import datetime

sugestoes_usuarios = {}

class SugestaoView(discord.ui.View):
    def __init__(self, bot, message_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.message_id = message_id
        self.votos = {"👍": 0, "👎": 0}
        self.ja_votaram = set()

    def porcentagens(self):
        total = sum(self.votos.values())
        if total == 0:
            return {k: 0 for k in self.votos}
        return {k: round(v / total * 100, 1) for k, v in self.votos.items()}

    @discord.ui.button(label="(0 - 0%)", style=discord.ButtonStyle.success, emoji="<:like:1410744039493468220>")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.ja_votaram:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・Você já votou!", ephemeral=True)
            return
        
        self.votos["👍"] += 1
        self.ja_votaram.add(interaction.user.id)
        pct = self.porcentagens()["👍"]
        button.label = f" ({self.votos['👍']} - {pct}%)"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="(0 - 0%)", style=discord.ButtonStyle.danger, emoji="<:dislike:1410744037111234640>")
    async def rejeitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.ja_votaram:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・Você já votou!", ephemeral=True)
            return
        
        self.votos["👎"] += 1
        self.ja_votaram.add(interaction.user.id)
        pct = self.porcentagens()["👎"]
        button.label = f" ({self.votos['👎']} - {pct}%)"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji="⭐")
    async def aceitarsugest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("<:bloqueio:1410436751427899563>・Você precisa ser administrador para usar este botão.", ephemeral=True)
            return

        user_id = sugestoes_usuarios.get(self.message_id)
        if user_id:
            user = await self.bot.fetch_user(user_id)
            try:
                config = get_config(interaction.guild.id)
                sugestao_id = config[5]

                sugestaoLink = f"https://discord.com/channels/{interaction.guild.id}/{sugestao_id}"

                botaoLink1 = discord.ui.Button(label="Ir ao Canal", url=sugestaoLink, style=discord.ButtonStyle.link, emoji="<:canaldiscord:1410436772231385169>")

                embedAceita = discord.Embed(title="🎉 Sugestão aceita!", description="Sua sugestão foi aceita! Obrigado por contribuir com ideias para melhorar o servidor. Sua opinião é muito importante para a comunidade!", color=0xaaffff)
                embedAceita.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                embedAceita.set_footer(text=interaction.guild.name)
                embedAceita.timestamp = datetime.utcnow()

                viewButao = discord.ui.View()
                viewButao.add_item(botaoLink1)

                await user.send(embed=embedAceita, view=viewButao)
            except:
                await interaction.response.send_message("<:bloqueio:1410436751427899563>・Não consegui enviar DM para o usuário.", ephemeral=True)
                return
        
        await interaction.response.edit_message(view=self)

class SugestoesCfg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        config = get_config(message.guild.id)
        if not config:
            return
        
        canalSugestao = config[5]
        if canalSugestao is None:
            return

        if message.channel.id == canalSugestao:
            sugestoes_usuarios[message.id] = message.author.id

            embedSugestao=discord.Embed(title="<:categoriadiscord:1410436778891939871> Nova sugestão!", description="> **Mensagens indevidas** ou que não tenham relação com este **canal de sugestões** poderão ser **removidas**. Sugestões que não forem pertinentes ao servidor ou à comunidade podem resultar em **medidas administrativas**.\n\n> **Evite** o texto **muito grande** para não perder tudo e ter que refazer do zero.", color=0xF1C40F)
            embedSugestao.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
            embedSugestao.set_thumbnail(url=message.guild.icon.url if message.guild.icon else None)
            embedSugestao.add_field(name="<:quest:1410743950431617126> Sugestão", value=f"```{message.content}```", inline=False)

            viewSug = SugestaoView(self.bot, message.id)
            await message.channel.send(embed=embedSugestao, view=viewSug)
            await message.delete()

async def setup(bot: commands.Bot):
    await bot.add_cog(SugestoesCfg(bot))