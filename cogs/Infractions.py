import discord
from discord import app_commands
from discord.ext import commands




class infractions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #mostra as infraçoes do Usuario
    @app_commands.command(name='infractions',help="Informa infraçoes do Usuario")
    @app_commands.has_permissions(administrator=True)
    async def infractions(self, ctx,member : discord.Member,*,reason="sem motivo fornecido"):
        if member is None:
            member = ctx.author
        #guild id recebe o Id da guilda
        #user id recebe o id do membro guilda
        guild_id = ctx.guild.id
        user_id = member.id
        #user infractions recebe o get Das infraçoes ou seja Reune todas as infraçoes do Usuario
        user_infractions = infractions.get(guild_id,{}).get( user_id,[])
        # se nao tiver infraçoes
        if not user_infractions:
            await ctx.send(f"{member.mention} Nao possui infraçoes")
        else:
            #embed de Infraçoes
            embed = discord.Embed(
                title=f"Infraçoes de {member.name}",
                description="\n".join(f"{i+1}.{reason}"for i,reason in enumerate(user_infractions)),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)










async def setup(bot):
    await bot.add_cog(infractions(bot))