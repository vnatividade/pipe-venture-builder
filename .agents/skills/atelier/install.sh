#!/bin/bash
# Atelier — idempotent bootstrap for this machine.
# 1. Symlinks the shared skill into ~/.claude/skills/atelier
# 2. Symlinks the Claude Code subagent into ~/.claude/agents/atelier.md
# 3. Clones/updates external dependencies at the refs pinned in dependencies.lock.json
# Rerun any time; it converges to the declared state.
set -euo pipefail

MODULE="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
DEPS_ROOT="$CLAUDE_DIR/atelier-deps"
LOCK="$MODULE/dependencies.lock.json"

command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }
mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents" "$DEPS_ROOT"
mkdir -p "$MODULE/knowledge/inbox" "$MODULE/knowledge/learnings" "$MODULE/knowledge/patterns"

link() { # link <target> <linkpath>
  [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ] && return 0
  [ -e "$2" ] && [ ! -L "$2" ] && { echo "SKIP: $2 exists and is not a symlink" >&2; return 0; }
  ln -sfn "$1" "$2" && echo "linked: $2 -> $1"
}

link "$MODULE" "$CLAUDE_DIR/skills/atelier"
link "$MODULE/adapters/claude-code-agent.md" "$CLAUDE_DIR/agents/atelier.md"

count=$(jq '.dependencies | length' "$LOCK")
for i in $(seq 0 $((count - 1))); do
  name=$(jq -r ".dependencies[$i].name" "$LOCK")
  repo=$(jq -r ".dependencies[$i].repo" "$LOCK")
  ref=$(jq -r ".dependencies[$i].ref" "$LOCK")
  dir="$DEPS_ROOT/$name"
  if [ ! -d "$dir/.git" ]; then
    git clone -q --depth 1 "$repo" "$dir"
  fi
  current=$(git -C "$dir" rev-parse HEAD)
  if [ "$current" != "$ref" ]; then
    git -C "$dir" fetch -q --depth 1 origin "$ref" 2>/dev/null || git -C "$dir" fetch -q origin
    git -C "$dir" reset -q --hard "$ref" 2>/dev/null || echo "WARN: $name could not pin $ref (stays at $current)" >&2
  fi
  echo "dep: $name @ $(git -C "$dir" rev-parse --short HEAD)"
done

echo "Atelier installed. Invoke via the 'atelier' subagent or read ~/.claude/skills/atelier/SKILL.md"
