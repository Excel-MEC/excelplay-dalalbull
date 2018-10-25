from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

from django.urls import path

from api.consumers import GraphConsumer, TickerConsumer, NiftyConsumer

application = ProtocolTypeRouter({
		"websocket":URLRouter([
		                path("channel/nifty/", NiftyConsumer),
				path("channel/graph/", GraphConsumer),
				path("channel/ticker/", TickerConsumer),
				
			]),
                })

