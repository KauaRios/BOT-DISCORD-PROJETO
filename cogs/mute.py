import discord
from discord.ext import commands




class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        guild=ctx.guild
        role=discord.utils.get(guild.roles,name='Muted')


        if not role:
            role=await guild.create_role(name='Muted')
            for channel in guild.channels:
                await channel.set_permissions(role,speak=False,send_messages=False,add_reactions=False)
        await member.add_roles(role)
        await ctx.send(f'Mute **{member.name}** for **{reason}**')



    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        guild=ctx.guild
        role=discord.utils.get(guild.roles,name='Muted')
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"{member.mention} foi desmutado")
        else:
            await ctx.send (f"{member.mention} nao esta Mutado")







async def setup(bot):
    await bot.add_cog(Mute(bot))