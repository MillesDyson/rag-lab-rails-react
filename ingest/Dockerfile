FROM python:3.12-slim

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID app && useradd -u $UID -g $GID -m app

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"
RUN mkdir -p /opt/venv && chown app:app /opt/venv

USER app
WORKDIR /app

COPY --chown=app:app pyproject.toml uv.lock ./
RUN uv sync --frozen

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
