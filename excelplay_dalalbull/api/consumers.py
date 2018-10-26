import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import simplejson as json

from .views import leaderboardData, portfolio, niftyData, graph, sell_data, ticker_data, portfolio
from asgiref.sync import async_to_sync

from django.contrib.sessions.backends.db import SessionStore

import redis

from channels.layers import get_channel_layer

# redis_conn = redis.Redis("localhost", 6379)

class PortfolioConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.scope['session']['user_channel'] = self.channel_name
        self.scope['session'].save()
        await self.accept()
        

    async def receive(self, portfolio_data):
        await self.channel_layer.send(
            "self.channel_name",
            {
                'type': "portfolio.data",
                'text': portfolio_data,
            },
        )

    async def portfolio_data(self, event):
        portfoliodata = event['text']
        await self.send_json({'data': portfoliodata})
    
    async def disconnect(self, close_code):
        userid = self.scope['session']['user_channel']
        print(userid)
        await self.close()

# class NiftyConsumer(JsonWebsocketConsumer):
#     def connect(self):
#         self.accept()
#         self.channel_layer.group_add("nifty", self.channel_name)
    
#     def receive(self, nifty_data):
#         async_to_sync(self.channel_layer.group_send)
#         (
#                 "nifty-data",
#                 {
#                     'type': "nifty.data",
#                     'text': nifty_data,
#                 },
#         )

#     def nifty_data(self, event):
#         nifty_data = event['text']
#         self.send_json({'data': nifty_data})

#     def disconnect(self, close_code):
#         async_to_sync(self.channel_layer.group_discard)("nifty-data", self.channel_name)

class GraphConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("graph-data", self.channel_name)
        await self.send_json(
            {
                'msg': "success",
            },
        )
    
    async def receive(self, graph_data):
        await self.channel_layer.group_send(
                "graph-data",
                {
                    'type': "graph.data",
                    'text': graph_data,
                },
        )

    async def graph_data(self, event):
        graphdata = event['text']
        await self.send_json({'data': graphdata})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("graph-data", self.channel_name)


class TickerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("ticker", self.channel_name)
        await self.send_json(
            {
                'msg': "success",
            },
        )
    
    async def receive(self, ticker_data):
        # async_to_sync(self.channel_layer.group_send)
        await self.channel_layer.group_send(
            "graph-data",
            {
                'type': "ticker.data",
                'text': ticker_data,
            },
        )

    async def ticker_data(self, event):
        tickerdata = event['text']
        await self.send_json({'data': tickerdata})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("ticker", self.channel_name)

def portfolioDataPush():
    # data = json.dumps(portfolio())
    layer = get_channel_layer()
    # print(layer.scope['session']['user'])
    s = SessionStore()
    if ('user' in s):
        user_id = s['user']
        print('User ID is', user_id)
        data = json.dumps(portfolio(user_id))
        async_to_sync(layer.group_send)(s['user_channel'], {"type": "portfolio.data", "text": data})

def niftyChannelDataPush():
    nifty_data = niftyData()
    layer = get_channel_layer()
    async_to_sync(layer.group_send)("nifty", {"type": "nifty.data", "text": nifty_data})


def tickerDataPush():
    data = json.dumps(ticker_data())
    layer = get_channel_layer()
    async_to_sync(layer.group_send)("ticker", {"type": "ticker.data", "text": data})


def graphDataPush():
    data = json.dumps(graph('NIFTY 50'))
    layer=get_channel_layer()
    async_to_sync(layer.group_send)("graph-data", {"type": "graph.data", "text": data})



