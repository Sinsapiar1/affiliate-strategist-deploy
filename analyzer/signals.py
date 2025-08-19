from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.create(user=instance)
            # Inicializar límites por plan free
            instance.profile.analyses_limit_monthly = 5
            instance.profile.analyses_this_month = 0
            instance.profile.save(update_fields=['analyses_limit_monthly', 'analyses_this_month'])
        except Exception:
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

