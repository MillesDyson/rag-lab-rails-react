#!/usr/bin/env bash
set -e

if [ -f Gemfile ]; then
  bundle check || bundle install
fi

rm -f tmp/pids/server.pid

exec "$@"
