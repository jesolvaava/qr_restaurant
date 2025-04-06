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

# Create staticfiles directory if it doesn't exist
static_root = os.path.join(os.path.dirname(__file__), 'staticfiles')
os.makedirs(static_root, exist_ok=True)

application = WhiteNoise(
    application,
    root=static_root,  # Now using the created directory
    max_age=31536000  # 1 year cache
)
application.add_files('/opt/render/project/src/media', prefix='/media/')
