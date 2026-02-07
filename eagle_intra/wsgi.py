"""WSGI config for eagle_intra project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eagle_intra.settings")

application = get_wsgi_application()
