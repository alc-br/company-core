# Integrations — Integrações Externas
## Descrição
Gerenciamento de integrações com serviços externos, com credenciais criptografadas e log de requisições.
## Responsabilidades
- Registro de integrações (Stripe, SendGrid, etc.)
- Credenciais criptografadas
- Health check periódico
- Log completo de requisições e respostas
## Modelos
- Integration: configuração da integração externa
- IntegrationLog: registro de cada chamada à integração
## Dependências
- apps.common (TimestampMixin)
- apps.organizations (Organization)
