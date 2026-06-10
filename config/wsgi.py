import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
app = application

# run migrate once on startup so tables exist on Vercel (ephemeral filesystem)
try:
    from django.core.management import call_command
    call_command('migrate', '--noinput', verbosity=0)
except Exception:
    pass
