from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.sessions import SessionMiddlewareStack

from django.urls import path

from api.consumers import GraphConsumer, TickerConsumer, PortfolioConsumer

application = ProtocolTypeRouter({
	"websocket": SessionMiddlewareStack(
		URLRouter([
			path("channel/graph/", GraphConsumer),
			path("channel/ticker/", TickerConsumer),
			path("channel/portfolio/", PortfolioConsumer),
		])
	),
})

