"""Avisa o Rails quando a ingestao termina (ou falha)."""

import httpx

from .config import settings


def notify(document_id: int, payload: dict) -> None:
    url = f"{settings().rails_callback_url}/api/v1/documents/{document_id}/ingested"
    try:
        httpx.post(
            url,
            json=payload,
            headers={"X-Internal-Token": settings().internal_token},
            timeout=30,
        ).raise_for_status()
    except httpx.HTTPError as error:
        print(f"[callback] falhou para o documento {document_id}: {error}")
