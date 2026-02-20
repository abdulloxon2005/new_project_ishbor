from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AuditLog, User

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditLog.objects.create(
        user=user,
        action="Login",
        ip_address=ip
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditLog.objects.create(
        action=f"Login Failed: {credentials.get('username')}",
        ip_address=ip
    )

@receiver(post_save, sender=User)
def set_admin_permissions(sender, instance, created, **kwargs):
    """Admin roliga ega foydalanuvchilarga Django admin kirish huquqini berish"""
    if created and instance.role == 'admin':
        instance.is_staff = True
        instance.is_superuser = True
        instance.save(update_fields=['is_staff', 'is_superuser'])
