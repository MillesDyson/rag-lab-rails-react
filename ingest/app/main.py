import logging
import traceback

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from pydantic import BaseModel

from . import callbacks, pipeline, query
from .config import settings
from .extractors import UnsupportedFile
from .vectorstore import delete_document

# o uvicorn configura apenas os loggers dele; sem isso o nosso fica mudo
logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")

app = FastAPI(title="raglab-ingest")


class QueryRequest(BaseModel):
    question: str
    k: int = 5
    kinds: list[str] | None = None


class IngestRequest(BaseModel):
    document_id: int
    file_url: str
    content_type: str
    filename: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query")
def ask(request: QueryRequest, x_internal_token: str = Header(default="")) -> dict:
    _authorize(x_internal_token)
    resultado = query.run(request.question, k=request.k, kinds=request.kinds)
    return {
        "answer": resultado.answer,
        "sources": [vars(source) for source in resultado.sources],
    }


@app.post("/ingest", status_code=202)
def ingest(
    request: IngestRequest,
    background: BackgroundTasks,
    x_internal_token: str = Header(default=""),
) -> dict:
    _authorize(x_internal_token)
    background.add_task(_process, request)
    return {"status": "accepted", "document_id": request.document_id}


@app.delete("/documents/{document_id}")
def destroy(document_id: int, x_internal_token: str = Header(default="")) -> dict:
    _authorize(x_internal_token)
    delete_document(document_id)
    return {"status": "deleted", "document_id": document_id}


def _authorize(token: str) -> None:
    if token != settings().internal_token:
        raise HTTPException(status_code=401, detail="token interno invalido")


def _process(request: IngestRequest) -> None:
    try:
        result = pipeline.run(
            document_id=request.document_id,
            file_url=request.file_url,
            content_type=request.content_type,
            filename=request.filename,
        )
    except UnsupportedFile as error:
        callbacks.notify(request.document_id, {"status": "failed", "error": str(error)})
    except Exception as error:
        traceback.print_exc()
        callbacks.notify(
            request.document_id,
            {"status": "failed", "error": f"{type(error).__name__}: {error}"},
        )
    else:
        callbacks.notify(
            request.document_id,
            {
                "status": "completed",
                "chunks_count": result.chunks,
                "characters_count": result.characters,
                "kind": result.kind,
                "extracted_text": result.text,
                "extracted_preview": result.text[:pipeline.PREVIEW_LENGTH],
            },
        )
