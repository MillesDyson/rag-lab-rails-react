#!/usr/bin/env bash
set -e

# as gems vivem num volume nomeado, entao instalamos na subida e nao no build:
# adicionar uma gem ao Gemfile so exige reiniciar o container, nao rebuildar a imagem
if [ -f Gemfile ]; then
  bundle check || bundle install
fi

rm -f tmp/pids/server.pid

exec "$@"
