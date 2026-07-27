# Workflows — Automações e Pipelines
## Descrição
Motor de workflows para automatizar processos multi-etapa da plataforma.
## Responsabilidades
- Definição de workflows com etapas configuráveis
- Execução e tracking de workflows
- Log detalhado por etapa
- Suporte a JSON para configuração e dados
## Modelos
- Workflow: definição do workflow
- WorkflowExecution: instância de execução
- WorkflowStepLog: log de cada etapa
## Dependências
- apps.common (TimestampMixin, WorkflowExecutionStatus)
- apps.organizations (Organization)
