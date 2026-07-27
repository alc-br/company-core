# Organizations — Multi-Tenancy

## Descrição
Módulo de gerenciamento de organizações, times, convites e membros. Implementa o modelo multi-tenant da plataforma Company Core.

## Responsabilidades
- Gerenciamento de organizações (tenants)
- Gestão de membros e papéis (Owner, Admin, Member, Viewer)
- Sistema de convites por email
- Middleware de tenant para injeção do tenant ativo
- Armazenamento de tenant em thread-local para uso em tasks assíncronas

## Modelos
- `Organization` — Representa um tenant/organização
- `Membership` — Vínculo entre usuário e organização com papel e status
- `Invitation` — Convite para participar de uma organização

## Serviços
- `OrganizationService.create_organization()` — Cria organização com owner
- `OrganizationService.invite_member()` — Convida novo membro
- `OrganizationService.accept_invitation()` — Aceita convite
- `OrganizationService.remove_member()` — Remove membro
- `OrganizationService.update_member_role()` — Altera papel

## Selectors
- `get_organization_by_id()` — Busca organização por ID
- `get_organization_by_slug()` — Busca por slug
- `get_user_organizations()` — Organizações de um usuário
- `get_organization_members()` — Membros de uma organização
- `check_user_is_member()` — Verifica se é membro
- `get_user_role()` — Papel do usuário

## Dependências
- `apps.common` (mixins, constants, exceptions)

## Integração com Pegasus
- Extende o CustomUser do Pegasus via ForeignKey
- Usa allauth para autenticação
