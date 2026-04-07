FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN corepack enable && corepack prepare pnpm@10.30.3 --activate
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm run build-only


FROM python:3.14-alpine
COPY --from=docker.io/astral/uv:0.11 /uv /uvx /bin

WORKDIR /backend

COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen --no-dev

COPY backend/ ./

COPY --from=frontend-builder /frontend/dist /backend/static

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]
