from django.conf import settings
from django.urls import reverse
from django.test.signals import setting_changed
from rest_framework.settings import APISettings
from django.utils.module_loading import import_string
from drf_oauth2.providers.base import BaseOAuthProvider

USER_SETTINGS = getattr(settings, "OAUTH_PROVIDERS", None)


class OAuthSettings(APISettings):
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.defaults = defaults or DEFAULTS
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    def __check_user_settings(self, user_settings):
        for settings_name, setting in user_settings.items():
            if isinstance(setting, dict) and settings_name in user_settings:
                user_settings[settings_name] = {
                    **self.defaults[settings_name],
                    **setting,
                }

        return user_settings

    def get_enabled_providers(self):
        enabled_providers = []
        for provider, config in self.user_settings.items():
            if isinstance(config, dict):
                if config.get("CLIENT_ID", None) and config.get("CLIENT_SECRET", None):
                    enabled_providers.append(provider.lower())
        return enabled_providers

    def get_provider_class(self, provider_name: str):
        provider_class = self.user_settings.get(provider_name.upper(), {}).get(
            "PROVIDER_CLASS", None
        )
        if isinstance(provider_class, str):
            provider_class = import_string(provider_class)
            if issubclass(provider_class, BaseOAuthProvider):
                return provider_class
        raise ValueError("Invalid provider class")

    def get_provider_config(self, provider_name: str, request=None):
        provider_config = self.user_settings.get(provider_name.upper())
        if not provider_config:
            return None

        if "REDIRECT_URI" not in provider_config and request:
            provider_config["REDIRECT_URI"] = request.build_absolute_uri(
                reverse("oauth-callback", kwargs={"provider": provider_name.lower()})
            )
        return provider_config


GOOGLE_DEFAULTS = {
    "PROVIDER_CLASS": "drf_oauth2.providers.google.GoogleOAuthProvider",
    "RESPONSE_TYPE": "code",
    "GRANT_TYPE": "authorization_code",
}

GITHUB_DEFAULTS = {
    "PROVIDER_CLASS": "drf_oauth2.providers.github.GitHubOAuthProvider",
    "RESPONSE_TYPE": "code",
    "GRANT_TYPE": "authorization_code",
}

FACEBOOK_DEFAULTS = {
    'PROVIDER_CLASS': 'drf_oauth2.providers.facebook.FacebookOAuthProvider',
    'RESPONSE_TYPE': 'code',
    'GRANT_TYPE': 'authorization_code',
}

DEFAULTS = {
    "REQUIRED_USER_FIELDS": ["email", "username"],
    "CALLBACK_HANDLER_CLASS": "drf_oauth2.handlers.jwt.JWTCallbackHandler",
    "JWT_TOKEN_RESPONSE_SERIALIZER": "drf_oauth2.serializers.JWTTokenResponseSerializer",
    "USER_INFO_RESPONSE_SERIALIZER": "drf_oauth2.serializers.UserInfoSerializer",
    "USER_IN_CALLBACK_RESPONSE": True,
    "GOOGLE": GOOGLE_DEFAULTS,
    "GITHUB": GITHUB_DEFAULTS,
    "FACEBOOK": FACEBOOK_DEFAULTS,
}

IMPORT_STRINGS = (
    "CALLBACK_HANDLER_CLASS",
    "JWT_TOKEN_RESPONSE_SERIALIZER",
    "USER_INFO_RESPONSE_SERIALIZER",
)


oauth_settings = OAuthSettings(USER_SETTINGS, DEFAULTS)


def reload_oauth_settings(*args, **kwargs) -> None:  # pragma: no cover
    global oauth_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "OAUTH_PROVIDERS":
        oauth_settings = APISettings(value, DEFAULTS)


setting_changed.connect(reload_oauth_settings)
