import discord
from discord import app_commands
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Testar um comando só")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Testado coe mao?", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))