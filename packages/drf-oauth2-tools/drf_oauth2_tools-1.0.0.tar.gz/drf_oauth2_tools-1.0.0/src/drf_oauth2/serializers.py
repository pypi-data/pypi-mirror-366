from rest_framework import serializers
from drf_oauth2.settings import oauth_settings
from django.contrib.auth import get_user_model

User = get_user_model()


class OAuthLoginSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=50)
    state = serializers.CharField(required=False)
    redirect_uri = serializers.URLField(required=False)

    def validate_provider(self, value):
        providers = oauth_settings.get_enabled_providers()
        if value.lower() not in providers:
            raise serializers.ValidationError(f"Provider {value} is not enabled")
        return value.lower()


class OAuthCallbackSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=150)
    state = serializers.CharField(required=False)


class OAuthLoginResponseSerializer(serializers.Serializer):
    authorization_url = serializers.URLField()
    provider = serializers.CharField(max_length=50)
    state = serializers.CharField()


class JWTTokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")
    expires_in = serializers.IntegerField(required=False)


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class OAuthCallbackResponseSerializer(serializers.Serializer):
    """Serializer for OAuth callback response"""

    success = serializers.BooleanField(default=True)
    provider = serializers.CharField()
    if oauth_settings.USER_IN_CALLBACK_RESPONSE:
        user = oauth_settings.USER_INFO_RESPONSE_SERIALIZER(required=False)
    tokens = oauth_settings.JWT_TOKEN_RESPONSE_SERIALIZER(
        required=False
    )  # For JWTCallbackHandler
    token = serializers.CharField(required=False)  # For TokenCallbackHandler
