#!/usr/bin/env bash

set -euo pipefail

PROGRAMMING_KB_DIR="${PROGRAMMING_KB_DIR:-}"
COMMAND="${1:-help}"

usage() {
  cat <<'USAGE'
Usage:
  kb-query.sh tags
  kb-query.sh tag <tag>
  kb-query.sh search <terms>
  kb-query.sh stale [YYYY-MM-DD]

Environment:
  PROGRAMMING_KB_DIR  Required path to the user's local programming KB
USAGE
}

require_kb() {
  if [ -z "$PROGRAMMING_KB_DIR" ]; then
    echo "PROGRAMMING_KB_DIR is not set." >&2
    exit 2
  fi
  if [ ! -d "$PROGRAMMING_KB_DIR" ]; then
    echo "PROGRAMMING_KB_DIR not found: $PROGRAMMING_KB_DIR" >&2
    exit 2
  fi
}

frontmatter_summary() {
  awk '
    FNR == 1 { title = ""; type = ""; status = ""; updated = "" }
    /^title:[[:space:]]*/ { title = $0; sub(/^title:[[:space:]]*/, "", title) }
    /^type:[[:space:]]*/ { type = $0; sub(/^type:[[:space:]]*/, "", type) }
    /^status:[[:space:]]*/ { status = $0; sub(/^status:[[:space:]]*/, "", status) }
    /^updated:[[:space:]]*/ { updated = $0; sub(/^updated:[[:space:]]*/, "", updated) }
    /^---[[:space:]]*$/ && FNR > 1 {
      printf "%s | title=%s | type=%s | status=%s | updated=%s\n", FILENAME, title, type, status, updated
      nextfile
    }
  ' "$@"
}

tags() {
  require_kb
  find "$PROGRAMMING_KB_DIR" \
    -path "$PROGRAMMING_KB_DIR/raw" -prune -o \
    -name '*.md' -type f -exec awk '
    /^tags:[[:space:]]*$/ { in_tags = 1; next }
    in_tags && /^[[:space:]]*-[[:space:]]+/ {
      tag = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", tag)
      gsub(/["'"'"']/, "", tag)
      print tag
      next
    }
    in_tags && /^[^[:space:]-]/ { in_tags = 0 }
  ' {} + 2>/dev/null | sort -u
}

tag_search() {
  require_kb
  local tag="${1:-}"
  if [ -z "$tag" ]; then
    echo "Missing tag." >&2
    usage >&2
    exit 2
  fi

  if [[ ! "$tag" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "Invalid tag shape: $tag" >&2
    exit 2
  fi

  mapfile -t files < <(
    rg -l --glob '*.md' --glob '!**/raw/**' \
      "^[[:space:]]*-[[:space:]]*${tag}[[:space:]]*$" \
      "$PROGRAMMING_KB_DIR"
  )

  if [ "${#files[@]}" -eq 0 ]; then
    echo "No notes found for tag: $tag"
    exit 0
  fi

  frontmatter_summary "${files[@]}"
}

text_search() {
  require_kb
  shift || true
  local terms="$*"
  if [ -z "$terms" ]; then
    echo "Missing search terms." >&2
    usage >&2
    exit 2
  fi

  rg -n -i --glob '*.md' --glob '!**/raw/**' "$terms" "$PROGRAMMING_KB_DIR"
}

stale() {
  require_kb
  local cutoff="${1:-2025-01-01}"
  find "$PROGRAMMING_KB_DIR" \
    -path "$PROGRAMMING_KB_DIR/raw" -prune -o \
    -name '*.md' -type f -exec awk -v cutoff="$cutoff" '
    FNR == 1 { file = FILENAME; title = ""; status = ""; updated = "" }
    /^title:[[:space:]]*/ { title = $0; sub(/^title:[[:space:]]*/, "", title) }
    /^status:[[:space:]]*/ { status = $0; sub(/^status:[[:space:]]*/, "", status) }
    /^updated:[[:space:]]*/ { updated = $0; sub(/^updated:[[:space:]]*/, "", updated) }
    /^---[[:space:]]*$/ && FNR > 1 {
      if (status ~ /(needs-review|deprecated)/ || (updated != "" && updated < cutoff)) {
        printf "%s | title=%s | status=%s | updated=%s\n", file, title, status, updated
      }
      nextfile
    }
  ' {} + 2>/dev/null
}

case "$COMMAND" in
  tags)
    tags
    ;;
  tag)
    shift
    tag_search "${1:-}"
    ;;
  search)
    text_search "$@"
    ;;
  stale)
    shift || true
    stale "${1:-2025-01-01}"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    usage >&2
    exit 2
    ;;
esac
