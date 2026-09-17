import os
import discord
from google import genai

# Configura tu cliente de Gemini con tu API Key
client_genai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Configura los intents de Discord
intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'¡Conectado con éxito como {self.user}!')

    async def on_message(self, message):
        # Si el autor del mensaje es un bot (incluyéndose a sí mismo), ignorar el mensaje 
        if message.author == self.user:
            return

        # El bot responderá cuando lo menciones en el chat
        if self.user.mentioned_in(message):
            # Limpiamos la mención para que la IA reciba solo el texto limpio
            prompt = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()
            
            if not prompt:
                await message.reply("¡Hola! ¿En qué te puedo ayudar hoy?")
                return

            try:
                # Envía la pregunta a Gemini
                response = client_genai.models.generate_content(
                    model='gemini-1.5-flash',
                    contents="Habla muy sarcástico, rebelde y directo. REGLA: Sé MUY breve, responde en máximo 1 o 2 oraciones. El usuario te dice esto: " + prompt
)
                
                # Envía la respuesta generada de vuelta a Discord
                await message.reply(response.text)
            except Exception as e:
                await message.reply("Ups, ocurrió un error al procesar tu solicitud.")
                print(e)

# === SERVIDOR FANTASMA PARA RENDER ===
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

def iniciar_servidor():
    puerto = int(os.environ.get("PORT", 8080))
    servidor = HTTPServer(('0.0.0.0', puerto), SimpleHTTPRequestHandler)
    servidor.serve_forever()

threading.Thread(target=iniciar_servidor, daemon=True).start()
# =====================================

client = MyClient(intents=intents)
client.run(os.environ.get("DISCORD_TOKEN"))


