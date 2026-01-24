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

Use the example script to summarize total time by event name:

```bash
python3 examples/perf-timings.py build/timings.json
```

### CLI Examples

```bash
# Top 5 rows
python3 examples/perf-timings.py build/timings.json --top 5

# Only entries with total >= 50ms
python3 examples/perf-timings.py build/timings.json --min-ms 50

# Filter by substring
python3 examples/perf-timings.py build/timings.json --contains layout --top 3

# Sort by count instead of total time
python3 examples/perf-timings.py build/timings.json --sort count --top 3

# JSON output for tooling
python3 examples/perf-timings.py build/timings.json --json --top 2
```

## Example

Run the bundled perf test:

```bash
typst compile examples/perf-test.typ build/perf-test.pdf --root . --timings build/timings.json
python3 examples/perf-timings.py build/timings.json
```

## Practical Tips

- Re-run with the same inputs to compare timing deltas.
- Use `--font-path` if your project relies on non-system fonts.
- Large `query()` or `state()` usage can dominate timelines; optimize those first.
