import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin superuser from environment variables (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'))
        parser.add_argument('--email', default=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'))
        parser.add_argument('--password', default=os.environ.get('DJANGO_SUPERUSER_PASSWORD'))

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if not password:
            self.stderr.write(self.style.ERROR(
                'Password required. Set DJANGO_SUPERUSER_PASSWORD env var or pass --password.'
            ))
            return

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.role != 'ADMIN':
                user.role = 'ADMIN'
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.WARNING(f'Updated existing user "{username}" to ADMIN role.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" already exists. Skipping.'))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.role = 'ADMIN'
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully.'))
