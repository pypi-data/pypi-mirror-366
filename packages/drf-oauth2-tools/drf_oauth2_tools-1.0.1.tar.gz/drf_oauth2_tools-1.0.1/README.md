# README.md

# DRF Social OAuth


A highly extensible Django REST Framework library for OAuth social login with customizable providers and handlers.

## ✨ Features

- 🔐 **Multiple OAuth Providers**: Google, Facebook, GitHub, Twitter out of the box
- 🎛️ **Highly Customizable**: Custom providers, handlers, and response formats  
- 🏗️ **DRF Native**: Built with ViewSets, Serializers, and proper REST patterns
- 🔑 **Multiple Auth Types**: JWT, Sessions, DRF Tokens supported
- 🛡️ **Security First**: CSRF protection, proper error handling, secure defaults
- 📊 **Admin Integration**: Django admin interface for social accounts
- 🧪 **Well Tested**: Comprehensive test suite with high coverage
- 📚 **Great Documentation**: Detailed docs with examples

## 🚀 Quick Start

### Installation

```bash
pip install drf-oauth2-tools
```

### Basic Setup

1. Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'drf_oauth2',
]
```

2. Configure OAuth providers in `settings.py`:

```python
OAUTH_PROVIDERS = {
    'GOOGLE': {
        'CLIENT_ID': 'your-google-client-id',
        'CLIENT_SECRET': 'your-google-client-secret',
    },
    'GITHUB': {
        'CLIENT_ID': 'your-github-client-id',
        'CLIENT_SECRET': 'your-github-client-secret',
    },
}
```

3. Add URLs to your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('drf_oauth2.urls')),
]
```

4. Run migrations:

```bash
python manage.py migrate
```

## 🎯 Usage

### API Endpoints

```bash           # List available providers
GET  /api/auth/oauth/login/google/        # Initiate Google OAuth
GET  /api/auth/oauth/callback/google/     # Handle OAuth callback
```

### Frontend Integration

```javascript
// Get authorization URL
const response = await fetch('/api/auth/oauth/login/google/');
const data = await response.json();

// Redirect user to OAuth provider
window.location.href = data.authorization_url;

// After callback, you'll receive JWT tokens
```


## 🔧 Advanced Configuration

### Custom Callback Handler

```python
from drf_oauth2.handlers import BaseCallbackHandler

class CustomHandler(BaseCallbackHandler):
    def handle_callback(self, user_info, tokens, provider, request=None):
        user = self.get_or_create_user(user_info, provider)
        return {
            'success': True,
            'user_id': user.id,
            'custom_data': 'your custom response'
        }

# Configure in settings
OAUTH_PROVIDERS = {
    'GOOGLE': {
        'CLIENT_ID': 'your-client-id',
        'CLIENT_SECRET': 'your-client-secret',   
    },
    "CALLBACK_HANDLER_CLASS": 'myapp.handlers.CustomHandler',
}
```

### Custom OAuth Provider

```python
from drf_oauth2.providers import BaseOAuthProvider, register_provider

class LinkedInProvider(BaseOAuthProvider):
    PROVIDER = "linkedin"
    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    
    # ... implement other required methods

# Configure in settings
OAUTH_PROVIDERS = {
    'LINKEDIN': {
        'CLIENT_ID': 'your-client-id',
        'CLIENT_SECRET': 'your-client-secret',
        "PROVIDER_CLASS": "myapp.providers.linkedin.LinkedInProvider'
    },
}

```

## 📋 Supported Providers

- **Google** - `google`
- **Facebook** - `facebook` 
- **GitHub** - `github`
- **Twitter** - `twitter`
- **Custom providers** - Easy to add

## 🔐 Supported Authentication Types

- **JWT Tokens** (via `djangorestframework-simplejwt`) (DEFAULT)
- **Django Sessions** 
- **DRF Tokens**
- **Custom handlers**


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django REST Framework team
- OAuth provider documentation
- Contributors and users

---


Made with ❤️ by [AstralMortem](https://github.com/AstralMortem)

