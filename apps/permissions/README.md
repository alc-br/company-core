# Permissions — RBAC

## Descrição
Sistema de controle de acesso baseado em papéis (RBAC). Permite definir papéis customizados com conjuntos de permissões granulares por organização.

## Responsabilidades
- Definição de permissões granulares por módulo
- Criação de papéis customizados por organização
- Verificação de permissões de usuário
- Integração com o sistema de memberships

## Modelos
- `Permission` — Permissão granular (código, módulo, descrição)
- `Role` — Papel com conjunto de permissões
- `RolePermission` — Relação N:N entre papéis e permissões

## Dependências
- `apps.organizations`, `apps.common`
