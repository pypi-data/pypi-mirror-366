from typing import Any, Dict
import requests
from functools import cached_property
from urllib.parse import urlencode


class BaseOAuthProvider:
    PROVIDER: str = ""
    SCOPE_DELIMETER: str = ""
    AUTHORIZATION_URL: str = ""
    TOKEN_URL: str = ""
    USER_INFO_URL: str = ""
    DEFAULT_SCOPES: list = []
    PROVIDER_ID_FIELD_NAME: str = "sub"

    def __init__(self, provider_config: dict):
        self.config = provider_config

    @cached_property
    def client_id(self):
        return self.config.get("CLIENT_ID")

    @cached_property
    def client_secret(self):
        return self.config.get("CLIENT_SECRET")

    @cached_property
    def scope(self):
        scope = self.config.get("SCOPE", self.DEFAULT_SCOPES)
        if isinstance(scope, list):
            return self.SCOPE_DELIMETER.join(scope)
        elif isinstance(scope, str):
            return scope
        else:
            raise ValueError("Invalid scope")

    @cached_property
    def extra_auth_params(self):
        return self.config.get("EXTRA_AUTH_PARAMS", {})

    @cached_property
    def redirect_uri(self):
        return self.config.get("REDIRECT_URI")

    @cached_property
    def response_type(self):
        return self.config.get("RESPONSE_TYPE", "code")

    @cached_property
    def provider_name(self):
        return self.PROVIDER

    @cached_property
    def grant_type(self):
        return self.config.get("GRANT_TYPE", "authorization_code")

    @cached_property
    def token_headers(self):
        return {}

    def get_authorization_url(self, state: str = None):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": self.response_type,
            **self.extra_auth_params,
        }

        if state:
            params["state"] = state

        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": self.grant_type,
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(self.TOKEN_URL, data=data, headers=self.token_headers)
        return self.decode_token_response(response)

    def decode_token_response(self, response: requests.Response) -> Dict[str, Any]:
        return response.json()

    def get_user_info_headers(self, access_token: str) -> Dict[str, str]:
        """Get headers for user info request"""
        return {"Authorization": f"Bearer {access_token}"}

    def get_user_info_params(self, access_token: str) -> Dict[str, str]:
        """Get parameters for user info request"""
        return {}

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information using access token"""
        headers = self.get_user_info_headers(access_token)
        params = self.get_user_info_params(access_token)

        response = requests.get(self.USER_INFO_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def normalize_user_info(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        from drf_oauth2.settings import oauth_settings

        user_fields = oauth_settings.REQUIRED_USER_FIELDS
        result = {k: user_info.get(k, "") for k in user_fields}

        # Ensure we have provider_in
        if "provider_id" not in result:
            result["provider_id"] = user_info.get(self.PROVIDER_ID_FIELD_NAME, "")

        # Ensure we have email
        if "email" not in result:
            result["email"] = user_info.get("email", "")

        return result
