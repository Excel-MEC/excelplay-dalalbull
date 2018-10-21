import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import AsyncConsumer

from .views import leaderboardData,portfolio

from asgiref.sync import async_to_sync

import redis

# from channels import Group
redis_conn = redis.Redis("localhost", 6379)

import json

from channels.layers import get_channel_layer
#LeaderBoard
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

		userid = 100#self.scope['session']['user']
		print('Portfolio listener added!',userid)
		redis_conn.hset("online-users", userid, self.channel_name)
		await self.channel_layer.group_add("user-{}".format(userid), self.channel_name)
		await self.send_json({"msg": "success"})

	async def disconnect(self,x):
		try:
			userid = 100#self.scope['session']['user']	
			redis_conn.hdel("online-users",userid)
			await self.channel_layer.group_discard("user-{}".format(userid), self.channel_name)
		except:
			pass

		print('disonnected')

def portfolioDataPush():
	layer=get_channel_layer()
	for userid in redis_conn.hkeys("online-users"):
		userid = userid.decode("utf-8")
		print(userid)
		async_to_sync(layer.group_send)("user-{}".format(userid),{"type": "chat.system_message", "text": portfolio(userid)})


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