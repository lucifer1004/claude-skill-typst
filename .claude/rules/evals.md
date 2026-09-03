# Skill evaluation (evals/)

`evals/` holds Harbor-based eval tasks that measure whether the bundled
skills improve agent behavior. Each task: `instruction.md` (prompt),
`environment/` (Dockerfile + fixtures), `solution/solve.sh` (oracle),
`tests/test.sh` (deterministic verifier).

- Run: `evals/run.sh` (all tasks, base + skill variants) or
  `evals/run.sh <task-name>`. Credentials via `evals/.env` (see
  `.env.example`).
- Oracle sanity check: `uvx harbor run -p evals/tasks/<name> -a oracle`.
- `base` and `skill` variants differ only in whether `skills/typst` is
  copied into `/app/.claude/skills/typst` before the run.
