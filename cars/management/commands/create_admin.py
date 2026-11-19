"""Create the admin-panel user with a random password and save it to ADMIN-LOGIN.txt."""
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create (or reset) the 'admin' user and write the login to ADMIN-LOGIN.txt"

    def handle(self, *args, **opts):
        User = get_user_model()
        password = secrets.token_urlsafe(9)
        user, _ = User.objects.get_or_create(username="admin")
        user.is_staff = user.is_superuser = True
        user.set_password(password)
        user.save()
        path = settings.BASE_DIR / "ADMIN-LOGIN.txt"
        path.write_text(
            "لوحة التحكم / Admin panel\n"
            "http://127.0.0.1:8000/admin/\n\n"
            f"Username: admin\nPassword: {password}\n\n"
            "غيّر كلمة المرور بعد أول دخول (أعلى يسار لوحة التحكم ← تغيير كلمة المرور)\n"
            "Change this password after your first login.\n",
            encoding="utf-8",
        )
        self.stdout.write(self.style.SUCCESS(f"Admin user ready. Login saved to {path}"))
