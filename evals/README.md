# Skill Evaluation (Harbor)

Local, on-demand evaluation of the bundled Typst skill using
[Harbor](https://github.com/laude-institute/harbor). Not part of CI and not
bundled into the skill.

Each task under `tasks/` is a self-contained Harbor task: an agent gets
`instruction.md` inside a container with a pinned Typst release, and
`tests/test.sh` verifies the result deterministically (compile checks,
`typst eval` structure assertions, MathML inspection for silent render traps).
`solution/solve.sh` is the oracle used to sanity-check the task itself.

## Setup

1. A container runtime: Docker, or podman (a running `podman machine`; the
   runner shims `docker` → `podman` automatically).
2. `uv` (for `uvx harbor`).
3. `cp .env.example .env` and fill in your LLM API key.

## Usage

```bash
evals/run.sh                    # all tasks, base and with-skill variants
evals/run.sh math-script-trap   # a single task
```

Each task runs twice: `base` (plain container) and `skill` (the bundled
`skills/typst` copied into `/app/.claude/skills/typst`). Comparing the two
variants shows whether the skill changes agent behavior.

Sanity-check a task without an LLM (runs the oracle solution + verifier):

```bash
uvx harbor run -p evals/tasks/math-script-trap -a oracle
```

## Tasks

| Task                  | Trap / change exercised                                | Verifier signal                               |
| --------------------- | ------------------------------------------------------ | --------------------------------------------- |
| `math-script-trap`    | `alpha_c(N)` folds the call into the subscript         | MathML `<msub>` must not contain `(`          |
| `math-fraction-trap`  | `cal(Z)(tilde(S)) / cal(Z)(0)` binds `/` to one atom   | `<mfrac>` must contain `0` in the denominator |
| `api-curve-migration` | `path` element removed in 0.15, use `curve`            | compiles + drawing element in source          |
| `data-json-table`     | `json.decode` removed in 0.15                          | compiles + table + all rows rendered          |
| `weekly-report`       | general authoring (headings, table, numbered equation) | `typst eval` structure assertions             |
