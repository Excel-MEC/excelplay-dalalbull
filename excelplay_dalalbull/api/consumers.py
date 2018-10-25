import asyncio
from channels.generic.websocket import JsonWebsocketConsumer


from .views import leaderboardData, portfolio, niftyData, graph, sell_data, ticker_data
from asgiref.sync import async_to_sync

import redis
import json

from channels.layers import get_channel_layer


'''
################PORTFOLIO UPDATE#################
class Portfolio(AJsonWebsocketConsumer):
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

'''

class NiftyConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        self.channel_layer.group_add("nifty", self.channel_name)
    
    def receive(self, nifty_data):
        async_to_sync(self.channel_layer.group_send)
        (
                "nifty-data",
                {
                    'type': "nifty.data",
                    'text': nifty_data,
                },
        )

    def graph_data(self, event):
        nifty_data = event['text']
        self.send_json({'data': nifty_data})

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("nifty-data", self.channel_name)


class GraphConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        self.channel_layer.group_add("graph-data", self.channel_name)
    
    def receive(self, graph_data):
        async_to_sync(self.channel_layer.group_send)
        (
                "graph-data",
                {
                    'type': "graph.data",
                    'text': graph_data,
                },
        )

    def graph_data(self, event):
        graph_data = event['text']
        self.send_json({'data': graph_data})

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("graph-data", self.channel_name)


class TickerConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        self.channel_layer.group_add("ticker", self.channel_name)
    
    def receive(self, ticker_data):
        async_to_sync(self.channel_layer.group_send)
        (
                "graph-data",
                {
                    'type': "ticker.data",
                    'text': ticker_data,
                },
        )

    def ticker_data(self, event):
        ticker_data = event['text']
        self.send_json({'data': ticker_data})

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("ticker", self.channel_name)


def niftyChannelDataPush():
    nifty_data = niftyData()
    layer=get_channel_layer()
    async_to_sync(layer.group_send)("nifty", {"type": "nifty.data", "text": nifty_data})


def tickerDataPush():
    data = ticker_data()
    layer = get_channel_layer()
    async_to_sync(layer.group_send)("Ticker", {"type": "ticker.data", "text": data})


def graphDataPush():
    data = graph('NIFTY 50')
    layer=get_channel_layer()
    async_to_sync(layer.group_send)("graph-data", {"type": "grpah.data", "text": data})



