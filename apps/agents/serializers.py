from rest_framework import serializers


class AgentSerializer(serializers.Serializer):
    """Basic agent serializer."""
    name = serializers.CharField()
    agent_type = serializers.CharField()
