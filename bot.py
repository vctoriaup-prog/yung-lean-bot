import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import discord
from google import genai

# === SERVIDOR FANTASMA PARA RENDER (UPTIMEROBOT) ===
def iniciar_servidor():
    puerto = int(os.environ.get("PORT", 8080))
    servidor = HTTPServer(('0.0.0.0', puerto), SimpleHTTPRequestHandler)
    servidor.serve_forever()

threading.Thread(target=iniciar_servidor, daemon=True).start()

# === LECTURA DE CLAVES SEGURAS DESDE RENDER ===
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# Configura tu cliente de Gemini
client_genai = genai.Client(api_key=GEMINI_API_KEY)

# Configura los intents de Discord
intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'¡Conectado con éxito como {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            prompt = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()
            
            if not prompt:
                await message.reply("¡Hola! ¿En qué te puedo ayudar hoy?")
                return

            try:
                response = client_genai.models.generate_content(
                    model='gemini-1.5-flash',
                    contents="Habla muy sarcástico, rebelde y directo. REGLA: Sé MUY breve, responde en máximo 1 o 2 oraciones. El usuario te dice esto: " + prompt
                )
                await message.reply(response.text)
            except Exception as e: 
                print(f"ERROR OCULTO: {e}", flush=True)
                await message.reply("Ups, ocurrió un error al procesar tu solicitud.")    

client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
