# Company Core

<p align="center">
  <strong>Plataforma SaaS multi-tenant de referencia para dezenas de produtos.</strong><br>
  Infraestrutura horizontal completa: auth, billing, permissões, IA, auditoria, workflows.<br>
  <code>Django 6 + Python 3.12 + PostgreSQL + Redis + Celery + DRF + Stripe + OpenAI</code>
</p>

---

## O que e?

O **Company Core** e uma fundacao SaaS multi-tenant que fornece toda a infraestrutura horizontal que todo produto precisa. Em vez de recriar login, cobranca, permissões e notificacoes para cada app, voce cria apenas a regra de negocio do seu produto e consome os servicos do Core via SDK.

```
Company Core + Office Blueprint  =  SaaS de Gestao para Escritorios
Company Core + AI CRM           =  SaaS de CRM com IA
Company Core + Restaurant AI    =  SaaS para Restaurantes
Company Core + Legal AI         =  SaaS Juridico
```

### Numeros atuais

| Metrica | Valor |
|---------|-------|
| Django apps | 24 apps transversais |
| Migracoes | 86 aplicadas |
| API ViewSets | 40 registrados no DRF router |
| Celery tasks | 11 tarefas reais em 7 filas |
| Testes | 65 passando (pytest) |
| Templates | 24 templates DaisyUI/Tailwind |
| SDK facades | 5 (Billing, Quota, AI, Storage, Notification) |
| Webhook handlers | 6 eventos Stripe |
| Workflow step types | 4 (action, condition, delay, parallel) |
| AI Agent tools | Loop de execucao com 5 iteracoes |

---

## Stack Tecnologica

| Camada | Tecnologia | Versao |
|--------|-----------|--------|
| Backend | Django | 6.0.7 |
| Linguagem | Python | 3.12 |
| Banco de dados | PostgreSQL | 17+ |
| Cache/Broker | Redis | 7+ |
| Frontend | HTMX + Alpine.js | 2.0 / 3.x |
| CSS | Tailwind CSS v4 + DaisyUI | v4 / 4.12 |
| API REST | Django REST Framework + drf-spectacular | 3.15+ |
| Tasks async | Celery + django-celery-beat | 5.4+ |
| Storage | S3 / MinIO / Cloudflare R2 | 1.14+ |
| Billing | Stripe (checkout + webhooks) | 11.0+ |
| IA | OpenAI, Anthropic, Gemini | latest |
| Auth | django-allauth (email as username) | 65.0+ |
| Package manager | uv | latest |
| CI/CD | GitHub Actions | -- |
| Container | Docker + docker-compose | -- |

---

## Arquitetura

O projeto segue **Service Layer + Selector Layer** -- nenhuma logica de negocio em views ou models.

```
┌─────────────────────────────────────────────┐
│  Camada de Produto (dominio especifico)     │  <- apps/blueprint, apps/crm, etc.
├─────────────────────────────────────────────┤
│  Company Core (24 apps transversais)         │  <- infraestrutura SaaS
│  ┌───────────────────────────────────────┐   │
│  │  views.py       (HTMX + DRF)          │   │
│  │  services.py    (logica de negocio)   │   │
│  │  selectors.py   (consultas complexas)  │   │
│  │  models.py      (dados + TenantMixin) │   │
│  │  tasks.py       (Celery async)        │   │
│  │  serializers.py (DRF)                 │   │
│  └───────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  Infraestrutura (PostgreSQL, Redis, S3)      │
└─────────────────────────────────────────────┘
```

### Multitenancy em 3 niveis

1. **TenantMixin** -- todo modelo de negocio herda `organization = ForeignKey(Organization)`.
2. **TenantMiddleware** -- injeta `request.tenant` a partir da sessao do usuario logado.
3. **Thread-local** -- `get_current_tenant()` / `set_current_tenant()` para tasks async.

```python
from apps.organizations.utils import get_current_tenant
tenant = get_current_tenant()  # Organization do tenant atual
```

---

## Modulos (24 apps em 6 camadas)

### Camada 0 -- Fundacao

| App | Descricao |
|-----|-----------|
| `common` | Mixins (Timestamp, Tenant, SoftDelete), excecoes customizadas, helpers, IntegerChoices |
| `users` | CustomUser (email as username), avatar com Gravatar, bio, timezone, allauth adapter |
| `core` | Configuracoes compartilhadas |
| `settings` | TenantSetting e GlobalSetting com cache |
| `health` | Health checks: `/health/`, `/ready/`, `/live/` |

### Camada 1 -- Organizacao e Acesso

| App | Descricao |
|-----|-----------|
| `organizations` | Organization, Membership, Invitation, TenantMiddleware, switch de tenant |
| `permissions` | Permission, Role, RolePermission -- RBAC completo com papeis por org |
| `feature_flags` | FeatureFlag com ativacao global, por usuario, grupo e organizacao |

### Camada 2 -- Operacoes

| App | Descricao |
|-----|-----------|
| `billing` | Plan, Subscription, Invoice, Stripe checkout sessions, 6 webhook handlers |
| `quotas` | QuotaDefinition, QuotaAllocation com `remaining` e `is_exceeded` |
| `audit` | AuditLog completo com `AuditService.log()` |
| `usage` | UsageRecord com agregacao diaria/semanal/mensal |
| `jobs` | Job model com status, retries, fila e agendamento |

### Camada 3 -- Capacidades

| App | Descricao |
|-----|-----------|
| `ai` | AIProviderConfig (OpenAI/Anthropic/Gemini), AIModelConfig, AICallLog |
| `agents` | Agent com system_prompt, tools, e AgentExecution com loop de 5 iteracoes |
| `notifications` | NotificationChannel, NotificationTemplate, NotificationLog (email/webhook/slack/discord) |
| `storage` | StorageBackendConfig, StoredObject com upload/download/delete |
| `webhooks` | WebhookEndpoint, WebhookDelivery com retry e log |
| `workflows` | Workflow com steps_config JSON, 4 tipos de step, execucao via Celery |

### Camada 4 -- Inteligencia

| App | Descricao |
|-----|-----------|
| `analytics` | AnalyticsEvent, AnalyticsAggregation |
| `search` | SearchIndex (Whoosh-based) |
| `integrations` | Integration, IntegrationLog |

### Camada 5 -- Interfaces

| App | Descricao |
|-----|-----------|
| `api` | APIKey (`cc_live_` prefix), PAT, ServiceAccount, auth, pagination, throttling |
| `sdk` | Facades: BillingSDK, QuotaSDK, AISDK, StorageSDK, NotificationSDK |
| `admin_ext` | Django Admin centralizado com todos os modelos |
| `web` | Dashboard principal e navegacao base |

---

## Como Rodar

### Pre-requisitos

- **Python 3.12**
- **[uv](https://docs.astral.sh/uv/)** (gerenciador de pacotes)
- PostgreSQL 17 e Redis 7 (ou Docker para ambos)

### Opcao A: Desenvolvimento local (sem Docker)

```bash
# 1. Clonar o repositorio
git clone https://github.com/alc-br/company-core.git
cd company-core

# 2. Instalar dependencias (inclui dev deps: pytest, ruff, mypy)
uv sync --all-extras

# 3. Criar o .env (para dev, SQLite funciona sem config extra)
cp .env.example .env
# O minimo para dev:
#   SECRET_KEY=django-insecure-dev-key
#   DEBUG=True
#   DATABASE_URL=sqlite:///db.sqlite3
#   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# 4. Aplicar migrations (86 migrations)
uv run python manage.py migrate

# 5. Criar superusuariouv run python manage.py createsuperuser
#   Email: admin@companycore.dev  Senha: admin123

# 6. Rodar o servidor
uv run python manage.py runserver
```

Acesse:
- **App:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **API:** http://localhost:8000/api/v1/
- **Health:** http://localhost:8000/health/

### Opcao B: Docker Compose (producao)

```bash
# 1. Clonar e configurar
git clone https://github.com/alc-br/company-core.git
cd company-core
cp .env.example .env
# Editar .env com credenciais reais de PostgreSQL, Redis, Stripe, etc.

# 2. Subir todos os servicos (app + PostgreSQL + Redis + MinIO + Celery)
docker compose up -d

# 3. Aplicar migrations
docker compose exec app python manage.py migrate

# 4. Criar superusuariodocker compose exec app python manage.py createsuperuser

# 5. Coletar staticos (producao)
docker compose exec app python manage.py collectstatic --noinput
```

### Opcao C: Docker apenas para DB/Redis, app local

```bash
# Subir PostgreSQL e Redis
docker run -d --name cc-postgres \
  -e POSTGRES_DB=company_core -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 postgres:17

docker run -d --name cc-redis -p 6379:6379 redis:7

# No .env:
#   DATABASE_URL=postgres://postgres:postgres@localhost:5432/company_core
#   REDIS_URL=redis://localhost:6379/0

# Depois siga a Opcao A a partir do passo 4
```

### Celery (obrigatorio para tarefas async)

```bash
# Worker com todas as filas
uv run celery -A company_core.celery worker -l info \
  -Q default,billing,ai,webhooks,workflows,analytics,notifications

# Scheduler (beat)
uv run celery -A company_core.celery beat -l info
```

### Verificacao de saude

```bash
# Django system check (deve retornar 0 issues)
uv run python manage.py check

# Health endpoints
curl http://localhost:8000/health/   # Liveness + DB + Redis
curl http://localhost:8000/ready/    # Readiness
curl http://localhost:8000/live/     # Liveness basico
```

---

## Como Personalizar

### 1. Criar um novo produto SaaS

Cada produto e um Django app dentro de `apps/` que consome os servicos do Core:

```bash
# Criar a estrutura do app
mkdir -p apps/blueprint/tests apps/blueprint/migrations
touch apps/blueprint/__init__.py apps/blueprint/apps.py \
      apps/blueprint/models.py apps/blueprint/services.py \
      apps/blueprint/selectors.py apps/blueprint/views.py \
      apps/blueprint/tasks.py apps/blueprint/serializers.py \
      apps/blueprint/urls.py apps/blueprint/admin.py
```

**Models** -- herde de TenantMixin + TimestampMixin para ter multitenancy automatico:

```python
from django.db import models
from apps.common.mixins import TenantMixin, TimestampMixin

class Client(TenantMixin, TimestampMixin):
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    status = models.IntegerField(choices=BaseStatus.choices, default=BaseStatus.ACTIVE)

    def __str__(self):
        return self.name
```

**Services** -- toda logica de negocio fica aqui, views chamam services:

```python
class ClientService:
    @staticmethod
    def create_client(organization, name, cnpj, **kwargs):
        client = Client.objects.create(organization=organization, name=name, cnpj=cnpj, **kwargs)
        AuditService.log(actor=kwargs.get('actor'), action='create_client', target=client)
        return client
```

**Selectors** -- consultas complexas com `select_related` e filtros:

```python
def get_organization_clients(organization_id, **filters):
    qs = Client.objects.filter(organization_id=organization_id, status=BaseStatus.ACTIVE)
    if filters.get('search'):
        qs = qs.filter(name__icontains=filters['search'])
    return qs.order_by('-created_at')
```

**Registrar o app** em `company_core/settings/base.py` na lista `COMPANY_CORE_APPS`.

### 2. Configurar um provedor de IA

```bash
# No .env:
OPENAI_API_KEY=sk-...
# ou
ANTHROPIC_API_KEY=sk-ant-...
# ou
GOOGLE_AI_API_KEY=...
```

Depois crie os registros no Admin (`/admin/ai/`):
1. **AIProviderConfig** -- configure o provider (openai, anthropic, gemini) com API key
2. **AIModelConfig** -- registre os modelos disponiveis (gpt-4o, claude-3.5-sonnet, etc.)

Use via SDK:

```python
from apps.sdk.ai import AISDK

response = AISDK.complete(
    organization=org,
    provider='openai',
    model='gpt-4o',
    messages=[{'role': 'user', 'content': 'Hello!'}],
    temperature=0.7,
)
```

### 3. Configurar Stripe Billing

```bash
# No .env:
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

1. Crie **Plans** no Admin ou via API (`POST /api/v1/plans/`) com `stripe_price_id`
2. Use `BillingSDK.create_checkout()` para gerar sessoes de checkout:

```python
from apps.sdk.billing import BillingSDK

session = BillingSDK.create_checkout(
    organization=org,
    plan=plan,
    success_url='https://app.seudominio.com/billing/success/',
    cancel_url='https://app.seudominio.com/billing/cancel/',
)
# Redireciona o usuario para session['url']
```

3. Configure o webhook endpoint em `https://app.seudominio.com/api/v1/billing/stripe-webhook/`

6 eventos sao tratados automaticamente: `checkout.session.completed`, `customer.subscription.created/updated/deleted`, `invoice.payment_succeeded/failed`.

### 4. Configurar storage (S3/MinIO/R2)

```bash
# No .env para S3 AWS:
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=company-core
AWS_S3_REGION_NAME=us-east-1

# No .env para MinIO (local):
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_STORAGE_BUCKET_NAME=company-core
AWS_S3_ENDPOINT_URL=http://localhost:9000
```

```python
from apps.sdk.storage import StorageSDK

# Upload
file_info = StorageSDK.upload(
    organization=org,
    file=uploaded_file,
    folder=f'clients/{client_id}/documents',
    metadata={'category': 'contract'},
)
```

### 5. Configurar notificacoes

1. Crie **NotificationChannel** (email, webhook, slack, discord) no Admin
2. Crie **NotificationTemplate** com codigo e conteudo (suporta Jinja2)
3. Envie via SDK:

```python
from apps.sdk.notifications import NotificationSDK

NotificationSDK.send(
    organization=org,
    user=target_user,
    channel='email',
    template_code='task_assigned',
    context={'task_title': 'Nova tarefa', 'client': 'Empresa X'},
)
```

### 6. Configurar quotas por plano

1. Defina **QuotaDefinition** (ex: `max_clients`, `ai_prompts_monthly`)
2. Aloque via Admin ou API em **QuotaAllocation** por organizacao
3. Verifique no codigo:

```python
from apps.sdk.quotas import QuotaSDK

if not QuotaSDK.check(org, 'max_clients'):
    raise QuotaExceededError('Limite de clientes atingido')

QuotaSDK.increment(org, 'active_clients')
```

### 7. Configurar permissoes (RBAC)

```python
from apps.permissions.services import PermissionService

# Criar papel
PermissionService.create_role(
    organization=org,
    name='Gestor',
    permissions=['client.create', 'client.edit', 'template.view'],
)

# Verificar permissao
PermissionService.check_permission(user, org, 'client.create')
```

Padrao: `<entidade>.<acao>` (ex: `client.create`, `template.publish`, `admin.billing`).

### 8. Configurar feature flags

```python
from apps.feature_flags.services import FeatureFlagService

# Criar flag
flag = FeatureFlagService.create_flag(code='new_dashboard', name='Novo Dashboard')

# Ativar globalmente
FeatureFlagService.enable('new_dashboard')

# Ativar para uma organizacao especifica
FeatureFlagService.assign_flag_to_organization(flag, organization)

# Verificar no template ou view
if FeatureFlagService.is_active('new_dashboard', user=request.user, organization=tenant):
    # renderiza novo dashboard
```

### 9. Configurar workflows

```python
from apps.workflows.services import WorkflowService

# Criar workflow com steps
workflow = Workflow.objects.create(
    name='onboarding',
    organization=org,
    steps_config=[
        {'type': 'action', 'name': 'send_welcome', 'handler_path': 'apps.notifications.tasks.send_welcome_email'},
        {'type': 'delay', 'name': 'wait', 'config': {'seconds': 60}},
        {'type': 'condition', 'name': 'check_plan', 'config': {'field': 'plan_type', 'operator': 'equals', 'value': 'pro'}},
        {'type': 'http_call', 'name': 'notify_slack', 'config': {'url': 'https://hooks.slack.com/...', 'method': 'POST'}},
    ]
)

# Executar (dispatcha para Celery)
WorkflowService.start_workflow(workflow, organization=org)
```

### 10. Configurar webhooks de saida

```python
from apps.webhooks.services import WebhookService

# Registrar endpoint
endpoint = WebhookService.register_endpoint(
    organization=org,
    url='https://api.seusistema.com/webhooks/companycore/',
    events=['user.created', 'invoice.paid', 'subscription.canceled'],
)

# Disparar evento (automaticamente via signals ou manual)
WebhookService.trigger(organization=org, event_type='user.created', payload={'user_id': 42, 'email': '...'})
```

### 11. Usar a API REST

**Autenticacao por API Key** (prefixo `cc_live_`):

```bash
# Criar chave no Admin ou via API
curl -X POST http://localhost:8000/api/v1/api-keys/ \
  -H 'Authorization: Bearer cc_live_...' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Integracao X"}'

# Usar a chave
curl http://localhost:8000/api/v1/organizations/ \
  -H 'Authorization: Bearer cc_live_abc123...'
```

**40 ViewSets disponiveis** cobrem: users, organizations, memberships, invitations, permissions, roles, plans, subscriptions, invoices, quotas, feature-flags, AI providers/models/logs, agents/tools/executions, notifications, storage, webhooks, workflows, jobs, audit, analytics, integrations, search, settings, API keys, service accounts.

Resposta padronizada:

```json
{
  "success": true,
  "data": [...],
  "pagination": {"page": 1, "page_size": 100, "total_pages": 5, "total_items": 420}
}
```

---

## Comandos do Dia a Dia

```bash
# Dependencias
uv sync --all-extras              # instalar/atualizar
duv run python manage.py makemigrations   # gerar migrations
uv run python manage.py migrate            # aplicar migrations

# Servidor
uv run python manage.py runserver         # dev server
uv run python manage.py runserver --noreload  # sem auto-reload

# Celery
uv run celery -A company_core.celery worker -l info -Q default,billing,ai,webhooks,workflows,analytics,notifications
uv run celery -A company_core.celery beat -l info

# Testes
uv run pytest apps/ --no-cov -v                      # rodar todos
uv run pytest apps/billing/ -v --no-cov              # rodar um app
uv run pytest apps/organizations/tests/test_services.py -v  # um arquivo
uv run pytest --cov=apps --cov-report=html           # com cobertura

# Qualidade
uv run ruff check apps/                          # lint
uv run ruff format apps/                         # formatar
uv run mypy apps/                                # type check

# Utilitarios
uv run python manage.py check                   # sistema check
uv run python manage.py shell_plus               # shell com auto-import
uv run python manage.py createsuperuser           # criar admin
uv run python manage.py show_urls                 # listar todas as URLs
```

---

## Estrutura de Diretorios

```
company-core/
├── company_core/           # Configuracao do projeto Django
│   ├── settings/           # base.py, development.py, production.py, test.py
│   ├── urls.py             # Router principal
│   ├── celery.py           # Configuracao do Celery
│   ├── wsgi.py / asgi.py
│   └── context_processors.py
├── apps/                   # 24 apps transversais
│   ├── common/             # Mixins, excecoes, helpers
│   ├── users/              # Autenticacao
│   ├── organizations/      # Multi-tenancy
│   ├── permissions/        # RBAC
│   ├── billing/            # Stripe + planos
│   ├── ai/                 # OpenAI/Anthropic/Gemini
│   ├── agents/             # Agentes com ferramentas
│   ├── workflows/          # Motor de workflows
│   ├── api/                # REST API + API Keys
│   ├── sdk/                # Facades internas
│   └── ... (24 apps)
├── templates/              # HTML (Tailwind + DaisyUI + HTMX)
│   ├── base.html           # Layout principal
│   └── */                  # Templates por app
├── docs/                   # Documentacao tecnica
│   ├── ARCHITECTURE.md
│   ├── MODULE_MAP.md
│   └── PEGASUS_REUSE_PLAN.md
├── static/                 # Arquivos estaticos
├── media/                  # Uploads
├── scripts/                # Scripts utilitarios
├── pyproject.toml          # Dependencias e config (ruff, mypy, pytest)
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── .env.example
├── conftest.py             # pytest path config
└── manage.py
```

---

## Variaveis de Ambiente (.env)

```env
# === Obrigatorias ===
SECRET_KEY=sua-chave-secreta
DATABASE_URL=postgres://user:pass@localhost:5432/company_core
REDIS_URL=redis://localhost:6379/0

# === App ===
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# === Email (padrao: console) ===
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.sendgrid.net
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=apikey
# EMAIL_HOST_PASSWORD=SG.xxx

# === Celery ===
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# === Storage (padrao: local) ===
STORAGE_BACKEND=local
# STORAGE_BACKEND=s3
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=company-core
# AWS_S3_ENDPOINT_URL=          # MinIO: http://localhost:9000
# AWS_S3_REGION_NAME=us-east-1

# === Stripe ===
# STRIPE_SECRET_KEY=sk_live_...
# STRIPE_WEBHOOK_SECRET=whsec_...

# === AI Providers ===
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_AI_API_KEY=...
```

---

## Filas Celery

| Fila | Uso | Exemplos |
|------|-----|----------|
| `default` | Tarefas gerais | cleanup, sync |
| `billing` | Pagamentos e invoices | `process_invoice_task`, `check_overdue_subscriptions_task` |
| `ai` | Chamadas a provedores de IA | `process_ai_call_task`, `aggregate_ai_usage_task` |
| `webhooks` | Entrega de webhooks | `deliver_webhook_task` |
| `workflows` | Execucao de workflows | `execute_workflow_task`, `retry_workflow_task` |
| `analytics` | Agregacao de metricas | -- |
| `notifications` | Emails e notificacoes | `send_notification_task`, `send_bulk_notifications_task` |

---

## Licenca

MIT. Veja [LICENSE](LICENSE) para detalhes.
