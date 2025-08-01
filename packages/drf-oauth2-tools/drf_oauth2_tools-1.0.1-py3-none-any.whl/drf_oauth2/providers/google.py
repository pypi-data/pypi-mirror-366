from .base import BaseOAuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    PROVIDER = "google"
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
    DEFAULT_SCOPES = ["openid", "email", "profile"]
    SCOPE_DELIMETER = " "

    def get_auth_params(self) -> dict:
        return {"access_type": "offline"}
