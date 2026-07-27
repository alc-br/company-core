# Jobs — Gerenciamento de Tarefas Agendadas
## Descrição
Sistema de gerenciamento de jobs com prioridade, retry e agendamento.
## Responsabilidades
- Fila de jobs com prioridade
- Retry automático com limite configurável
- Tracking de execução (início, conclusão, erro)
- Agendamento de jobs futuros
## Modelo
- Job: registro de job com status, prioridade e tracking
## Dependências
- apps.common (TimestampMixin, JobStatus)
- apps.organizations (Organization)
