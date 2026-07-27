# Mapa de Dependências de Módulos — Company Core

> **Versão:** 1.0
> **Data:** 2025
> **Projeto:** Company Core — Plataforma Multi-Tenant SaaS com IA

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Mapa de Dependências Principal](#2-mapa-de-dependências-principal)
3. [Camadas de Dependência](#3-camadas-de-dependência)
4. [Diagrama de Dependências (ASCII)](#4-diagrama-de-dependências-ascii)
5. [Regras de Dependência](#5-regras-de-dependência)
6. [Interface Pública de Cada Módulo](#6-interface-pública-de-cada-módulo)
7. [Integração com Pegasus](#7-integração-com-pegasus)
8. [Plano de Implementação por Fase](#8-plano-de-implementação-por-fase)

---

## 1. Visão Geral

### Filosofia de Dependências

O Company Core é composto por **24 módulos** (apps Django) que seguem um princípio fundamental de arquitetura: **cada módulo deve ser o mais independente possível**, funcionando como uma unidade coesa e autocontida.

### Princípios Norteadores

| Princípio | Descrição |
|-----------|-----------|
| **Independência** | Todo módulo deve poder ser testado e executado isoladamente, sem depender de outros módulos além da fundação (`core` e `common`). |
| **Fluxo Inward** | As dependências fluem das camadas superiores para as inferiores. Módulos de camadas mais altas importam de camadas mais baixas, nunca o contrário. |
| **Proibição de Ciclos** | Dependências circulares são **estritamente proibidas**. Se o módulo A depende de B, então B não pode depender de A (nem indiretamente). |
| **Interface Pública** | Cada módulo expõe apenas uma interface pública bem definida (services, selectors, signals). Importações de detalhes internos são proibidas. |
| **Comunicação via Signals** | Quando módulos precisam reagir a eventos de outros módulos sem criar dependências diretas, utilizam o sistema de signals do Django. |
| **Camada de Integração** | O módulo `sdk` serve como fachada (facade) para comunicação entre módulos, centralizando imports e fornecendo uma API estável. |

### Convenções

- **Importação obrigatória:** Todo módulo pode importar de `core` e `common` sem restrição.
- **Importação permitida:** Um módulo pode importar de módulos em camadas inferiores à sua.
- **Importação proibida:** Um módulo nunca deve importar de módulos em camadas superiores à sua.
- **Importação cruzada:** Imports entre módulos da mesma camada são desencorajados, mas permitidos apenas com justificativa explícita no código (comentário `# CROSS-LAYER-IMPORT: razão`).

---

## 2. Mapa de Dependências Principal

A tabela abaixo detalha as dependências de cada módulo. As dependências são classificadas em **obrigatórias** (necessárias para o funcionamento básico) e **opcionais** (funcionalidades extras ativadas por configuração).

### Legenda

- 🔴 **Obrigatória** — O módulo não funciona sem essa dependência.
- 🟡 **Opcional** — Funcionalidade adicional ativada por configuração.
- ⚪ **Nenhuma** — Sem dependências além de `core`/`common`.

> **Nota:** Todos os 24 módulos dependem implicitamente de `core`. As dependências de `common` são omitidas quando triviais. Para manter a tabela legível, apenas as dependências além de `core`/`common` estão listadas.

### Tabela de Dependências

| # | Módulo | Depende De (Obrigatório 🔴) | Depende De (Opcional 🟡) | É Dependido Por |
|---|--------|----------------------------|--------------------------|-----------------|
| 1 | `core` | ⚪ Nenhuma | — | Todos os outros 23 módulos |
| 2 | `common` | 🔴 `core` | — | Todos os outros 22 módulos |
| 3 | `settings` | 🔴 `core`, `common` | 🟡 `organizations` (multitenant) | `organizations`, `billing`, `quotas`, `feature_flags`, `ai`, `agents`, `notifications`, `search` |
| 4 | `organizations` | 🔴 `core`, `common`, `settings` | — | `permissions`, `billing`, `quotas`, `feature_flags`, `storage`, `api`, `webhooks`, `audit`, `analytics`, `usage`, `notifications`, `integrations`, `workflows`, `ai`, `agents`, `search`, `admin` |
| 5 | `permissions` | 🔴 `core`, `common`, `organizations` | 🟡 `feature_flags` | `api`, `admin`, `agents`, `workflows`, `integrations` |
| 6 | `billing` | 🔴 `core`, `common`, `organizations`, `settings` | 🟡 `quotas`, `feature_flags` | `quotas`, `feature_flags`, `usage`, `analytics`, `audit`, `admin` |
| 7 | `quotas` | 🔴 `core`, `common`, `organizations`, `settings` | 🟡 `billing` (sync de limites) | `ai`, `agents`, `storage`, `usage`, `feature_flags`, `admin` |
| 8 | `feature_flags` | 🔴 `core`, `common`, `organizations`, `settings` | 🟡 `billing` (flags por plano) | `ai`, `agents`, `quotas`, `permissions`, `api`, `admin` |
| 9 | `ai` | 🔴 `core`, `common`, `organizations`, `settings` | 🔴 `feature_flags`, `quotas` | `agents`, `workflows`, `audit`, `analytics`, `usage`, `admin` |
| 10 | `agents` | 🔴 `core`, `common`, `organizations`, `ai`, `settings` | 🔴 `feature_flags`, `quotas`, `permissions` | `workflows`, `audit`, `analytics`, `admin` |
| 11 | `notifications` | 🔴 `core`, `common`, `organizations`, `settings` | 🟡 `webhooks`, `billing` | `integrations`, `workflows`, `billing`, `admin` |
| 12 | `integrations` | 🔴 `core`, `common`, `organizations` | 🔴 `webhooks`, `jobs`, `notifications`, `permissions` | `admin` |
| 13 | `audit` | 🔴 `core`, `common`, `organizations` | 🟡 `billing`, `ai`, `webhooks` | `analytics`, `admin` |
| 14 | `analytics` | 🔴 `core`, `common`, `organizations` | 🔴 `usage`, `billing`, `ai` | `admin` |
| 15 | `usage` | 🔴 `core`, `common`, `organizations` | 🔴 `quotas`, `billing` | `analytics`, `ai`, `agents`, `admin` |
| 16 | `storage` | 🔴 `core`, `common`, `settings` | 🔴 `organizations` (isolamento por tenant), `quotas` | `ai`, `agents`, `workflows`, `health`, `admin` |
| 17 | `api` | 🔴 `core`, `common`, `organizations`, `permissions` | 🟡 `feature_flags`, `billing` | `admin`, `sdk` |
| 18 | `webhooks` | 🔴 `core`, `common`, `organizations` | 🔴 `jobs` | `notifications`, `integrations`, `audit`, `workflows`, `admin` |
| 19 | `workflows` | 🔴 `core`, `common`, `organizations` | 🔴 `jobs`, `ai`, `agents`, `webhooks`, `notifications` | `admin` |
| 20 | `jobs` | 🔴 `core`, `common`, `settings` | 🟡 `organizations` (contexto por tenant) | `webhooks`, `integrations`, `workflows`, `admin` |
| 21 | `sdk` | 🔴 `core`, `common` | 🟡 (facade para todos — sem dependência direta, usa lazy imports) | — |
| 22 | `health` | 🔴 `core`, `common` | 🟡 `storage`, `database`, `jobs`, `api` | — |
| 23 | `search` | 🔴 `core`, `common` | 🔴 `organizations` (escopo por tenant) | `admin` |
| 24 | `admin` | 🔴 `core`, `common` | 🟡 (todos os módulos — via `admin.site.register`) | — |

### Estatísticas de Dependências

| Métrica | Valor |
|---------|-------|
| Total de módulos | 24 |
| Total de dependências obrigatórias (arestas diretas) | 87 |
| Módulo com mais dependentes | `organizations` (dependido por 19 módulos) |
| Módulo com mais dependências obrigatórias | `agents` (6 obrigatórias) |
| Módulos sem dependências além de core/common | `core`, `common`, `health`, `search` |
| Módulos mais isolados (leaf nodes) | `sdk`, `health`, `admin`, `search` |

---

## 3. Camadas de Dependência

Os módulos estão organizados em **6 camadas** hierárquicas. Dependências só fluem de camadas superiores para inferiores.

```
┌─────────────────────────────────────────────────┐
│           Camada 5 (Integração)                  │
│           sdk, admin                             │
├─────────────────────────────────────────────────┤
│           Camada 4 (Operações)                   │
│    audit, analytics, usage, notifications,       │
│    integrations, workflows                       │
├─────────────────────────────────────────────────┤
│           Camada 3 (Inteligência)                │
│           ai, agents                             │
├─────────────────────────────────────────────────┤
│           Camada 2 (Infraestrutura)              │
│    billing, quotas, feature_flags, storage,      │
│    jobs, api, webhooks, health, search           │
├─────────────────────────────────────────────────┤
│           Camada 1 (Identidade & Acesso)         │
│    organizations, permissions, settings         │
├─────────────────────────────────────────────────┤
│           Camada 0 (Fundação)                    │
│           core, common                           │
└─────────────────────────────────────────────────┘
```

### Camada 0 — Fundação (Foundation)

| Módulo | Responsabilidade |
|--------|-----------------|
| `core` | Configurações base do projeto, modelos abstratos (`TimeStampedModel`, `UUIDModel`), constants, utilities mínimas, configuração do Django. |
| `common` | Funções reutilizáveis, mixins (CRUD, filtering, soft delete), helpers, exceções customizadas (`AppException`), utilities de validação, serialização, paginação. |

> **Regra:** Nenhum outro módulo da base de código pode substituir `core` ou `common`. São a fundação de tudo.

### Camada 1 — Identidade & Acesso (Identity & Access)

| Módulo | Responsabilidade |
|--------|-----------------|
| `organizations` | Multi-tenancy: `Organization`, `Team`, `Member`, `Invitation`, `Role`. Gerencia contextos de tenant. |
| `permissions` | RBAC: `Permission`, `RolePermission`, `UserPermission`. Verificação de permissões por contexto (org, team, global). |
| `settings` | Configurações dinâmicas por tenant: `TenantSetting`, `GlobalSetting`. Cache de settings com invalidação. |

> **Regra:** Módulos das camadas 2–5 podem depender livremente de qualquer módulo desta camada.

### Camada 2 — Infraestrutura (Infrastructure)

| Módulo | Responsabilidade |
|--------|-----------------|
| `billing` | Integração Stripe: `Plan`, `Subscription`, `Invoice`, `PaymentMethod`, `Trial`. Webhooks de pagamento. |
| `quotas` | Sistema de cotas configuráveis: `Quota`, `QuotaUsage`, `QuotaLimit`. (ex: 100 vídeos, 1000 prompts, 50GB). |
| `feature_flags` | Flags de features por plano/tenant/user/ambiente: `FeatureFlag`, `FeatureFlagRule`. Rollout percentual, A/B testing. |
| `storage` | Abstração de storage: backends S3, MinIO, Cloudflare R2, local. `StorageBackend`, `StoredFile`. Isolamento por tenant. |
| `jobs` | Gerenciamento Celery: `Job`, `JobLog`, `JobRetry`, `DeadLetterQueue`. Filas, prioridades, retry com backoff. |
| `api` | API REST versionada, API Keys, rate limiting, Swagger/OpenAPI. Serializers, viewsets, pagination. |
| `webhooks` | Sistema universal de webhooks: inbound e outbound. Assinaturas (signatures), retry com backoff, logs de entrega. |
| `health` | Endpoints de saúde: `/health` (básico), `/ready` (dependências), `/live` (liveness probe). |
| `search` | Funcionalidade de busca: indexação, consulta, filtros. Abstração de backend (Elasticsearch, Meilisearch, etc.). |

> **Regra:** Módulos desta camada podem depender de Camada 0 e Camada 1. Não podem depender de Camadas 3, 4 ou 5.

### Camada 3 — Inteligência (Intelligence)

| Módulo | Responsabilidade |
|--------|-----------------|
| `ai` | Abstração de provedores de IA: OpenAI, Anthropic, Gemini, provedores futuros. `AIProvider`, `AIModel`, `AIRequest`, `AIResponse`. Rate limiting, fallback, caching. |
| `agents` | Framework de agentes: `Agent` (nome, descrição, tools, modelo, prompt, temperature, memória). Execução de agentes, ferramentas, cadeias. |

> **Regra:** Módulos desta camada podem depender de Camadas 0, 1 e 2. Não podem depender de Camadas 4 ou 5.

### Camada 4 — Operações (Operations)

| Módulo | Responsabilidade |
|--------|-----------------|
| `audit` | Trilha de auditoria: login, logout, CRUD, billing, chamadas IA, webhooks, API. `AuditLog`, `AuditEvent`. Imutabilidade. |
| `analytics` | Análises de uso por tenant, user, módulo, consumo IA, consumo storage. Dashboards, relatórios. |
| `usage` | Métricas centralizadas: tokens, requests, files, uploads, downloads. `UsageMetric`, `UsageAggregation`. |
| `notifications` | Sistema de notificações: email, webhook, Slack, Discord. Canais extensíveis. Templates, preferências do usuário. |
| `integrations` | Framework de integrações: credenciais, status, logs, retry, health check. Registro dinâmico de integrações. |
| `workflows` | Motor de workflows: pipeline, steps, execution, logs, retry. `Workflow`, `WorkflowStep`, `WorkflowExecution`. |

> **Regra:** Módulos desta camada podem depender de Camadas 0, 1, 2 e 3. Não podem depender de Camada 5.

### Camada 5 — Integração (Integration)

| Módulo | Responsabilidade |
|--------|-----------------|
| `sdk` | SDK interno reutilizável para comunicação inter-módulos. Fachada (facade) que expõe APIs simplificadas para cada módulo. Lazy imports para evitar dependências circulares. |
| `admin` | Painéis estendidos do Django Admin para todos os módulos. Customização de listas, filtros, ações, dashboards admin. |

> **Regra:** Módulos desta camada são os de mais alto nível. Podem depender de qualquer camada inferior. Não devem ser importados por nenhum outro módulo das camadas 0–4.

---

## 4. Diagrama de Dependências (ASCII)

O diagrama abaixo mostra todas as dependências entre os 24 módulos. Setas (`→`) indicam "depende de".

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CAMADA 5 — INTEGRAÇÃO                                 ║
║                                                                              ║
║    ┌──────────────────────────────────────────────────────────────────┐      ║
║    │  sdk  (fachada para todos — lazy imports, sem dependência dir.) │      ║
║    └──────────────────────────────────────────────────────────────────┘      ║
║    ┌──────────────────────────────────────────────────────────────────┐      ║
║    │  admin  (extende Django Admin para todos os 22 módulos restantes)│      ║
║    └──────────────────────────────────────────────────────────────────┘      ║
╚══════════════════════════════════════════════════════════════════════════════╝
          │                                           │
          ▼                                           ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CAMADA 4 — OPERAÇÕES                                  ║
║                                                                              ║
║  ┌──────────┐  ┌───────────┐  ┌───────┐  ┌──────────────┐  ┌───────────┐   ║
║  │   audit  │  │ analytics │  │ usage │  │ notifications│  │integrations│   ║
║  └────┬─────┘  └─────┬─────┘  └───┬───┘  └──────┬───────┘  └─────┬─────┘   ║
║       │              │            │             │                │          ║
║       │              └──────┬─────┘             │                │          ║
║       │                     ▼                   │                │          ║
║       │               ┌──────────┐              │                │          ║
║       │               │  usage   │◄─────────────┘                │          ║
║       │               └──────────┘                               │          ║
║       │                                                         │          ║
║  ┌────┴─────────────────────────────────────────────────────────┴─────┐   ║
║  │                          workflows                                   │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
          │          │          │          │             │          │
          ▼          ▼          ▼          ▼             ▼          ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CAMADA 3 — INTELIGÊNCIA                               ║
║                                                                              ║
║  ┌──────────┐                                                               ║
║  │    ai    │◄───────────────────────────────────────────────────┐           ║
║  └────┬─────┘                                                     │           ║
║       │                                                           │           ║
║       ▼                                                           │           ║
║  ┌──────────┐                                                    │           ║
║  │  agents  │────────────────────────────────────────────────────┘           ║
║  └──────────┘                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
          │          │          │          │             │          │
          ▼          ▼          ▼          ▼             ▼          ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CAMADA 2 — INFRAESTRUTURA                             ║
║                                                                              ║
║  ┌────────┐ ┌───────┐ ┌───────────────┐ ┌─────────┐ ┌──────┐                ║
║  │billing │ │quotas │ │feature_flags  │ │ storage │ │ jobs │                ║
║  └───┬────┘ └───┬───┘ └──────┬────────┘ └────┬────┘ └──┬───┘                ║
║      │         │             │               │          │                     ║
║      └────┬────┘             │               │          │                     ║
║           ▼                  ▼               │          │                     ║
║      ┌─────────────────────────┐             │          │                     ║
║      │  feature_flags ◄───────┘             │          │                     ║
║      └─────────────────────────┘             │          │                     ║
║                                              │          │                     ║
║  ┌───────┐  ┌──────────┐  ┌───────┐  ┌──────────┐                             ║
║  │  api  │  │ webhooks │  │health │  │  search  │                             ║
║  └───────┘  └──────────┘  └───────┘  └──────────┘                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
          │          │          │          │             │          │
          ▼          ▼          ▼          ▼             ▼          ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CAMADA 1 — IDENTIDADE & ACESSO                        ║
║                                                                              ║
║  ┌───────────────────┐  ┌──────────────┐  ┌──────────┐                      ║
║  │   organizations   │  │  permissions  │  │ settings │                      ║
║  └───────────────────┘  └──────────────┘  └──────────┘                      ║
║           ▲                    │                ▲                           ║
║           │                    │                │                           ║
║           └────────────────────┘                │                           ║
║                        permissions → organizations │                        ║
║                                       settings → (autônomo, optional org)   ║
╚══════════════════════════════════════════════════════════════════════════════╝
          │          │          │          │             │          │
          ▼          ▼          ▼          ▼             ▼          ▼
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CAMADA 0 — FUNDAÇÃO                                    ║
║                                                                              ║
║  ┌──────────┐                                                               ║
║  │   core   │◄── Todos os 22 módulos acima                                  ║
║  └────┬─────┘                                                               ║
║       │                                                                      ║
║       ▼                                                                      ║
║  ┌──────────┐                                                               ║
║  │  common  │◄── Todos os 22 módulos acima                                  ║
║  └──────────┘                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Mapa Detalhado de Arestas (Dependências Diretas)

```
settings           → core, common
organizations       → core, common, settings
permissions        → core, common, organizations
billing             → core, common, organizations, settings
quotas              → core, common, organizations, settings
feature_flags       → core, common, organizations, settings
ai                  → core, common, organizations, settings, feature_flags, quotas
agents              → core, common, organizations, ai, settings, feature_flags, quotas
notifications       → core, common, organizations, settings
integrations        → core, common, organizations
audit               → core, common, organizations
analytics           → core, common, organizations
usage               → core, common, organizations
storage             → core, common, settings
api                 → core, common, organizations, permissions
webhooks            → core, common, organizations
workflows           → core, common, organizations
jobs                → core, common, settings
sdk                 → core, common  (lazy imports para todos os demais)
health              → core, common
search              → core, common
admin               → core, common  (registra models de todos os demais)

--- Dependências opcionais (setas tracejadas) ---

settings            ⇢ organizations (multitenant)
permissions         ⇢ feature_flags
billing             ⇢ quotas, feature_flags
quotas              ⇢ billing (sync de limites)
feature_flags       ⇢ billing (flags por plano)
ai                  ⇢ usage (métricas de consumo)
agents              ⇢ permissions (permissões por agente)
notifications       ⇢ webhooks, billing
integrations        ⇢ webhooks, jobs, notifications, permissions
audit               ⇢ billing, ai, webhooks
analytics           ⇢ usage, billing, ai
usage               ⇢ quotas, billing
storage             ⇢ organizations (isolamento por tenant), quotas
api                 ⇢ feature_flags, billing
webhooks            ⇢ jobs
workflows           ⇢ jobs, ai, agents, webhooks, notifications
health              ⇢ storage, jobs, api
search              ⇢ organizations (escopo por tenant)
```

---

## 5. Regras de Dependência

### 5.1 Regras Estritas (Obrigatórias)

| # | Regra | Descrição | Punição em caso de violação |
|---|-------|-----------|----------------------------|
| R1 | **Sem ciclos** | Dependências circulares (diretas ou indiretas) são proibidas. Se A→B, B não pode depender de A, mesmo transitivamente. | Rejeição imediata no code review. CI falha com `dependency-check`. |
| R2 | **Fluxo descendente** | Módulos de camada inferior (0, 1, 2...) NÃO podem importar módulos de camada superior (5, 4, 3...). | Bloqueio no PR. Lint personalizado (`python manage.py check_deps`). |
| R3 | **core e common são universais** | Todos os módulos podem depender de `core` e `common`. Esses dois nunca dependem de nenhum outro módulo. | Violação de R2 se `core` ou `common` importarem qualquer outro módulo. |
| R4 | **Interface pública apenas** | Módulos só devem importar a interface pública de outros módulos (services, selectors, signals). Importar models internos, utils ou implementações privadas é proibido. | Warning no CI. Code review obrigatório. |
| R5 | **sdk como fachada** | Para comunicação entre módulos de camadas não adjacentes, utilizar o `sdk` como fachada em vez de imports diretos. | Code review obrigatório. Justificativa por comentário `# SDK-IMPORT: razão`. |

### 5.2 Regras Recomendadas (Boas Práticas)

| # | Regra | Descrição |
|---|-------|-----------|
| B1 | **Signals para desacoplamento** | Preferir signals para comunicação entre módulos em vez de imports diretos. Ex: `billing` emite signal `subscription_changed`; `quotas` escuta e reconfigura. |
| B2 | **Lazy imports** | Quando o módulo `sdk` precisar acessar funcionalidades de outros módulos, usar imports dentro de funções (lazy imports) para evitar dependências de inicialização. |
| B3 | **Injeção de dependências** | Services devem receber dependências via parâmetro (injeção) em vez de importá-las diretamente, facilitando testes. |
| B4 | **Mínimo de dependências** | Manter o número de dependências o menor possível. Cada dependência adicional é custo de manutenção. |
| B5 | **Documentar cross-layer imports** | Qualquer import entre módulos da mesma camada deve ser documentado com comentário `# CROSS-LAYER-IMPORT: [razão detalhada]`. |

### 5.3 Matriz de Permissão de Imports

A matriz abaixo indica se um módulo da camada X pode importar de um módulo da camada Y:

| Da \ Para ↓ | C0 (Fundação) | C1 (Identidade) | C2 (Infra) | C3 (Inteligência) | C4 (Operações) | C5 (Integração) |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| **C0 (Fundação)** | ⬛ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **C1 (Identidade)** | ✅ | ⚠️¹ | ❌ | ❌ | ❌ | ❌ |
| **C2 (Infra)** | ✅ | ✅ | ⚠️¹ | ❌ | ❌ | ❌ |
| **C3 (Inteligência)** | ✅ | ✅ | ✅ | ⚠️¹ | ❌ | ❌ |
| **C4 (Operações)** | ✅ | ✅ | ✅ | ✅ | ⚠️¹ | ❌ |
| **C5 (Integração)** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️¹ |

> ✅ = Permitido sem restrição
> ⚠️¹ = Mesma camada — permitido apenas com justificativa (`# CROSS-LAYER-IMPORT`)
> ❌ = Proibido — violação de arquitetura

### 5.4 Verificação Automática

Para garantir o cumprimento das regras, será implementado um comando de gerenciamento Django:

```bash
python manage.py check_dependencies
```

Este comando:
1. Constrói o grafo de dependências a partir dos imports reais de cada módulo.
2. Detecta ciclos (DFS com detecção de back edges).
3. Verifica se imports respeitam as camadas definidas.
4. Lista todos os cross-layer imports sem comentário de justificativa.
5. Emite relatório com status: ✅ PASS ou ❌ FAIL.

---

## 6. Interface Pública de Cada Módulo

Cada módulo expõe uma interface pública bem definida. Abaixo estão listados os componentes públicos de cada um.

### 6.1 `core`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `TimeStampedModel` (abstrato), `UUIDModel` (abstrato), `SoftDeleteModel` (abstrato) |
| **Services** | Nenhum (módulo de configuração) |
| **Selectors** | Nenhum |
| **Signals** | Nenhum |
| **Escuta Signals** | Nenhum |
| **Constants** | `APP_NAME`, `APP_VERSION`, `ENVIRONMENT` |
| **Exceptions** | `CoreException` (base para todas as exceções do projeto) |

---

### 6.2 `common`

| Tipo | Componentes |
|------|------------|
| **Modelos** | Nenhum modelo concreto |
| **Mixins** | `CRUDMixin`, `FilterableMixin`, `PaginatedMixin`, `TenantScopeMixin` |
| **Services** | `ValidationService` — validação genérica de dados |
| **Helpers** | `get_client_ip()`, `generate_random_token()`, `mask_sensitive_data()`, `sanitize_input()` |
| **Exceptions** | `AppException`, `NotFoundException`, `ValidationException`, `PermissionDeniedException`, `RateLimitException`, `ExternalServiceException` |
| **Utilities** | `PaginationHandler`, `DateTimeUtils`, `FileUtils` |
| **Serializers** | `CommonSerializer` (base), `PaginatedResponseSerializer` |
| **Signals** | Nenhum |
| **Escuta Signals** | Nenhum |

---

### 6.3 `settings`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `TenantSetting`, `GlobalSetting` |
| **Services** | `SettingsService.get(key, tenant=None)`, `SettingsService.set(key, value, tenant=None)`, `SettingsService.invalidate_cache(tenant=None)` |
| **Selectors** | `get_settings_for_tenant(tenant_id)`, `get_global_settings()` |
| **Signals Emitidos** | `setting_changed` (enviado após alteração) |
| **Signals Escutados** | Nenhum |

---

### 6.4 `organizations`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Organization`, `Team`, `Member`, `Invitation`, `Role` |
| **Services** | `OrganizationService.create()`, `OrganizationService.add_member()`, `OrganizationService.remove_member()`, `InvitationService.send()`, `InvitationService.accept()`, `InvitationService.revoke()` |
| **Selectors** | `get_organization(org_id)`, `get_members(org_id)`, `get_teams(org_id)`, `get_pending_invitations(org_id)`, `get_user_organizations(user_id)` |
| **Signals Emitidos** | `organization_created`, `organization_updated`, `member_added`, `member_removed`, `member_role_changed`, `invitation_sent`, `invitation_accepted`, `invitation_revoked`, `organization_deleted` |
| **Signals Escutados** | Nenhum |

---

### 6.5 `permissions`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Permission`, `RolePermission`, `UserPermission`, `GroupPermission` |
| **Services** | `PermissionService.assign()`, `PermissionService.revoke()`, `PermissionService.check(user, permission, context=None)`, `PermissionService.get_user_permissions(user, context=None)`, `RolePermissionService.sync_role()` |
| **Selectors** | `get_permissions_for_user(user_id, context=None)`, `get_permissions_for_role(role_id)` |
| **Signals Emitidos** | `permission_granted`, `permission_revoked`, `role_permissions_synced` |
| **Signals Escutados** | `member_added` (organizations) — para atribuir permissões padrão, `member_removed` (organizations) — para limpar permissões, `role_created` (organizations) — para criar permissões padrão do role |

---

### 6.6 `billing`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Plan`, `Subscription`, `Invoice`, `PaymentMethod`, `Trial`, `BillingEvent` |
| **Services** | `BillingService.create_subscription()`, `BillingService.cancel_subscription()`, `BillingService.change_plan()`, `BillingService.get_billing_status()`, `StripeWebhookService.process_event()`, `TrialService.start_trial()`, `TrialService.extend_trial()`, `InvoiceService.generate()` |
| **Selectors** | `get_active_subscription(org_id)`, `get_plan(plan_id)`, `get_invoices(org_id)`, `get_billing_history(org_id)`, `is_trial_active(org_id)` |
| **Signals Emitidos** | `subscription_created`, `subscription_cancelled`, `subscription_changed`, `subscription_renewed`, `payment_succeeded`, `payment_failed`, `trial_started`, `trial_ended`, `trial_expired`, `invoice_generated` |
| **Signals Escutados** | `organization_created` (organizations) — para criar subscription padrão, `organization_deleted` (organizations) — para cancelar subscription |

---

### 6.7 `quotas`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Quota`, `QuotaUsage`, `QuotaLimit`, `QuotaResetSchedule` |
| **Services** | `QuotaService.check_quota(org_id, quota_key)`, `QuotaService.consume(org_id, quota_key, amount=1)`, `QuotaService.get_usage(org_id, quota_key)`, `QuotaService.reset(org_id, quota_key)`, `QuotaService.configure(org_id, quota_key, limit)` |
| **Selectors** | `get_all_quotas(org_id)`, `get_quota_usage(org_id, quota_key)`, `get_quotas_near_limit(org_id, threshold=0.8)` |
| **Signals Emitidos** | `quota_consumed`, `quota_limit_reached`, `quota_warning` (80% do limite), `quota_reset`, `quota_configured` |
| **Signals Escutados** | `subscription_changed` (billing) — para reconfigurar cotas do novo plano, `subscription_cancelled` (billing) — para aplicar cotas do plano gratuito |

---

### 6.8 `feature_flags`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `FeatureFlag`, `FeatureFlagRule` |
| **Services** | `FeatureFlagService.is_enabled(flag_key, tenant=None, user=None)`, `FeatureFlagService.get_value(flag_key, tenant=None, user=None)`, `FeatureFlagService.enable(flag_key, tenant=None)`, `FeatureFlagService.disable(flag_key, tenant=None)`, `FeatureFlagService.create_flag()` |
| **Selectors** | `get_flags_for_tenant(tenant_id)`, `get_flags_for_user(user_id)` |
| **Signals Emitidos** | `feature_enabled`, `feature_disabled`, `feature_flag_created` |
| **Signals Escutados** | `subscription_changed` (billing) — para ajustar flags disponíveis por plano, `organization_created` (organizations) — para aplicar flags padrão |

---

### 6.9 `ai`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `AIProvider`, `AIModel`, `AIRequest`, `AIResponse`, `AIProviderCredential` |
| **Services** | `AIService.chat(messages, model, provider=None)`, `AIService.complete(prompt, model, provider=None)`, `AIService.embed(text, model, provider=None)`, `AIService.stream(messages, model)`, `AIProviderService.register_provider()`, `AIProviderService.get_provider()`, `AIModelService.list_models(provider)` |
| **Selectors** | `get_available_providers()`, `get_models_for_provider(provider_id)`, `get_request_history(org_id, limit=100)` |
| **Signals Emitidos** | `ai_request_started`, `ai_request_completed`, `ai_request_failed`, `ai_provider_registered`, `ai_provider_disabled` |
| **Signals Escutados** | `quota_limit_reached` (quotas) — para bloquear chamadas IA, `feature_disabled` (feature_flags) — para desabilitar provedor |

---

### 6.10 `agents`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Agent`, `AgentTool`, `AgentExecution`, `AgentMemory`, `AgentTemplate` |
| **Services** | `AgentService.create()`, `AgentService.execute(agent_id, input_data)`, `AgentService.configure(agent_id, config)`, `AgentToolService.register_tool()`, `AgentMemoryService.store()`, `AgentMemoryService.retrieve(agent_id, query)` |
| **Selectors** | `get_agent(agent_id)`, `get_agents_for_org(org_id)`, `get_agent_executions(agent_id)`, `get_agent_tools(agent_id)` |
| **Signals Emitidos** | `agent_created`, `agent_executed`, `agent_execution_completed`, `agent_execution_failed`, `agent_tool_registered`, `agent_memory_stored` |
| **Signals Escutados** | `ai_request_failed` (ai) — para retry ou fallback do agente, `quota_limit_reached` (quotas) — para pausar execuções |

---

### 6.11 `notifications`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Notification`, `NotificationTemplate`, `NotificationPreference`, `NotificationChannel` |
| **Services** | `NotificationService.send(recipient, template_key, context, channels=None)`, `NotificationService.send_bulk(recipients, template_key, context)`, `EmailChannelService.send()`, `SlackChannelService.send()`, `DiscordChannelService.send()`, `WebhookChannelService.send()`, `NotificationPreferenceService.get_preferences(user_id)` |
| **Selectors** | `get_notifications(user_id, status=None)`, `get_notification_preferences(user_id)`, `get_templates()` |
| **Signals Emitidos** | `notification_sent`, `notification_delivered`, `notification_failed`, `notification_read`, `notification_preference_changed` |
| **Signals Escutados** | `payment_failed` (billing) — para notificar admins, `trial_expiring` (billing) — para notificar usuario, `quota_warning` (quotas) — para alertar sobre cota, `invitation_sent` (organizations) — para enviar email de convite |

---

### 6.12 `integrations`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Integration`, `IntegrationCredential`, `IntegrationStatus`, `IntegrationLog`, `IntegrationHealthCheck` |
| **Services** | `IntegrationService.register()`, `IntegrationService.enable(integration_id)`, `IntegrationService.disable(integration_id)`, `IntegrationService.test_connection(integration_id)`, `IntegrationHealthService.check(integration_id)`, `IntegrationLogService.log()` |
| **Selectors** | `get_integrations(org_id)`, `get_integration_status(integration_id)`, `get_integration_logs(integration_id, limit=100)` |
| **Signals Emitidos** | `integration_registered`, `integration_enabled`, `integration_disabled`, `integration_health_check_passed`, `integration_health_check_failed` |
| **Signals Escutados** | `organization_created` (organizations) — para ativar integrações padrão |

---

### 6.13 `audit`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `AuditLog`, `AuditEvent`, `AuditEventType` |
| **Services** | `AuditService.log(actor, action, resource, details=None, metadata=None)`, `AuditService.query(filters, ordering, pagination)`, `AuditService.export(org_id, format='csv')`, `AuditService.get_timeline(resource_id)` |
| **Selectors** | `get_audit_logs(org_id, filters=None)`, `get_audit_events_for_user(user_id)`, `get_audit_events_for_resource(resource_type, resource_id)` |
| **Signals Emitidos** | `audit_log_created` (para analytics/processamento assíncrono) |
| **Signals Escutados** | `member_added` (organizations) — log automático, `member_removed` (organizations) — log automático, `permission_granted` (permissions) — log automático, `ai_request_started` (ai) — log de chamada IA, `ai_request_completed` (ai) — log de resultado IA, `payment_succeeded` (billing) — log de pagamento, `webhook_delivered` (webhooks) — log de entrega |

---

### 6.14 `analytics`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `AnalyticsEvent`, `AnalyticsReport`, `AnalyticsDashboard`, `AnalyticsWidget` |
| **Services** | `AnalyticsService.track_event(event_type, properties, org_id, user_id=None)`, `AnalyticsService.get_usage_report(org_id, period)`, `AnalyticsService.get_ai_consumption_report(org_id, period)`, `AnalyticsService.get_storage_report(org_id, period)`, `AnalyticsService.build_dashboard(org_id)` |
| **Selectors** | `get_events(org_id, event_type=None, period=None)`, `get_dashboard_data(org_id)`, `get_top_consumers(org_id, metric, limit=10)` |
| **Signals Emitidos** | `analytics_report_generated`, `analytics_dashboard_updated` |
| **Signals Escutados** | `audit_log_created` (audit) — para agregar dados de auditoria, `quota_consumed` (quotas) — para rastrear consumo, `ai_request_completed` (ai) — para rastrear consumo IA |

---

### 6.15 `usage`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `UsageMetric`, `UsageAggregation`, `UsageCounter` |
| **Services** | `UsageService.increment(org_id, metric_key, amount=1, metadata=None)`, `UsageService.get_current(org_id, metric_key, period='day')`, `UsageService.get_aggregated(org_id, metric_key, period='month')`, `UsageService.reset_counter(org_id, metric_key, period)` |
| **Selectors** | `get_usage_metrics(org_id, period=None)`, `get_usage_by_module(org_id, period='month')`, `get_usage_ranking(metric_key, period, limit=10)` |
| **Signals Emitidos** | `usage_metric_updated`, `usage_threshold_reached` |
| **Signals Escutados** | Nenhum (é um módulo coletor passivo) |

---

### 6.16 `storage`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `StoredFile`, `StorageBackend`, `StorageBucket` |
| **Services** | `StorageService.upload(file, path, org_id, metadata=None)`, `StorageService.download(file_id)`, `StorageService.delete(file_id)`, `StorageService.get_presigned_url(file_id, expires=3600)`, `StorageService.get_url(file_id)`, `StorageBackendService.configure(backend_type, config)` |
| **Selectors** | `get_file(file_id)`, `get_files(org_id, filters=None)`, `get_storage_usage(org_id)` |
| **Signals Emitidos** | `file_uploaded`, `file_downloaded`, `file_deleted`, `storage_usage_updated` |
| **Signals Escutados** | `organization_deleted` (organizations) — para limpar arquivos do tenant, `quota_limit_reached` (quotas) — para bloquear uploads |

---

### 6.17 `api`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `APIKey`, `APIRequestLog`, `RateLimitRule`, `APIVersion` |
| **Services** | `APIKeyService.create_key(user_id, name)`, `APIKeyService.revoke_key(key_id)`, `APIKeyService.validate_key(key)`, `RateLimitService.check_limit(user_id, endpoint)`, `RateLimitService.record_request(user_id, endpoint)`, `APIVersioningService.get_version(request)` |
| **Selectors** | `get_api_keys(user_id)`, `get_api_request_logs(user_id, period=None)`, `get_rate_limits(user_id)` |
| **Signals Emitidos** | `api_key_created`, `api_key_revoked`, `api_request_logged`, `rate_limit_exceeded` |
| **Signals Escutados** | Nenhum |

---

### 6.18 `webhooks`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `WebhookEndpoint`, `WebhookDelivery`, `WebhookEvent`, `WebhookSignature` |
| **Services** | `WebhookService.register(endpoint, events)`, `WebhookService.unregister(endpoint_id)`, `WebhookService.send(event_type, payload)`, `WebhookService.retry_delivery(delivery_id)`, `WebhookSignatureService.sign(payload, secret)`, `WebhookSignatureService.verify(payload, signature, secret)` |
| **Selectors** | `get_webhooks(org_id)`, `get_deliveries(webhook_id, status=None)`, `get_failed_deliveries(limit=100)` |
| **Signals Emitidos** | `webhook_registered`, `webhook_delivered`, `webhook_delivery_failed`, `webhook_event_received` (inbound) |
| **Signals Escutados** | `subscription_changed` (billing) — para notificar via webhook, `payment_succeeded` (billing) — para notificar via webhook, `member_added` (organizations) — para notificar via webhook |

---

### 6.19 `workflows`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Workflow`, `WorkflowStep`, `WorkflowExecution`, `WorkflowLog`, `WorkflowRetryPolicy` |
| **Services** | `WorkflowService.create()`, `WorkflowService.execute(workflow_id, input_data)`, `WorkflowService.cancel(execution_id)`, `WorkflowStepService.execute_step(step_id, context)`, `WorkflowRetryService.retry(execution_id)` |
| **Selectors** | `get_workflows(org_id)`, `get_workflow_executions(workflow_id, status=None)`, `get_pending_executions()` |
| **Signals Emitidos** | `workflow_created`, `workflow_started`, `workflow_step_completed`, `workflow_step_failed`, `workflow_completed`, `workflow_failed`, `workflow_cancelled` |
| **Signals Escutados** | `organization_created` (organizations) — para executar workflows de onboarding |

---

### 6.20 `jobs`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `Job`, `JobLog`, `JobRetry`, `DeadLetterQueueEntry` |
| **Services** | `JobService.enqueue(task, args, kwargs, queue, priority)`, `JobService.cancel(job_id)`, `JobService.retry(job_id)`, `JobService.get_status(job_id)`, `DeadLetterService.reprocess(entry_id)`, `DeadLetterService.discard(entry_id)` |
| **Selectors** | `get_jobs(queue=None, status=None)`, `get_dead_letter_entries(limit=100)`, `get_job_logs(job_id)` |
| **Signals Emitidos** | `job_enqueued`, `job_started`, `job_completed`, `job_failed`, `job_retried`, `job_dead_lettered` |
| **Signals Escutados** | Nenhum |

---

### 6.21 `sdk`

| Tipo | Componentes |
|------|------------|
| **Modelos** | Nenhum |
| **Facades** | `SDK.organizations`, `SDK.permissions`, `SDK.billing`, `SDK.quotas`, `SDK.feature_flags`, `SDK.ai`, `SDK.agents`, `SDK.notifications`, `SDK.integrations`, `SDK.audit`, `SDK.analytics`, `SDK.usage`, `SDK.storage`, `SDK.api`, `SDK.webhooks`, `SDK.workflows`, `SDK.jobs`, `SDK.settings`, `SDK.search` |
| **Services** | `SDK.initialize()` — configura SDK com contexto de tenant, `SDK.get_service(module_name)` — retorna fachada do módulo |
| **Selectors** | Nenhum (delega para selectors dos módulos) |
| **Signals Emitidos** | Nenhum (delega signals dos módulos) |
| **Signals Escutados** | Nenhum (delega para signals dos módulos) |
| **Notas** | O SDK utiliza **lazy imports** (`importlib.import_module`) para evitar dependências circulares. Cada fachada carrega o módulo real apenas no primeiro acesso. |

---

### 6.22 `health`

| Tipo | Componentes |
|------|------------|
| **Modelos** | Nenhum |
| **Services** | `HealthCheckService.check_live()` — liveness probe, `HealthCheckService.check_ready()` — readiness probe (verifica DB, Redis, storage, Celery), `HealthCheckService.check_health()` — health check completo com detalhes |
| **Selectors** | Nenhum |
| **Signals Emitidos** | Nenhum |
| **Signals Escutados** | Nenhum |
| **Views** | `/health` (200 OK se vivo), `/ready` (200 OK se pronto + info de dependências), `/live` (200 OK se processo está vivo) |

---

### 6.23 `search`

| Tipo | Componentes |
|------|------------|
| **Modelos** | `SearchIndex`, `SearchDocument`, `SearchQuery` |
| **Services** | `SearchService.index(doc_type, doc_id, data, tenant_id=None)`, `SearchService.remove_from_index(doc_type, doc_id)`, `SearchService.search(query, filters=None, tenant_id=None, limit=20)`, `SearchService.suggest(query, field, tenant_id=None)` |
| **Selectors** | `get_indexed_documents(doc_type, tenant_id=None)`, `get_search_stats(tenant_id=None)` |
| **Signals Emitidos** | `document_indexed`, `document_removed_from_index`, `search_performed` |
| **Signals Escutados** | `organization_created` (organizations) — para indexar dados do tenant, `organization_deleted` (organizations) — para limpar índice do tenant |

---

### 6.24 `admin`

| Tipo | Componentes |
|------|------------|
| **Modelos** | Nenhum (registra models de outros módulos) |
| **Admin Classes** | `OrganizationAdmin`, `MemberAdmin`, `PlanAdmin`, `SubscriptionAdmin`, `AgentAdmin`, `AuditLogAdmin`, `WebhookAdmin`, `WorkflowAdmin`, `JobAdmin`, `NotificationAdmin`, `IntegrationAdmin`, `StorageAdmin` (um admin para cada modelo principal dos módulos) |
| **Services** | Nenhum (decoradores e customizações de admin) |
| **Selectors** | Nenhum |
| **Signals Emitidos** | Nenhum |
| **Signals Escutados** | Nenhum |
| **Notas** | O módulo `admin` é puramente decorativo para o Django Admin. Não possui lógica de negócio. |

---

## 7. Integração com Pegasus

O Company Core estende e integra com os componentes do **Pegasus** (framework Django de referência). A tabela abaixo mapeia quais componentes do Pegasus cada módulo estende.

### 7.1 Visão Geral da Integração

| Módulo Company Core | Componente Pegasus | Tipo de Extensão | Descrição |
|---------------------|-------------------|------------------|-----------|
| `organizations` | `User` (pegasus users) | **Extensão de modelo** | Adiciona relação many-to-many `User → Organization` via `Member`. O modelo `User` do Pegasus é estendido (não substituído) para suportar multi-tenancy. |
| `organizations` | `Team` | **Novo modelo** | Pegasus não possui conceito de teams. Adicionado pela Company Core. |
| `organizations` | `Invitation` | **Extensão** | Pegasus possui invitations básicas. Company Core estende com contexto de organização, roles e permissões. |
| `permissions` | `Auth` (pegasus auth) | **Extensão** | Estende o sistema de autenticação/autorização do Pegasus com RBAC granular (por organização, time, global). |
| `permissions` | `Groups` | **Substituição** | O sistema de `GroupPermission` do Company Core substitui os groups padrão do Django/Pegasus com um sistema de roles e permissions mais flexível. |
| `api` | `DRF` (pegasus REST framework) | **Extensão** | Adiciona versionamento de API, API Keys, rate limiting avançado ao DRF que o Pegasus já configura. |
| `api` | `Swagger/OpenAPI` | **Extensão** | Pegasus gera documentação Swagger básica. Company Core adiciona autenticação API Key, exemplos e agrupamento por módulo. |
| `billing` | `Payments` (pegasus payments) | **Substituição** | O módulo de billing do Company Core substitui o módulo de pagamentos básico do Pegasus com suporte a Stripe completo (subscriptions, trials, invoices). |
| `settings` | `Settings` (pegasus settings) | **Extensão** | Pegasus possui `app_settings` básicos. Company Core estende com cache, invalidação, settings por tenant e tipagem forte. |
| `audit` | `Audit log` (pegasus audit) | **Extensão** | Pegasus possui auditoria básica. Company Core estende com mais tipos de eventos (IA, webhooks, billing), imutabilidade, consultas avançadas e exportação. |
| `notifications` | `Email` (pegasus email) | **Extensão** | Pegasus possui sistema de email básico. Company Core adiciona múltiplos canais (Slack, Discord, webhook), templates, preferências e histórico. |
| `jobs` | `Celery` (pegasus celery) | **Extensão** | Pegasus configura Celery. Company Core adiciona dashboard de jobs, dead letter queue, retry inteligente, prioridades e monitoramento. |
| `admin` | `Django Admin` (pegasus admin) | **Extensão** | Pegasus customiza o admin padrão. Company Core adiciona painéis estendidos com dashboards, filtros avançados, ações em lote e exportação. |
| `core` | `Base models` (pegasus base) | **Extensão** | Company Core define modelos abstratos que complementam os modelos base do Pegasus (`TimeStampedModel`, `SoftDeleteModel`, `UUIDModel`). |

### 7.2 Módulos sem integração direta com Pegasus

Estes módulos são **novos** e não estendem nenhum componente existente do Pegasus:

| Módulo | Justificativa |
|--------|---------------|
| `common` | Utilities genéricas — complementa mas não estende Pegasus. |
| `quotas` | Pegasus não possui sistema de cotas. |
| `feature_flags` | Pegasus não possui feature flags. |
| `ai` | Pegasus não possui integração com IA. |
| `agents` | Pegasus não possui framework de agentes. |
| `integrations` | Pegasus não possui framework de integrações. |
| `analytics` | Pegasus não possui analytics avançado. |
| `usage` | Pegasus não possui métricas centralizadas. |
| `storage` | Pegasus possui storage básico. Company Core adiciona abstração multi-backend e isolamento por tenant. |
| `webhooks` | Pegasus não possui sistema de webhooks universal. |
| `workflows` | Pegasus não possui motor de workflows. |
| `sdk` | Camada de integração interna — sem equivalente Pegasus. |
| `health` | Pegasus possui health checks mínimos. Company Core expande significativamente. |
| `search` | Pegasus não possui funcionalidade de busca. |

---

## 8. Plano de Implementação por Fase

A implementação segue uma ordem incremental baseada nas camadas de dependência. Cada fase constrói sobre a anterior, garantindo que todas as dependências estejam satisfeitas antes de começar um novo módulo.

### Visão Geral das Fases

```
Fase 1     Fase 2      Fase 3       Fase 4      Fase 5       Fase 6      Fase 7       Fase 8
(3 mod.)   (2 mod.)    (3 mod.)     (2 mod.)    (4 mod.)     (3 mod.)    (3 mod.)     (4 mod.)
  ████       ████        ████         ████        ████         ████        ████         ████
  ▓▓▓▓       ▓▓▓▓        ▓▓▓▓         ▓▓▓▓        ▓▓▓▓         ▓▓▓▓        ▓▓▓▓         ▓▓▓▓
```

### Fase 1 — Fundação (Semana 1-2)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 1.1 | `core` | Configurar projeto Django, modelos abstratos (`TimeStampedModel`, `UUIDModel`, `SoftDeleteModel`), exceções base, constantes, configurações de settings. | Nenhuma |
| 1.2 | `common` | Implementar mixins (CRUD, Filtering, Pagination), helpers, utilities, exceções customizadas, validadores genéricos. | `core` ✅ |
| 1.3 | `settings` | Modelo `TenantSetting`/`GlobalSetting`, service com cache e invalidação, migração de settings estáticos para dinâmicos. | `core` ✅, `common` ✅ |

**Critério de Conclusão:** Tests passando para os 3 módulos. Comando `python manage.py check` sem erros.

---

### Fase 2 — Identidade & Acesso (Semana 3-4)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 2.1 | `organizations` | Modelos `Organization`, `Team`, `Member`, `Invitation`, `Role`. Services CRUD. Signals. Extensão do User model do Pegasus. Multi-tenancy com middleware. | `core` ✅, `common` ✅, `settings` ✅ |
| 2.2 | `permissions` | Modelos `Permission`, `RolePermission`, `UserPermission`. Service de checagem de permissões. Backend de autenticação customizado. Extensão do auth do Pegasus. | `core` ✅, `common` ✅, `organizations` ✅ |

**Critério de Conclusão:** Usuário pode criar organização, convidar membros, atribuir permissões. Middleware de tenant funcionando.

---

### Fase 3 — Negócio & Limites (Semana 5-6)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 3.1 | `billing` | Integração Stripe: planos, subscriptions, trials, invoices. Webhooks Stripe. Services CRUD. Substituição do módulo de pagamentos do Pegasus. | `core` ✅, `common` ✅, `organizations` ✅, `settings` ✅ |
| 3.2 | `quotas` | Sistema de cotas configuráveis. Modelos `Quota`, `QuotaUsage`, `QuotaLimit`. Service de verificação e consumo. Sincronização com planos do billing. | `core` ✅, `common` ✅, `organizations` ✅, `settings` ✅, `billing` ✅ |
| 3.3 | `feature_flags` | Modelos `FeatureFlag`, `FeatureFlagRule`. Service de verificação (por tenant, user, ambiente). Integração com planos de billing. | `core` ✅, `common` ✅, `organizations` ✅, `settings` ✅, `billing` ✅ |

**Critério de Conclusão:** Tenant pode assinar plano, cotas são configuradas automaticamente, features são habilitadas/desabilitadas por plano.

---

### Fase 4 — Inteligência (Semana 7-8)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 4.1 | `ai` | Abstração de provedores (OpenAI, Anthropic, Gemini). Models `AIProvider`, `AIModel`, `AIRequest`, `AIResponse`. Services de chat, complete, embed, stream. Fallback entre provedores. Rate limiting. | `core` ✅, `common` ✅, `organizations` ✅, `settings` ✅, `feature_flags` ✅, `quotas` ✅ |
| 4.2 | `agents` | Framework de agentes: `Agent`, `AgentTool`, `AgentExecution`, `AgentMemory`. Services de criação e execução. Registro de tools. Memória por agente. | `core` ✅, `common` ✅, `organizations` ✅, `ai` ✅, `settings` ✅, `feature_flags` ✅, `quotas` ✅, `permissions` ✅ |

**Critério de Conclusão:** Agente pode ser criado, configurado com modelo/tools, e executado. Chamadas IA são rastreadas e limitadas por cotas.

---

### Fase 5 — Infraestrutura (Semana 9-11)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 5.1 | `storage` | Abstração de backends (S3, MinIO, R2, local). Modelo `StoredFile`. Services de upload/download/delete. Presigned URLs. Isolamento por tenant. | `core` ✅, `common` ✅, `settings` ✅, `organizations` ✅, `quotas` ✅ |
| 5.2 | `jobs` | Gerenciamento Celery: modelo `Job`, `JobLog`, `DeadLetterQueueEntry`. Dashboard de jobs. Retry com backoff. Prioridades. | `core` ✅, `common` ✅, `settings` ✅, `organizations` ✅ |
| 5.3 | `api` | Versionamento de API, modelo `APIKey`, `RateLimitRule`, `APIRequestLog`. Services de geração/validação de keys. Rate limiting. Swagger/OpenAPI extendido. | `core` ✅, `common` ✅, `organizations` ✅, `permissions` ✅, `feature_flags` ✅ |
| 5.4 | `webhooks` | Sistema universal: `WebhookEndpoint`, `WebhookDelivery`, `WebhookEvent`. Services de registro/envio/retry. Assinatura HMAC. Logs de entrega. | `core` ✅, `common` ✅, `organizations` ✅, `jobs` ✅ |

**Critério de Conclusão:** Files podem ser uploaded/downloaded. Jobs Celery são monitorados. API REST versionada com API Keys. Webhooks são enviados com retry e assinatura.

---

### Fase 6 — Observabilidade (Semana 12-13)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 6.1 | `audit` | Modelos `AuditLog`, `AuditEvent`. Service de logging automático. Integração com signals de outros módulos. Consultas e exportação (CSV). Imutabilidade. | `core` ✅, `common` ✅, `organizations` ✅, `billing` ✅, `ai` ✅, `webhooks` ✅ |
| 6.2 | `analytics` | Modelos `AnalyticsEvent`, `AnalyticsReport`, `AnalyticsDashboard`. Agregação de dados de audit, usage, quotas. Relatórios de uso por tenant, módulo, IA, storage. | `core` ✅, `common` ✅, `organizations` ✅, `usage` ✅, `billing` ✅, `ai` ✅, `audit` ✅ |
| 6.3 | `usage` | Modelos `UsageMetric`, `UsageAggregation`, `UsageCounter`. Service de incrementação. Agregação por período. Sincronização com cotas e billing. | `core` ✅, `common` ✅, `organizations` ✅, `quotas` ✅, `billing` ✅ |

**Critério de Conclusão:** Todas as ações são auditadas. Analytics mostra dashboards de uso. Métricas de consumo são rastreadas e agregadas.

---

### Fase 7 — Operações (Semana 14-15)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 7.1 | `notifications` | Múltiplos canais (email, Slack, Discord, webhook). Modelo `NotificationTemplate`. Services de envio bulk. Preferências do usuário. Integração com signals de billing, quotas, organizations. | `core` ✅, `common` ✅, `organizations` ✅, `settings` ✅, `webhooks` ✅, `billing` ✅ |
| 7.2 | `integrations` | Framework de integrações: `Integration`, `IntegrationCredential`, `IntegrationStatus`. Health check. Logs. Retry. Registro dinâmico. | `core` ✅, `common` ✅, `organizations` ✅, `webhooks` ✅, `jobs` ✅, `notifications` ✅, `permissions` ✅ |
| 7.3 | `workflows` | Motor de workflows: `Workflow`, `WorkflowStep`, `WorkflowExecution`. Pipeline, steps condicionais, paralelos. Logs. Retry. Integração com IA e agents. | `core` ✅, `common` ✅, `organizations` ✅, `jobs` ✅, `ai` ✅, `agents` ✅, `webhooks` ✅, `notifications` ✅ |

**Critério de Conclusão:** Notificações são enviadas por múltiplos canais. Integrações podem ser registradas e monitoradas. Workflows são criados, executados e monitorados.

---

### Fase 8 — Integração & Polimento (Semana 16-17)

| Ordem | Módulo | Tarefas Principais | Dependências |
|-------|--------|--------------------|--------------|
| 8.1 | `sdk` | Fachada para todos os módulos. Lazy imports. API simplificada por módulo. Documentação da API do SDK. Testes de integração. | `core` ✅, `common` ✅ (todos os demais via lazy) |
| 8.2 | `admin` | Painéis Django Admin para todos os modelos principais. Dashboards admin. Filtros avançados. Ações em lote. Exportação. | `core` ✅, `common` ✅ (todos os demais via admin.site.register) |
| 8.3 | `health` | Endpoints `/health`, `/ready`, `/live`. Verificação de dependências (DB, Redis, Celery, Storage). | `core` ✅, `common` ✅, `storage` ✅, `jobs` ✅, `api` ✅ |
| 8.4 | `search` | Abstração de backend de busca. Indexação, consulta, sugestão. Escopo por tenant. Integração com models de outros módulos. | `core` ✅, `common` ✅, `organizations` ✅ |

**Critério de Conclusão:** SDK fornece API unificada para todos os módulos. Admin é completo e funcional. Health checks são implementados. Busca funciona em todos os models indexados.

---

### Resumo do Plano

| Fase | Semanas | Módulos | Módulos Acumulados | Marco Principal |
|------|---------|---------|---------------------|-----------------|
| 1 | 1-2 | `core`, `common`, `settings` | 3 | Fundação estável |
| 2 | 3-4 | `organizations`, `permissions` | 5 | Multi-tenancy e RBAC |
| 3 | 5-6 | `billing`, `quotas`, `feature_flags` | 8 | Monetização e limites |
| 4 | 7-8 | `ai`, `agents` | 10 | Inteligência Artificial |
| 5 | 9-11 | `storage`, `jobs`, `api`, `webhooks` | 14 | Infraestrutura completa |
| 6 | 12-13 | `audit`, `analytics`, `usage` | 17 | Observabilidade |
| 7 | 14-15 | `notifications`, `integrations`, `workflows` | 20 | Operações |
| 8 | 16-17 | `sdk`, `admin`, `health`, `search` | 24 | Integração e polimento |

### Tempo Total Estimado: **17 semanas** (~4 meses)

---

## Anexo A — Glossário

| Termo | Definição |
|-------|-----------|
| **Módulo** | App Django dentro do projeto Company Core. Cada módulo é uma pasta com models, services, selectors, signals. |
| **Camada (Layer)** | Agrupamento lógico de módulos por nível de abstração. Camadas inferiores são mais fundamentais. |
| **Dependência** | Quando o módulo A importa código do módulo B, diz-se que A depende de B. |
| **Dependência Circular** | Quando A depende de B e B depende de A (direta ou indiretamente). Proibido. |
| **Fachada (Facade)** | Padrão de projeto onde um módulo (sdk) expõe uma interface simplificada para um conjunto de módulos complexos. |
| **Lazy Import** | Importação realizada dentro de uma função, não no topo do arquivo. Evita dependências de inicialização. |
| **Signal** | Mecanismo do Django para comunicação desacoplada entre módulos. Um emite, outros escutam. |
| **Service** | Classe que contém lógica de negócio de um módulo. Ponto de entrada principal para operações. |
| **Selector** | Função/classe responsável por consultas (queries) ao banco de dados. Separado de services para reutilização. |
| **Tenant** | Organização/cliente que utiliza a plataforma. Cada tenant tem dados isolados. |
| **RBAC** | Role-Based Access Control — controle de acesso baseado em papéis (roles). |

---

## Anexo B — Checklist de Validação

Use este checklist para validar se um novo módulo está em conformidade com as regras de dependência:

- [ ] O módulo está na camada correta
- [ ] Não há dependências circulares (diretas ou indiretas)
- [ ] Não há imports de módulos de camadas superiores
- [ ] Imports de módulos da mesma camada estão documentados com `# CROSS-LAYER-IMPORT`
- [ ] Imports usam apenas a interface pública dos módulos (services, selectors, signals)
- [ ] O módulo está registrado no `INSTALLED_APPS`
- [ ] A interface pública está documentada neste arquivo (Seção 6)
- [ ] O módulo está no diagrama ASCII (Seção 4)
- [ ] O módulo está na tabela de dependências principal (Seção 2)
- [ ] `python manage.py check_dependencies` passa sem erros

---

> **Documento mantido por:** Equipe de Arquitetura — Company Core
> **Atualizado em:** 2025
> **Próxima revisão:** Após conclusão de cada fase de implementação
