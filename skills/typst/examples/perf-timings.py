#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict


def parse_durations(events):
    begins = {}
    durations = []

    for event in events:
        name = event.get("name", "")
        ph = event.get("ph", "")
        ts = event.get("ts", 0)
        tid = event.get("tid", 0)
        key = (name, tid)

        if ph == "B":
            begins.setdefault(key, []).append(ts)
        elif ph == "E" and begins.get(key):
            start_ts = begins[key].pop()
            durations.append((name, ts - start_ts))

    return durations


def aggregate(durations):
    agg = defaultdict(lambda: {"count": 0, "total": 0})
    for name, dur in durations:
        agg[name]["count"] += 1
        agg[name]["total"] += dur
    return agg


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize Typst --timings trace by event name."
    )
    parser.add_argument("timings", help="Path to timings JSON")
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
        "--json",
        dest="json_output",
        action="store_true",
        help="Output as JSON instead of table",
    )
    return parser.parse_args()


def sort_key(sort_by):
    if sort_by == "count":
        return lambda item: item[1]["count"]
    if sort_by == "name":
        return lambda item: item[0].lower()
    return lambda item: item[1]["total"]


def main():
    args = parse_args()
    with open(args.timings, "r", encoding="utf-8") as f:
        events = json.load(f)

    durations = parse_durations(events)
    agg = aggregate(durations)

    items = list(agg.items())
    if args.contains:
        items = [i for i in items if args.contains in i[0]]

    items = sorted(items, key=sort_key(args.sort), reverse=args.sort != "name")

    if args.min_ms > 0:
        min_us = args.min_ms * 1000
        items = [i for i in items if i[1]["total"] >= min_us]

    items = items[: args.top]

    if args.json_output:
        out = [
            {
                "name": name,
                "count": stats["count"],
                "total_ms": stats["total"] / 1000,
            }
            for name, stats in items
        ]
        print(json.dumps(out, indent=2))
        return

    print(f"Top {args.top} timings:")
    print(f'{"Name":<50} {"Count":>8} {"Total (ms)":>12}')
    print("-" * 72)
    for name, stats in items:
        total_ms = stats["total"] / 1000
        print(f'{name[:50]:<50} {stats["count"]:>8} {total_ms:>12.2f}')


if __name__ == "__main__":
    main()
