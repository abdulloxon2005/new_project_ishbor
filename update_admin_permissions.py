#!/usr/bin/env python
import os
import django

# Django sozlamalari
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from hr_bolim.models import User

# Mavjud admin foydalanuvchilarni yangilash
admin_users = User.objects.filter(role='admin')
print(f"Found {admin_users.count()} admin users")

for user in admin_users:
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"Updated admin user: {user.email}")

print("Admin users updated successfully!")
