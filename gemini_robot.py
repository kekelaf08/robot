import os
import asyncio
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from live_audio_handler import LiveAudioHandler

# Charger les variables d'environnement
load_dotenv()

class LiveGeminiRobot:
    def __init__(self, api_key=None, model_id='gemini-3.1-flash-live-preview', chunk_size=2048):
        """
        Initialise le robot pour l'interaction Multimodale Live.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API Google AI est manquante.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = model_id
        self.audio_handler = LiveAudioHandler(chunk_size=chunk_size)
        self.input_queue = asyncio.Queue()

    async def run(self):
        """ Boucle principale de l'interaction Live avec auto-reconnexion. """
        print(f"--- Démarrage de l'IA Temps Réel (Modèle: {self.model_id}) ---")
        
        config = {
            "generation_config": {"response_modalities": ["AUDIO"]},
            "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": "Aoede"}}}
        }

        self.audio_handler.start_input(self.input_queue)
        self.audio_handler.start_output()

        retries = 2
        while retries > 0:
            try:
                async with self.client.aio.live.connect(model=self.model_id, config=config) as session:
                    print("[Robot] Prêt ! Parlez-moi...")

                    async def send_audio():
                        while True:
                            audio_data = await self.input_queue.get()
                            await session.send_realtime_input(
                                audio=types.Blob(data=audio_data, mime_type="audio/pcm;rate=16000")
                            )

                    async def receive_audio():
                        async for response in session.receive():
                            if response.server_content and response.server_content.model_turn:
                                parts = response.server_content.model_turn.parts
                                for part in parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        audio_bytes = part.inline_data.data
                                        if isinstance(audio_bytes, str):
                                            audio_bytes = base64.b64decode(audio_bytes)
                                        self.audio_handler.play_chunk(audio_bytes)
                            
                            if response.server_content and response.server_content.interrupted:
                                self.audio_handler.stop_output()

                    await asyncio.gather(send_audio(), receive_audio())
                    break # Si on sort proprement, on ne réessaie pas

            except Exception as e:
                retries -= 1
                if retries > 0:
                    print(f"[Robot] Reconnexion en cours après erreur : {e}")
                    await asyncio.sleep(2)
                else:
                    print(f"[ERREUR Finale] : {e}")
        
        self.audio_handler.close()

if __name__ == "__main__":
    robot = LiveGeminiRobot()
    asyncio.run(robot.run())
