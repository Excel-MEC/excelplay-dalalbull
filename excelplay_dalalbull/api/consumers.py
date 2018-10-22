import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import AsyncConsumer

from .views import leaderboardData,portfolio,niftyData,graph,sell_data,ticker_data

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

		try:
			userid = self.scope['session']['user']
		except:
			userid=100
		print('Portfolio listener added!',userid)
		redis_conn.hset("online-users", userid, self.channel_name)
		await self.channel_layer.group_add("user-{}".format(userid), self.channel_name)
		await self.send_json({"msg": "success"})

	async def disconnect(self,x):
		try:
			try:
				userid = self.scope['session']['user']
			except:
				userid=100
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



class nifty_channel(AsyncJsonWebsocketConsumer):
	async def connect(self):
		await self.accept()
		await self.channel_layer.group_add("nifty-channel", self.channel_name)
		await self.send_json({"msg": "success"})
def niftyChannelDataPush():
	nifty_data = niftyData()
	layer=get_channel_layer()
	async_to_sync(layer.group_send)("nifty-channel",{"type": "chat.system_message", "text": nifty_data})


class graph_data_channel(AsyncJsonWebsocketConsumer):
	async def connect(self):
		await self.accept()
		await self.channel_layer.group_add("graph-data", self.channel_name)
		await self.send_json({"msg": "success"})
def graphDataPush():
	data = graph('NIFTY 50')
	layer=get_channel_layer()
	async_to_sync(layer.group_send)("graph-data",{"type": "chat.system_message", "text": data})


class sell_channel(AsyncJsonWebsocketConsumer):
	async def connect(self):
		await self.accept()
		try:
			userid = self.scope['session']['user']
		except:
			userid=100
		redis_conn.hset("online-sellers", userid, self.channel_name)
		await self.channel_layer.group_add("user-sell-{}".format(userid), self.channel_name)
		await self.send_json({"msg": "success"})
	async def disconnect(self,x):
		try:
			try:
				userid = self.scope['session']['user']
			except:
				userid=100
			redis_conn.hdel("online-sellers",userid)
			await self.channel_layer.group_discard("user-sell-{}".format(userid), self.channel_name)
		except:
			pass
		print('disonnected')

def sellDataPush():
	layer=get_channel_layer()
	for userid in redis_conn.hkeys("online-sellers"):
		userid = userid.decode("utf-8")
		sellData = sell_data(userid)
		print(userid)
		async_to_sync(layer.group_send)("user-sell-{}".format(userid),{"type": "chat.system_message", "text": sellData })



class ticker_data_channel(AsyncJsonWebsocketConsumer):
	async def connect(self):
		await self.accept()
		await self.channel_layer.group_add("ticker-data", self.channel_name)
		await self.send_json({"msg": "success"})
def tickerDataPush():
	tickerData = ticker_data()
	layer=get_channel_layer()
	async_to_sync(layer.group_send)("ticker-data",{"type": "chat.system_message", "text": tickerData})