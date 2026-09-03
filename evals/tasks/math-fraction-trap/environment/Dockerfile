FROM ubuntu:24.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates xz-utils python3 \
 && rm -rf /var/lib/apt/lists/*

# Pin the Typst release under evaluation.
RUN arch="$(dpkg --print-architecture)" \
 && case "$arch" in amd64) t=x86_64 ;; arm64) t=aarch64 ;; *) echo "unsupported arch: $arch" >&2; exit 1 ;; esac \
 && curl -fsSL "https://github.com/typst/typst/releases/download/v0.15.1/typst-${t}-unknown-linux-musl.tar.xz" -o /tmp/typst.tar.xz \
 && tar -xJf /tmp/typst.tar.xz -C /usr/local/bin --strip-components=1 \
 && rm /tmp/typst.tar.xz

WORKDIR /app

# Task assets (and optionally a `skill/` dir injected by run.sh) land in /app.
COPY . /tmp/ctx
RUN cp -r /tmp/ctx/. /app/ && rm -f /app/Dockerfile \
 && if [ -d /app/skill ]; then mkdir -p /app/.claude/skills && mv /app/skill /app/.claude/skills/typst; fi \
 && rm -rf /tmp/ctx
