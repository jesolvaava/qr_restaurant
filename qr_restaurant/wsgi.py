import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Add this line to define BASE_DIR (should match your settings.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_restaurant.settings')

application = get_wsgi_application()

# Configure WhiteNoise
application = WhiteNoise(
    application,
    root=os.path.join(BASE_DIR, 'staticfiles'),
    max_age=31536000  # 1 year cache
)
application.add_files(os.path.join(BASE_DIR, 'media'), prefix='/media/')
