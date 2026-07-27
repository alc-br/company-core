# Common — Utilitários Compartilhados

## Descrição
Módulo de utilitários compartilhados entre todos os apps do Company Core. Contém mixins, managers, exceptions, helpers e constantes usados em toda a plataforma.

## Responsabilidades
- Fornecer mixins reutilizáveis para models (TimestampMixin, TenantMixin, SoftDeleteMixin)
- Fornecer managers especializados (TenantManager, ActiveManager)
- Definir hierarquia de exceptions do Service Layer
- Prover helpers para paginação e validação
- Centralizar constantes e enums da plataforma

## Componentes

### Mixins
- `TimestampMixin` — Campos created_at/updated_at
- `TenantMixin` — Escopo de organização/tenant
- `SoftDeleteMixin` — Deleção lógica

### Managers
- `TenantManager` — Filtragem automática por tenant ativo
- `ActiveManager` — Filtragem de registros não deletados

### Exceptions
- `ServiceException` — Base para todas as exceptions de serviço
- `NotFoundException` — Recurso não encontrado
- `PermissionDeniedError` — Sem permissão
- `QuotaExceededError` — Quota excedida
- `ValidationError` — Erro de validação
- `IntegrationError` — Erro de integração externa
- `AIProviderError` — Erro de provedor IA

### Helpers
- `PaginationHelper` — Paginação padronizada
- `ValidationHelper` — Validações comuns

### Constantes
- Enums para status, roles, billing cycles, providers, etc.

## Dependências
- `apps.organizations` (para TenantMixin)

## Público
Todos os componentes são públicos e podem ser importados por qualquer app.
