# Company Core — Guia de Instalação e Configuração

Este guia documenta o processo completo de setup, instalação e configuração do Company Core para desenvolvimento e produção.

## Pré-requisitos

- Python 3.12+
- PostgreSQL 17+ (ou SQLite para desenvolvimento)
- Redis 7+
- Docker e Docker Compose (opcional, para infraestrutura)

## Instalação Local

### 1. Clonar o repositório

```bash
git clone https://github.com/alc-br/company-core.git
cd company-core
```

### 2. Copiar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Instalar dependências

```bash
pip install uv
uv sync --all-extras --group=dev
```

### 4. Gerar migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar superuser

```bash
python manage.py createsuperuser
```

### 6. Rodar o servidor

```bash
python manage.py runserver
```

Acesse: `http://localhost:8000/`

## Setup com Docker

### 1. Variáveis de ambiente

```bash
cp .env.example .env
# Editar .env
```

### 2. Subir serviços

```bash
docker compose up -d
```

### 3. Aplicar migrations

```bash
docker compose exec app python manage.py migrate
```

### 4. Criar superuser

```bash
docker compose exec app python manage.py createsuperuser
```

### 5. Acessar

`http://localhost:8000/`

## Estrutura do Projeto

```
company-core/
    apps/                    # 25 Django apps
        users/                 # CustomUser, autenticação
        common/                # Mixins, exceptions, helpers
        core/                  # Configurações base
        settings/              # Settings dinâmicos por tenant
        organizations/         # Multi-tenancy
        permissions/           # RBAC
        billing/               # Stripe billing
        quotas/                # Sistema de quotas
        feature_flags/         # Feature flags
        ai/                    # Abstração IA (OpenAI, Anthropic, Gemini)
        agents/                # Framework de agentes
        notifications/          # Notificações
        integrations/         # Framework de integrações
        audit/                 # Logs de auditoria
        analytics/             # Dashboard de uso
        usage/                 # Métricas centralizadas
        storage/               # Abstração S3/MinIO/R2
        api/                   # REST API, API Keys
        webhooks/              # Sistema de webhooks
        workflows/             # Motor de workflows
        jobs/                  # Gerenciamento de filas
        sdk/                   # SDK interno
        health/                # Health checks
        search/                # Busca
        admin_ext/             # Admin estendido
        web/                   # Dashboard, views gerais
    company_core/             # Django project package
        settings/              # Settings (base, dev, production, test)
        urls.py
        celery.py
        wsgi.py
        asgi.py
    templates/               # HTMX + Tailwind/DaisyUI templates
    docs/                    # Documentação de arquitetura
    scripts/                 # Scripts utilitários
    static/                  # Arquivos estáticos
    tests/                   # Testes
    pyproject.toml            # Dependências e configuração
    Dockerfile                # Imagem Docker
    docker-compose.yml       # Compose (App + DB + Redis + MinIO)
    Makefile                 # Comandos de desenvolvimento
    .github/workflows/ci.yml  # CI/CD pipeline
```

## Cada App Segue o Padrão

```
apps/<nome>/
    models.py        # Modelos Django
    views.py         # Views (HTMX)
    services.py      # Lógica de negócio (Service Layer)
    selectors.py     # Consultas complexas (Selector Layer)
    tasks.py         # Tarefas Celery
    signals.py       # Signals Django
    serializers.py   # Serializadores DRF
    urls.py          # Rotas
    admin.py         # Django Admin
    tests/           # Testes
    README.md        # Documentação
```

## Commands Disponíveis (Makefile)

```bash
make install       # Instalar dependências
make dev            # Servidor de desenvolvimento
make migrate        # Aplicar migrations
make makemigrations  # Criar novas migrations
make test           # Rodar testes com coverage
make lint           # Verificar linting
make format         # Formatar código
make typecheck      # Verificar tipos
make check          # Lint + typecheck + test
make createsuperuser # Criar superuser
make docker-up      # Subir Docker
make docker-down    # Parar Docker
```

## Settings

### Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta Django | Gerado automaticamente |
| `DEBUG` | Modo debug | `True` |
| `DATABASE_URL` | URL do PostgreSQL | `postgres://localhost:5432/company_core` |
| `REDIS_URL` | URL do Redis | `redis://localhost:6379/0` |
| `STRIPE_TEST_PUBLIC_KEY` | Chave pública Stripe | |
| `OPENAI_API_KEY` | API key OpenAI | |
| `ANTHROPIC_API_KEY` | API key Anthropic | |
| `GEMINI_API_KEY` | API key Gemini | |

### Ambientes de Settings

- `company_core.settings.base` — Base (produção e dev)
- `company_core.settings.development` — Overrides de desenvolvimento
- `company_core.settings.production` — Hardening de produção
- `company_core.settings.test` — Isolamento de testes

## Templates e Frontend

- **DaisyUI** (Tailwind CSS component library) para todos os componentes
- **HTMX** para interações dinâmicas sem JavaScript
- **Alpine.js** para lógica client-side mínima
- Todas as interfaces em **Português Brasileiro**

## Testes

```bash
# Rodar todos os testes
make test

# Rodar apenas testes unitários
pytest -v -m unit

# Rodar com coverage
pytest --cov=apps --cov-report=html
```

## CI/CD

O pipeline de CI/CD (`ci.yml`) executa:

1. Linting (ruff format + ruff check)
2. Type checking (mypy)
3. Security scan (secrets detection)
4. Migration validation
5. Tests with coverage (minimum 90%)
