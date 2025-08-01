from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_oauth2.settings import oauth_settings
from drf_oauth2 import serializers
from rest_framework.serializers import ValidationError
import secrets
from django.shortcuts import redirect
from drf_oauth2.providers.base import BaseOAuthProvider

# Add suport for drf_spectacular
try:
    from drf_spectacular.utils import extend_schema
except ImportError:
    extend_schema = lambda **kwargs: lambda x: x


class OAuthViewSet(GenericViewSet):
    def get_queryset(self):
        return None

    def get_provider(self, provider_name: str, request=None) -> BaseOAuthProvider:
        provider_config = oauth_settings.get_provider_config(
            provider_name.upper(), request
        )
        if (
            not provider_config
            or provider_name not in oauth_settings.get_enabled_providers()
        ):
            raise ValidationError(f"Provider {provider_name} is not enabled")

        provider_class = oauth_settings.get_provider_class(provider_name.upper())
        if not provider_class:
            raise ValidationError(f"Provider class for {provider_name} is not enabled")

        return provider_class(provider_config)

    @extend_schema(responses=serializers.OAuthLoginResponseSerializer())
    @action(
        detail=False,
        methods=["get", "post"],
        url_path="login/(?P<provider>[^/.]+)",
        serializer_class=serializers.OAuthLoginSerializer,
    )
    def login(self, request, provider=None):
        data = {"provider": provider, **request.query_params.dict()}
        if request.method == "POST":
            data.update(request.data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            oauth_provider = self.get_provider(provider, request)
            state = serializer.validated_data.get("state") or secrets.token_urlsafe(32)
            request.session[f"{provider}_oauth_state"] = state

            redirect_uri = serializer.validated_data.get("redirect_uri")
            if redirect_uri:
                request.session[f"{provider}_oauth_redirect_uri"] = redirect_uri

            auth_url = oauth_provider.get_authorization_url(state=state)
            response_payload = {
                "authorization_url": auth_url,
                "provider": provider,
                "state": state,
            }

            response_serializer = serializers.OAuthLoginResponseSerializer(
                response_payload
            )
            return Response(response_serializer.data)
        except Exception as e:
            raise e
    
    @extend_schema(responses=serializers.OAuthCallbackResponseSerializer())
    @action(
        detail=False,
        methods=["get", "post"],
        url_path="callback/(?P<provider>[^/.]+)",
        serializer_class=serializers.OAuthCallbackSerializer,
    )
    def callback(self, request, provider=None):
        data = {"provider": provider, **request.query_params.dict()}
        if request.method == "POST":
            data.update(request.data)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            code = serializer.validated_data.get("code")
            state = serializer.validated_data.get("state")

            if not code:
                raise ValidationError("Missing code parameter")

            # Get provider configuration
            oauth_provider = self.get_provider(provider, request)

            # Verify state for CSRF protection
            session_state = request.session.get(f"{provider}_oauth_state")
            if not session_state or session_state != state:
                raise ValidationError("Invalid state parameter")

            # Exchange code for tokens
            tokens = oauth_provider.exchange_code_for_token(code, state)

            # Get user info
            raw_user_info = oauth_provider.get_user_info(tokens["access_token"])
            user_info = oauth_provider.normalize_user_info(raw_user_info)

            # Get and execute callback handler
            handler_class = oauth_settings.CALLBACK_HANDLER_CLASS
            handler = handler_class()
            result = handler.handle_callback(user_info, tokens, provider, request)

            # Get next URL if stored
            redirect_uri = request.session.pop(f"{provider}_oauth_redirect_uri", None)
            if redirect_uri:
                result["redirect_url"] = redirect_uri

            # Clean up session
            request.session.pop(f"{provider}_oauth_state", None)

            # Handle redirect for session-based authentication
            if request.GET.get("redirect", "").lower() == "true" and redirect_uri:
                return redirect(redirect_uri)

            response_serializer = serializers.OAuthCallbackResponseSerializer(result)
            return Response(response_serializer.data)

        except Exception as e:
            raise e
