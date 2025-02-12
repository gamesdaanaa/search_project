
from myproject.wsgi import application
import os
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    import sys
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    if len(sys.argv) == 1:
        sys.argv.append('runserver')
        sys.argv.append('0.0.0.0:3000')
    execute_from_command_line(sys.argv)
