from channels import Group
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user
from django.core.serializers.json import DjangoJSONEncoder

import json
# from .views import niftyData,sell_data,graph,portfolio,ticker_data
from .models import Stock_data

import redis
from channels import Channel
redis_conn = redis.Redis("localhost", 6379)


@http_session_user
def connect_to_portfolio_channel(message):
	userid = message.http_session['user']	
	print('Portfolio listner added!',userid)
	redis_conn.hset("online-users",
		userid,
		message.reply_channel.name)
	message.reply_channel.send({
		'text' : json.dumps({"accept": True}) #{ "close" : True }
		})


@http_session_user
def disconnect_from_portfolio_channel(message):
	try:
		userid = message.http_session['user']
		redis_conn.hdel("online-users",userid)
	except:
		pass

def portfolioDataPush():
	for userid in redis_conn.hkeys("online-users"):
		userid = userid.decode("utf-8")
		try:
			portfolioData = portfolio(userid)
			Channel( redis_conn.hget("online-users",userid)).send(
				{
				'text': json.dumps(portfolioData,cls=DjangoJSONEncoder)
				})
		except:
			print("Error in portfolioPush")