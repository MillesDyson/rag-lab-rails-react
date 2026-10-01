"""Orquestra a ingestao: baixa -> extrai texto -> divide -> vetoriza -> grava."""

import logging
import mimetypes
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import httpx
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import extractors
from .config import settings
from .vectorstore import store

logger = logging.getLogger("raglab.pipeline")

PREVIEW_LENGTH = 500


@dataclass
class Result:
    chunks: int
    characters: int
    kind: str
    text: str


def run(document_id: int, file_url: str, content_type: str, filename: str) -> Result:
    with _timed(document_id, "download"):
        path = _download(file_url, filename)

    try:
        with _timed(document_id, f"extract ({content_type})"):
            text, kind = extractors.extract(path, content_type)
    finally:
        path.unlink(missing_ok=True)

    text = text.strip()
    if not text:
        raise ValueError("a extracao nao produziu nenhum texto")

    chunks = _split(text)
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "document_id": document_id,
                "filename": filename,
                "kind": kind,
                "chunk_index": index,
            },
        )
        for index, chunk in enumerate(chunks)
    ]
    ids = [f"doc-{document_id}-chunk-{index}" for index in range(len(documents))]

    with _timed(document_id, f"embed + upsert ({len(documents)} chunks)"):
        store().add_documents(documents=documents, ids=ids)

    return Result(chunks=len(documents), characters=len(text), kind=kind, text=text)


@contextmanager
def _timed(document_id: int, label: str):
    started = time.monotonic()
    logger.info("[doc %s] %s...", document_id, label)
    yield
    logger.info("[doc %s] %s levou %.1fs", document_id, label, time.monotonic() - started)


def _split(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings().chunk_size,
        chunk_overlap=settings().chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def _download(url: str, filename: str) -> Path:
    suffix = Path(filename).suffix or mimetypes.guess_extension("application/octet-stream") or ""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        path = Path(tmp.name)
        with httpx.stream("GET", url, follow_redirects=True, timeout=120) as response:
            response.raise_for_status()
            for block in response.iter_bytes():
                tmp.write(block)
    return path
