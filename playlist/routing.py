# chat/routing.py
from django.conf.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path('ws/(?P<bar>[\w-]+)$', consumers.ChatConsumer),
]
