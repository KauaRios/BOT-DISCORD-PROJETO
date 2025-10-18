import discord
from discord import app_commands
from discord.ext import commands
import asyncio


class Limparchat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="limparchat", description="[MODERAÇAO]Limpa uma quantidade de mensagens do chat (até 1000).")
    @app_commands.checks.has_permissions(administrator=True)
    async def limparchat(self, interaction: discord.Interaction, quantidade: int,):

        # --- Verificações de Segurança ---
        # Aumentamos o limite para 1000, mas você pode escolher outro valor.
        if quantidade > 1000:
            await interaction.response.send_message("Você não pode apagar mais de 1000 mensagens de uma vez.",
                                                    ephemeral=True)
            return
        if quantidade <= 0:
            await interaction.response.send_message("A quantidade de mensagens deve ser maior que 0.", ephemeral=True)
            return

        # --- Ação de Limpeza em Lotes ---

        # Adia a resposta. Essencial, pois o processo pode demorar.
        await interaction.response.defer(ephemeral=True, thinking=True)  # thinking=True mostra "Bot está pensando..."

        mensagens_apagadas_total = 0
        quantidade_restante = quantidade

        # Inicia o loop para apagar em lotes
        while quantidade_restante > 0:
            # Calcula quantas apagar nesta rodada (o menor valor entre 100 e o que falta)
            quantidade_lote = min(quantidade_restante, 100)

            try:
                # O 'purge' retorna uma lista das mensagens que conseguiu apagar
                # Ele não apaga mensagens com mais de 14 dias
                mensagens_apagadas = await interaction.channel.purge(limit=quantidade_lote)
                mensagens_apagadas_total += len(mensagens_apagadas)

                # Se o purge não apagar nada (ex: todas as mensagens são muito antigas), paramos o loop
                if not mensagens_apagadas:
                    break

            except Exception as e:
                print(f"Erro durante o purge: {e}")
                await interaction.followup.send(f"Ocorreu um erro ao tentar apagar as mensagens: {e}", ephemeral=True)
                return

            # Subtrai o que já foi apagado do total
            quantidade_restante -= quantidade_lote
            # Espera um pouco para não sobrecarregar a API do Discord
            await asyncio.sleep(1)

        # Envia a confirmação final com o total de mensagens que foram realmente apagadas
        await interaction.followup.send(f"✅ {mensagens_apagadas_total} mensagens foram apagadas com sucesso!")

async def setup(bot):
    await bot.add_cog(Limparchat(bot))