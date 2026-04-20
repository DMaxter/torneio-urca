FROM node:22-alpine AS builder

WORKDIR /frontend
COPY frontend/package.json frontend/pnpm-lock.yaml* ./
RUN corepack enable && corepack prepare pnpm@10.30.3 --activate
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm run build-only


FROM nginx:alpine

COPY --from=builder /frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
