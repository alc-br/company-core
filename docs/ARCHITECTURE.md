# Company Core — Arquitetura Técnica

> **Versão**: 1.0.0
> **Data**: 2026-07-28
> **Autor**: Staff+ Software Architect
> **Status**: Aprovado para implementação

---

## 1. Visão Geral da Arquitetura

A arquitetura do Company Core segue o princípio de **camadas concêntricas**, onde cada camada tem uma responsabilidade bem definida e depende apenas das camadas inferiores. A plataforma é construída sobre o SaaS Pegasus, que atua como a fundação, e o Company Core atua como uma camada de infraestrutura compartilhada que habilita a criação rápida de novos produtos SaaS.

O modelo de três camadas garante que cada novo produto SaaS precise conter apenas sua lógica de domínio específica, enquanto toda a infraestrutura comum (autenticação, billing, IA, multi-tenancy, etc.) permanece centralizada e reutilizável no Company Core.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE PRODUTO                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Video KG │ │ AI SEO   │ │ AI CRM   │ │ Legal AI │  ...      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                      apps/<product_name>/                       │
├─────────────────────────────────────────────────────────────────┤
│                 CAMADA COMPANY CORE                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │ Billing  │ │   AI    │ │  Auth   │ │ Storage  │              │
│  │ Quotas   │ │ Agents  │ │ Orgs    │ │ Webhooks │              │
│  │ Audit    │ │ Workflo │ │ Perms   │ │ API      │              │
│  │ Analytics│ │ Notif.  │ │ Search  │ │ Health   │              │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
│                    apps/<core_module>/                           │
├─────────────────────────────────────────────────────────────────┤
│               CAMADA SAAS PEGASUS                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐      │
│  │ Django │ │ allauth│ │ Celery │ │  DRF   │ │Waffle  │      │
│  │ ORM    │ │ Auth   │ │ Tasks  │ │OpenAPI │ │FFlags  │      │
│  │ HTMX   │ │Tailwind│ │ Docker │ │  Vite  │ │  CI    │      │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘      │
│              SaaS Pegasus Foundation                           │
└─────────────────────────────────────────────────────────────────┘
```

### Princípios Arquiteturais

1. **Reutilização máxima**: Nunca substituir funcionalidades do Pegasus quando existir um mecanismo oficial de extensão.
2. **Desacoplamento**: Cada app Django é totalmente independente e plugável.
3. **Extensibilidade**: Todo módulo é projetado para ser estendido sem modificação.
4. **Isolamento de inquilinos**: Garantia de isolamento absoluto de dados entre tenants (multi-tenancy).
5. **Clean Architecture**: Separação clara entre domínio, infraestrutura e apresentação.

---

## 2. Arquitetura de Camadas

### 2.1 Camada 0 — Fundação SaaS Pegasus

Esta camada fornece a fundação técnica sobre a qual todo o sistema é construído. Nenhuma modificação é permitida nesta camada; toda integração ocorre por meio de mecanismos oficiais de extensão (INSTALLED_APPS, settings overrides, herança de templates, signals).

**Componentes fornecidos:**
- **Django 6 + Python 3.14**: Framework web, ORM, sistema de migrações
- **allauth**: Autenticação (email-as-username, magic links, captcha)
- **Celery + Redis**: Processamento assíncrono com agendamento
- **DRF + drf-spectacular**: API REST com documentação OpenAPI
- **django-waffle**: Feature flags por usuário e por time
- **HTMX + Alpine.js + Tailwind v4 + DaisyUI**: Frontend server-rendered
- **Docker (Postgres 17 + Redis)**: Infraestrutura de desenvolvimento
- **GitHub Actions CI/CD**: Pipeline de integração contínua
- **ruff + mypy**: Linting e type checking
- **CustomUser(AbstractUser)**: Modelo de usuário base
- **BaseModel**: Modelo abstrato com timestamps

### 2.2 Camada 1 — Infraestrutura Compartilhada (Company Core)

Contém todos os módulos de infraestrutura que são compartilhados entre produtos. Esta camada é o coração do Company Core e implementa toda a lógica transversal que qualquer produto SaaS precisaria.

**Módulos agrupados por domínio:**

| Domínio | Módulos | Responsabilidade |
|---------|---------|-----------------|
| Identidade | organizations, permissions, settings | Multi-tenancy, RBAC, configurações dinâmicas |
| Monetização | billing, quotas, feature_flags | Stripe, assinaturas, limites, funcionalidades |
| Inteligência | ai, agents | Abstração IA, framework de agentes |
| Comunicação | notifications, webhooks, integrations | Email, Slack, Discord, webhooks universais |
| Observabilidade | audit, analytics, usage | Rastreio, métricas, consumo |
| Processamento | workflows, jobs | Motor de workflows, filas Celery |
| Infraestrutura | storage, api, sdk, health, search | S3, REST, SDK interno, health checks |
| Fundação | common, core | Utilitários, configurações base |

### 2.3 Camada 2 — Produto (Extensão)

Cada produto SaaS é um app Django independente que:
- Herda toda infraestrutura do Company Core
- Contém apenas lógica de domínio específica
- Se registra via INSTALLED_APPS
- Usa services/selectors compartilhados
- Configura seus próprios models, views e templates

---

## 3. Padrões Arquiteturais

### 3.1 Service Layer Pattern

Toda lógica de negócio reside em classes de serviço. Views nunca contêm regra de negócio; Models nunca contêm lógica pesada. Services são a camada que orquestra operações de domínio.

```python
# apps/billing/services.py

from typing import Optional
from django.db import transaction
from apps.billing.models import Subscription, Plan
from apps.organizations.selectors import get_organization_by_id
from apps.audit.services import create_audit_log


class BillingService:
    """Serviço responsável por operações de billing."""

    @staticmethod
    @transaction.atomic
    def create_subscription(
        organization_id: int,
        plan_id: str,
        stripe_customer_id: str,
    ) -> Subscription:
        """Cria uma nova assinatura para uma organização."""
        organization = get_organization_by_id(organization_id)
        plan = Plan.objects.get(stripe_price_id=plan_id)

        subscription = Subscription.objects.create(
            organization=organization,
            plan=plan,
            stripe_customer_id=stripe_customer_id,
            status=Subscription.Status.ACTIVE,
        )

        create_audit_log(
            action="subscription.created",
            actor=organization.owner,
            target=subscription,
            metadata={"plan_id": plan_id},
        )

        return subscription

    @staticmethod
    def check_quota(
        organization_id: int,
        quota_code: str,
        increment: int = 1,
    ) -> bool:
        """Verifica se a organização possui quota disponível."""
        subscription = BillingService.get_active_subscription(organization_id)
        if not subscription:
            return False

        return subscription.plan.has_quota(quota_code, increment)
```

**Regras do Service Layer:**
- Cada service é uma classe com métodos estáticos ou uma instância singleton
- Services orquestram operações entre models, selectors e outros services
- Services gerenciam transações de banco de dados
- Services emitem signals para desacoplar efeitos colaterais
- Services nunca retornam objetos HTTP (Request/Response); isso é responsabilidade da view

### 3.2 Selector Layer Pattern

Toda consulta complexa ao banco de dados reside em selectors. Selectors são funções puras que recebem parâmetros e retornam QuerySets ou instâncias de models.

```python
# apps/organizations/selectors.py

from typing import Optional
from django.db.models import QuerySet
from apps.organizations.models import Organization, Membership


def get_organization_by_id(
    organization_id: int,
    *,
    select_related: tuple[str, ...] = ("owner",),
    prefetch_related: tuple[str, ...] = ("members",),
) -> Organization:
    """Retorna uma organização pelo ID com otimizações de queryset."""
    return Organization.objects\
        .select_related(*select_related)\
        .prefetch_related(*prefetch_related)\
        .get(id=organization_id)


def get_user_organizations(
    user_id: int,
    *,
    role: Optional[str] = None,
    status: Optional[str] = Membership.Status.ACTIVE,
) -> QuerySet[Organization]:
    """Retorna todas as organizações de um usuário com filtro opcional."""
    queryset = Organization.objects.filter(
        memberships__user_id=user_id,
        memberships__status=status,
    )

    if role:
        queryset = queryset.filter(memberships__role=role)

    return queryset.distinct()


def get_organization_members(
    organization_id: int,
    *,
    role: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> QuerySet[Membership]:
    """Retorna membros de uma organização com paginação e filtro."""
    queryset = Membership.objects.filter(
        organization_id=organization_id,
        status=Membership.Status.ACTIVE,
    ).select_related("user", "invited_by")

    if role:
        queryset = queryset.filter(role=role)

    return queryset[offset:offset + limit]
```

**Regras do Selector Layer:**
- Selectors são funções puras (sem efeitos colaterais)
- Selectors nunca modificam dados (apenas leitura)
- Selectors sempre recebem parâmetros tipados
- Selectors usam select_related/prefetch_related para otimização
- Selectors suportam paginação via parâmetros limit/offset

### 3.3 Strategy Pattern — Provedores de IA

```python
# apps/ai/providers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Optional


@dataclass
class AIMessage:
    role: str  # "system", "user", "assistant"
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class AIResponse:
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: dict = field(default_factory=dict)


class AIProvider(ABC):
    """Interface base para provedores de IA."""

    name: str
    models: list[str]

    @abstractmethod
    async def complete(
        self,
        messages: list[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AIResponse:
        """Executa uma chamada de completude síncrona."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[AIMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Executa uma chamada de streaming."""
        ...

    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Conta tokens para o texto dado."""
        ...

    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Valida se a API key configurada é válida."""
        ...
```

### 3.4 Observer Pattern — Signals

```python
# apps/billing/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.billing.models import Subscription
from apps.quotas.services import initialize_quotas
from apps.notifications.services import send_notification


@receiver(post_save, sender=Subscription)
def on_subscription_created(sender, instance, created, **kwargs):
    """Quando uma assinatura é criada, inicializa quotas e notifica."""
    if created:
        initialize_quotas(
            organization_id=instance.organization_id,
            plan_id=instance.plan_id,
        )
        send_notification(
            channel="email",
            recipient=instance.organization.owner.email,
            template="billing.subscription_created",
            context={"plan": instance.plan.name},
        )
```

### 3.5 Factory Pattern — Criação de Agentes

```python
# apps/agents/factories.py

from apps.agents.models import Agent, AgentTool
from apps.ai.services import get_provider


class AgentFactory:
    """Fábrica para criação e configuração de agentes de IA."""

    @staticmethod
    def create_agent(
        name: str,
        description: str,
        model: str,
        system_prompt: str,
        temperature: float = 0.7,
        tools: list[str] = None,
        organization_id: int = None,
        **kwargs,
    ) -> Agent:
        """Cria um novo agente com configuração completa."""
        agent = Agent.objects.create(
            name=name,
            description=description,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            organization_id=organization_id,
            **kwargs,
        )

        if tools:
            agent_tools = AgentTool.objects.filter(code__in=tools)
            agent.tools.set(agent_tools)

        return agent

    @staticmethod
    def get_executable_agent(agent: Agent):
        """Retorna um agente pronto para execução com provider configurado."""
        provider = get_provider(agent.provider)
        return ExecutableAgent(agent=agent, provider=provider)
```

### 3.6 Adapter Pattern — Armazenamento

```python
# apps/storage/adapters/base.py

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from dataclasses import dataclass


@dataclass
class StorageObject:
    key: str
    url: str
    size: int
    content_type: str
    metadata: dict


class StorageBackend(ABC):
    """Interface base para backends de armazenamento."""

    name: str

    @abstractmethod
    def upload(self, key: str, data: BinaryIO, content_type: str = None,
               metadata: dict = None) -> StorageObject:
        """Faz upload de um arquivo."""
        ...

    @abstractmethod
    def download(self, key: str) -> BinaryIO:
        """Faz download de um arquivo."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Deleta um arquivo."""
        ...

    @abstractmethod
    def get_url(self, key: str, expires_in: int = 3600) -> str:
        """Gera uma URL assinada temporária."""
        ...

    @abstractmethod
    def list_objects(self, prefix: str = "") -> list[StorageObject]:
        """Lista objetos com determinado prefixo."""
        ...
```

---

## 4. Arquitetura dos Apps

### 4.1 core — Configurações Compartilhadas

- **Responsabilidade**: Ponto central de configuração do Company Core
- **Modelos**: Nenhum (apenas configurações)
- **Serviços**: `get_setting(tenant, key, default)`, `set_setting(tenant, key, value)`
- **Dependências**: Nenhuma (módulo base)

### 4.2 common — Utilitários Reutilizáveis

- **Responsabilidade**: Funções, mixins, helpers, exceptions e utilities compartilhadas
- **Modelos**: Nenhum
- **Componentes-chave**:
  - `TenantMixin` — Mixin para models com escopo de tenant
  - `TimestampMixin` — Herdado do BaseModel do Pegasus
  - `ServiceException` — Hierarquia de exceptions de negócio
  - `PaginationHelper` — Helpers de paginação
  - `ValidationHelper` — Validações comuns
- **Dependências**: Nenhuma (módulo base)

### 4.3 settings — Configurações Dinâmicas

- **Responsabilidade**: Configurações dinâmicas por tenant e ambiente
- **Modelos**: `TenantSetting(key, value, tenant, environment)`
- **Serviços**: `get_tenant_setting()`, `set_tenant_setting()`, `get_global_setting()`
- **Dependências**: organizations

### 4.4 organizations — Multi-Tenancy

- **Responsabilidade**: Gerenciamento de organizações, times, convites e membros
- **Modelos**:
  - `Organization(name, slug, owner, status, metadata)`
  - `Membership(user, organization, role, status, invited_by)`
  - `Invitation(email, organization, role, token, accepted_at)`
- **Serviços**: `create_organization()`, `invite_member()`, `accept_invitation()`, `remove_member()`
- **Selectors**: `get_user_organizations()`, `get_org_members()`, `get_org_by_slug()`
- **Signals**: `organization_created`, `member_added`, `member_removed`
- **Dependências**: common, core

### 4.5 permissions — RBAC

- **Responsabilidade**: Sistema de controle de acesso baseado em papéis
- **Modelos**:
  - `Role(name, organization, permissions)`
  - `Permission(code, name, description, module)`
  - `RolePermission(role, permission)`
- **Serviços**: `assign_role()`, `check_permission()`, `create_role()`
- **Selectors**: `get_user_permissions()`, `get_role_permissions()`
- **Dependências**: organizations, common

### 4.6 billing — Stripe Billing

- **Responsabilidade**: Gestão de planos, assinaturas, pagamentos e consumo via Stripe
- **Modelos**:
  - `Plan(name, stripe_price_id, features, limits, is_active)`
  - `Subscription(organization, plan, stripe_subscription_id, status, current_period_start, current_period_end)`
  - `PaymentAttempt(subscription, amount, status, stripe_payment_intent_id)`
- **Serviços**: `create_subscription()`, `cancel_subscription()`, `upgrade_plan()`, `handle_webhook()`
- **Tasks**: `sync_stripe_products`, `process_retry_payment`
- **Dependências**: organizations, quotas, feature_flags, audit

### 4.7 quotas — Sistema de Quotas

- **Responsabilidade**: Gestão configurável de quotas por tenant (vídeos, prompts, GB, etc.)
- **Modelos**:
  - `QuotaDefinition(code, name, unit, default_limit, description)`
  - `QuotaAllocation(organization, definition, limit, used, period)`
- **Serviços**: `check_quota()`, `increment_usage()`, `reset_quotas()`, `get_quota_status()`
- **Dependências**: organizations, billing

### 4.8 feature_flags — Funcionalidades

- **Responsabilidade**: Sistema de feature flags por plano, tenant, usuário e ambiente (extende django-waffle)
- **Modelos**:
  - `FeatureFlag(code, name, description, is_active)`
  - `FeatureFlagAssignment(flag, organization, user, environment, is_active)`
- **Serviços**: `is_feature_enabled()`, `enable_feature()`, `disable_feature()`
- **Dependências**: organizations, billing

### 4.9 ai — Provedores de IA

- **Responsabilidade**: Abstração única para múltiplos provedores de IA
- **Modelos**:
  - `AIProviderConfig(provider_name, api_key_ref, models, is_default, organization)`
  - `AIModelConfig(model_id, display_name, provider, max_tokens, cost_per_token)`
  - `AICallLog(organization, model, tokens_input, tokens_output, cost, latency_ms)`
- **Provedores implementados**: `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`
- **Serviços**: `get_provider()`, `call_ai()`, `stream_ai()`, `log_ai_call()`
- **Dependências**: organizations, usage, audit

### 4.10 agents — Framework de Agentes

- **Responsabilidade**: Framework para criação e execução de agentes de IA
- **Modelos**:
  - `Agent(name, description, system_prompt, model, temperature, memory_config, organization)`
  - `AgentTool(name, code, description, handler_path)`
  - `AgentExecution(agent, status, input, output, tokens_used, duration_ms)`
- **Serviços**: `create_agent()`, `execute_agent()`, `get_agent_response()`
- **Dependências**: ai, organizations, usage, audit

### 4.11 notifications — Notificações

- **Responsabilidade**: Sistema extensível de notificações (email, webhook, Slack, Discord)
- **Modelos**:
  - `NotificationTemplate(code, subject, body_html, body_text, channel)`
  - `NotificationLog(recipient, template, channel, status, sent_at)`
  - `NotificationChannel(type, name, config, organization)`
- **Serviços**: `send_notification()`, `register_channel()`, `render_template()`
- **Dependências**: organizations, common

### 4.12 integrations — Integrações

- **Responsabilidade**: Framework para integrações com serviços externos
- **Modelos**:
  - `Integration(name, type, credentials_encrypted, status, organization)`
  - `IntegrationLog(integration, action, request, response, status, duration_ms)`
- **Serviços**: `create_integration()`, `call_integration()`, `health_check()`
- **Dependências**: organizations, storage, audit

### 4.13 audit — Auditoria

- **Responsabilidade**: Registro completo de ações (login, CRUD, billing, IA, webhooks, API)
- **Modelos**:
  - `AuditLog(actor, action, target_type, target_id, ip_address, user_agent, metadata)`
- **Selectors**: `get_audit_logs()`, `get_entity_history()`, `get_user_activity()`
- **Serviços**: `create_audit_log()`, `export_audit_logs()`
- **Dependências**: organizations, common

### 4.14 analytics — Análise de Uso

- **Responsabilidade**: Dashboard de uso por tenant, usuário, módulo, consumo IA e storage
- **Modelos**:
  - `AnalyticsEvent(tenant, user, event_type, module, metadata, timestamp)`
  - `AnalyticsAggregation(tenant, period, module, metric, value)`
- **Serviços**: `track_event()`, `get_tenant_analytics()`, `get_module_usage()`
- **Dependências**: usage, organizations, ai

### 4.15 usage — Métricas de Uso

- **Responsabilidade**: Centralização de métricas (tokens, requests, arquivos, uploads, downloads)
- **Modelos**:
  - `UsageRecord(tenant, user, metric_type, value, unit, period, metadata)`
  - `UsageAggregation(tenant, metric_type, period, total)`
- **Serviços**: `record_usage()`, `get_usage()`, `get_usage_summary()`
- **Dependências**: organizations, common

### 4.16 storage — Armazenamento

- **Responsabilidade**: Abstração de armazenamento (S3, MinIO, Cloudflare R2, local)
- **Modelos**:
  - `StorageBackendConfig(name, type, config_encrypted, is_default, organization)`
  - `StoredObject(key, bucket, size, content_type, checksum, uploaded_by, organization)`
- **Serviços**: `upload_file()`, `download_file()`, `delete_file()`, `get_signed_url()`
- **Dependências**: organizations, usage, audit

### 4.17 api — Framework REST

- **Responsabilidade**: API REST versionada com API Keys, rate limiting e OpenAPI
- **Modelos**:
  - `APIKey(name, key_hash, user, organization, scopes, is_active, last_used_at, expires_at)`
  - `PersonalAccessToken(name, token_hash, user, scopes, expires_at)`
  - `ServiceAccount(name, token_hash, organization, permissions)`
- **Serviços**: `create_api_key()`, `validate_api_key()`, `check_rate_limit()`
- **Dependências**: organizations, permissions, usage, audit

### 4.18 webhooks — Webhooks Universais

- **Responsabilidade**: Sistema de webhooks de entrada e saída com retry e assinaturas
- **Modelos**:
  - `WebhookEndpoint(url, secret, events, organization, is_active)`
  - `WebhookDelivery(endpoint, event, payload, status, attempts, response_code)`
  - `WebhookEvent(type, data, timestamp)`
- **Serviços**: `register_webhook()`, `deliver_webhook()`, `process_incoming()`, `verify_signature()`
- **Tasks**: `deliver_webhooks_task`, `retry_failed_webhooks`
- **Dependências**: organizations, audit, jobs

### 4.19 workflows — Motor de Workflows

- **Responsabilidade**: Motor de workflows com pipeline, etapas, execução e retry
- **Modelos**:
  - `Workflow(name, description, steps_config, organization)`
  - `WorkflowExecution(workflow, status, current_step, input_data, output_data)`
  - `WorkflowStepLog(execution, step, status, input, output, error, duration_ms)`
- **Serviços**: `create_workflow()`, `execute_workflow()`, `resume_workflow()`
- **Dependências**: jobs, organizations, audit

### 4.20 jobs — Gerenciamento de Filas

- **Responsabilidade**: Gestão de filas Celery com retry, dead letter e prioridades
- **Modelos**:
  - `Job(name, task_path, status, priority, retries, max_retries, last_error, organization)`
- **Serviços**: `enqueue_job()`, `retry_job()`, `get_queue_status()`, `purge_dead_letter()`
- **Dependências**: common, organizations

### 4.21 sdk — SDK Interno

- **Responsabilidade**: SDK interno para facilitar comunicação entre módulos
- **Componentes**:
  - `BillingSDK` — Interface simplificada para operações de billing
  - `QuotaSDK` — Interface simplificada para verificação de quotas
  - `AISDK` — Interface simplificada para chamadas de IA
  - `StorageSDK` — Interface simplificada para upload/download
  - `NotificationSDK` — Interface simplificada para envio de notificações
- **Dependências**: billing, quotas, ai, storage, notifications

### 4.22 health — Health Checks

- **Responsabilidade**: Endpoints de verificação de saúde do sistema
- **Endpoints**: `/health` (básico), `/ready` (dependências), `/live` (liveness probe)
- **Serviços**: `check_database()`, `check_redis()`, `check_storage()`, `check_ai_providers()`
- **Dependências**: storage, ai, jobs

### 4.23 search — Busca

- **Responsabilidade**: Funcionalidade de busca全文 com suporte a múltiplos backends
- **Modelos**: `SearchIndex(content_type, object_id, content, metadata)`
- **Serviços**: `index_object()`, `search()`, `remove_index()`
- **Dependências**: organizations, common

### 4.24 admin — Painéis Administrativos

- **Responsabilidade**: Extensão do Django Admin com painéis para billing, uso, filas, IA, health
- **Componentes**: `BillingAdmin`, `QuotaAdmin`, `AIAdmin`, `QueueAdmin`, `HealthAdmin`
- **Dependências**: billing, quotas, ai, jobs, health, analytics

---

## 5. Multi-Tenancy

### Modelo de Isolamento

O Company Core utiliza **isolamento lógico por tenant** (shared database, isolated rows). Cada organização é um tenant e todas as operações são automaticamente filtradas pelo tenant ativo.

```python
# apps/common/mixins.py

class TenantMixin(models.Model):
    """Mixin que adiciona escopo de tenant a qualquer modelo."""
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True

    objects = TenantManager()
```

### Tenant Middleware

```python
# apps/organizations/middleware.py

class TenantMiddleware:
    """Middleware que injeta o tenant ativo na request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Tenta determinar o tenant ativo
            org_id = request.session.get("active_organization_id")
            if org_id:
                try:
                    request.tenant = Organization.objects.get(
                        id=org_id,
                        memberships__user=request.user,
                    )
                except Organization.DoesNotExist:
                    request.tenant = None
            else:
                # Usa a primeira organização do usuário
                first_org = Organization.objects.filter(
                    memberships__user=request.user,
                ).first()
                request.tenant = first_org
        else:
            request.tenant = None

        return self.get_response(request)
```

### Tenant Manager

```python
# apps/common/managers.py

class TenantManager(models.Manager):
    """Manager que automaticamente filtra por tenant ativo."""

    def get_queryset(self):
        queryset = super().get_queryset()
        # Se houver tenant ativo no contexto, filtra automaticamente
        tenant = get_current_tenant()
        if tenant:
            queryset = queryset.filter(organization=tenant)
        return queryset
```

---

## 6. API Design

### Versionamento

A API segue versionamento por URL path: `/api/v1/`, `/api/v2/`. Cada versão é um módulo Django separado.

```python
# project/urls.py

urlpatterns = [
    path("api/v1/", include("apps.api.v1.urls")),
    path("api/v2/", include("apps.api.v2.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema")),
]
```

### Autenticação API Key

```python
# apps/api/authentication.py

class APIKeyAuthentication(BaseAuthentication):
    """Autenticação via API Key para acesso programático."""

    def authenticate(self, request):
        api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not api_key:
            return None

        try:
            key_obj = APIKey.objects.select_related("user", "organization")\
                .get(key_hash=hash_api_key(api_key), is_active=True)

            if key_obj.expires_at and key_obj.expires_at < timezone.now():
                raise AuthenticationFailed("API key expired")

            key_obj.last_used_at = timezone.now()
            key_obj.save(update_fields=["last_used_at"])

            return (key_obj.user, {"organization": key_obj.organization, "api_key": key_obj})
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")
```

### Rate Limiting

```python
# apps/api/throttling.py

class TenantRateThrottle(BaseThrottle):
    """Rate limiting por tenant baseado em plano."""

    def allow_request(self, request, view):
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return True

        plan = get_tenant_plan(tenant.id)
        rate_limit = plan.api_rate_limit  # Ex: "1000/hour"

        key = f"tenant:{tenant.id}"
        if not self.cache.get(key):
            self.cache.set(key, plan.api_requests_per_hour, 3600)

        return self.cache.incr(key) <= plan.api_requests_per_hour
```

### Padrão de Resposta

```python
# apps/api/paginaton.py

class StandardizedResponse(Pagination):
    """Resposta padronizada com metadados."""

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "data": data,
            "pagination": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "total_pages": self.page.paginator.num_pages,
            },
        })
```

---

## 7. Padrão de App (Template)

Cada app segue exatamente esta estrutura:

```
apps/<app_name>/
    __init__.py
    models.py            # Modelos de dados
    views.py            # Views (HTMX e/ou DRF)
    services.py         # Lógica de negócio (Service Layer)
    selectors.py        # Consultas complexas (Selector Layer)
    tasks.py            # Tarefas Celery
    signals.py          # Signals Django
    serializers.py      # Serializadores DRF
    urls.py             # Rotas da app
    admin.py            # Configuração do Django Admin
    apps.py             # App config
    migrations/
        __init__.py
    tests/
        __init__.py
        test_models.py
        test_services.py
        test_views.py
        test_selectors.py
        test_tasks.py
        test_api.py
        factories.py    # Factories para testes
    README.md           # Documentação do módulo
```

---

## 8. Configurações

### Hierarquia de Settings

```
pegasus settings.py (base)
    └── company_core.settings.base (extensões Company Core)
        ├── company_core.settings.development
        ├── company_core.settings.staging
        └── company_core.settings.production
            └── .env (variáveis de ambiente por ambiente)
```

### Configuração Dinâmica por Tenant

```python
# apps/settings/services.py

class SettingsService:
    """Serviço para configurações dinâmicas."""

    @staticmethod
    def get(tenant, key: str, default=None):
        """Obtém uma configuração por tenant."""
        cache_key = f"settings:{tenant.id}:{key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            setting = TenantSetting.objects.get(
                organization=tenant, key=key,
            )
            result = setting.value
        except TenantSetting.DoesNotExist:
            result = default

        cache.set(cache_key, result, timeout=300)
        return result

    @staticmethod
    def set(tenant, key: str, value: str):
        """Define uma configuração por tenant."""
        TenantSetting.objects.update_or_create(
            organization=tenant,
            key=key,
            defaults={"value": value},
        )
        cache.delete(f"settings:{tenant.id}:{key}")
```

---

## 9. Fluxo de Dados

### Ciclo de Vida de Requisição HTTP

```
Cliente → Nginx → Django WSGI/ASGI
    → TenantMiddleware (determina tenant)
    → AuthMiddleware (verifica autenticação)
    → RateLimitMiddleware (verifica limites)
    → View (HTMX ou DRF)
        → Service (lógica de negócio)
            → Selector (consulta de dados)
            → Model (ORM)
            → Signal (efeitos colaterais)
    → Response
    → AuditLog (registra ação)
    → UsageRecord (registra métrica)
→ Cliente
```

### Ciclo de Vida de Tarefa Celery

```
Evento → enqueue_job()
    → Celery Queue (por prioridade)
    → Worker executa tarefa
        → Service.process()
        → Result stored in Redis
    → On success:
        → Signal (task_completed)
        → Webhook delivery (se configurado)
        → Audit log
    → On failure:
        → Retry (com backoff exponencial)
        → Max retries → Dead Letter Queue
        → Notification (alerta)
```

### Fluxo de Chamada IA

```
Agent.execute(prompt)
    → AIService.get_provider(provider_name)
    → provider.complete(messages, model, temperature)
    → OpenAI/Anthropic/Gemini API call
    → AIResponse recebido
    → AICallLog (tokens, custo, latência)
    → UsageRecord.record("ai.tokens", token_count)
    → QuotaService.increment_usage(tenant, "ai_prompts")
    → Response retornada ao Agent
```

---

## 10. Segurança

### Autenticação

| Mecanismo | Uso | Implementação |
|-----------|-----|--------------|
| Session (Cookies) | Navegadores (HTMX) | Pegasus allauth |
| API Key | Acesso programático | Company Core API |
| Personal Access Token | CLI / Scripts | Company Core API |
| Service Account | Integrações sistema-a-sistema | Company Core API |

### RBAC (Controle de Acesso Baseado em Papéis)

```
Organization Owner (todas as permissões)
    └── Organization Admin (permissoes administrativas)
        └── Organization Member (permissoes de uso)
            └── Custom Roles (definidas pelo tenant)
```

### Isolamento de Dados

- **Row-Level Security**: Todos os models usam `TenantMixin` com `TenantManager`
- **Middleware enforcement**: `TenantMiddleware` garante que `request.tenant` está sempre presente
- **API enforcement**: Todas as APIs filtram por tenant automaticamente
- **Service enforcement**: Services recebem `organization_id` obrigatório
- **Test coverage**: Testes automatizados para vazamento cross-tenant

### Audit Trail

Todas as ações sensíveis são registradas:
- Login/Logout
- Criação/Alteração/Exclusão de qualquer recurso
- Chamadas de API (incluindo parâmetros)
- Chamadas IA (modelo, tokens, custo)
- Webhooks enviados/recebidos
- Alterações de billing (upgrade, downgrade, cancelamento)
- Alterações de permissões

---

## 11. Escalabilidade

### Estratégia de Filas Celery

```
default      → Tarefas gerais (baixa prioridade)
billing      → Tarefas de billing (média prioridade)
ai           → Tarefas de IA (alta prioridade)
webhooks     → Entrega de webhooks (média prioridade)
workflows    → Execução de workflows (alta prioridade)
analytics    → Agregação de métricas (baixa prioridade)
notifications → Envio de notificações (média prioridade)
```

### Estratégia de Cache

```
Redis Cache Layers:
    L1: Query cache (selectors, 5 min TTL)
    L2: Settings cache (tenant settings, 5 min TTL)
    L3: Feature flags cache (1 min TTL)
    L4: Quota cache (real-time, 30 sec TTL)
```

### Estratégia de Armazenamento

```
Storage Tiers:
    Hot (S3/R2): Arquivos ativos (últimos 30 dias)
    Warm (S3 Glacier): Arquivos antigos (30+ dias)
    Cold: Arquivos deletados (retenção 30 dias antes de purge)
```

---

## 12. Diagramas

### Visão Geral do Sistema

```
                        ┌─────────────┐
                        │   Cliente    │
                        │ (Browser/CLI)│
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │    Nginx     │
                        │ (Reverse    │
                        │  Proxy + SSL│
                        └──────┬──────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
       ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
       │  Django     │ │   Celery   │ │  Celery     │
       │  (WSGI/ASGI)│ │  Worker 1  │ │  Worker N   │
       └──────┬──────┘ └─────┬──────┘ └──────┬──────┘
              │              │               │
       ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
       │ PostgreSQL  │ │  Redis   │ │   S3/R2     │
       │  (Dados)   │ │(Cache/   │ │ (Storage)   │
       │            │ │ Broker)  │ │             │
       └────────────┘ └──────────┘ └─────────────┘
              │              │               │
       ┌──────▼──────────────▼───────────────▼──┐
       │        Serviços Externos                │
       │ Stripe │ OpenAI │ Anthropic │ Gemini    │
       │ SMTP   │ Slack  │ Discord  │ Webhooks  │
       └────────────────────────────────────────┘
```

### Fluxo Multi-Tenancy

```
Request → TenantMiddleware
              │
              ├─ Request.User autenticado?
              │    │
              │    ├─ Sim → Busca tenant ativo
              │    │         ├─ Session tem active_organization_id?
              │    │         │    ├─ Sim → request.tenant = org
              │    │         │    └─ Não → primeira org do user
              │    │         └─ Salva na request
              │    │
              │    └─ Não → request.tenant = None
              │
              └─ View usa request.tenant para filtro
                   Service usa organization_id para operações
                   Selector usa TenantManager para consultas
```

---

## Anexo: Glossário

| Termo | Definição |
|-------|----------|
| **Tenant** | Organização/cliente no modelo multi-tenant |
| **Service Layer** | Camada de serviços onde reside toda lógica de negócio |
| **Selector Layer** | Camada de consultas otimizadas para o banco de dados |
| **Pegasus** | SaaS Pegasus — boilerplate Django utilizado como fundação |
| **Quota** | Limite configurável de uso por tenant |
| **Feature Flag** | Flag para habilitar/desabilitar funcionalidades |
| **Provider** | Provedor de IA (OpenAI, Anthropic, Gemini) |
| **Agent** | Instância configurável de IA com ferramentas e memória |
| **Webhook** | Callback HTTP para notificação de eventos |
| **Dead Letter Queue** | Fila para tarefas com falha permanente |
