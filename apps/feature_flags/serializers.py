from rest_framework import serializers
from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class FeatureFlagAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlagAssignment
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
