"""Tools for ElevenLabs audio server."""

from .tts import (
    text_to_speech,
    text_to_speech_with_timestamps,
    generate_dialogue
)

from .stt import (
    speech_to_text,
    transcribe_from_base64,
    batch_transcribe
)

from .effects import (
    generate_sound_effect,
    batch_generate_effects
)

from .voice_transform import (
    speech_to_speech,
    isolate_audio,
    batch_voice_transform
)

__all__ = [
    # TTS tools
    "text_to_speech",
    "text_to_speech_with_timestamps",
    "generate_dialogue",
    
    # STT tools
    "speech_to_text",
    "transcribe_from_base64",
    "batch_transcribe",
    
    # Effects tools
    "generate_sound_effect",
    "batch_generate_effects",
    
    # Voice transformation tools
    "speech_to_speech",
    "isolate_audio",
    "batch_voice_transform"
]