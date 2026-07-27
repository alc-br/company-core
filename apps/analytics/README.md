# Analytics — Eventos e Agregações
## Descrição
Sistema de analytics para rastrear eventos de usuário e gerar agregações por período.
## Responsabilidades
- Registro de eventos de analytics
- Agregação de métricas por período e módulo
- Suporte a metadados flexíveis
## Modelos
- AnalyticsEvent: evento individual com tipo, módulo e metadados
- AnalyticsAggregation: agregação pré-calculada por período/módulo/métrica
## Dependências
- apps.common (TimestampMixin)
- apps.organizations (Organization)
