import os
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from google import genai
from google.genai import types # Importamos los tipos para configurar las instrucciones

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

# === 3. CEREBRO DEL BOT (MEMORIA POR USUARIO) ===
# Este diccionario guardará el historial de chat de cada persona que le hable
memoria_usuarios = {}

class YungLeanBot(discord.Client):
    async def on_ready(self):
        print(f'¡Conectado con éxito como {self.user}!', flush=True)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            prompt = message.content.replace(f'<@!{self.user.id}>', '').replace(f'<@{self.user.id}>', '').strip()

            if not prompt:
                await message.reply("¿Qué pasó?")
                return

            async with message.channel.typing():
                
                usuario_id = message.author.id
                
                # Si el usuario le habla por primera vez, le creamos un chat nuevo con memoria
                if usuario_id not in memoria_usuarios:
                    instruccion_personalidad = "Actúa como Yung Lean: sarcástico, relajado y directo. REGLA ESTRICTA: Responde en máximo 1 sola oración corta, sin discursos largos ni insultos agresivos."
                    
                    memoria_usuarios[usuario_id] = gemini_client.chats.create(
                        model='gemini-3.6-flash',
                        config=types.GenerateContentConfig(
                            system_instruction=instruccion_personalidad
                        )
                    )
                
                # Extraemos el historial de conversación específico de quien está hablando
                chat_actual = memoria_usuarios[usuario_id]

                max_intentos = 3
                for intento in range(max_intentos):
                    try:
                        # En vez de generate_content, usamos send_message para que recuerde
                        response = chat_actual.send_message(prompt)
                        await message.reply(response.text)
                        return
                    except Exception as e:
                        print(f"Intento {intento + 1} falló: {e}", flush=True)
                        if intento < max_intentos - 1:
                            await asyncio.sleep(2)
                        else:
                            await message.reply("Google se pegó un segundo, habla ahora.")

client = YungLeanBot(intents=intents)
client.run(DISCORD_TOKEN)
