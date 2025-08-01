from .base import BaseOAuthProvider
from drf_oauth2.settings import oauth_settings

class FacebookOAuthProvider(BaseOAuthProvider):
    PROVIDER = "facebook"
    SCOPE_DELIMETER = ","
    AUTHORIZATION_URL = "https://www.facebook.com/v12.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v12.0/oauth/access_token"
    USER_INFO_URL = "https://graph.facebook.com/v12.0/me"
    DEFAULT_SCOPES = ["email", "public_profile"]
    PROVIDER_ID_FIELD_NAME = "id"

    def get_user_info_headers(self, access_token):
        return {}
    
    def get_user_info_params(self, access_token):
        return {
            'access_token': access_token,
            'fields': oauth_settings.REQUIRED_USER_FIELDS
        }