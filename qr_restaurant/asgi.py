"""
ASGI config for qr_restaurant project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# qr_restaurant/asgi.py
# qr_restaurant/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_restaurant.settings')

application = get_asgi_application()