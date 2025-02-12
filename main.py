
from myproject.wsgi import application
import os
from django.core.wsgi import get_wsgi_application

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    import sys
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    if len(sys.argv) == 1:
        sys.argv.append('runserver')
        sys.argv.append('0.0.0.0:3001')
    execute_from_command_line(sys.argv)
