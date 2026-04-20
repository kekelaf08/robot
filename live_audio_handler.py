import asyncio
import pyaudio

class LiveAudioHandler:
    def __init__(self, sample_rate=16000, chunk_size=512):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.pa = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.is_playing = False

    def start_input(self, queue):
        """ Démarre la capture du microphone et met les chunks dans la file. """
        def callback(in_data, frame_count, time_info, status):
            queue.put_nowait(in_data)
            return (None, pyaudio.paContinue)

        self.input_stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=callback
        )

    def start_output(self):
        """ Prépare le flux de sortie pour les haut-parleurs. """
        self.output_stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size
        )

    def play_chunk(self, audio_data):
        """ Joue un chunk audio reçu de l'API. """
        if self.output_stream:
            self.output_stream.write(audio_data)

    def stop_output(self):
        """ Arrête immédiatement le son en cours (utile pour l'interruption). """
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.start_stream() # On relance pour être prêt pour la suite

    def close(self):
        """ Ferme proprement les flux. """
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.pa.terminate()

async def audio_input_generator(queue):
    """ Générateur asynchrone qui lit les chunks de la file. """
    while True:
        chunk = await queue.get()
        yield chunk
