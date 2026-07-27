# Billing — Stripe Billing

## Descrição
Módulo de gestão de billing via Stripe. Controla planos, assinaturas, faturas e integração com o Stripe.

## Responsabilidades
- Gestão de planos e preços
- Criação/cancelamento de assinaturas
- Sincronização com Stripe webhooks
- Registro de faturas

## Modelos
- `Plan` — Plano de assinatura com preços e limites
- `Subscription` — Assinatura ativa de uma organização
- `Invoice` — Fatura gerada pelo Stripe

## Dependências
- `apps.organizations`, `apps.common`
