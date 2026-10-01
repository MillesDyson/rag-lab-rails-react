"""Consulta: recupera trechos relevantes e gera uma resposta citando as fontes."""

import logging
from dataclasses import dataclass

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import settings
from .vectorstore import store

logger = logging.getLogger("raglab.query")

SISTEMA = """Voce responde perguntas usando APENAS os trechos fornecidos.

Regras:
- Responda em portugues do Brasil, de forma direta.
- Cite a origem de cada afirmacao com o numero do trecho, no formato [1], [2].
  Uma afirmacao pode citar mais de um trecho.
- Raciocinar sobre os dados dos trechos NAO e conhecimento externo: voce pode
  comparar, ordenar, contar e somar os valores que aparecem neles. Ao fazer
  conta, liste as parcelas usadas para que o leitor confira.
- Se os trechos trazem uma listagem e o item perguntado nao esta nela, responda
  que ele nao aparece na listagem recuperada -- isso e diferente de dizer que a
  informacao nao existe.
- So diga que a informacao nao esta nos documentos quando os dados realmente
  nao estiverem nos trechos. Nunca complete com conhecimento proprio.
- Preste atencao a negacoes e a decisoes rejeitadas: nao trate como aprovado
  algo que os trechos descrevem como recusado."""

USUARIO = """Trechos:

{contexto}

Pergunta: {pergunta}"""

PROMPT = ChatPromptTemplate.from_messages([("system", SISTEMA), ("human", USUARIO)])


@dataclass
class Source:
    document_id: int
    filename: str
    kind: str
    chunk_index: int
    score: float
    excerpt: str


@dataclass
class Answer:
    answer: str
    sources: list[Source]


def run(pergunta: str, k: int = 5, kinds: list[str] | None = None) -> Answer:
    sources = retrieve(pergunta, k=k, kinds=kinds)
    if not sources:
        return Answer(answer="Nenhum documento indexado corresponde a essa pergunta.", sources=[])

    logger.info("[query] %r -> %d trechos", pergunta, len(sources))
    chain = PROMPT | _model() | StrOutputParser()
    texto = chain.invoke({"contexto": _format(sources), "pergunta": pergunta})
    return Answer(answer=texto, sources=sources)


def retrieve(pergunta: str, k: int = 5, kinds: list[str] | None = None) -> list[Source]:
    # o Pinecone guarda todo numero de metadata como float, dai o int()
    filtro = {"kind": {"$in": kinds}} if kinds else None
    encontrados = store().similarity_search_with_score(pergunta, k=k, filter=filtro)

    return [
        Source(
            document_id=int(doc.metadata["document_id"]),
            filename=doc.metadata["filename"],
            kind=doc.metadata["kind"],
            chunk_index=int(doc.metadata["chunk_index"]),
            score=round(float(score), 4),
            excerpt=doc.page_content,
        )
        for doc, score in encontrados
    ]


def _format(sources: list[Source]) -> str:
    return "\n\n".join(
        f"[{i}] (arquivo: {s.filename})\n{s.excerpt}" for i, s in enumerate(sources, start=1)
    )


def _model() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings().answer_model,
        api_key=settings().openai_api_key,
        temperature=0,
    )
