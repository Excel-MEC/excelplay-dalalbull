import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import AsyncConsumer

from .views import leaderboardData,portfolio


import redis

from channels import Group
redis_conn = redis.Redis("localhost", 6379)

import json

class LeaderBoard(AsyncJsonWebsocketConsumer):
	async def connect(self):
		await self.accept()
		while 1:
			await self.send_json(leaderboardData()['leaderboard_data'])
			await asyncio.sleep(1)



################PORTFOLIO UPDATE#################
class Portfolio(AsyncJsonWebsocketConsumer):
	async def connect(self):
		
		await self.accept()

		userid = self.scope['session']['user']
		
		print('Portfolio listener added!',userid)
		
		redis_conn.hset("online-users", userid, 'portfolio')
		
		Group("user-{}".format(userid)).add(self.reply_channel)

		await self.send_json({"msg": "success"}) #{ "close" : True }

	async def disconnect(self,x):
		try:
			userid = self.scope['session']['user']	
			redis_conn.hdel("online-users",userid)
		except:
			pass
		print('disonnected')



def portfolioDataPush():
	for userid in redis_conn.hkeys("online-users"):
		userid = userid.decode("utf-8")
		print(userid)

		Group("user-{}".format(user.id)).send({
			"type":"websocket.send",
        	"text": json.dumps(portfolio(userid)),
    	})


class EchoConsumer(AsyncConsumer):
	async def websocket_connect(self,event):
		await self.send({
			"type":"websocket.accept"
		})
		async def websocket_receive(self, event):
			await self.send({
				"type":"websocket.send",
				"text":event["text"]
			})
			#To close the websocket
			# await self.send({
			# 	"type":"websocket.close"
			# })




# from channels import Group
# from channels.sessions import channel_session
# from channels.auth import http_session_user, channel_session_user
# from django.core.serializers.json import DjangoJSONEncoder

# import json
# # from .views import niftyData,sell_data,graph,portfolio,ticker_data
# from .models import Stock_data

# import redis
# from channels import Channel
# redis_conn = redis.Redis("localhost", 6379)


# @http_session_user
# def connect_to_portfolio_channel(message):
# 	userid = message.http_session['user']	
# 	print('Portfolio listner added!',userid)
# 	redis_conn.hset("online-users",
# 		userid,
# 		message.reply_channel.name)
# 	message.reply_channel.send({
# 		'text' : json.dumps({"accept": True}) #{ "close" : True }
# 		})


# @http_session_user
# def disconnect_from_portfolio_channel(message):
# 	try:
# 		userid = message.http_session['user']
# 		redis_conn.hdel("online-users",userid)
# 	except:
# 		pass

# def portfolioDataPush():
# 	for userid in redis_conn.hkeys("online-users"):
# 		userid = userid.decode("utf-8")
# 		try:
# 			portfolioData = portfolio(userid)
# 			Channel( redis_conn.hget("online-users",userid)).send(
# 				{
# 				'text': json.dumps(portfolioData,cls=DjangoJSONEncoder)
# 				})
# 		except:
# 			print("Error in portfolioPush")