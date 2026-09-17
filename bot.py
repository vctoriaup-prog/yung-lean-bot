import discord
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai

# 1. Servidor web ligero para el Health Check de Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot activo")
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Servidor Web de salud iniciado en el puerto {port}")
    server.serve_forever()

# Iniciar servidor web en un hilo secundario
threading.Thread(target=run_web_server, daemon=True).start()

# 2. Configuración de credenciales
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 3. Inicialización de clientes
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@discord_client.event
async def on_ready():
    print(f'¡Conectado con éxito como {discord_client.user}!')

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if discord_client.user in message.mentions:
        try:
            prompt = message.content.replace(f'<@{discord_client.user.id}>', '').strip()
            
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            
            await message.reply(response.text)
            
        except Exception as e:
            error_revelado = f"**El sistema falló. Este es el error técnico real:**\n```python\n{str(e)}\n```"
            print(f"ERROR CRÍTICO: {e}")
            await message.reply(error_revelado)

discord_client.run(DISCORD_TOKEN)
