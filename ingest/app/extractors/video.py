"""Video -> texto: extrai a trilha de audio com ffmpeg e manda pro Whisper."""

import subprocess
import tempfile
from pathlib import Path

from . import audio


def transcribe(path: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        audio_path = Path(tmp.name)

    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(path),
            "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
            str(audio_path),
        ],
        check=True,
    )
    return audio.transcribe(audio_path)
