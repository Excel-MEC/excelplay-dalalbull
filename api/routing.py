from channels.staticfiles import StaticFilesConsumer
from channels import route
from . import consumers


channel_routing = [
	route('websocket.connect',
    	consumers.connect_to_portfolio_channel,
    	path = r'^/portfolio-channel/'
     	),

	route('websocket.disconnect',
		consumers.disconnect_from_portfolio_channel,
		path = r'^/portfolio-channel/',
     	),
]