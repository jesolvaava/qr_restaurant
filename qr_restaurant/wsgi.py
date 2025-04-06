"""
WSGI config for qr_restaurant project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_restaurant.settings')

application = get_wsgi_application()
application = WhiteNoise(
    application,
    root=os.path.join(os.path.dirname(__file__), 'staticfiles'),
    max_age=31536000  # 1-year cache for static files
)
application.add_files('/opt/render/project/src/media', prefix='/media/')

# Media files configuration
media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
application.add_files(media_root, prefix='/media/')
