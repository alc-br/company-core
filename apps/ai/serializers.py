from rest_framework import serializers


class AIModelSerializer(serializers.Serializer):
    """Basic AI model serializer."""
    name = serializers.CharField()
    provider = serializers.CharField()
    model_id = serializers.CharField()
