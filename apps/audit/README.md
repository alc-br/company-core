# Audit — Logs de Auditoria
## Descrição
Sistema de auditoria para rastrear todas as ações relevantes dentro da plataforma.
## Responsabilidades
- Registro de ações de usuários e sistemas
- Rastreamento de IP e User Agent
- Metadados flexíveis via JSONField
- Indexação otimizada para consultas
## Modelo
- AuditLog: registro de cada ação auditável
## Dependências
- apps.common (TimestampMixin)
- apps.organizations (Organization)
