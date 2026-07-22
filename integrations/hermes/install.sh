#!/bin/sh
set -eu

pipe_script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
pipe_source_skill="$pipe_script_dir/skill/SKILL.md"
pipe_action=plan
pipe_hermes_home=${PIPE_HERMES_HOME:-}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --plan)
      pipe_action=plan
      ;;
    --apply)
      pipe_action=apply
      ;;
    --hermes-home)
      shift
      if [ "$#" -eq 0 ]; then
        printf '%s\n' 'missing value for --hermes-home' >&2
        exit 2
      fi
      pipe_hermes_home=$1
      ;;
    *)
      printf '%s\n' 'unsupported installer argument' >&2
      exit 2
      ;;
  esac
  shift
done

if [ -z "$pipe_hermes_home" ]; then
  printf '%s\n' 'set PIPE_HERMES_HOME or pass --hermes-home' >&2
  exit 8
fi

case "$pipe_hermes_home" in
  /|.|..)
    printf '%s\n' 'unsafe Hermes home target' >&2
    exit 8
    ;;
esac

pipe_destination="$pipe_hermes_home/skills/autonomous-ai-agents/pipe-product-delivery"

if [ "$pipe_action" = plan ]; then
  printf '%s\n' "plan: copy skill to $pipe_destination"
  printf '%s\n' 'no files were written'
  exit 0
fi

if [ -L "$pipe_hermes_home" ] || [ -L "$pipe_destination" ]; then
  printf '%s\n' 'symlinked Hermes install target is not allowed' >&2
  exit 8
fi
if [ -e "$pipe_destination" ]; then
  printf '%s\n' 'Hermes skill already exists; no files were overwritten' >&2
  exit 8
fi

mkdir -p "$pipe_destination"
cp "$pipe_source_skill" "$pipe_destination/SKILL.md"
chmod 0644 "$pipe_destination/SKILL.md"
printf '%s\n' "installed: $pipe_destination/SKILL.md"
printf '%s\n' 'restart or open a new Hermes session before loading the skill'
