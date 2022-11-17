"""
ASGI config for stockproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""
#problme while deploying => https://stackoverflow.com/questions/71119024/improperlyconfigured-requested-setting-installed-apps-but-settings-are-not-con

import os
import django


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from mainapp.routings import websocket_urlpatters
from channels.security.websocket import AllowedHostsOriginValidator


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockproject.settings')
django.setup()

application = ProtocolTypeRouter(
    {
    "http":get_asgi_application(),
     "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
               websocket_urlpatters
            )
        )
    ),

    }
    
)
