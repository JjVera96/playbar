from django.apps import AppConfig


class PlaylistConfig(AppConfig):
    name = 'playlist'

    def ready(self):
    	from . import signals

