
import discord
from discord import app_commands
from discord.ext import commands




class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bane um membro do servidor.")
    @app_commands.describe(member="O membro que você quer banir.", reason="O motivo do banimento (opcional).")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member,
                  reason: str = "Nenhum motivo fornecido."):
        await interaction.response.defer(ephemeral=True)

        # Verificações de segurança
        if member == interaction.user:
            await interaction.followup.send("Você não pode banir a si mesmo!", ephemeral=True)
            return

        if member == self.bot.user:
            await interaction.followup.send("Eu não posso me banir!", ephemeral=True)
            return

        # Verificação de hierarquia de cargos com a mensagem correta
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send("Eu não posso banir este membro, pois o cargo dele é mais alto que o meu.",
                                            ephemeral=True)
            return

        # Tenta enviar DM para o membro
        try:
            await member.send(f"Você foi banido do servidor **{interaction.guild.name}** pelo motivo: *{reason}*")
        except discord.Forbidden:
            print(f"Não foi possível enviar DM para {member.name}.")

        # Efetua o banimento
        try:
            await member.ban(reason=reason)
            await interaction.followup.send(
                f"✅ O membro **{member.name}** foi banido com sucesso pelo motivo: *{reason}*", ephemeral=False)
        except discord.Forbidden:
            await interaction.followup.send("Eu não tenho a permissão 'Banir Membros' para fazer isso.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Ocorreu um erro inesperado: {e}", ephemeral=True)

    # Tratamento de erro com o tipo correto de exceção
    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Você não tem permissão para usar este comando!", ephemeral=True)
        else:
            print(f"Erro no comando /ban: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Ocorreu um erro ao executar o comando.", ephemeral=True)
            else:
                await interaction.followup.send("Ocorreu um erro ao executar o comando.", ephemeral=True)


# Função setup com o nome da classe correto
async def setup(bot):
    await bot.add_cog(Ban(bot))