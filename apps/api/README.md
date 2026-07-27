# API — Gerenciamento de Chaves de API
## Descrição
Gerenciamento de chaves de API, tokens de acesso pessoal e service accounts.
## Responsabilidades
- Geração e validação de API Keys (cc_live_*)
- Personal Access Tokens para usuários
- Service Accounts para integrações máquina-a-máquina
- Autenticação por API Key
- Paginação e throttling padronizados
## Modelos
- APIKey: chave de API com hash, prefixo, scopes e expiração
- PersonalAccessToken: token de acesso pessoal
- ServiceAccount: conta de serviço para automação
## Módulos Extras
- authentication.py: APIKeyAuthentication
- pagination.py: StandardizedPagination
- exception_handler.py: standard_exception_handler
- throttling.py: TenantRateThrottle
## Dependências
- apps.common (TimestampMixin)
- apps.organizations (Organization)
- djangorestframework
