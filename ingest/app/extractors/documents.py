"""CSV / DOCX / PDF / XLSX -> markdown, via LlamaParse."""

from pathlib import Path

from llama_parse import LlamaParse

from ..config import settings


def parse(path: Path) -> str:
    parser = LlamaParse(
        api_key=settings().llama_cloud_api_key,
        result_type="markdown",
        language="pt",
        verbose=False,
    )
    documents = parser.load_data(str(path))
    return "\n\n".join(doc.text for doc in documents if doc.text)
