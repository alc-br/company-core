# Usage — Métricas de Uso
## Descrição
Registro e agregação de métricas de uso da plataforma por organização.
## Responsabilidades
- Registro de métricas de uso (API calls, storage, etc.)
- Agregação por período
- Suporte a múltiplos tipos de métrica
## Modelo
- UsageRecord: registro de uso com tipo, valor, unidade e período
## Dependências
- apps.common (TimestampMixin, MetricType)
- apps.organizations (Organization)
