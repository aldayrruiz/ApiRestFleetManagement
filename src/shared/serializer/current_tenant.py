class CurrentTenantDefault:
    """
    May be applied as a `default=...` value on a serializer field.
    Returns the current tenant.
    """
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.tenant
