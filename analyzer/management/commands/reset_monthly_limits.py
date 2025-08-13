# analyzer/management/commands/reset_monthly_limits.py

from django.core.management.base import BaseCommand
from analyzer.models import UserProfile
from django.utils import timezone

class Command(BaseCommand):
    help = 'Resetea los contadores mensuales de análisis'
    
    def handle(self, *args, **options):
        profiles = UserProfile.objects.all()
        reset_count = 0
        
        for profile in profiles:
            old_count = profile.analyses_this_month
            profile.reset_monthly_counter_if_needed()
            
            if profile.analyses_this_month == 0 and old_count > 0:
                reset_count += 1
                self.stdout.write(
                    f"Reset: {profile.user.username} ({old_count} → 0)"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Reseteados {reset_count} usuarios')
        )