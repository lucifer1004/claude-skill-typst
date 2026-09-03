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
| `silent-audit`        | find and fix multiple silent traps in one draft        | per-trap MathML checks, partial credit        |
| `legacy-modernize`    | port a 0.12 doc past 5 removed APIs                    | compiles + removed APIs gone + data intact    |
| `template-build`      | reusable conference template with running header       | compiles + structure + `N / M` footer in PDF  |

## Calibration results (2026-09-03, subagent guinea pigs, Typst 0.15.1)

Tier-1 tasks (`math-script-trap` … `weekly-report`) are smoke tests: a strong
model without the skill passes all five on the first or second attempt. They
validate the harness, not the skill.

`silent-audit` is the only task so far with demonstrated discriminative power
on pass/fail:

| Variant         | Score | Notes                                                      |
| --------------- | ----- | ---------------------------------------------------------- |
| draft unchanged | 0.25  | only the false-alarm check passes                          |
| base (no skill) | 0.75  | fraction trap "fixed" with `\(...\)` escapes — still wrong |
| with skill      | 1.00  | SKILL.md routed the agent to debug.md's trap list          |

`legacy-modernize` and `template-build` saturate on pass/fail for a strong
model (both variants pass) but still differ on efficiency: base needed 3
compile attempts vs 2 with skill on both tasks. For such tasks the useful
signal is Harbor's turn/time/token stats, not the binary reward.

New tasks should be calibrated the same way before being trusted: run a base
subagent first; if it passes easily, the task measures the harness, not the
skill.
