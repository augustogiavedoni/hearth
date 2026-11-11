# syntax=docker/dockerfile:1
# Skeleton only (milestone M6). Build from the repo root:
#   docker build -f deploy/Dockerfile .
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Unprivileged runtime user. Code stays root-owned (read-only for the app).
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
RUN uv sync --locked --no-dev \
    && mkdir -p /app/data && chown app:app /app/data

USER app

# No EXPOSE: the assistant only makes outbound connections.
# TODO(augusto): replace with the real entrypoint.
CMD ["python", "-c", "print('hearth: no entrypoint yet')"]
