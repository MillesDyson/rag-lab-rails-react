# Setup e arquitetura

Detalhe operacional do RAG Lab. Para a visão geral, veja o [README](../README.md).

## Arquitetura

```
[React SPA :5173] ──fetch──> [Rails API :3000] ──HTTP──> [FastAPI :8000]
                                   │                          │
                              Postgres                   LangChain
                         (documentos + status)    Whisper │ Vision │ LlamaParse
                                   ▲                          │
                                   └──── callback ────────────┤
                                                              ▼
                                                    [Pinecone Local :5080]
```

### Fluxo de ingestão

1. O React envia o arquivo para `POST /api/v1/documents` (multipart).
2. O Rails guarda o arquivo no ActiveStorage, cria o `Document` com status `pending`
   e enfileira um job.
3. O job chama `POST /ingest` no serviço Python com a URL assinada do arquivo.
4. O Python baixa o arquivo e roteia pelo content type:

   | tipo        | caminho                                                    |
   |-------------|------------------------------------------------------------|
   | `video/*`   | ffmpeg extrai o áudio → Whisper (`whisper-1`)               |
   | `audio/*`   | Whisper direto (corta em blocos de 10min se passar de 24MB) |
   | `image/*`   | `gpt-4o-mini` com visão descreve e transcreve o que aparece |
   | csv/docx/xlsx/pdf | LlamaParse → markdown                                 |
   | txt/md      | leitura direta                                              |

5. O texto passa pelo `RecursiveCharacterTextSplitter` (1000 chars, 150 de overlap).
6. Cada chunk vira um vetor com `text-embedding-3-small` (1536 dims) e é gravado no
   Pinecone com metadata `document_id`, `filename`, `kind`, `chunk_index`.
7. O Python chama de volta `POST /api/v1/documents/:id/ingested` e o Rails atualiza o status.
8. O front faz polling a cada 2s enquanto houver documento em andamento.

## Pré-requisitos

Único passo que precisa de sudo:

```bash
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER   # depois: deslogar/relogar ou `newgrp docker`
```

Ruby, Rails, Python, ffmpeg, libpq — tudo isso vive dentro dos containers.
No host ficam apenas o Docker e o Node (já instalado via `mise`), usado pelo front.

## Setup

```bash
cp .env.example .env         # preencha OPENAI_API_KEY e LLAMA_CLOUD_API_KEY
docker compose build
docker compose up -d         # postgres, pinecone, api, ingest
docker compose exec api bin/rails db:prepare

cd frontend && npm install
```

### Gerando o app Rails (uma vez só)

A imagem `api` não embute o código — ele vem por volume. Então o próprio
container serve para criar o app, sem precisar de Ruby no host:

```bash
docker compose build api
docker compose run --rm --no-deps api bash -c \
  "gem install rails -v 8.1.4 --no-document && \
   rails new . --name=raglab_api --api --database=postgresql \
     --skip-bundle --skip-test --skip-docker --skip-kamal --skip-ci \
     --skip-solid --skip-action-cable --skip-action-mailer \
     --skip-action-mailbox --skip-action-text --skip-jbuilder"
```

`--skip-action-cable` tira o `websocket-driver` da jogada (é a gem que não
compilava no host). `--skip-docker` evita que o Rails gere um Dockerfile
próprio por cima do nosso. Os jobs usam o adapter `:async`, suficiente aqui
porque o job só dispara um POST para o serviço de ingestão e volta.

## Rodando

```bash
docker compose up            # api :3000, ingest :8000, postgres, pinecone
cd frontend && npm run dev   # http://localhost:5173
```

Comandos do Rails rodam dentro do container:

```bash
docker compose exec api bin/rails console
docker compose exec api bin/rails generate model Foo
docker compose exec api bundle add alguma_gem   # depois: docker compose restart api
```

Ao mudar o `.env`, `restart` **não** basta — ele reinicia o processo dentro do
container existente, que mantém o environment de quando foi criado:

```bash
docker compose up -d --force-recreate ingest
```

As gems ficam num volume nomeado (`bundle`), então adicionar uma gem só exige
reiniciar o container — não rebuildar a imagem.

## Chaves de API

| variável | onde pegar | usado para |
|----------|-----------|------------|
| `OPENAI_API_KEY` | platform.openai.com | Whisper, embeddings, visão |
| `LLAMA_CLOUD_API_KEY` | cloud.llamaindex.ai | LlamaParse (csv/docx/pdf/xlsx) |
| `PINECONE_API_KEY` | não precisa — `pclocal` | o emulador aceita qualquer valor |

## Observações sobre o Pinecone Local

- É um emulador; **não persiste** nada entre restarts do container.
- Cada índice criado abre uma porta própria (5081, 5082...), por isso o
  `docker-compose.yml` publica a faixa `5080-5090`.
- O índice `raglab` é criado sozinho na primeira ingestão.
- O serviço tem o alias de rede `pinecone.local`. O nome curto `pinecone` não
  serve: o cliente recusa host sem ponto (`check_realistic_host`), por assumir
  que você passou o nome do índice no lugar do host.

## Estrutura

```
docker-compose.yml   postgres, pinecone, api, ingest
api/                 Rails 8 API-only (container)
ingest/               FastAPI + LangChain (container)
  app/
  main.py            endpoints FastAPI
  pipeline.py        orquestra extract → split → embed → store
  vectorstore.py     conexão Pinecone + embeddings
  extractors/        um módulo por tipo de mídia
frontend/            Vite + React (roda no host)
  src/
  api/client.ts      wrapper de fetch
  hooks/             useDocuments (polling)
  components/        UploadDropzone, DocumentList, DocumentRow, StatusBadge
```

## Consulta

Aba "Consulta" no front. O fluxo:

```
pergunta -> POST /api/v1/search -> POST /query no serviço Python
  -> similarity_search no Pinecone (k=5, filtro opcional por tipo)
  -> cadeia LCEL: prompt | gpt-4o-mini | StrOutputParser
  -> resposta com citações [1], [2] + trechos usados
```

O Rails enriquece as fontes com os dados do Postgres, então o nome do arquivo
vem do banco e um documento apagado aparece marcado como removido.

### Limitação conhecida: aritmética

O modelo recupera e **lista** os valores corretamente, mas erra as somas.
Exemplo real, com os dados do `samples/`:

```
parcelas citadas: 4.930,20 + 1.207,00 + 1.829,00   (todas corretas)
total informado:  6.966,20
total correto:    7.966,20
```

O prompt pede que as parcelas sejam listadas justamente para que o erro fique
auditável. A correção de verdade é dar uma ferramenta de cálculo ao modelo
(tool calling) em vez de deixar a soma para a geração de texto.

## Próxima etapa

- Ferramenta de cálculo para as agregações numéricas
- Resposta em streaming (hoje o front espera a resposta inteira)
- Histórico de consultas
