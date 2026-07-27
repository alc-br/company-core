# Settings — Configurações Dinâmicas
## Descrição
Gerenciamento de configurações dinâmicas por tenant e configurações globais do sistema.
## Responsabilidades
- Configurações por organização (TenantSetting)
- Configurações globais do sistema (GlobalSetting)
- Cache de configurações para performance
## Modelos
- TenantSetting: chave-valor por organização e ambiente
- GlobalSetting: chave-valor global
## Dependências
- apps.common (TimestampMixin)
- apps.organizations (Organization)
