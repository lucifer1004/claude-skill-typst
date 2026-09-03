#!/bin/bash
set -euo pipefail
cat > /app/gantt.yaml <<'EOF'
tasks:
  - name: Design
    start: 2026-01-05
    end: 2026-01-16
  - name: Implementation
    start: 2026-01-19
    end: 2026-02-13
  - name: Testing
    start: 2026-02-16
    end: 2026-02-27
EOF
cat > /app/main.typ <<'EOF'
#import "@preview/gantty:0.5.1": gantt

= Project Plan

#gantt(yaml("gantt.yaml"))

The three phases run sequentially through January and February 2026.
EOF
cd /app && typst compile main.typ main.pdf
