import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
myproject_dir = project_root / 'myproject'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append(str(myproject_dir))
sys.path.append(str(project_root))

try:
    import django
    django.setup()
    from django.contrib.auth import get_user_model
except Exception as e:
    print(f"[-] Django setup failed: {e}")
    sys.exit(1)


def create_admin():
    User = get_user_model()
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@hospital.com')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    print('[*] Checking / Creating Automatic Admin Superuser...')
    try:
        if not User.objects.db_manager('default').filter(username=username).exists():
            User.objects.db_manager('default').create_superuser(username=username, email=email, password=password)
            print(f"[+] Superuser '{username}' created successfully! (Password: {password})")
        else:
            print(f"[*] Superuser '{username}' already exists.")
    except Exception as e:
        print(f"[-] Error creating superuser: {e}")


if __name__ == '__main__':
    create_admin()
