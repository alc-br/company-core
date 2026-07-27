# Plano de Reutilização do SaaS Pegasus — Company Core

> **Documento de Arquitetura — Nível Staff+**  
> **Versão:** 1.0  
> **Data:** 2025  
> **Classificação:** Interno — Equipe de Engenharia

---

## 1. Visão Geral

O **Company Core** é a plataforma central que serve como fundação para todos os produtos SaaS da empresa. Em vez de construir do zero toda a infraestrutura de autenticação, UI, tarefas assíncronas, documentação de API e CI/CD, a equipe tomou a decisão arquitetural de adotar o **SaaS Pegasus** como base geradora do projeto.

O SaaS Pegasus é um starter kit open source para Django que fornece uma fundação sólida e bem testada para aplicações SaaS. A edição open source oferece três apps (users, web, utils), um modelo de usuário customizado (`CustomUser` estendendo `AbstractUser`), um `BaseModel` com timestamps automáticos, autenticação completa via django-allauth (incluindo e-mail como username, magic links e captcha), infraestrutura de Celery com Redis, DRF com OpenAPI, feature flags com Waffle, stack frontend com HTMX + Alpine.js + Tailwind v4 + DaisyUI, Docker com Postgres 17 e Redis, CI com GitHub Actions, e ferramentas de qualidade com ruff e mypy.

A relação entre Company Core e SaaS Pegasus é de **herança controlada com extensão massiva**. O Pegasus fornece o esqueleto e a fundação; o Company Core adiciona 23 módulos próprios que formam o verdadeiro valor de negócio da plataforma. A edição Pro do Pegasus oferece funcionalidades como Teams (multi-tenancy), Stripe billing, AI chat/agents, social login, 2FA, API keys e impersonation — porém, por decisão estratégica de controle total e customização profunda, implementaremos nossas próprias versões dessas funcionalidades como parte do Company Core.

É fundamental entender que o Pegasus **não utiliza camada de serviço nem padrão selector**. Ele segue a filosofia Django clássica de "fat models, thin views" com signals para lógica transversal. Respeitaremos essa convenção no código herdado do Pegasus, embora o Company Core possa adotar padrões adicionais em seus próprios módulos quando justificado pela complexidade.

A configuração do projeto utiliza `django-environ` para leitura de variáveis de ambiente a partir de arquivos `.env`, e o Celery emprega `django-celery-beat` como scheduler e `celery-progress` para acompanhamento de tarefas. Essas decisões técnicas do Pegasus serão mantidas e estendidas.

---

## 2. Componentes do Pegasus que SERÃO REUTILIZADOS (sem modificação)

Estes componentes serão utilizados exatamente como fornecidos pelo SaaS Pegasus (edição open source). Qualquer necessidade de customização será feita por meio de extensão, sobrescrita em settings ou criação de módulos paralelos no Company Core — **nunca** modificando o código fonte original do Pegasus.

### 2.1 Estrutura do Projeto e Sistema de Settings

A estrutura de diretórios gerada pelo Pegasus — incluindo a separação entre apps, configurações por ambiente (development, production, testing), e o sistema de `django-environ` para leitura do `.env` — será adotada integralmente. Isso nos dá imediatamente um projeto Django bem organizado com suporte a múltiplos ambientes sem esforço adicional. O padrão de arquivos `settings/base.py`, `settings/development.py`, `settings/production.py` e `settings/test.py` é suficiente para nossas necessidades atuais. O sistema de settings do Pegasus já inclui configurações sensatas para logging, middleware, static files e segurança que atendem aos requisitos de uma aplicação SaaS em produção.

### 2.2 CustomUser + BaseModel

O modelo `CustomUser` que estende `AbstractUser` do Django será utilizado como base para o sistema de usuários. Ele já inclui campos essenciais como e-mail (usado como username), e integra-se nativamente com o django-allauth. O `BaseModel` com campos `created_at` e `updated_at` (timestamps automáticos via `auto_now_add` e `auto_now`) servirá como classe abstrata para todos os modelos do Company Core, garantindo consistência na rastreabilidade temporal de registros em todo o sistema.

### 2.3 Sistema de Autenticação (django-allauth)

Toda a infraestrutura de autenticação fornecida pelo django-allauth será reaproveitada: fluxo de login/logout, registro de novos usuários, reset de senha, confirmação por e-mail, e-mail como identificador principal (email-as-username), magic links para login sem senha, e integração com captcha para proteção contra bots. Essa é uma das maiores economias do projeto, pois autenticação é uma das funcionalidades mais complexas e sensíveis à segurança em qualquer aplicação SaaS.

### 2.4 Infraestrutura Celery

A configuração completa do Celery com Redis como broker e result backend será reaproveitada. Isso inclui o arquivo `celery_app.py` com as configurações de broker, serializer, resultado e rotas. O `django-celery-beat` para agendamento de tarefas periódicas via interface admin e o `celery-progress` para acompanhamento de progresso de tarefas longas na interface web também farão parte da base. Essa infraestrutura é essencial para os 23 módulos do Company Core que dependem de processamento assíncrono, como o engine de workflows, sistema de webhooks, tracking de uso e notificações.

### 2.5 DRF + OpenAPI

O Django REST Framework já configurado com geração automática de documentação OpenAPI (Swagger UI / ReDoc) será utilizado como base para todas as APIs do Company Core. O Pegasus já fornece uma configuração sensata de DRF com autenticação por sessão e token, paginação, filtering e parsing. Economizaremos semanas de configuração inicial ao reaproveitar essa fundação API.

### 2.6 Feature Flags (Waffle)

O Waffle será utilizado como base para o sistema de feature flags do Company Core. Suas três primitivas — Flags (feature toggles binários), Switches (flags por usuário) e Samples (rollout percentual) — cobrem a maioria dos casos de uso básicos. O Company Core estenderá essa funcionalidade com flags baseadas em plano (plan-based flags), mas a infraestrutura base do Waffle permanecerá intocada.

### 2.7 Templates HTMX + Tailwind v4 + DaisyUI

Todo o stack frontend do Pegasus — HTMX para interatividade server-driven, Alpine.js para estado no cliente, Tailwind CSS v4 para estilização utilitária e DaisyUI como biblioteca de componentes — será utilizado como base visual do Company Core. O Pegasus já fornece templates base (layout, navbar, footer, formulários, tabelas, modais) que seguem as melhores práticas de acessibilidade e responsividade. O Company Core adicionará seus próprios templates estendendo essa base.

### 2.8 Infraestrutura Docker

A configuração Docker do Pegasus com Postgres 17 e Redis será reaproveitada integralmente. Isso inclui o `Dockerfile` otimizado para desenvolvimento e produção, o `docker-compose.yml` com os serviços necessários, e os scripts de entrypoint. Essa infraestrutura já está otimizada para desenvolvimento local e deploy em produção, incluindo health checks e volume management adequados.

### 2.9 Pipeline CI (GitHub Actions)

Os workflows de CI do Pegasus — incluindo linting com ruff, type checking com mypy, execução de testes, e build de Docker image — serão utilizados como base. Esses workflows garantem que cada pull request passe por verificações automáticas de qualidade antes do merge, estabelecendo um padrão mínimo de qualidade desde o primeiro dia do projeto.

### 2.10 Makefile

O Makefile do Pegasus com comandos padronizados para operações comuns (setup, test, lint, migrate, manage, shell, etc.) será mantido e estendido com comandos específicos do Company Core. Isso padroniza a interface de linha de comando para todos os desenvolvedores da equipe, independentemente de sua familiaridade com Django.

---

## 3. Componentes do Pegasus que SERÃO ESTENDIDOS

Estes componentes do Pegasus servirão como base, mas receberão extensões significativas por parte do Company Core. A regra geral é: **extender por composição e herança, nunca por modificação direta do código do Pegasus**.

### 3.1 CustomUser — Extensões

O modelo `CustomUser` do Pegasus será estendido por meio de um modelo de perfil (`UserProfile`) vinculado por relação one-to-one, ou por herança de modelo, conforme avaliação técnica durante a implementação. As extensões planejadas incluem:

| Extensão | Descrição | Justificativa |
|----------|-----------|---------------|
| Contexto de tenant (organization) | Relação many-to-many com Organization | Necessário para multi-tenância |
| API Key support | Relação com modelo de API Keys | Controle de acesso programático |
| Papéis por organização | Relação com modelo de Role | Controle de acesso granular |
| Preferências de notificação | Campo JSON ou modelo relacionado | Personalização do usuário |
| Metadata extensível | Campo JSON genérico | Extensibilidade futura |

A decisão entre perfil one-to-one vs. herança será tomada na fase de design detalhado, considerando impacto em migrações, performance de queries e complexidade de serialização.

### 3.2 Settings — Extensões

O módulo de settings do Company Core (`companycore/settings/`) herdará toda a configuração base do Pegasus e adicionará:

- **Configurações específicas do Company Core**: chaves para Stripe, provedores de AI (OpenAI, Anthropic), serviços de e-mail transacional, armazenamento de objetos (S3/GCS), e integrações de terceiros.
- **Configurações de multi-tenancy**: middleware de tenant resolution, schema de isolamento (database-per-tenant vs. schema-per-tenant vs. row-level).
- **Configurações de quotas e billing**: limites padrão por plano, configuração de webhooks do Stripe, regras de grace period.
- **Configurações de AI**: modelos padrão, timeouts, rate limits por provedor, fallback chains.
- **Configurações de monitoramento**: Sentry DSN, DataDog API key, métricas customizadas.

A estratégia seguirá o padrão do Pegasus: variáveis de ambiente via `django-environ`, com valores padrão sensatos para desenvolvimento e obrigatoriedade em produção.

### 3.3 Templates — Extensão

Os templates base do Pegasus (`base.html`, `dashboard.html`, etc.) serão estendidos por meio de blocos Django template. O Company Core criará:

- **Layout principal do Company Core**: `companycore/base.html` que estende `base.html` do Pegasus, adicionando navegação contextual baseada no tenant ativo, seletor de organização, e barra de status de quota.
- **Templates de admin customizados**: painéis administrativos específicos para gestão de organizações, billing, e configurações de AI.
- **Componentes reutilizáveis**: cards de métricas, tabelas com exportação, formulários com validação client-side, modais de confirmação.

### 3.4 Celery — Extensão de Filas

Além da fila padrão do Celery fornecida pelo Pegasus, o Company Core definirá filas dedicadas para:

| Fila | Prioridade | Uso |
|------|-----------|-----|
| `default` | Normal | Tarefas gerais (herdada do Pegasus) |
| `ai` | Baixa | Chamadas a provedores de AI (long running) |
| `billing` | Alta | Processamento de pagamentos e webhooks Stripe |
| `notifications` | Média | Envio de e-mails, push notifications |
| `webhooks` | Média | Dispatch de webhooks para clientes |
| `workflows` | Baixa | Execução de steps de workflows |
| `analytics` | Baixa | Agregação e processamento de métricas |

### 3.5 Feature Flags — Extensão com Flags Baseadas em Plano

O Waffle fornece flags binárias, por usuário e por porcentagem. O Company Core estenderá esse sistema com:

- **Plan-based flags**: feature disponível apenas para determinados planos (Free, Pro, Enterprise).
- **Quota-based flags**: feature desabilitada automaticamente quando quota é atingida.
- **Tenant-scoped flags**: flags específicas por organização.
- **Flag dependency chains**: uma feature só pode ser ativada se sua dependência também estiver ativa.

A implementação será feita por meio de um middleware e um sistema de helpers que consultam tanto o Waffle quanto o contexto do tenant/plano do usuário.

### 3.6 DRF — Extensão com Versionamento, Rate Limiting e API Key Auth

O DRF base do Pegasus será estendido com:

- **Versionamento de API**: suporte a `/api/v1/`, `/api/v2/` com possibilidade de versões paralelas.
- **Rate limiting**: throttle classes baseadas em plano, por usuário e por API key.
- **Autenticação por API Key**: além de session e token, suporte a chaves de API para acesso programático.
- **Paginação customizada**: cursores otimizados para grandes datasets.
- **Serializers base**: serializers abstratos com campos padrão (id, created_at, updated_at, tenant).
- **Error handling padronizado**: response format consistente para erros de validação, permissão e rate limit.

---

## 4. Componentes que SERÃO IMPLEMENTADOS no Company Core

Estes são os 23 módulos que compõem o valor de negócio do Company Core. Cada um será implementado como um Django app independente dentro do projeto, seguindo as convenções do Pegasus quando aplicável e implementando padrões próprios quando a complexidade justificar.

### 4.1 Organizations (Multi-tenancy)

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.organizations` |
| **Propósito** | Gerenciamento de organizações (tenants) com isolamento completo de dados |
| **Justificativa** | O Pegasus Pro oferece Teams como recurso pago. Para controle total sobre a estratégia de multi-tenancy (row-level security, schema isolation, billing integration), construímos nosso próprio módulo. Isso permite evolução independente sem dependência de atualizações do Pegasus Pro. |
| **Modelos principais** | `Organization`, `OrganizationMember`, `OrganizationInvitation`, `Role`, `Permission` |
| **Funcionalidades** | CRUD de organizações, convites por e-mail, RBAC granular, transferência de propriedade, audit log de mudanças de membership |

### 4.2 API Keys / PAT / Service Accounts

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.apikeys` |
| **Propósito** | Gerenciamento de chaves de API, Personal Access Tokens e contas de serviço |
| **Justificativa** | APIs programáticas são essenciais para integrações e automação. O Pegasus Pro oferece API keys básicas, mas precisamos de granularidade maior: escopos por chave, rate limiting individual, expiração automática, rotacionamento forçado, e distinção entre PATs (usuário) e Service Accounts (organização). |
| **Modelos principais** | `APIKey`, `ServiceAccount`, `APIKeyScope`, `APIKeyUsageLog` |
| **Funcionalidades** | Geração segura com prefixo identificável, hash seguro no banco, scopes granulares, last used tracking, expiração e rotacionamento |

### 4.3 Billing (Integração com Stripe)

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.billing` |
| **Propósito** | Ciclo completo de cobrança via Stripe |
| **Justificativa** | Embora o Pegasus Pro utilize dj-stripe, construímos nossa própria camada de abstração para ter controle sobre a modelagem de dados, suportar modelos de precificação customizados (usage-based, tiered, per-seat), e integrar profundamente com o sistema de quotas e feature flags do Company Core. |
| **Modelos principais** | `Plan`, `Subscription`, `SubscriptionItem`, `Invoice`, `PaymentMethod`, `BillingEvent` |
| **Funcionalidades** | Gerenciamento de planos, checkout sessions, portal do cliente, webhooks do Stripe, prorationamento, grace period, dunning |

### 4.4 Sistema de Quotas

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.quotas` |
| **Propósito** | Limites de uso por organização/plano |
| **Justificativa** | Fundamental para monetização e proteção contra abuso. Cada funcionalidade do Company Core precisa de limites configuráveis: número de requisições API, armazenamento, execução de workflows, chamadas AI, etc. Este módulo fornece a infraestrutura unificada de quotas. |
| **Modelos principais** | `QuotaDefinition`, `QuotaUsage`, `QuotaLimit`, `QuotaAlert` |
| **Funcionalidades** | Definição de quotas por plano, tracking em tempo real, alertas de limite, bloqueio gracioso, relatórios de uso |

### 4.5 Feature Flags (Extensão do Waffle)

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.featureflags` |
| **Propósito** | Sistema avançado de feature flags estendendo o Waffle |
| **Justificativa** | O Waffle base atende casos simples, mas o Company Core precisa de flags baseadas em plano, quota e tenant. Este módulo cria uma camada de abstração sobre o Waffle sem modificá-lo. |
| **Modelos principais** | `FeatureFlag`, `FeatureFlagCondition`, `FeatureFlagUsage` |
| **Funcionalidades** | Flags por plano, dependência entre flags, rollout gradual, targeting por organização, integração com quotas |

### 4.6 Abstração de Provedores de AI

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.ai_providers` |
| **Propósito** | Camada de abstração para múltiplos provedores de IA |
| **Justificativa** | O Pegasus Pro oferece AI chat básico, mas o Company Core precisa de abstração multi-provedor (OpenAI, Anthropic, Google, provedores locais) com fallback automático, roteamento por custo/latência, e suporte a múltiplos modelos por provedor. |
| **Modelos principais** | `AIProvider`, `AIModel`, `AIProviderCredential`, `AIRequestLog` |
| **Funcionalidades** | Roteamento inteligente, fallback chains, caching de respostas, rate limiting por provedor, monitoring de custo e latência |

### 4.7 Framework de Agentes

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.agents` |
| **Propósito** | Criação e execução de agentes de IA |
| **Justificativa** | Agentes são o diferencial competitivo da plataforma. O Pegasus Pro tem AI chat, mas não um framework de agentes com tools, memory e multi-step reasoning. Construímos nosso próprio framework para suportar casos de uso avançados. |
| **Modelos principais** | `Agent`, `AgentTool`, `AgentExecution`, `AgentMemory`, `AgentRun` |
| **Funcionalidades** | Definição de agentes com system prompts, tools registáveis, execução assíncrona, memory persistente, streaming de respostas |

### 4.8 Biblioteca de Prompts

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.prompts` |
| **Propósito** | Gerenciamento centralizado de prompts de IA |
| **Justificativa** | Prompts são assets de alto valor que precisam de versionamento, A/B testing, controle de acesso e reutilização. Uma biblioteca centralizada evita duplicação e permite otimização contínua. |
| **Modelos principais** | `PromptTemplate`, `PromptVersion`, `PromptVariable`, `PromptExecution` |
| **Funcionalidades** | Versionamento de prompts, variáveis com validação, A/B testing, organização por categorias, approval workflow |

### 4.9 Engine de Workflows

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.workflows` |
| **Propósito** | Motor de execução de workflows definidos por usuário |
| **Justificativa** | Workflows permitem que clientes automatem processos complexos sem código. Não existe no Pegasus em nenhuma edição. Este é um dos módulos mais complexos e de maior valor do Company Core. |
| **Modelos principais** | `Workflow`, `WorkflowStep`, `WorkflowExecution`, `WorkflowStepExecution`, `WorkflowTrigger` |
| **Funcionalidades** | Editor visual (definição JSON), execução assíncrona com retry, branching condicional, loops, timeouts, sub-workflows |

### 4.10 Gerenciamento de Filas

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.queues` |
| **Propósito** | Monitoramento e gerenciamento das filas Celery |
| **Justificativa** | Com múltiplas filas dedicadas (ai, billing, notifications, webhooks, workflows, analytics), precisamos de visibilidade e controle sobre o estado das filas: depth, throughput, errors, dead letter queues. |
| **Modelos principais** | `QueueStatus`, `QueueEvent`, `DeadLetterEntry` |
| **Funcionalidades** | Dashboard de filas em tempo real, reprocessamento de tarefas falhas, alertas de backlog, auto-scaling hints |

### 4.11 Abstração de Storage

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.storage` |
| **Propósito** | Camada de abstração sobre armazenamento de arquivos |
| **Justificativa** | Diferentes clientes podem ter requisitos diferentes de storage (S3, GCS, Azure Blob, local). Esta abstração permite configurar o backend por tenant e implementa quotas de armazenamento integradas com o módulo de quotas. |
| **Modelos principais** | `StorageBackend`, `StorageQuota`, `StoredFile`, `StorageTransfer` |
| **Funcionalidades** | Multi-backend, quotas por tenant, upload assinado, CDN integration, lifecycle policies |

### 4.12 Sistema de Webhooks

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.webhooks` |
| **Propósito** | Emissão e recepção de webhooks |
| **Justificativa** | Webhooks são essenciais para integrações com sistemas de terceiros e notificações em tempo real. O Company Core atua tanto como emissor (eventos internos → clientes) quanto como receptor (eventos externos → workflows). |
| **Modelos principais** | `WebhookEndpoint`, `WebhookDelivery`, `WebhookEvent`, `WebhookSignature` |
| **Funcionalidades** | Registro de endpoints, entrega com retry exponencial, assinatura HMAC, logs de entrega, dead letter queue |

### 4.13 Framework de API

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.api_framework` |
| **Propósito** | Infraestrutura comum para todas as APIs do Company Core |
| **Justificativa** | Embora o DRF do Pegasus forneça a base, o Company Core precisa de padrões consistentes para versionamento, paginação, filtros, ordenação, inclusão de recursos relacionados, e response format. Este módulo define e implementa esses padrões. |
| **Componentes** | Base viewsets, mixins, serializers abstratos, paginadores, filtros, parsers, renderers, middleware de API |
| **Funcionalidades** | Versionamento, HATEOAS links, cursor pagination, sparse fieldsets, filtering avançado, bulk operations |

### 4.14 Sistema de Auditoria

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.audit` |
| **Propósito** | Registro completo de todas as ações no sistema |
| **Justificativa** | Auditoria é requisito não negociável para plataformas SaaS B2B. Regulamentações como LGPD, SOC 2 e GDPR exigem rastreabilidade completa de quem fez o quê, quando e a partir de onde. |
| **Modelos principais** | `AuditLog`, `AuditEvent`, `AuditSession` |
| **Funcionalidades** | Logging automático via signals, consulta eficiente por tenant/usuario/recurso, retenção configurável, exportação para SIEM |

### 4.15 Analytics

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.analytics` |
| **Propósito** | Coleta e agregação de métricas de negócio |
| **Justificativa** | Métricas de uso, engajamento e performance são essenciais para tomada de decisão de produto e identificação de oportunidades de upsell. O analytics interno complementa ferramentas externas como Mixpanel/Amplitude. |
| **Modelos principais** | `AnalyticsEvent`, `AnalyticsAggregation`, `AnalyticsDashboard`, `AnalyticsReport` |
| **Funcionalidades** | Event tracking, agregação por períodos, dashboards customizáveis, exportação de relatórios, funis e cohort analysis |

### 4.16 Tracking de Uso

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.usage` |
| **Propósito** | Medição granular de consumo por organização |
| **Justificativa** | Diferente do analytics (que foca em métricas de produto), o usage tracking foca em medição para billing: quantas API calls, quantos tokens AI, quanto storage, quantas execuções de workflow. Esses dados alimentam tanto o billing quanto o sistema de quotas. |
| **Modelos principais** | `UsageEvent`, `UsageMeter`, `UsageAggregation`, `UsageReport` |
| **Funcionalidades** | Coleta via middleware e signals, agregação por janela temporal, report diário/semanal/mensal, integração com billing |

### 4.17 Notificações

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.notifications` |
| **Propósito** | Sistema unificado de notificações multi-canal |
| **Justificativa** | Notificações são críticas para engajamento e comunicação operacional. O sistema precisa suportar múltiplos canais (in-app, e-mail, push, SMS, Slack) com preferências por usuário e organização, e batching para evitar spam. |
| **Modelos principais** | `Notification`, `NotificationTemplate`, `NotificationChannel`, `NotificationPreference` |
| **Funcionalidades** | Multi-canal, templates editáveis, preferências granulares, digest/batching, histórico de notificações |

### 4.18 Framework de Integrações

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.integrations` |
| **Propósito** | Infraestrutura para integrações com serviços de terceiros |
| **Justificativa** | Cada cliente pode ter necessidades diferentes de integração. Este framework fornece a base para desenvolver, configurar e gerenciar integrações de forma padronizada, com suporte a OAuth, webhooks entrantes, e polling. |
| **Modelos principais** | `Integration`, `IntegrationConfig`, `IntegrationConnection`, `IntegrationSyncLog` |
| **Funcionalidades** | Registry de integrações, OAuth flow genérico, sync scheduling, error handling, connector marketplace |

### 4.19 SDK

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.sdk` |
| **Propósito** | Client SDK para acesso programático à plataforma |
| **Justificativa** | Um SDK oficial reduz a fricção para integrações e aumenta a adoção da plataforma. Será construído como pacote Python separado que consome a API pública do Company Core. |
| **Componentes** | Client HTTP, auth helpers, typed models, retry logic, async support |
| **Funcionalidades** | Auto-configuração, type hints, error handling, pagination helpers, webhook verification |

### 4.20 Painéis Admin Customizados

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.admin_panels` |
| **Propósito** | Interface administrativa avançada para operação da plataforma |
| **Justificativa** | O Django admin padrão é funcional mas limitado. O Company Core precisa de painéis operacionais para: gestão de tenants, monitoramento de billing, análise de uso, gestão de feature flags, e operações de suporte. |
| **Componentes** | Dashboards admin customizados, ações em lote, filtros avançados, exportação, audit viewer |
| **Funcionalidades** | Views admin customizadas, integração com analytics, ações operacionais (reembolso, extensão de trial, etc.) |

### 4.21 Endpoints de Health

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.health` |
| **Propósito** | Endpoints de health check para orquestração e monitoramento |
| **Justificativa** | Necessário para Kubernetes liveness/readiness probes, load balancers, e monitoramento externo (UptimeRobot, DataDog). O Pegasus pode ter um health check básico, mas o Company Core precisa de checks granulares por dependência. |
| **Componentes** | Views de health check, middleware de health |
| **Funcionalidades** | `/healthz` (liveness), `/readyz` (readiness com checks de DB, Redis, Stripe), `/metrics` (Prometheus), version endpoint |

### 4.22 Utilitários Comuns

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.common` |
| **Propósito** | Funções e classes utilitárias compartilhadas |
| **Justificativa** | Utilitários como formatação, validação, helpers de data/hora, decorators, context managers e constantes precisam de um módulo dedicado para evitar duplicação e manter a consistência em toda a codebase. |
| **Componentes** | Helpers, validators, decorators, constants, exceptions, pagination utilities |
| **Funcionalidades** | Formatação de moeda/percentual, validação de CPF/CNPJ, rate limit decorator, pagination helpers, custom exceptions |

### 4.23 Configurações Core

| Aspecto | Detalhe |
|---------|--------|
| **Identificador** | `companycore.core_settings` |
| **Propósito** | Configurações dinâmicas gerenciáveis via admin |
| **Justificativa** | Algumas configurações precisam ser alteráveis em runtime sem deploy (ex: limites globais de taxa, maintenance mode, feature launches). Este módulo fornece um modelo de configurações com cache e invalidação. |
| **Modelos principais** | `Setting`, `SettingCategory`, `SettingHistory` |
| **Funcionalidades** | CRUD de settings via admin, cache com invalidação, histórico de alterações, validação por tipo |

---

## 5. Componentes do Pegasus que NUNCA deverão ser modificados

Estes componentes são considerados **sagrados** e não devem sofrer nenhuma modificação direta. Qualquer necessidade de customização deve ser feita por meio dos padrões de extensão descritos na Seção 6.

### 5.1 Estrutura Base de Settings do Django

Os arquivos de configuração base do Pegasus (`settings/base.py` e variantes por ambiente) não devem ser modificados diretamente. O Company Core deve criar seus próprios módulos de settings que importam e estendem a configuração base. Isso garante que atualizações do Pegasus possam ser aplicadas sem conflitos de merge e que a responsabilidade de cada camada de configuração seja claramente delimitada. Qualquer nova configuração necessária deve ser adicionada em um arquivo separado importado ao final do settings base, ou em um wrapper que sobrescreve valores específicos.

### 5.2 Código Core do django-allauth

O código do django-allauth (instalado via pip) nunca deve ser modificado. Qualquer customização no fluxo de autenticação deve ser feita por meio de adapters, views customizadas que estendem as views do allauth, templates sobrescritos, signals do allauth, ou middleware. O allauth é uma dependência de terceiros madura e bem mantida, e modifications locais criam dívida técnica severa e impedem atualizações de segurança.

### 5.3 Campos Base do CustomUser

Os campos definidos no modelo `CustomUser` do Pegasus (nome, e-mail, is_active, is_staff, etc.) não devem ser removidos ou ter seu tipo/comportamento alterado. Extensões devem ser feitas por meio de perfil relacionado (one-to-one), herança de modelo, ou campos adicionais em uma classe derivada. A integridade do modelo de usuário é crítica para a autenticação e autorização do sistema inteiro.

### 5.4 Classe Abstrata BaseModel

A classe `BaseModel` com seus campos `created_at` e `updated_at` é a fundação de todos os modelos do sistema. Nunca adicione campos a esta classe, pois isso afetaria TODOS os modelos que a herdam, incluindo os do próprio Pegasus. Extensões de modelo devem criar suas próprias classes abstratas que herdam de `BaseModel` e adicionam campos específicos.

### 5.5 Sistema de Templates do CLI do Pegasus

O template system do Pegasus CLI (utilizado para gerar novos projetos) não deve ser modificado. O Company Core é um projeto *gerado* pelo Pegasus, não um fork do Pegasus. Manter o CLI intacto permite gerar novos projetos Pegasus no futuro para outros produtos, e garante que a documentação e tutoriais do Pegasus continuem aplicáveis.

### 5.6 Estrutura de Configuração do Pegasus (pegasus-config.yaml)

O arquivo `pegasus-config.yaml` que controla a geração do projeto não deve ser modificado após a geração inicial. Se precisarmos re-gerar o projeto (ex: para atualizar para uma nova versão do Pegasus), o config original deve ser preservado para permitir comparação e merge controlado. Mudanças na configuração devem ser rastreadas em um arquivo separado documentando as diferenças.

---

## 6. Padrões de Extensão

Esta seção define **como** o Company Core estende o Pegasus sem modificá-lo. Estes padrões devem ser seguidos rigorosamente por toda a equipe de engenharia.

### 6.1 Django Apps Registrados via INSTALLED_APPS

Todos os módulos do Company Core serão implementados como Django apps independentes e registrados em `INSTALLED_APPS` após os apps do Pegasus. A ordem de registro é importante:

```python
INSTALLED_APPS = [
    # ... apps do Pegasus (NÃO modificar) ...
    "django.contrib.admin",
    "django.contrib.auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # ... demais apps do Pegasus ...
    # --- Apps do Company Core (adicionar AQUI) ---
    "companycore.organizations",
    "companycore.apikeys",
    "companycore.billing",
    "companycore.quotas",
    "companycore.featureflags",
    "companycore.ai_providers",
    "companycore.agents",
    "companycore.prompts",
    "companycore.workflows",
    "companycore.queues",
    "companycore.storage",
    "companycore.webhooks",
    "companycore.api_framework",
    "companycore.audit",
    "companycore.analytics",
    "companycore.usage",
    "companycore.notifications",
    "companycore.integrations",
    "companycore.admin_panels",
    "companycore.health",
    "companycore.common",
    "companycore.core_settings",
]
```

Cada app deve seguir a estrutura padrão Django com `models.py`, `views.py`, `urls.py`, `admin.py`, `serializers.py` (se aplicável), `tasks.py` (se aplicável), e `tests/`.

### 6.2 Sobrescrita de Settings em Módulo Próprio

O Company Core criará um módulo `companycore/settings_extensions.py` que será importado ao final do settings base. Este padrão garante que todas as configurações adicionais estejam centralizadas e claramente separadas do Pegasus:

```python
# Em settings/base.py (adicionar AO FINAL, sem modificar nada acima)
from companycore.settings_extensions import *  # noqa: F401, F403
```

O módulo `settings_extensions.py` conterá todas as configurações específicas do Company Core organizadas por categoria (AI, Billing, Storage, etc.). Valores existentes podem ser sobrescritos utilizando a função `globals().update()` ou atribuição direta.

### 6.3 Herança de Templates

Todos os templates do Company Core devem estender os templates base do Pegasus por meio de blocos Django:

```html
{% extends "base.html" %}

{% block title %}Company Core — Dashboard{% endblock %}

{% block content %}
{% include "companycore/partials/tenant_selector.html" %}
{% block companycore_content %}{% endblock %}
{% endblock %}
```

Isso permite que o Company Core se beneficie de toda a estrutura de layout, navbar, footer e componentes do Pegasus sem duplicação.

### 6.4 Hooks Baseados em Signals

Seguindo a filosofia "fat models, thin views" do Pegasus, o Company Core utilizará Django signals para integrar lógica transversal:

- **`post_save` no User**: criação automática de perfil, registro no sistema de audit, inicialização de quotas.
- **`post_save` no Organization**: criação de configurações padrão, inicialização de billing, setup de webhooks.
- **`request_finished`**: tracking de uso, analytics events, atualização de quotas.

Todos os receivers devem ser registrados nos respectivos `apps.py` dos módulos do Company Core, nunca em modelos do Pegasus.

### 6.5 Injeção de Middleware

O Company Core adicionará middleware específico por meio do setting `MIDDLEWARE`, sempre após os middleware do Pegasus:

```python
MIDDLEWARE += [
    "companycore.organizations.middleware.TenantMiddleware",
    "companycore.audit.middleware.AuditMiddleware",
    "companycore.usage.middleware.UsageTrackingMiddleware",
    "companycore.featureflags.middleware.FeatureFlagMiddleware",
]
```

A ordem dos middleware é crítica. O TenantMiddleware deve ser um dos primeiros para garantir que o contexto do tenant esteja disponível para todos os middleware e views subsequentes.

### 6.6 Integração de Apps de Terceiros

Além dos apps fornecidos pelo Pegasus, o Company Core integrará:

| App | Propósito | Justificativa |
|-----|-----------|---------------|
| `dj-stripe` | Integração Stripe (opcional) | Se optarmos por não construir abstração própria |
| `django-tenant-users` | Multi-tenancy (avaliar) | Se a solução row-level for insuficiente |
| `django-simple-history` | Versionamento de modelos | Para modelos críticos que precisam de histórico |
| `django-filter` | Filtragem avançada | Para a API framework |
| `drf-spectacular` | OpenAPI avançado | Se o schema gerado pelo Pegasus for insuficiente |
| `celery-redbeat` | Scheduler distribuído | Se django-celery-beat for limitante em multi-instance |
| `sentry-sdk` | Error tracking | Para monitoramento de erros em produção |
| `django-prometheus` | Métricas Prometheus | Para monitoramento de infraestrutura |

A decisão sobre quais apps de terceiros adotar será feita caso a caso durante o design detalhado de cada módulo.

---

## 7. Decision Log

A tabela abaixo registra todas as decisões arquiteturais sobre reutilização vs. construção própria, com justificativa e responsável.

| # | Decisão | Alternativas Consideradas | Escolha | Justificativa |
|---|---------|--------------------------|---------|---------------|
| 1 | Sistema de autenticação | Pergasus (allauth), Auth0, Keycloak, Construir próprio | **Reutilizar Pegasus (allauth)** | allauth é maduro, bem mantido, já configurado no Pegasus com magic links e captcha. Não há ganho em substituir. |
| 2 | Multi-tenancy | Pegasus Pro Teams, Construir próprio, django-tenant-users | **Construir próprio** | Controle total sobre estratégia de isolamento e integração com billing/quotas. Teams é recurso Pro e limitado. |
| 3 | Stripe Billing | Pegasus Pro (dj-stripe), Construir próprio, Stripe SDK direto | **Construir próprio** | Precisamos de abstração para suportar modelos de precificação customizados não cobertos pelo dj-stripe. |
| 4 | Feature Flags | Pegasus (Waffle base), LaunchDarkly, Unleash, Construir próprio | **Estender Waffle** | Waffle cobre 80% dos casos; Company Core adiciona os 20% restantes (plan-based, quota-based). Sem custo adicional. |
| 5 | AI Chat/Agents | Pegasus Pro AI, LangChain, Construir próprio | **Construir próprio** | Pegasus Pro tem AI básico; precisamos de framework multi-provedor com tools, memory e agents. LangChain adiciona complexidade desnecessária. |
| 6 | API Keys | Pegasus Pro API keys, Construir próprio | **Construir próprio** | Precisamos de scopes, Service Accounts, rate limiting por chave e distinção PAT vs. Service Account. |
| 7 | Social Login | Pegasus Pro, allauth providers, Construir próprio | **Extender allauth (via Pegasus)** | allauth já suporta social login via providers. Ativar quando necessário, sem build próprio. |
| 8 | 2FA | Pegasus Pro, django-allauth-2fa, Construir próprio | **Extender allauth** | django-allauth-2fa integra-se naturalmente com a stack existente. |
| 9 | Impersonation | Pegasus Pro, django-impersonate, Construir próprio | **Avaliar django-impersonate** | Se necessário para suporte, django-impersonate é maduro e bem integrado com Django admin. |
| 10 | Frontend (HTMX+Tailwind) | Pegasus stack, Next.js, React SPA, Vue | **Reutilizar Pegasus stack** | HTMX+Tailwind alinha com a filosofia server-driven do Pegasus. Reduz complexidade, melhora SEO e tempo de first load. |
| 11 | Celery Infrastructure | Pegasus config, Construir próprio, Temporal | **Reutilizar e estender Pegasus** | Celery é suficiente para nossa escala atual. Adicionar filas dedicadas e monitoring. |
| 12 | DRF + OpenAPI | Pegasus config, Ninja API, Graphene (GraphQL) | **Reutilizar e estender Pegasus** | DRF é o padrão de facto para Django REST. OpenAPI é necessário para SDK e documentação. |
| 13 | Docker Infrastructure | Pegasus config, Helm charts, Serverless | **Reutilizar e estender Pegasus** | Docker Compose para dev, extensão para Kubernetes em produção. |
| 14 | CI Pipeline | Pegasus GitHub Actions, GitLab CI, CircleCI | **Reutilizar e estender Pegasus** | GitHub Actions é suficiente. Adicionar stages para deploy e integração. |
| 15 | Linting/Type Checking | Pegasus (ruff+mypy), Construir próprio, pre-commit | **Reutilizar e estender Pegasus** | ruff e mypy são as melhores ferramentas atuais. Adicionar regras customizadas no Company Core. |
| 16 | Sistema de Quotas | Construir próprio, django-ratelimit | **Construir próprio** | Precisamos de quotas multidimensionais (API calls, storage, AI tokens, workflows) com integração billing. django-ratelimit é insuficiente. |
| 17 | Webhooks | Construir próprio, django-signal-hooks | **Construir próprio** | Precisamos de emissão E recepção com retry, signing, e dead letter queue. |
| 18 | Storage Abstraction | django-storages, Construir próprio | **Extender django-storages** | django-storages fornece backends; Company Core adiciona quotas e multi-backend. |
| 19 | Audit System | django-auditlog, Construir próprio | **Construir próprio** | Precisamos de audit logging otimizado por tenant com retenção configurável e exportação. |
| 20 | Notifications | Construir próprio, django-anymail | **Construir próprio + anymail** | Framework próprio para lógica; anymail para delivery de e-mail. |
| 21 | Analytics | Construir próprio, PostHog, Mixpanel SDK | **Construir próprio** | Analytics interno para dados sensíveis; integração com ferramentas externas para product analytics. |
| 22 | SDK | Construir próprio, OpenAPI generator | **Construir próprio** | SDK typed com helpers específicos da plataforma. Geradores genéricos produzem código inferior. |
| 23 | Health Endpoints | django-health-check, Construir próprio | **Construir próprio** | Checks customizados por dependência com integração Prometheus. django-health-check é limitado. |

---

## Apêndice A: Glossário

| Termo | Definição |
|-------|----------|
| **Pegasus** | SaaS Pegasus — starter kit open source para Django SaaS |
| **Company Core** | Plataforma central da empresa, baseada no Pegasus |
| **Tenant** | Organização/cliente que utiliza a plataforma em modo multi-tenant |
| **Quota** | Limite de uso configurável por plano/organização |
| **Feature Flag** | Toggle para habilitar/desabilitar funcionalidades sem deploy |
| **Service Account** | Conta de serviço para acesso programático por organização |
| **PAT** | Personal Access Token — token de acesso pessoal vinculado a um usuário |
| **Workflow** | Sequência automatizada de passos definida pelo usuário |
| **Agent** | Entidade de IA que pode executar tarefas com tools e memória |
| **Webhook** | Chamada HTTP automática para notificar sistemas externos sobre eventos |

---

## Apêndice B: Princípios Orientadores

1. **Nunca modificar o código fonte do Pegasus** — toda extensão é por composição, herança ou configuração.
2. **Favoritar extensão sobre substituição** — se o Pegasus já resolve 80%, estenda os 20% restantes.
3. **Isolamento de responsabilidades** — cada módulo do Company Core é independente e testável.
4. **Multi-tenancy first** — todo módulo deve considerar o contexto do tenant desde o design.
5. **Billing-aware** — funcionalidades devem respeitar limites de plano e quotas.
6. **API-first** — toda funcionalidade deve ser acessível via API, não apenas via UI.
7. **Auditable** — toda ação modificadora deve gerar registro de auditoria.
8. **Async por padrão** — operações longas devem usar Celery, nunca bloquear a request.

---

> **Próximos passos:** Após aprovação deste plano, o próximo documento será o *Design Técnico Detalhado* de cada módulo, começando por Organizations (multi-tenancy) e Billing, que são fundacionais para os demais módulos.
