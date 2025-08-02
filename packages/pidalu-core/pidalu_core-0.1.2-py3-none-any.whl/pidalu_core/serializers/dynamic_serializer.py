from django.utils.functional import cached_property
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` keyword argument
    to control which fields should be included in the serialized output.
    """

    def __init__(self, *args, **kwargs):
        # Extract 'fields' before passing to superclass
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    @cached_property
    def request(self):
        """
        Returns the request object if available, otherwise None.
        This is useful for serializers that need access to the request context.
        """
        return self.context.get("request", None)


class DynamicFieldsSerializer(serializers.Serializer):
    """
    A regular DRF Serializer that supports dynamic field inclusion like the model version.
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class DummySerializer(serializers.Serializer):
    """
    An empty serializer that accepts and returns nothing.
    Useful as a placeholder or no-op serializer.
    """

    pass
