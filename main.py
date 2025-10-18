# Arquivo: main.py

import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
#testando essa bagaça
# Carrega o token do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- Configuração do Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='?', intents=intents)

# MANTENHA APENAS ESTA VERSÃO DO ON_READY
@bot.event
async def on_ready():
    print(f'{bot.user.name} está online e pronto!')

    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Falha ao sincronizar comandos: {e}")

    print(f'Comandos carregados e prontos para uso.')
    print('-----------------------------------------')

# --- Função Principal para Carregar Cogs e Iniciar o Bot ---
async def main():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Carregado o cog: {filename}')

    await bot.start(TOKEN)

# Ponto de entrada para rodar o bot
if __name__ == "__main__":
    if TOKEN:
        asyncio.run(main())
    else:
        print("ERRO: O token não foi encontrado. Verifique seu arquivo .env")