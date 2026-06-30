#!/usr/bin/env bash
# Install MedViet pre-commit hook at repository root
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_SRC="$ROOT/medviet-governance/.github/hooks/pre-commit"
HOOK_DST="$ROOT/.git/hooks/pre-commit"

cd "$ROOT"
git secrets --install -f >/dev/null 2>&1 || true
git secrets --register-aws >/dev/null 2>&1 || true
git secrets --add 'CCCD[:\s]+\d{12}' >/dev/null 2>&1 || true
git secrets --add 'cccd[:\s]+\d{12}' >/dev/null 2>&1 || true

cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"
echo "✓ Installed pre-commit hook → $HOOK_DST"
