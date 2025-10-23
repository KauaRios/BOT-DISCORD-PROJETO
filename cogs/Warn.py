import discord
from discord import app_commands, Permissions
from discord.ext import commands


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #comando de warn no Usuario
    @app_commands.command(name="infraction",help="Informa infraçoes para o Usuario")
    @app_commands.has.permissions(administrator=True)
    async def infraction(self, ctx, member: discord.Member,*,reason="sem motivo fornecido"):
        # guild id recebe o Id da guilda
        # user id recebe o id do membro guilda
        guild_id = ctx.guild
        user_id = ctx.author


        if guild_id not in Warn:
            Warn[guild_id] = {}
        if user_id not in Warn[guild_id]:
            Warn[guild_id][user_id] = []
        #aplica a infraçao ao Usuario
        Warn[guild_id][user_id].append(reason)
        await ctx.send(f"{member.mention} recebeu uma infraçao: {reason}")



async def setup(bot):
    await bot.add_cog(Warn(bot))