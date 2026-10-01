# RAG Lab

Projeto de estudo de **RAG** (Retrieval-Augmented Generation): você envia
arquivos de qualquer tipo, o sistema extrai o texto de dentro deles, transforma
em vetores e depois responde perguntas em linguagem natural sobre esse conteúdo,
citando de onde tirou cada afirmação.

## O que ele faz

**1. Ingestão.** Cada tipo de arquivo vira texto por um caminho diferente:

| arquivo | como vira texto |
|---------|-----------------|
| vídeo | ffmpeg extrai o áudio, Whisper transcreve |
| áudio | Whisper transcreve |
| imagem | um modelo de visão descreve a cena e transcreve o texto visível |
| CSV, DOCX, XLSX, PDF | LlamaParse converte em markdown |
| TXT, MD | leitura direta |

O texto é dividido em trechos de ~1000 caracteres, cada trecho vira um vetor de
1536 dimensões e é gravado no Pinecone.

**2. Consulta.** A pergunta também vira vetor, os trechos mais próximos são
recuperados e entregues a um LLM, que responde usando apenas esse material e
marca a origem de cada afirmação com `[1]`, `[2]`. A interface transforma essas
marcas em botões que destacam o trecho correspondente.

## Stack

- **Rails 8** (API-only) — upload, ActiveStorage, fila de jobs, Postgres
- **React + TypeScript** (Vite) — SPA com as abas de ingestão e consulta
- **Python + FastAPI + LangChain** — extração, chunking, embeddings e a cadeia de resposta
- **Pinecone** — banco vetorial, rodando local via Docker
- **OpenAI** — Whisper, embeddings e geração; **LlamaParse** para documentos

Os três serviços conversam por HTTP. Rails e Python rodam em containers; o front
roda no host.

```
[React :5173] ──> [Rails API :3000] ──> [FastAPI :8000] ──> [Pinecone :5080]
                         │                                        │
                    Postgres                              OpenAI / LlamaParse
```

## Como rodar

Veja [docs/setup.md](docs/setup.md). O resumo: Docker instalado, chaves da OpenAI
e da LlamaParse no `.env`, `docker compose up` e `npm run dev` no front.

## Estado

As duas etapas funcionam e foram validadas com arquivos de exemplo em
[`samples/`](samples/), que acompanham um gabarito com os valores esperados.

Limitação conhecida: o modelo recupera e lista os valores corretamente, mas erra
somas. A correção seria dar uma ferramenta de cálculo a ele em vez de deixar a
aritmética para a geração de texto.

---

Projeto de aprendizado, sem pretensão de produção.
