import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Sattapana.settings')
django.setup()

from django.contrib.auth.models import User

# Check if admin user exists
if User.objects.filter(username='admin').exists():
    print("✅ Admin user already exists")
    admin = User.objects.get(username='admin')
    print(f"   Username: admin")
    print(f"   Is superuser: {admin.is_superuser}")
    print(f"   Is staff: {admin.is_staff}")
else:
    # Create admin user
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("✅ Admin user created successfully!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Please change the password after first login!")
