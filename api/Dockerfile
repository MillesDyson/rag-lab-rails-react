FROM ruby:3.3-slim

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
       build-essential libpq-dev libyaml-dev git curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID app && useradd -u $UID -g $GID -m app

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
