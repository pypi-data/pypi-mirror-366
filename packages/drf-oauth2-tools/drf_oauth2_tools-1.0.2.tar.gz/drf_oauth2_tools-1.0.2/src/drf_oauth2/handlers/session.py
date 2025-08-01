from .base import BaseCallbackHandler


class SessionCallbackHandler(BaseCallbackHandler):
    def handle_callback(self, user_info, tokens, provider, request=None):
        from django.contrib.auth import login

        user = self.get_or_create_user(user_info, tokens, provider)

        if request:
            login(request, user)

        return {"success": True, "provider": provider}
