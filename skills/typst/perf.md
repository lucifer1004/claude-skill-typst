# Typst Performance Profiling

Use Typst's built-in timing trace to find slow stages and hotspots.

## Generate Timing Trace

```bash
# Emit Chrome trace-style JSON
typst compile document.typ output.pdf --root . --timings build/timings.json 2>&1
```

Notes:

- `--timings` writes trace events in Chrome trace format.
- `--root` should match your project root for correct imports.

## View the Trace

Open in any trace viewer:

- Chrome: `chrome://tracing`
- Perfetto: https://ui.perfetto.dev/

Load `build/timings.json` to explore event timelines.

## Aggregate Hotspots (Top N)

Use the bundled script to summarize total time by event name:

```bash
python3 scripts/perf-timings.py build/timings.json
```

Output includes a summary header (event count, threads, wall time) followed by a table with count, total, avg, and max per event.

### CLI Examples

```bash
# Top 5 rows
python3 scripts/perf-timings.py build/timings.json --top 5

# Self time (excluding children) — reveals true hotspots vs containers
python3 scripts/perf-timings.py build/timings.json --self-time

# Show source file:line locations from trace args
python3 scripts/perf-timings.py build/timings.json --source --top 5

# Per-thread breakdown — check if work is balanced across threads
python3 scripts/perf-timings.py build/timings.json --by-thread --contains layout

# Only entries with total >= 50ms
python3 scripts/perf-timings.py build/timings.json --min-ms 50

# Filter by substring
python3 scripts/perf-timings.py build/timings.json --contains layout --top 3

# Sort by count instead of total time
python3 scripts/perf-timings.py build/timings.json --sort count --top 3

# JSON output for tooling (includes all fields: total, self, avg, max, sources)
python3 scripts/perf-timings.py build/timings.json --json --top 2
```

### Interpreting Self Time

Total time includes children. Self time subtracts direct child durations.

| Event      | Total | Self | Interpretation                           |
| ---------- | ----- | ---- | ---------------------------------------- |
| `page run` | 340ms | 9ms  | Container — time is in children          |
| `block`    | 317ms | 88ms | Mix — significant own work plus children |
| `prepare`  | 85ms  | 82ms | Leaf-like — most time is its own work    |

Use `--self-time` to sort by self time and find the actual bottlenecks.

## Example

Run the bundled perf test:

```bash
typst compile examples/perf-test.typ build/perf-test.pdf --root . --timings build/timings.json
python3 scripts/perf-timings.py build/timings.json
```

## Practical Tips

- Use `--self-time` first to find real bottlenecks, not just wrapper events.
- Use `--source` to map hotspots back to specific lines in your `.typ` files.
- Use `--by-thread` to check if one thread is bottlenecked while others are idle.
- Re-run with the same inputs to compare timing deltas.
- Use `--font-path` if your project relies on non-system fonts.
- Large `query()` or `state()` usage can dominate timelines; optimize those first.
