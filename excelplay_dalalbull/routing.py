from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path

from api.consumers import EchoConsumer, LeaderBoard, Portfolio

application = ProtocolTypeRouter({
		"websocket":URLRouter([
				path("ws/",EchoConsumer),
				path("ws/leaderboard/",LeaderBoard),
				path("ws/portfolio/",Portfolio),
			])

	})