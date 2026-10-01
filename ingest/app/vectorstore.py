"""Conexao com o Pinecone (emulador local) via LangChain."""

from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from .config import settings


@lru_cache
def embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings().embedding_model,
        api_key=settings().openai_api_key,
    )


@lru_cache
def client() -> Pinecone:
    return Pinecone(api_key=settings().pinecone_api_key, host=settings().pinecone_host)


@lru_cache
def store() -> PineconeVectorStore:
    pc = client()
    name = settings().pinecone_index

    if not pc.has_index(name):
        pc.create_index(
            name=name,
            dimension=settings().embedding_dimensions,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return PineconeVectorStore(index=pc.Index(host=_index_host(name)), embedding=embeddings())


def _index_host(name: str) -> str:
    """O Pinecone Local abre uma porta por indice e devolve o host sem esquema."""
    host = client().describe_index(name).host
    return host if host.startswith("http") else f"http://{host}"


def delete_document(document_id: int) -> None:
    """Apaga os vetores de um documento.

    Indices serverless (e o emulador local) nao aceitam delete por filtro de
    metadata, entao usamos o prefixo dos ids, que seguem o padrao
    "doc-<id>-chunk-<n>" definido no pipeline.
    """
    index = client().Index(host=_index_host(settings().pinecone_index))
    for page in index.list(prefix=f"doc-{document_id}-chunk-"):
        if page:
            index.delete(ids=page)
