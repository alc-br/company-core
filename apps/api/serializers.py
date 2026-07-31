class NullToBlankMixin:
    """Campos de texto opcionais (blank=True, null=False no model Django)
    devem aceitar null como equivalente a string vazia. Varios formularios
    do frontend mandam null explicito no campo vazio em vez de omitir a
    chave ou mandar "" — sem isso o DRF rejeita com "este campo pode nao
    ser nulo" mesmo o campo sendo opcional.

    Declare NULLABLE_FIELDS na subclasse para os campos que devem continuar
    aceitando null de verdade (FK, DateField, M2M). Declare JSON_OBJECT_FIELDS
    / JSON_ARRAY_FIELDS para JSONField com default=dict/list — nulo vira {}
    ou [], nao "" (senao quebra a validacao do JSONField do mesmo jeito).
    """

    NULLABLE_FIELDS = frozenset()
    JSON_OBJECT_FIELDS = frozenset()
    JSON_ARRAY_FIELDS = frozenset()

    def to_internal_value(self, data):
        if hasattr(data, "keys"):
            data = dict(data)
            for key in list(data.keys()):
                if data[key] is not None or key in self.NULLABLE_FIELDS:
                    continue
                if key in self.JSON_OBJECT_FIELDS:
                    data[key] = {}
                elif key in self.JSON_ARRAY_FIELDS:
                    data[key] = []
                else:
                    data[key] = ""
        return super().to_internal_value(data)
