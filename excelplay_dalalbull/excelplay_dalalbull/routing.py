from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

from django.urls import path

from api.consumers import LeaderBoard, Portfolio, nifty_channel, graph_data_channel, ticker_data_channel, sell_channel

application = ProtocolTypeRouter({
		"websocket":URLRouter([
				path("channel/leaderboard/", LeaderBoard),
				path("channel/portfolio/",Portfolio),
				path("channel/nifty/",nifty_channel),
				path("channel/graph/",graph_data_channel),
				path("channel/ticker/",ticker_data_channel),
				path("channel/sell/",sell_channel),
			]),
                })

