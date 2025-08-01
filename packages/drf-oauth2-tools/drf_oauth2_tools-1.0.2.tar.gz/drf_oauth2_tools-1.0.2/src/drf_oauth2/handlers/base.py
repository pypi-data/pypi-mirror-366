from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from drf_oauth2.models import SocialAccount
from django.contrib.auth import get_user_model
from drf_oauth2.settings import oauth_settings
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class BaseCallbackHandler(ABC):
    @abstractmethod
    def handle_callback(
        self,
        user_info: Dict[str, Any],
        tokens: Dict[str, Any],
        provider: str,
        request=None,
    ) -> Dict[str, Any]:
        """Handle the OAuth callback and return response data"""
        pass

    def get_or_create_user(
        self, user_info: Dict[str, Any], tokens: Dict[str, Any], provider: str
    ) -> User:
        provider_id = user_info.get("provider_id")
        email = user_info.get("email")

        if not provider_id:
            raise ValueError("Provider ID is required")

        try:
            social_account = SocialAccount.objects.get(
                provider=provider, provider_id=provider_id
            )
            user = social_account.user
            self.update_social_account(social_account, user_info, tokens)
            return user
        except SocialAccount.DoesNotExist:
            pass

        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

        if not user:
            if oauth_settings.ALLOW_USER_CREATION:
                user_data = self.extract_user_data(user_info)
                user = User.objects.create_user(**user_data)
                self.create_social_account(user, user_info, tokens, provider)
            else:
                raise AuthenticationFailed("User does not exist")

        return user

    def create_social_account(
        self,
        user: User,
        user_info: Dict[str, Any],
        tokens: Dict[str, Any],
        provider: str,
    ):
        expires_at = None
        if tokens.get("expires_in"):
            expires_at = datetime.now() + timedelta(seconds=tokens["expires_in"])

        SocialAccount.objects.create(
            user=user,
            provider=provider,
            provider_id=user_info.get("provider_id"),
            extra_data=user_info,
            access_token=tokens.get("access_token", ""),
            refresh_token=tokens.get("refresh_token", ""),
            token_expires_at=expires_at,
        )

    def update_social_account(
        self,
        social_account: SocialAccount,
        user_info: Dict[str, Any],
        tokens: Dict[str, Any],
    ):
        social_account.email = user_info.get("email", social_account.email)
        social_account.access_token = tokens.get(
            "access_token", social_account.access_token
        )
        social_account.refresh_token = tokens.get(
            "refresh_token", social_account.refresh_token
        )
        social_account.extra_data = user_info

        if tokens.get("expires_in"):
            social_account.token_expires_at = datetime.now() + timedelta(
                seconds=tokens["expires_in"]
            )

        social_account.save()
        return social_account

    def extract_user_data(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user data for user creation"""
        payload = {}
        for field in oauth_settings.REQUIRED_USER_FIELDS:
            payload[field] = user_info.get(field, "")
        if "username" in payload and username == '':
            username =  user_info.get("email", "") or f"user_{user_info.get('provider_id')}"
        return payload
