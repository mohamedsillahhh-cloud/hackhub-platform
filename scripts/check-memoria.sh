#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORIA_DIR="$ROOT_DIR/MEMORIA"
INDEX_FILE="$MEMORIA_DIR/INDEX.md"
MAX_LINES=600

if [[ ! -f "$INDEX_FILE" ]]; then
  echo "Erro: MEMORIA/INDEX.md não existe." >&2
  exit 1
fi

status=0

while IFS= read -r -d '' file; do
  lines="$(wc -l < "$file")"
  if (( lines > MAX_LINES )); then
    rel="${file#$ROOT_DIR/}"
    echo "Erro: $rel tem $lines linhas; máximo permitido: $MAX_LINES." >&2
    status=1
  fi
done < <(find "$MEMORIA_DIR" -type f -name '*.md' -print0)

exit "$status"
