from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            # Usar get_or_create para evitar errores de UNIQUE por duplicado
            profile, _ = UserProfile.objects.get_or_create(user=instance, defaults={
                'analyses_limit_monthly': 5,
                'analyses_this_month': 0,
            })
            # Asegurar límites iniciales
            if profile.analyses_limit_monthly != 5 or profile.analyses_this_month != 0:
                profile.analyses_limit_monthly = 5
                profile.analyses_this_month = 0
                profile.save(update_fields=['analyses_limit_monthly', 'analyses_this_month'])
        except Exception:
            # No bloquear creación de usuario por fallo en perfil
            pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Garantiza que exista el perfil
    try:
        instance.profile.save()
    except Exception:
        try:
            UserProfile.objects.get_or_create(user=instance)
        except Exception:
            pass

