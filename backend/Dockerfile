FROM python:3.14-alpine
COPY --from=docker.io/astral/uv:0.11 /uv /uvx /bin

WORKDIR /backend
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen --no-dev
COPY backend/ ./

ENV UV_NO_DEV=1

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]
