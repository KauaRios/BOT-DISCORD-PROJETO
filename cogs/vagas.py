from time import sleep

import discord
from discord.ext import commands, tasks
import requests
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
CANAL_VAGAS_ID = 1429126835828031679  # ID do canal de vagas

TERMS = [
    "python", "javascript", "java", "c#", "c++", "php", "ruby", "go", "typescript", "swift", "kotlin",
    "frontend", "backend", "fullstack", "desenvolvedor", "estagio","Estagio",
    "android", "ios", "flutter", "react native",
    "react", "angular", "vue", "nodejs", "express", "django", "flask",
    "sql", "mysql", "postgresql", "mongodb",
    "devops", "aws", "docker", "kubernetes",
    "data scientist", "machine learning", "ai",
    "junior","ESTAGIO"
]

MAX_TERMS = 500         # máximo de termos a serem processados
MAX_VAGAS_POR_EXEC = 25   # máximo de vagas a enviar por execução

class VagasAutomatizadas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vagas_enviadas = set()  # controla vagas já enviadas permanentemente
        self.postar_vagas.start()    # inicia o loop de vagas
        self.limpar_canal.start()    # inicia o loop de limpeza

    def cog_unload(self):
        self.postar_vagas.cancel()
        self.limpar_canal.cancel()

    @tasks.loop(minutes=2)
    async def postar_vagas(self):
        canal = self.bot.get_channel(CANAL_VAGAS_ID)
        if not canal:
            print("❌ Canal de vagas não encontrado!")
            return

        url = "https://api.adzuna.com/v1/api/jobs/br/search/1"
        vagas_enviadas_essa_exec = 0 # controla o máximo por execução

        for i, termo in enumerate(TERMS):
            if i >= MAX_TERMS:
                break

            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "what": termo,
                "where": "Rio de Janeiro",
                "results_per_page": 5,
                "content-type": "application/json"
            }

            try:
                response = requests.get(url, params=params)
                data = response.json()

                if "results" not in data or not data["results"]:
                    continue  # pula se não houver resultados

                for job in data["results"]:
                    job_id = job.get("id")
                    if job_id in self.vagas_enviadas:
                        continue  # pula vagas já enviadas
                    self.vagas_enviadas.add(job_id)

                    titulo = job.get("title", "Sem título")
                    empresa = job.get("company", {}).get("display_name", "Não informada")
                    local = job.get("location", {}).get("display_name", "Local não informado")
                    link = job.get("redirect_url", "Link indisponível")

                    embed = discord.Embed(
                        title=titulo,
                        description=f"**Empresa:** {empresa}\n**Local:** {local}\n[🔗 Ver vaga]({link})",
                        color=discord.Color.green()
                    )
                    await canal.send(embed=embed)

                    vagas_enviadas_essa_exec += 1
                    if vagas_enviadas_essa_exec >= MAX_VAGAS_POR_EXEC:
                        print(f"✅ Limite de {MAX_VAGAS_POR_EXEC} vagas atingido nesta execução.")
                        return  # sai da função para não enviar mais vagas

            except Exception as e:
                print(f"❌ Erro ao buscar vagas para '{termo}': {e}")

    @postar_vagas.before_loop
    async def before_postar_vagas(self):
        await self.bot.wait_until_ready()
        print("✅ Loop de vagas iniciado!")

    @tasks.loop(minutes=30)
    async def limpar_canal(self):
        canal = self.bot.get_channel(CANAL_VAGAS_ID)
        if not canal:
            print("❌ Canal não encontrado para limpeza")
            return
        await canal.purge(limit=100)
        print("✅ Canal limpo")

    @limpar_canal.before_loop
    async def before_limpar_canal(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(60)


async def setup(bot):
    await bot.add_cog(VagasAutomatizadas(bot))
