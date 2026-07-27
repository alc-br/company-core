# Storage — Armazenamento de Arquivos
## Descrição
Gerenciamento de backends de storage e objetos armazenados com metadados.
## Responsabilidades
- Configuração de múltiplos backends (S3, GCS, local)
- Upload e gerenciamento de objetos
- Checksum para integridade
- Metadados por objeto
## Modelos
- StorageBackendConfig: configuração do backend de storage
- StoredObject: registro de objeto armazenado
## Dependências
- apps.common (TimestampMixin, StorageBackendType)
- apps.organizations (Organization)
