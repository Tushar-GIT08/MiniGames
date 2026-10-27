FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

ENV DB_PATH=/data/users.db

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "gthread", "--threads", "100", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]