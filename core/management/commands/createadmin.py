from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Создаёт пользователя-администратора, если он ещё не существует'

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@ocelote.com'
        password = 'admin123'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Администратор с именем {username} уже существует.'))
            return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Администратор {username} успешно создан!'))
            self.stdout.write(self.style.SUCCESS(f'Логин: {username}, Пароль: {password}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при создании администратора: {str(e)}'))