import os
import threading
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
    print(f"Servidor HTTP listo en el puerto {puerto}", flush=True)
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
        print(f'¡Conectado con éxito como {self.user}!', flush=True)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            prompt = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()

            if not prompt:
                await message.reply("¿Qué quieres? Habla rápido o no molestes.")
                return

            try:
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents="Habla muy sarcástico, rebelde y directo. REGLA: Sé MUY breve, responde en máximo 1 o 2 oraciones. El usuario te dice esto: " + prompt
                )
                await message.reply(response.text)
            except Exception as e:
                error_msg = f"**Falló el modelo de IA:**\n```python\n{str(e)}\n```"
                print(f"ERROR: {e}", flush=True)
                await message.reply(error_msg)

client = YungLeanBot(intents=intents)
client.run(DISCORD_TOKEN)
