# brnow_tts/tts.py

from livekit.plugins import google

class TTS(google.TTS):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)