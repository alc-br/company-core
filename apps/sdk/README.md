# SDK — Facade de Integração
## Descrição
SDK interno que fornece uma interface simplificada para os módulos do Company Core.
## Responsabilidades
- Facade para Billing (BillingSDK)
- Facade para Quotas (QuotaSDK)
- Facade para AI (AISDK)
- Facade para Storage (StorageSDK)
- Facade para Notifications (NotificationSDK)
## Submódulos
- billing.py: BillingSDK
- quotas.py: QuotaSDK
- ai.py: AISDK
- storage.py: StorageSDK
- notifications.py: NotificationSDK
## Dependências
- apps.billing
- apps.quotas
- apps.ai
- apps.storage
- apps.notifications
