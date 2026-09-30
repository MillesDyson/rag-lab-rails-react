"""Audio -> texto, via Whisper da OpenAI."""

import subprocess
import tempfile
from pathlib import Path

from openai import OpenAI

from ..config import settings

# a API do Whisper recusa arquivos acima de 25MB; cortamos antes de chegar la
MAX_UPLOAD_BYTES = 24 * 1024 * 1024
SEGMENT_SECONDS = 600


def transcribe(path: Path) -> str:
    client = OpenAI(api_key=settings().openai_api_key)
    pieces = [path] if path.stat().st_size <= MAX_UPLOAD_BYTES else _split(path)

    texts = []
    for piece in pieces:
        with piece.open("rb") as handle:
            texts.append(
                client.audio.transcriptions.create(
                    model=settings().whisper_model,
                    file=handle,
                    response_format="text",
                )
            )
    return "\n\n".join(t.strip() for t in texts if t.strip())


def _split(path: Path) -> list[Path]:
    """Quebra o audio em blocos de 10min reencodando pra mp3 mono 16kHz."""
    outdir = Path(tempfile.mkdtemp(prefix="raglab-audio-"))
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(path),
            "-f", "segment", "-segment_time", str(SEGMENT_SECONDS),
            "-ac", "1", "-ar", "16000", "-b:a", "64k",
            str(outdir / "part-%03d.mp3"),
        ],
        check=True,
    )
    return sorted(outdir.glob("part-*.mp3"))
