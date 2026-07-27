# Notifications — Canais, Templates e Envio
## Descrição
Sistema de notificações multi-canal com templates e log de envio.
## Responsabilidades
- Gerenciamento de canais de notificação (email, SMS, push, webhook)
- Templates de notificação com suporte HTML/Text
- Log de todas as notificações enviadas
- Configuração por organização
## Modelos
- NotificationChannel: canal de envio (email, SMS, etc.)
- NotificationTemplate: template reutilizável de notificação
- NotificationLog: registro de cada notificação enviada
## Dependências
- apps.common (TimestampMixin, NotificationChannelType)
- apps.organizations (Organization)
