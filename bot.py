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

            # Reintentos automáticos para evitar el error 503
            max_intentos = 3
            for intento in range(max_intentos):
                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents="Habla muy sarcástico, rebelde y directo. REGLA: Sé MUY breve, responde en máximo 1 o 2 oraciones. El usuario te dice esto: " + prompt
                    )
                    await message.reply(response.text)
                    return # Si respondió con éxito, sale del bucle
                except Exception as e:
                    print(f"Intento {intento + 1} falló por saturación de la API: {e}", flush=True)
                    if intento < max_intentos - 1:
                        await asyncio.sleep(2) # Espera 2 segundos antes de reintentar
                    else:
                        # Respuesta en personaje en lugar del recuadro de error
                        await message.reply("Google está colapsado ahora mismo. Intenta hablarme de nuevo en 10 segundos.")

client = YungLeanBot(intents=intents)
client.run(DISCORD_TOKEN)
