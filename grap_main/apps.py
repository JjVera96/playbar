# apps.py

from django.apps.config import AppConfig


class GrapMainConfig(AppConfig):
    name = 'grap_main'

    def ready(self):
    	from . import signals
