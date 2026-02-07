"""ASGI config for eagle_intra project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eagle_intra.settings")

application = get_asgi_application()
