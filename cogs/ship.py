import discord
from discord import app_commands
from discord.ext import commands
import random


class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ship", description="shipa um usuario com outro")
    async def ship(self, interaction: discord.Interaction, membro1: discord.Member, membro2: discord.Member):
        membrolista = [membro1.id, membro2.id]
        membrolista.sort()
        membrolista = str(membrolista)
        random.seed(membrolista)
        porcentagem = random.randint(0, 100)
        membrolista = str(membrolista)

        total_blocos = 10
        x = (20 / 100 * total_blocos)
        y = (50 / 100 * total_blocos)
        z = (80 / 100 * total_blocos)
        blocos_cheios = round((porcentagem / 100) * total_blocos)
        blocos_vazios = total_blocos - blocos_cheios
        barra_final = f" Ual olha a quantidade de blocos de ship{blocos_cheios} cheio(s) e  {blocos_vazios} vazio(s)"

        mensagem_final = ""
        if porcentagem <= 20:
            mensagem_final = "Não parece muito promissor... 😬"
        elif porcentagem <= 50:
            mensagem_final = "Existe uma faísca, quem sabe? 😉"
        elif porcentagem <= 80:
            mensagem_final = "Uau, isso parece promissor! 🥰"
        else:
            mensagem_final = "É o casal perfeito! Destinados a ficarem juntos! ❤️"

        texto_do_embed = (
            f"Analisando {membro1.mention} e {membro2.mention} — {porcentagem}% ❤️\n"
            f"{barra_final}\n{mensagem_final}"
        )

        embed = discord.Embed(title="❤️ Medidor de Ship ❤️", description=texto_do_embed)
        embed.set_footer(text=f"Shippados por {interaction.user}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Ship(bot))
