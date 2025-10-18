import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Exibe a lista de comandos do bot")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Help",
            description="Lista de comandos disponíveis ",
            color=discord.Color.green()
        )

        # Loop pelas Cogs do bot
        for cog_name, cog in self.bot.cogs.items():
            comandos_lista = ""
            # Loop pelos comandos da Cog
            for command in cog.get_commands():
                descricao = command.help if command.help else "Sem descrição"
                comandos_lista += f"/{command.name} - {descricao}\n"

            # Adiciona um campo no embed para cada Cog
            embed.add_field(name=cog_name, value=comandos_lista, inline=False)

        # Envia o embed como resposta do slash command
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
