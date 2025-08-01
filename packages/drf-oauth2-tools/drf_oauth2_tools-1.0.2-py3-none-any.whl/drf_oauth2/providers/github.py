from .base import BaseOAuthProvider
from urllib.parse import parse_qs


class GitHubOAuthProvider(BaseOAuthProvider):
    PROVIDER = "github"
    SCOPE_DELIMETER = " "
    AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    DEFAULT_SCOPES = ["user", "email"]
    PROVIDER_ID_FIELD_NAME = "id"

    def get_user_info_headers(self, access_token):
        return {"Authorization": f"token {access_token}"}

    def decode_token_response(self, response):
        tokens = response.text
        parsed = parse_qs(tokens)
        result = {k: v[0] for k, v in parsed.items()}
        return result
    