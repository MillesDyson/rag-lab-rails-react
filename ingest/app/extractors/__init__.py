"""Roteia o arquivo para o extrator certo de acordo com o content type."""

from pathlib import Path
from typing import Callable

from . import audio, documents, image, plain, video

DOCUMENT_MIMES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
}

PLAIN_MIMES = {"text/plain", "text/markdown"}


class UnsupportedFile(Exception):
    pass


def extract(path: Path, content_type: str) -> tuple[str, str]:
    """Devolve (texto, tipo_logico). O tipo logico vai pro metadata do vetor."""
    handler, kind = _resolve(content_type)
    return handler(path), kind


def _resolve(content_type: str) -> tuple[Callable[[Path], str], str]:
    if content_type.startswith("video/"):
        return video.transcribe, "video"
    if content_type.startswith("audio/"):
        return audio.transcribe, "audio"
    if content_type.startswith("image/"):
        return image.describe, "image"
    if content_type in DOCUMENT_MIMES:
        return documents.parse, "document"
    if content_type in PLAIN_MIMES:
        return plain.read, "text"
    raise UnsupportedFile(f"content type nao suportado: {content_type}")
