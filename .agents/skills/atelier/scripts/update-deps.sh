#!/bin/bash
# Atelier — dependency updater (auto-update stream 1).
# Fetches each dependency in dependencies.lock.json, classifies the delta by
# trust tier, applies what policy allows, and writes a report.
#
#   official  -> fast-forward to remote HEAD, bump ref in the lock
#   community -> fast-forward ONLY if the delta touches no executable
#                instructions (SKILL.md, commands/, scripts, hooks, *.sh);
#                otherwise hold and report for review
#
# Usage: update-deps.sh [--dry-run]
# Report: ~/.claude/atelier-deps/update-report-<date>.md (also printed)
set -euo pipefail

LOCK="$(cd "$(dirname "$0")/.." && pwd)/dependencies.lock.json"
ROOT="$HOME/.claude/atelier-deps"
DRY="${1:-}"
DATE_TAG="$(date +%Y-%m-%d)"
REPORT="$ROOT/update-report-$DATE_TAG.md"
INSTRUCTION_PATTERN='(^|/)(SKILL\.md|AGENTS\.md|CLAUDE\.md|command.*\.md|commands/|hooks/|scripts/|.*\.sh$|.*\.js$|.*\.ts$)'

command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }
mkdir -p "$ROOT"
echo "# Atelier deps update — $DATE_TAG" > "$REPORT"

count=$(jq '.dependencies | length' "$LOCK")
for i in $(seq 0 $((count - 1))); do
  name=$(jq -r ".dependencies[$i].name" "$LOCK")
  repo=$(jq -r ".dependencies[$i].repo" "$LOCK")
  ref=$(jq -r ".dependencies[$i].ref" "$LOCK")
  tier=$(jq -r ".dependencies[$i].trustTier" "$LOCK")
  dir="$ROOT/$name"

  if [ ! -d "$dir/.git" ]; then
    git clone -q --depth 1 "$repo" "$dir"
    echo "- $name: fresh clone at $(git -C "$dir" rev-parse --short HEAD)" >> "$REPORT"
    continue
  fi

  git -C "$dir" fetch -q --depth 1 origin HEAD
  remote=$(git -C "$dir" rev-parse FETCH_HEAD)
  if [ "$remote" = "$ref" ]; then
    echo "- $name: up to date ($tier)" >> "$REPORT"
    continue
  fi

  changed=$(git -C "$dir" diff --name-only "$ref" "$remote" 2>/dev/null || echo "UNKNOWN")
  instr=$(echo "$changed" | grep -E "$INSTRUCTION_PATTERN" || true)

  if [ "$tier" = "official" ] || [ -z "$instr" ]; then
    action="bump"
    [ "$DRY" = "--dry-run" ] || {
      git -C "$dir" reset -q --hard "$remote"
      tmp=$(mktemp); jq ".dependencies[$i].ref = \"$remote\" | .updatedAt = \"$DATE_TAG\"" "$LOCK" > "$tmp" && mv "$tmp" "$LOCK"
    }
    echo "- $name: $action ${ref:0:8} -> ${remote:0:8} ($tier; $(echo "$changed" | wc -l | tr -d ' ') files)" >> "$REPORT"
  else
    echo "- $name: HELD at ${ref:0:8} — remote ${remote:0:8} changes executable instructions ($tier):" >> "$REPORT"
    echo "$instr" | sed 's/^/    - /' >> "$REPORT"
  fi
done

echo >> "$REPORT"
echo "Held bumps: review the diff, then update the ref in dependencies.lock.json manually or rerun after approval." >> "$REPORT"
cat "$REPORT"
