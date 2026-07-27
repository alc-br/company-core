# Company Core — Plataforma SaaS Multi-Tenant

<p align="center">
  <strong>Infraestrutura compartilhada para dezenas de produtos SaaS</strong>
</p>

<p align="center">
  <a href="#visão-geral">Visão Geral</a> •
  <a href="#arquitetura">Arquitetura</a> •
  <a href="#módulos">Módulos</a> •
  <a href="#instalação">Instalação</a> •
  <a href="#desenvolvimento">Desenvolvimento</a>
  •
  <a href="#documentação">Documentação</a>
</p>

---

## Visão Geral

O **Company Core** é uma plataforma SaaS multi-tenant construída sobre o [SaaS Pegasus](https://saaspegasus.com/), projetada para servir como fundação compartilhada para dezenas de produtos SaaS.

Cada novo produto precisa conter **apenas sua regra de negócio**, reutilizando toda a infraestrutura do Company Core:

```
Company Core + Video Knowledge Graph = SaaS de Vídeo
Company Core + AI SEO = SaaS de SEO
Company Core + AI CRM = SaaS de CRM
Company Core + Restaurant AI = SaaS de Restaurantes
Company Core + Medical AI = SaaS de Saúde
Company Core + Legal AI = SaaS Jurídico
```

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| **Base** | SaaS Pegasus, Django 6, Python 3.12, PostgreSQL 17 |
| **Frontend** | HTMX, Alpine.js, Tailwind CSS v4, DaisyUI |
| **API** | Django REST Framework, drf-spectacular (OpenAPI) |
| **Tasks** | Celery, Redis, django-celery-beat |
| **Storage** | S3 / MinIO / Cloudflare R2 |
| **Billing** | Stripe via dj-stripe |
| **IA** | OpenAI, Anthropic, Gemini |
| **Infra** | Docker, Nginx, GitHub Actions |

## Arquitetura

A arquitetura segue o padrão de **camadas concêntricas**:

```
┌─────────────────────────────────────────┐
│  Camada de Produto (domínio específico) │
├─────────────────────────────────────────┤
│  Company Core (infraestrutura)          │
├─────────────────────────────────────────┤
│  SaaS Pegasus (fundação)                │
└─────────────────────────────────────────┘
```

Veja a documentação completa em `docs/ARCHITECTURE.md`.

## Módulos

| # | Módulo | Descrição |
|---|--------|----------|
| 1 | `core` | Configurações compartilhadas |
| 2 | `common` | Utilitários, mixins, helpers |
| 3 | `settings` | Configurações dinâmicas por tenant |
| 4 | `organizations` | Multi-tenancy, times, convites |
| 5 | `permissions` | RBAC, papéis e permissões |
| 6 | `billing` | Stripe, planos, assinaturas |
| 7 | `quotas` | Sistema de quotas configurável |
| 8 | `feature_flags` | Feature flags por plano/tenant/user |
| 9 | `ai` | Abstração de provedores IA |
| 10 | `agents` | Framework de agentes IA |
| 11 | `notifications` | Email, Slack, Discord, webhooks |
| 12 | `integrations` | Framework de integrações |
| 13 | `audit` | Rastreio completo de ações |
| 14 | `analytics` | Dashboard de uso e métricas |
| 15 | `usage` | Centralização de métricas |
| 16 | `storage` | Abstração S3/MinIO/R2 |
| 17 | `api` | REST versionada, API Keys |
| 18 | `webhooks` | Sistema universal de webhooks |
| 19 | `workflows` | Motor de workflows |
| 20 | `jobs` | Gerenciamento de filas |
| 21 | `sdk` | SDK interno reutilizável |
| 22 | `health` | Health checks |
| 23 | `search` | Funcionalidade de busca |
| 24 | `admin` | Painéis administrativos |

Veja `docs/MODULE_MAP.md` para dependências entre módulos.

## Instalação

### Pré-requisitos

- Python 3.12+
- PostgreSQL 17+
- Redis 7+
- Docker (opcional)

### Setup com Docker

```bash
# Clonar o repositório
git clone https://github.com/alc-br/company-core.git
cd company-core

# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Subir serviços
docker compose up -d

# Criar bucket MinIO (primeira vez)
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mb local/company-core

# Aplicar migrações
docker compose exec app python manage.py migrate

# Criar superuser
docker compose exec app python manage.py createsuperuser
```

### Setup Local

```bash
# Clonar o repositório
git clone https://github.com/alc-br/company-core.git
cd company-core

# Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Instalar dependências
pip install uv
uv sync --all-extras

# Aplicar migrações
uv run python manage.py migrate

# Criar superuser
uv run python manage.py createsuperuser

# Rodar servidor
uv run python manage.py runserver
```

## Desenvolvimento

### Estrutura de Cada App

```
apps/<app_name>/
    models.py      # Modelos de dados
    views.py       # Views (HTMX / DRF)
    services.py    # Lógica de negócio (Service Layer)
    selectors.py   # Consultas complexas (Selector Layer)
    tasks.py       # Tarefas Celery
    signals.py     # Signals Django
    serializers.py # Serializadores DRF
    urls.py        # Rotas da app
    admin.py       # Django Admin
    tests/         # Testes
    README.md      # Documentação
```

### Comandos Úteis

```bash
# Rodar testes
uv run pytest

# Rodar testes com cobertura
uv run pytest --cov=apps --cov-report=html

# Linting
uv run ruff check apps/
uv run ruff format apps/

# Type checking
uv run mypy apps/

# Migrações
uv run python manage.py makemigrations
uv run python manage.py migrate

# Gerar diagrama de models
uv run python manage.py graph_models -o models.png
```

### Padrões de Commit

```
feat: add tenant quota framework
fix: resolve cross-tenant data leak in selector
test: add billing service tests
docs: add module architecture guide
refactor: simplify ai provider interface
ci: configure quality pipeline
chore: update dependencies
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| `docs/PEGASUS_REUSE_PLAN.md` | O que reutilizar, estender e implementar do Pegasus |
| `docs/ARCHITECTURE.md` | Arquitetura técnica completa |
| `docs/MODULE_MAP.md` | Mapa de dependências entre módulos |

## Licença

Este projeto é licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.
