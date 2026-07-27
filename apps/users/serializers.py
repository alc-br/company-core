from rest_framework import serializers
from apps.users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ImageField(source="avatar", read_only=True)
    display_name = serializers.CharField(source="get_display_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "id", "email", "first_name", "last_name",
            "avatar", "avatar_url", "display_name",
            "bio", "timezone", "language",
            "is_active", "is_staff", "is_superuser",
            "date_joined", "last_login",
        )
        read_only_fields = ("id", "date_joined", "last_login", "is_superuser")
