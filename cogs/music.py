# Arquivo: cogs/music.py

import discord
from discord.ext import commands
import asyncio
import yt_dlp
from collections import deque  # Importar deque para a fila

# --- Configurações de Áudio ---
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': True, 'default_search': 'ytsearch'}


# --- A Classe do Cog de Música ---
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.song_queues = {}  # NOVO: Dicionário para armazenar as filas por Guild ID

    # --- Função auxiliar para tocar a próxima música ---
    async def play_next_song(self, guild_id, channel):
        if guild_id in self.song_queues and self.song_queues[guild_id]:
            vc = self.voice_clients.get(guild_id)
            if not vc or not vc.is_connected():
                # Bot desconectou, limpar a fila para este guild
                del self.song_queues[guild_id]
                return

            # Pega a próxima música da fila
            song_info = self.song_queues[guild_id].popleft()
            song_url = song_info['url']
            title = song_info['title']

            source = discord.FFmpegOpusAudio(song_url, **FFMPEG_OPTIONS)

            # Quando a música terminar, chama play_next_song novamente
            vc.play(source, after=lambda e: self.bot.loop.create_task(self.play_next_song(guild_id, channel)))
            await channel.send(f"Tocando agora: **{title}**")
        else:
            # Fila está vazia, não há mais músicas para tocar.
            vc = self.voice_clients.get(guild_id)

            # Se o bot ainda estiver conectado, espera um tempo antes de sair.
            if vc and vc.is_connected():
                # Espera 60 segundos. Se outra música for adicionada nesse tempo, ele não desconecta.
                await asyncio.sleep(120)

                # Depois de esperar, verifica novamente se ainda está inativo.
                if vc.is_connected() and not vc.is_playing() and not vc.is_paused():
                    await vc.disconnect()
                    # Limpa as entradas do dicionário para este servidor
                    if guild_id in self.voice_clients:
                        del self.voice_clients[guild_id]
                    if guild_id in self.song_queues:
                        del self.song_queues[guild_id]
                    await channel.send("Fila vazia. Desconectando do canal de voz.")


    # --- Comandos ---
    @commands.command(name="play", help="Toca uma música do YouTube.")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            await ctx.send("Você precisa estar em um canal de voz!")
            return

        voice_channel = ctx.author.voice.channel
        guild_id = ctx.guild.id

        try:
            if guild_id not in self.voice_clients or not self.voice_clients[guild_id].is_connected():
                self.voice_clients[guild_id] = await voice_channel.connect()

            vc = self.voice_clients[guild_id]

            async with ctx.typing():
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YDL_OPTIONS).extract_info(query,
                                                                                                           download=False))

                if 'entries' in data:
                    data = data['entries'][0]

                song_url = data.get('url')
                title = data.get('title', 'Título Desconhecido')

                # NOVO: Inicializa a fila se não existir
                if guild_id not in self.song_queues:
                    self.song_queues[guild_id] = deque()

                # Adiciona a música à fila
                self.song_queues[guild_id].append({'url': song_url, 'title': title})

                # Se o bot não estiver tocando nada, inicia a reprodução
                if not vc.is_playing() and not vc.is_paused():
                    await ctx.send(f"Tocando agora: **{title}**")
                    await self.play_next_song(guild_id, ctx.channel)  # Inicia a primeira música
                else:
                    await ctx.send(f"Adicionado à fila: **{title}**")  # Informa que foi para a fila

        except Exception as e:
            print(f"Erro no comando play: {e}")
            await ctx.send("Ocorreu um erro ao tentar tocar a música.")

    @commands.command(name="pause", help="Pausa a música atual.")
    async def pause(self, ctx):
        vc = self.voice_clients.get(ctx.guild.id)
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("Música pausada.")
        else:
            await ctx.send("Não há música tocando para pausar.")

    @commands.command(name="resume", help="Retoma a música pausada.")
    async def resume(self, ctx):
        vc = self.voice_clients.get(ctx.guild.id)
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("Música retomada.")
        else:
            await ctx.send("Não há música pausada para retomar.")

    @commands.command(name="stop", help="Para a música e desconecta o bot.")
    async def stop(self, ctx):
        guild_id = ctx.guild.id
        vc = self.voice_clients.get(guild_id)

        # NOVO: Limpa a fila antes de desconectar
        if guild_id in self.song_queues:
            self.song_queues[guild_id].clear()

        if vc and vc.is_connected():
            vc.stop()  # Para qualquer reprodução imediatamente
            await vc.disconnect()
            del self.voice_clients[guild_id]
            if guild_id in self.song_queues:
                del self.song_queues[guild_id]
            await ctx.send("Bot desconectado e fila limpa.")
        else:
            await ctx.send("Não estou conectado a um canal de voz.")

    @commands.command(name="skip", help="Pula a música atual.")
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        vc = self.voice_clients.get(guild_id)

        if vc and vc.is_playing():
            vc.stop()  # Parar a música atual irá acionar 'play_next_song' através do callback 'after'
            await ctx.send("Música pulada!")
        elif guild_id in self.song_queues and self.song_queues[guild_id]:
            # Se não estiver tocando, mas tiver fila, podemos pular para a próxima sem 'stop'
            await ctx.send("Pulando para a próxima música na fila.")
            await self.play_next_song(guild_id, ctx.channel)
        else:
            await ctx.send("Não há música tocando para pular, e a fila está vazia.")

    @commands.command(name="exit",help="sai da call")
    async def exit(self, ctx):
        guild_id = ctx.guild.id
        vc = self.voice_clients.get(guild_id)
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("Bot desconectado e fila limpa.")
            await vc.disconnect()


    @commands.command(name="queue", help="Mostra a lista de musicas na fila.")
    async def queue(self, ctx):
        guild_id = ctx.guild.id

        # Verifica se existe uma fila para o servidor e se ela não está vazia
        if guild_id in self.song_queues and self.song_queues[guild_id]:
            queue = self.song_queues[guild_id]

            # Cria um Embed para uma aparência mais profissional
            embed = discord.Embed(
                title="🎵 Fila de Músicas",
                description=f"Atualmente há {len(queue)} música(s) na fila.",
                color=discord.Color.blue()
            )

            # Formata a lista de músicas
            # Usamos enumerate para ter um contador (1., 2., 3., etc.)
            # Limitamos a 10 músicas para não poluir o chat
            song_list = ""
            for i, song in enumerate(list(queue)[:10]):
                song_list += f"**{i + 1}.** {song['title']}\n"

            embed.add_field(name="Próximas Músicas:", value=song_list, inline=False)

            # Adiciona um rodapé
            embed.set_footer(text=f"Pedido por {ctx.author.display_name}")

            await ctx.send(embed=embed)

        else:
            # Mensagem para quando a fila está vazia ou não existe
            await ctx.send("A fila de músicas está vazia!")





# --- Função Setup para carregar o Cog ---
async def setup(bot):
    await bot.add_cog(Music(bot))