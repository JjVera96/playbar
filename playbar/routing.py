from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import playlist.routing


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
    	URLRouter(
    		playlist.routing.websocket_urlpatterns
    		)
    	),
})