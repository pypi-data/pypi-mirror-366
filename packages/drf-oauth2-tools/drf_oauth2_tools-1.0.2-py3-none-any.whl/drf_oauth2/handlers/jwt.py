from .base import BaseCallbackHandler


class JWTCallbackHandler(BaseCallbackHandler):
    def handle_callback(self, user_info, tokens, provider, request=None):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
        except ImportError:
            raise ImportError(
                "djangorestframework-simplejwt is required to JWTCallbackHandler"
            )

        user = self.get_or_create_user(user_info, tokens, provider)
        refresh = RefreshToken.for_user(user)

        return {
            "success": True,
            "provider": provider,
            "tokens": {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "token_type": "Bearer",
                "expires_in": refresh.access_token.lifetime.total_seconds(),
            },
        }
