FROM ruby:3.3-slim

# build-essential/libpq-dev compilam as gems nativas (pg, entre outras);
# ficam na imagem porque em desenvolvimento a gente adiciona gem o tempo todo.
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
       build-essential libpq-dev libyaml-dev git curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# mesmo uid/gid do host, senao os arquivos gerados dentro do container
# (migrations, scaffolds) aparecem como root no bind mount
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID app && useradd -u $UID -g $GID -m app

# gems e bundle no mesmo volume nomeado: sobrevivem a rebuild da imagem,
# e ficam graváveis pelo usuario app (o /usr/local/bundle padrao e do root)
ENV BUNDLE_PATH=/bundle \
    BUNDLE_APP_CONFIG=/bundle \
    GEM_HOME=/bundle \
    PATH=/bundle/bin:$PATH \
    LANG=C.UTF-8
RUN mkdir -p /bundle && chown app:app /bundle

USER app
WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 3000
CMD ["bin/rails", "server", "-b", "0.0.0.0"]
