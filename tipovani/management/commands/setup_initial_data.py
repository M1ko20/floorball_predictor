from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tipovani.models import UserProfile, Team

class Command(BaseCommand):
    help = 'Nastaví počáteční data pro aplikaci'

    def handle(self, *args, **options):
        # Vytvořit uživatele
        users_data = [
            ('AdamChoma', 'druhyAdam', False),
            ('Bc.Peterkys', 'abbMistr68', False),
            ("PanMarcel", 'Zkusenosti',False),
            ('Host1', 'AdamNaMeZapomnel', False),
            ('Host2', 'NereklJsemZeHraju', False),
            ('TOP1CENTR', 'Hesloheslo', True)
        ]
        
        for username, password, is_staff in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'is_staff': is_staff,
                    'is_superuser': is_staff,
                }
            )
            if created:
                user.set_password(password)
                user.save()
                UserProfile.objects.get_or_create(user=user)
                self.stdout.write(f'Vytvořen uživatel: {username}')
            else:
                self.stdout.write(f'Uživatel {username} již existuje')
        
        # Vytvořit týmy
        teams = [
            'ACEMA Sparta Praha',
            'BA SOKOLI Pardubice',
            'ESA logistika Tatran Střešovice',
            'FAT PIPE FLORBAL CHODOV',
            'FBC 4CLEAN Česká Lípa',
            'FBC ČPP Bystroň Group OSTRAVA',
            'FBC Liberec',
            'FBŠ Hummel Hattrick Brno',
            'Florbal Ústí',
            'HDT.cz Florbal Vary Bohemians',
            'Kanonýři Kladno',
            'Předvýběr.CZ Florbal MB',
            'TJ Sokol Královské Vinohrady',
            'SC NATIOS Vítkovice',
        ]
        
        for team_name in teams:
            team, created = Team.objects.get_or_create(name=team_name)
            if created:
                self.stdout.write(f'Vytvořen tým: {team_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Počáteční data byla úspěšně nastavena!')
        )