"""Texto puro: le o arquivo e pronto."""

from pathlib import Path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")
