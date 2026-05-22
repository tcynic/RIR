#!/usr/bin/env bash
# Create a new Release Delta from templates/minimal.md.
# Usage:
#   scripts/new-delta.sh checkout-redesign
#   scripts/new-delta.sh checkout-redesign "Checkout redesign"
#   scripts/new-delta.sh

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/new-delta.sh [slug] [title]

Creates docs/release-deltas/RD-NNNN-slug.md from templates/minimal.md.

Examples:
  scripts/new-delta.sh checkout-redesign
  scripts/new-delta.sh checkout-redesign "Checkout redesign"
  scripts/new-delta.sh
USAGE
}

fail() {
  printf 'new-delta: %s\n' "$1" >&2
  exit 1
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$repo_root" ]]; then
  fail "must be run inside the repository"
fi
cd "$repo_root"

[[ -f "templates/minimal.md" ]] || fail "templates/minimal.md not found; run from an RDR repository"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

slug="${1:-}"
if [[ -z "$slug" ]]; then
  read -r -p "Slug (lowercase dashed, e.g. checkout-redesign): " slug
fi

[[ -n "$slug" ]] || fail "slug is required"
if [[ ! "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  fail "slug must be lowercase letters/numbers separated by single dashes"
fi

if [[ $# -gt 2 ]]; then
  fail "too many arguments; pass the title as one quoted argument"
fi

title="${2:-}"
if [[ -z "$title" ]]; then
  default_title="$(printf '%s' "$slug" | tr '-' ' ' | awk '{ for (i = 1; i <= NF; i++) { $i = toupper(substr($i,1,1)) substr($i,2) } print }')"
  read -r -p "Title [$default_title]: " title
  title="${title:-$default_title}"
fi

[[ -n "$title" ]] || fail "title is required"

max=0
while IFS= read -r file; do
  name="$(basename "$file")"
  if [[ "$name" =~ ^RD-([0-9]{4})- ]]; then
    number="${BASH_REMATCH[1]}"
    # Force base-10 so numbers with leading zeroes are safe.
    value=$((10#$number))
    if (( value > max )); then
      max=$value
    fi
  fi
done < <(find docs/release-deltas examples -maxdepth 1 -type f -name 'RD-[0-9][0-9][0-9][0-9]-*.md' 2>/dev/null | sort)

next=$((max + 1))
printf -v id 'RD-%04d' "$next"

target_dir="docs/release-deltas"
target="$target_dir/$id-$slug.md"

mkdir -p "$target_dir"
[[ ! -e "$target" ]] || fail "$target already exists"

cp "templates/minimal.md" "$target"

python3 - "$target" "$id" "$title" "$(date +%F)" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
id_ = sys.argv[2]
title = sys.argv[3]
today = sys.argv[4]

text = path.read_text(encoding="utf-8")
text = text.replace("RD-NNNN", id_)
text = text.replace("declared: YYYY-MM-DD", f"declared: {today}")
text = text.replace("{short title naming the release}", title)
text = text.replace("{Short title naming the release}", title)
path.write_text(text, encoding="utf-8")
PY

printf 'Created %s\n' "$target"

if [[ -n "${EDITOR:-}" ]]; then
  "$EDITOR" "$target"
elif command -v open >/dev/null 2>&1; then
  open "$target"
else
  printf 'Set EDITOR or open the file manually: %s\n' "$target"
fi
