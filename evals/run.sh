#!/usr/bin/env bash
# Run the Typst skill evaluation suite with Harbor.
#
# Usage:
#   evals/run.sh                      # all tasks, base + with-skill variants
#   evals/run.sh math-script-trap     # one task only
#   AGENT=claude-code MODEL=anthropic/claude-opus-4-1 evals/run.sh
#
# LLM credentials come from evals/.env (see .env.example) or the environment.
set -euo pipefail
cd "$(dirname "$0")"

AGENT="${AGENT:-claude-code}"
MODEL="${MODEL:-anthropic/claude-sonnet-4-5}"

ENV_ARGS=()
[[ -f .env ]] && ENV_ARGS=(--env-file .env)

# Harbor drives a `docker` CLI; shim to podman when docker is absent.
if ! command -v docker >/dev/null 2>&1 && command -v podman >/dev/null 2>&1; then
  mkdir -p bin
  ln -sf "$(command -v podman)" bin/docker
  export PATH="$PWD/bin:$PATH"
  export DOCKER_HOST="unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')"
fi

tasks=("$@")
[[ ${#tasks[@]} -eq 0 ]] && tasks=(tasks/*/)

printf '%-22s %-6s %s\n' TASK VARIANT REWARD
for variant in base skill; do
  for task in "${tasks[@]}"; do
    name="$(basename "$task")"
    if [[ $variant == skill ]]; then
      cp -r ../skills/typst "$task/environment/skill"
    fi
    out=$(uvx harbor run -p "$task" -a "$AGENT" -m "$MODEL" -y -q \
      --job-name "$name-$variant" "${ENV_ARGS[@]}" 2>&1) || true
    if [[ $variant == skill ]]; then
      rm -rf "$task/environment/skill"
    fi
    job_dir=$(printf '%s\n' "$out" | grep -oE 'jobs/[^ ]+' | head -1)
    reward=$(python3 -c "
import json, sys
try:
    d = json.load(open('$job_dir/result.json'))
    for v in d.get('stats', {}).get('evals', {}).values():
        print(v['metrics'][0]['mean'])
        break
except Exception:
    print('n/a')
")
    printf '%-22s %-6s %s\n' "$name" "$variant" "$reward"
  done
done
