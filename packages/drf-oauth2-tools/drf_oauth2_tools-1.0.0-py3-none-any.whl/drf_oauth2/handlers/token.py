from .base import BaseCallbackHandler


class TokenCallbackHandler(BaseCallbackHandler):
    def handle_callback(self, user_info, tokens, provider, request=None):
        from rest_framework.authtoken.models import Token

        user = self.get_or_create_user(user_info, tokens, provider)
        token, created = Token.objects.get_or_create(user=user)

        return {"success": True, "provider": provider, "token": token.key, "user": user}
