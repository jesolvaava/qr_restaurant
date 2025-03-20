import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_restaurant.settings')
django.setup()

# Now you can import Django models
from restaurant.models import Table
import qrcode

def generate_qr_codes():
    tables = Table.objects.all()
    for table in tables:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Replace with your domain or local development URL
        qr.add_data(f"http://127.0.0.1:8000/menu/{table.id}/")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(f"restaurant/static/qr_codes/table_{table.table_number}.png")

if __name__ == "__main__":
    generate_qr_codes()