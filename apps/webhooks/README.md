# Webhooks — Endpoints e Entregas
## Descrição
Sistema de webhooks para notificar clientes sobre eventos da plataforma.
## Responsabilidades
- Registro de endpoints de webhook por organização
- Fila de entregas com retry automático
- Suporte a múltiplos eventos por endpoint
- Secret criptografado para assinatura
## Modelos
- WebhookEndpoint: URL e configuração do endpoint
- WebhookDelivery: registro de cada tentativa de entrega
## Dependências
- apps.common (TimestampMixin)
- apps.organizations (Organization)
- Celery (para entrega assíncrona)
