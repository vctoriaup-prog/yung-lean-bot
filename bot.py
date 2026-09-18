import os
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from google import genai

# === 1. SERVIDOR FANTASMA PARA HEALTH CHECK DE RENDER ===
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot OK")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def iniciar_servidor():
    puerto = int(os.environ.get("PORT", 10000))
    servidor = HTTPServer(('0.0.0.0', puerto), HealthCheckHandler)
    servidor.serve_forever()

threading.Thread(target=iniciar_servidor, daemon=True).start()

# === 2. LECTURA DE CLAVES Y CONFIGURACIÓN ===
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

class YungLeanBot(discord.Client):
    async def on_ready(self):
        print(f'¡Conectado como {self.user}!', flush=True)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            prompt = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()

            if not prompt:
                await message.reply("¿Qué pasó?")
                return

            ultimo_error = ""
            for intento in range(3):
                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=f"Actúa como Yung Lean: sarcástico, relajado e ironico SE BREVE. El usuario te dice: {prompt}"
                    )
                    if response and response.text:
                        await message.reply(response.text)
                        return
                except Exception as e:
                    ultimo_error = str(e)
                    print(f"[ERROR GEMINI] Intento {intento + 1}: {e}", flush=True)
                    await asyncio.sleep(2)

            await message.reply(f"Google falló. Detalle: `{ultimo_error}`")

client = YungLeanBot(intents=intents)
client.run(DISCORD_TOKEN)
