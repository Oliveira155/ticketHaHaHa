import discord
from discord import app_commands
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Latência do bot")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"⭐・Minha latência de ping está atualmente: **{self.bot.latency*1000:.0f}ms**", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))