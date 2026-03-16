#!/usr/bin/env python3
"""Summarize Typst --timings trace by event name.

Parses Chrome trace-format JSON emitted by `typst compile --timings` and
aggregates duration-pair (B/E) events into a sorted hotspot table.

Usage:
    python3 scripts/perf-timings.py build/timings.json
    python3 scripts/perf-timings.py build/timings.json --top 5
    python3 scripts/perf-timings.py build/timings.json --min-ms 50
    python3 scripts/perf-timings.py build/timings.json --contains layout --top 3
    python3 scripts/perf-timings.py build/timings.json --sort count --top 3
    python3 scripts/perf-timings.py build/timings.json --self-time
    python3 scripts/perf-timings.py build/timings.json --by-thread --top 5
    python3 scripts/perf-timings.py build/timings.json --source
    python3 scripts/perf-timings.py build/timings.json --json --top 2
"""

import argparse
import json
import sys
from collections import defaultdict


def parse_events(events):
    """Match B/E pairs into structured records with nesting info.

    Returns list of dicts: {name, tid, start, dur, depth, source}.
    Events are sorted by start time per thread.
    """
    begins = {}  # (name, tid) -> [(ts, depth, args)]
    depth = defaultdict(int)  # tid -> current depth
    records = []

    for event in events:
        name = event.get("name", "")
        ph = event.get("ph", "")
        ts = event.get("ts", 0)
        tid = event.get("tid", 0)
        key = (name, tid)

        if ph == "B":
            d = depth[tid]
            depth[tid] += 1
            begins.setdefault(key, []).append((ts, d, event.get("args")))
        elif ph == "E" and begins.get(key):
            start_ts, d, args = begins[key].pop()
            depth[tid] -= 1
            source = None
            if args and isinstance(args, dict):
                f = args.get("file")
                ln = args.get("line")
                if f and ln:
                    source = f"{f}:{ln}"
            records.append(
                {
                    "name": name,
                    "tid": tid,
                    "start": start_ts,
                    "dur": ts - start_ts,
                    "depth": d,
                    "source": source,
                }
            )

    return records


def compute_self_time(records):
    """Compute self time by subtracting direct children's duration.

    For each event, subtract durations of events that are one depth level
    deeper and nested within its time range on the same thread.
    """
    # Group by thread, sort by start time
    by_thread = defaultdict(list)
    for r in records:
        by_thread[r["tid"]].append(r)

    self_times = {}  # id(record) -> self_us
    for tid, thread_records in by_thread.items():
        thread_records.sort(key=lambda r: r["start"])
        # Stack of active parents: [(record, child_sum)]
        stack = []
        for r in thread_records:
            # Pop finished parents
            while stack and r["start"] >= stack[-1][0]["start"] + stack[-1][0]["dur"]:
                parent, child_sum = stack.pop()
                self_times[id(parent)] = parent["dur"] - child_sum
            # Add our duration to parent's child_sum
            if stack:
                stack[-1] = (stack[-1][0], stack[-1][1] + r["dur"])
            stack.append((r, 0))
        # Flush remaining
        while stack:
            parent, child_sum = stack.pop()
            self_times[id(parent)] = parent["dur"] - child_sum

    return self_times


def aggregate(records, self_times=None):
    """Aggregate records by name. Returns {name: {count, total, self, avg, max, sources}}."""
    agg = defaultdict(
        lambda: {"count": 0, "total": 0, "self": 0, "max": 0, "sources": set()}
    )
    for r in records:
        name = r["name"]
        dur = r["dur"]
        a = agg[name]
        a["count"] += 1
        a["total"] += dur
        if self_times:
            a["self"] += self_times.get(id(r), dur)
        else:
            a["self"] += dur
        if dur > a["max"]:
            a["max"] = dur
        if r["source"]:
            a["sources"].add(r["source"])
    return agg


def aggregate_by_thread(records, self_times=None):
    """Aggregate records by (name, tid). Returns {(name, tid): stats}."""
    agg = defaultdict(
        lambda: {"count": 0, "total": 0, "self": 0, "max": 0, "sources": set()}
    )
    for r in records:
        key = (r["name"], r["tid"])
        dur = r["dur"]
        a = agg[key]
        a["count"] += 1
        a["total"] += dur
        if self_times:
            a["self"] += self_times.get(id(r), dur)
        else:
            a["self"] += dur
        if dur > a["max"]:
            a["max"] = dur
        if r["source"]:
            a["sources"].add(r["source"])
    return agg


def sort_key(sort_by, use_self=False):
    field = "self" if use_self else "total"
    if sort_by == "count":
        return lambda item: item[1]["count"]
    if sort_by == "name":
        return lambda item: (
            item[0] if isinstance(item[0], str) else item[0][0]
        ).lower()
    return lambda item: item[1][field]


def us_to_ms(us):
    return round(us / 1000, 2)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize Typst --timings trace by event name.",
    )
    parser.add_argument("timings", help="Path to timings JSON file")
    parser.add_argument(
        "-n",
        "--top",
        type=int,
        default=10,
        help="Number of rows to show (default: 10)",
    )
    parser.add_argument(
        "--min-ms",
        type=float,
        default=0.0,
        help="Filter out entries with total < min-ms (default: 0)",
    )
    parser.add_argument(
        "--sort",
        choices=("total", "count", "name"),
        default="total",
        help="Sort by total, count, or name (default: total)",
    )
    parser.add_argument(
        "--contains",
        default="",
        help="Only include event names containing this substring",
    )
    parser.add_argument(
        "--self-time",
        action="store_true",
        help="Show self time (excluding children) and sort by it",
    )
    parser.add_argument(
        "--by-thread",
        action="store_true",
        help="Break down timings per thread",
    )
    parser.add_argument(
        "--source",
        action="store_true",
        help="Show source file:line locations from trace args",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output as JSON instead of table",
    )
    args = parser.parse_args()

    try:
        with open(args.timings, encoding="utf-8") as f:
            events = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {args.timings}: {e}", file=sys.stderr)
        sys.exit(1)

    records = parse_events(events)
    if not records:
        print("No duration events found in trace.", file=sys.stderr)
        sys.exit(1)

    # Compute self time if requested or if JSON (include all fields)
    self_times = None
    if args.self_time or args.json_output:
        self_times = compute_self_time(records)

    # Summary header
    tids = set(r["tid"] for r in records)
    wall_us = max(r["start"] + r["dur"] for r in records) - min(
        r["start"] for r in records
    )
    if not args.json_output:
        print(
            f"Trace: {len(records)} events, {len(tids)} threads, "
            f"{us_to_ms(wall_us)}ms wall time"
        )
        print()

    # Aggregate
    if args.by_thread:
        agg = aggregate_by_thread(records, self_times)
    else:
        agg = aggregate(records, self_times)

    items = list(agg.items())

    if args.contains:
        if args.by_thread:
            items = [i for i in items if args.contains in i[0][0]]
        else:
            items = [i for i in items if args.contains in i[0]]

    use_self = args.self_time
    items = sorted(
        items, key=sort_key(args.sort, use_self), reverse=args.sort != "name"
    )

    if args.min_ms > 0:
        min_us = args.min_ms * 1000
        field = "self" if use_self else "total"
        items = [i for i in items if i[1][field] >= min_us]

    items = items[: args.top]

    # JSON output
    if args.json_output:
        out = []
        for key, stats in items:
            entry = {
                "name": key[0] if args.by_thread else key,
                "count": stats["count"],
                "total_ms": us_to_ms(stats["total"]),
                "self_ms": us_to_ms(stats["self"]),
                "avg_ms": us_to_ms(stats["total"] / stats["count"]),
                "max_ms": us_to_ms(stats["max"]),
            }
            if args.by_thread:
                entry["tid"] = key[1]
            if stats["sources"]:
                entry["sources"] = sorted(stats["sources"])
            out.append(entry)
        print(json.dumps(out, indent=2))
        return

    # Table output
    if args.by_thread:
        name_hdr = f"{'Name':<40} {'TID':>4}"
    else:
        name_hdr = f"{'Name':<50}"

    if use_self:
        hdr = (
            f"{name_hdr} {'Count':>7} {'Total':>10} {'Self':>10} {'Avg':>9} {'Max':>9}"
        )
    else:
        hdr = f"{name_hdr} {'Count':>7} {'Total':>10} {'Avg':>9} {'Max':>9}"

    src_hdr = "  Source" if args.source else ""
    print(hdr + src_hdr)
    print("-" * len(hdr) + ("-" * 40 if args.source else ""))

    for key, stats in items:
        if args.by_thread:
            name, tid = key
            name_col = f"{name[:40]:<40} {tid:>4}"
        else:
            name_col = f"{key[:50]:<50}"

        count = stats["count"]
        total_ms = us_to_ms(stats["total"])
        avg_ms = us_to_ms(stats["total"] / count)
        max_ms = us_to_ms(stats["max"])

        if use_self:
            self_ms = us_to_ms(stats["self"])
            row = f"{name_col} {count:>7} {total_ms:>9.2f}ms {self_ms:>9.2f}ms {avg_ms:>8.2f}ms {max_ms:>8.2f}ms"
        else:
            row = f"{name_col} {count:>7} {total_ms:>9.2f}ms {avg_ms:>8.2f}ms {max_ms:>8.2f}ms"

        if args.source and stats["sources"]:
            row += "  " + ", ".join(sorted(stats["sources"]))

        print(row)


if __name__ == "__main__":
    main()
