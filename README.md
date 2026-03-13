# Torneio de Futsal de São Pedro - URCA

Código para a aplicação do Torneio de Futsal de Porto de Mós que decorre em 2026

## Tecnologias

- **Backend**: FastAPI + Python com `uv` como gerenciador de pacotes
  - Dependências: FastAPI, Uvicorn, Pymongo, Pydantic
  - Banco de dados: MongoDB
- **Frontend**: Vue 3 + PrimeVue + TailwindCSS com `pnpm` como gerenciador de pacotes

## MongoDB com Docker

Para executar o MongoDB localmente usando Docker:

```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=123 \
  mongo:latest
```

Ou usando docker-compose (criar um arquivo `docker-compose.yml`):

```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: 123
    volumes:
      - mongodb_data:/data/db
volumes:
  mongodb_data:
```

Executar com:
```bash
docker-compose up -d
```

## Pré-requisitos

- Python 3.14+
- Node.js 20.19+ ou 22.12+
- uv (para backend)
- pnpm (para frontend)

## Configuração

### Backend

1. Navegar até a pasta do backend:
   ```bash
   cd backend
   ```

2. Instalar as dependências com uv:
   ```bash
   uv sync
   ```

3. Configurar o arquivo `.env` na pasta `backend/` com a variável:
   ```
   db_connection_string=mongodb://utilizador:senha@host:porta/seu_banco?authSource=admin
   ```
   Exemplo `.env`:
   ```env
   db_connection_string=mongodb://root:123@localhost:27017/tournament?authSource=admin
   http_host=0.0.0.0
   ```

4. Executar o servidor:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   A API estará disponível em `http://localhost:8000`

### Frontend

1. Navegar até a pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instalar as dependências com pnpm:
   ```bash
   pnpm install
   ```

3. Executar o servidor de desenvolvimento:
   ```bash
   pnpm dev
   ```

   A aplicação estará disponível em `http://localhost:5173`

## Build

### Backend
```bash
cd backend
uv build
```

### Frontend
```bash
cd frontend
pnpm build
```

Os arquivos finais estarão na pasta `dist/` do frontend
