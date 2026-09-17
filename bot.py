import discord
import os
from google import genai

# 1. Configuración de credenciales
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. Inicialización de clientes
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

# Cliente actualizado para la nueva librería google-genai
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@discord_client.event
async def on_ready():
    print(f'¡Conectado con éxito como {discord_client.user}!')

@discord_client.event
async def on_message(message):
    # Evitar que el bot se responda a sí mismo
    if message.author == discord_client.user:
        return

    # Responder solo si lo mencionan
    if discord_client.user in message.mentions:
        try:
            # Limpiar la mención del texto para que Gemini lea solo la pregunta
            prompt = message.content.replace(f'<@{discord_client.user.id}>', '').strip()
            
            # Llamada a la API usando el modelo que confirmaste en tu terminal
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            
            await message.reply(response.text)
            
        except Exception as e:
            # LA SOLUCIÓN TRASCENDENTE: Escupir el error real en Discord
            error_revelado = f"**El sistema falló. Este es el error técnico real:**\n```python\n{str(e)}\n```"
            print(f"ERROR CRÍTICO: {e}")
            await message.reply(error_revelado)

discord_client.run(DISCORD_TOKEN)
