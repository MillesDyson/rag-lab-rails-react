"""Imagem -> texto, via modelo de visao."""

import base64
import mimetypes
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ..config import settings

PROMPT = (
    "Descreva esta imagem em portugues de forma detalhada e objetiva, para que o texto "
    "possa ser indexado e pesquisado depois. Inclua: o que aparece na cena, objetos, "
    "pessoas, cores dominantes e TODO texto visivel transcrito literalmente. "
    "Nao invente nada que nao esteja na imagem."
)


def describe(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode()

    model = ChatOpenAI(
        model=settings().vision_model,
        api_key=settings().openai_api_key,
        temperature=0,
    )
    message = HumanMessage(
        content=[
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}},
        ]
    )
    return model.invoke([message]).content
