#!/usr/bin/env bash
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"
git config core.hooksPath .githooks
git config user.name "Gielinor Wayfinder"
git config user.email "gielinor-wayfinder@localhost"
printf '%s\n' 'Git hooks enabled: .githooks' 'Local Git identity set for repository checkpoints.'
