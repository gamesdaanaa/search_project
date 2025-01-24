
import os
from myproject.wsgi import application

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    port = int(os.environ.get("PORT", 8080))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    execute_from_command_line(["", "runserver", f"0.0.0.0:{port}", "--noreload"])
