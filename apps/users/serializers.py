from rest_framework import serializers
from apps.users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model."""

    display_name = serializers.CharField(
        source="get_display_name", read_only=True
    )
    avatar_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "id", "email", "first_name", "last_name",
            "avatar", "avatar_url", "display_name",
            "bio", "timezone", "language",
            "is_active", "is_staff", "is_superuser",
            "date_joined", "last_login",
        )
        read_only_fields = (
            "id", "email", "is_superuser", "date_joined", "last_login"
        )

    def get_avatar_url(self, obj):
        return obj.avatar_url


class CustomUserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user list views."""

    display_name = serializers.CharField(
        source="get_display_name", read_only=True
    )

    class Meta:
        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "display_name", "is_active")
        read_only_fields = fields


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile fields."""

    class Meta:
        model = CustomUser
        fields = (
            "first_name", "last_name", "avatar", "bio", "timezone", "language",
        )


class CustomUserAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin operations on users."""

    display_name = serializers.CharField(
        source="get_display_name", read_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            "id", "email", "first_name", "last_name", "display_name",
            "bio", "timezone", "language",
            "is_active", "is_staff", "is_superuser",
        )
        read_only_fields = ("id", "email", "display_name")
