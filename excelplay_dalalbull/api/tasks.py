from __future__ import absolute_import, unicode_literals
import requests
import json
from celery import shared_task, task
import os
import datetime
from currency_converter import CurrencyConverter

# from redis_leaderboard.wrapper import RedisLeaderboard

from excelplay_dalalbull import settings
from .models import *
from .consumers import graphDataPush, tickerDataPush, portfolioDataPush
from .utils import (
    submit_buy_fun,
    submit_shortSell_fun,
    submit_sell_fun,
    submit_shortCover_fun,
)

currency_converter = CurrencyConverter()
# rdb = RedisLeaderboard('redis', 6379, 0)
_start_time, _end_time = [settings._start_time, settings._end_time]


@shared_task
def stock_update():
    if isStockMarketTime():
        print("Stock Update")
        stockdata()
    else:
        print("Stock update: Not trading time")
    print("Orders")
    orders()
    return


@shared_task
def leaderboard_update():
    if isStockMarketTime():
        print("Leaderboard ordered!")
        ordered_data = Portfolio.objects.order_by("-net_worth", "last_transaction_time")
        rank = 1
        for e in ordered_data:
            e.rank = rank
            rank += 1
            e.save()
    return


@shared_task
def broadcastGraphData():
    if isStockMarketTime():
        print("Graph Values Update")
        graphDataPush()
    else:
        print("Not the time for graph broadcast")
    return


@shared_task
def StockDataHistoryUpdate():
    if isStockMarketTime():
        print("Stock data History")
        updateGraphData()
    else:
        print("Wrong Time")


@shared_task
def broadcastTickerData():
    if isStockMarketTime():
        print("Ticker broadcasted!")
        tickerDataPush()
    else:
        print("Not the time for ticker broadcast")


@shared_task
def broadcastNiftyData():
    if isStockMarketTime():
        print("Nifty data broadcasted!")
        niftyChannelDataPush()
    else:
        print("Not the time for nifty broadcast")


@shared_task
def net():
    print("Networth Update")
    networth()
    return


@shared_task
def broadcastPortfolioData():
    if isStockMarketTime():
        print("Portfolio data broadcasted!")
        portfolioDataPush()
    else:
        print("Not the time for portfolio broadcast")


@shared_task
def delete_history():
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=5)

    results = StockDataHistory.objects.filter(time__lt=time_threshold)

    results.delete()


# =================================================================================================================

# NIFTY50 companies as of December 2020
company_symbols = [
    "ADANIPORTS",
    "ASIANPAINT",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BAJFINANCE",
    "BAJAJFINSV",
    "BHARTIARTL",
    "BPCL",
    "BRITANNIA",
    "CIPLA",
    "COALINDIA",
    "DIVISLAB",
    "DRREDDY",
    "EICHERMOT",
    "GAIL",
    "GRASIM",
    "HCLTECH",
    "HDFC",
    "HDFCBANK",
    "HDFCLIFE",
    "HEROMOTOCO",
    "HINDALCO",
    "HINDUNILVR",
    "ICICIBANK",
    "INDUSINDBK",
    "INFY",
    "IOC",
    "ITC",
    "JSWSTEEL",
    "KOTAKBANK",
    "LT",
    "M&M",
    "MARUTI",
    "NESTLEIND",
    "NTPC",
    "ONGC",
    "POWERGRID",
    "RELIANCE",
    "SBIN",
    "SBILIFE",
    "SHREECEM",
    "SUNPHARMA",
    "TCS",
    "TATAMOTORS",
    "TATASTEEL",
    "TECHM",
    "TITAN",
    "ULTRACEMCO",
    "UPL",
    "WIPRO",
]

from nsetools import Nse

nse = Nse()


def stockdata():
    for c in company_symbols:
        try:
            data = nse.get_quote(c)
            c, __ = Stock_data.objects.get_or_create(symbol=c)
            c.name = data["companyName"]
            c.current_price = float(data["lastPrice"])
            c.high = float(data["dayHigh"])
            c.low = float(data["dayLow"])
            c.open_price = float(data["open"])
            c.change = float(data["lastPrice"]) - float(data["previousClose"])
            c.change_per = (
                (float(data["lastPrice"]) - float(data["previousClose"])) * 100
            ) / float(data["open"])
            c.trade_Qty = float(data["quantityTraded"])
            c.trade_Value = 0
            c.save()
        except Exception as e:
            print("Failed to fetch stock data of {}".format(c))
            print(e)


# CODE FOR OLD API USING US COMPANY DATA, API IS NO LONGER AVAILABLE
# api_token_key = "75706fc939f61154ed943df0a874c831"
# # root_url = "https://api.worldtradingdata.com/api/v1/stock?symbol={}&api_token={}"
# company_symbols = [
#     "AAPL",
#     "GOOGL",
#     "MSFT",
#     "FB",
#     "SNAP",
#     "NFLX",
#     "AMZN",
#     "ADBE",
#     "ORCL",
#     "TSLA",
#     "INTC",
#     "AMD",
#     "NVDA",
#     "IBM",
#     "QCOM",
#     "CSCO",
#     "TXN",
#     "ACN",
#     "UBER",
#     "CRM",
#     "CTSH",
#     "SNE",
#     "INFY",
#     "BIDU",
#     "BABA",
#     "NOW",
#     "DIS",
#     "SPOT",
#     "HPQ",
#     "DELL",
#     "PYPL",
#     "EBAY",
#     "SAP",
#     "TM",
#     "TWTR",
#     "T",
#     "VZ",
#     "PEP",
#     "SBUX",
#     "MAR",
#     "WDC",
#     "ADSK",
#     "AKAM",
#     "ANSS",
#     "APA",
#     "JPM",
#     "PAAS",
#     "MVIS",
#     "SPPI",
#     "SNPS",
# ]
# no_companies_at_a_time = 50


# def stockdata():
#     company_data_generator = []
#     for i in range(0, len(company_symbols), no_companies_at_a_time):
#         symbols = company_symbols[i : i + no_companies_at_a_time]
#         url = root_url.format(",".join(symbols), api_token_key)
#         r = requests.get(url)
#         try:
#             data = r.json()["data"]
#         except KeyError:
#             print(f"Failed to fetch stock data. The data returned is: {r.content}")
#             break
#         company_data_generator += data

#     for data in company_data_generator:
#         data["price"] = float(data["price"])
#         data["day_high"] = float(data["day_high"])
#         data["day_low"] = float(data["day_low"])
#         data["price_open"] = float(data["price_open"])
#         try:
#             data["day_change"] = float(data["day_change"])
#         except ValueError:
#             data["day_change"] = float(0)
#         if data["currency"] != "USD":
#             multiplier = currency_converter.convert(1, data["currency"], "USD")
#             data["currency"] = "USD"
#             data["price"] = data["price"] * multiplier
#             data["day_high"] = data["day_high"] * multiplier
#             data["day_low"] = data["day_low"] * multiplier
#             data["price_open"] = data["price_open"] * multiplier
#             data["day_change"] = data["day_change"] * multiplier

#         symbol = data["symbol"]
#         c, __ = Stock_data.objects.get_or_create(symbol=symbol)
#         c.name = data["name"]
#         c.current_price = data["price"]
#         c.high = data["day_high"]
#         c.low = data["day_low"]
#         c.open_price = data["price_open"]
#         c.change = data["day_change"]
#         c.change_per = data["change_pct"]
#         c.trade_Qty = data["volume"]
#         c.trade_Value = 0  # data['trade_Value']
#         c.save()

# ========Networth Update========#
def networth():
    u = User.objects.all()
    for k in u:
        try:
            i = Portfolio.objects.get(user_id=k.user_id)
            net_worth = float(i.cash_bal + i.margin)
            try:
                trans = TransactionBuy.objects.filter(user_id=i.user_id)
                for j in trans:
                    try:
                        current_price = float(
                            Stock_data.objects.get(symbol=j.symbol).current_price
                        )
                        net_worth += current_price * float(j.quantity)
                        # rdb.add("dalalbull", i.user_id, net_worth)
                    except Stock_data.DoesNotExist:
                        print("Company Not Listed")
                # rdb.add("dalalbull", i.user_id, net_worth)
                i.net_worth = net_worth
                i.save()
            except TransactionBuy.DoesNotExist:
                print("No Transactons")
        except Portfolio.DoesNotExist:
            print(
                "Networth Failed for user {0} (Portfolio does not exist)".format(
                    k.user_id
                )
            )
    return


# ===============Orders=================#
def orders():
    if isStockMarketTime():
        try:
            pending_ord = Pending.objects.all()
            for i in pending_ord:
                idn = i.id
                user_id = i.user_id
                symbol = i.symbol
                typ = i.buy_ss
                quantity = i.quantity
                price = i.value
                try:
                    stock_qry = Stock_data.objects.get(symbol=symbol)
                    current_price = stock_qry.current_price
                    if current_price > 0:
                        if current_price <= price:
                            if typ == "BUY":
                                ret = submit_buy_fun(user_id, quantity, symbol)
                            elif typ == "SHORT COVER":
                                ret = submit_shortCover_fun(user_id, quantity, symbol)
                        elif current_price >= price:
                            if typ == "SELL":
                                ret = submit_sell_fun(user_id, quantity, symbol)
                            elif typ == "SHORT SELL":
                                ret = submit_shortSell_fun(user_id, quantity, symbol)
                        try:
                            error = ret["error"]
                        except (KeyError, NameError):
                            error = True
                        if error is False:
                            del_query = Pending.objects.get(
                                id=idn,
                                user_id=user_id,
                                symbol=symbol,
                                buy_ss=typ,
                                quantity=quantity,
                                value=price,
                            )
                            del_query.delete()
                except Stock_data.DoesNotExist:
                    print("Company Not Listed")
        except Pending.DoesNotExist:
            print("No Pending Orders")
    else:
        try:
            day_endq = TransactionShortSell.objects.all()
            for i in day_endq:
                user_id = i.user_id
                symbol = i.symbol
                quantity = i.quantity
                type_temp = "SHORT COVER"
                print("Short Cover")
                ret = submit_shortCover_fun(user_id, quantity, symbol)
        except:
            print("No Transactions")
        Portfolio.objects.all().update(margin=0)
        Pending.objects.all().delete()


# ========= Store company data in History ===========#
def updateGraphData():
    latest_stock_data = Stock_data.objects.all()

    for stock in latest_stock_data:
        StockDataHistory.objects.create(
            symbol=stock.symbol,
            current_price=stock.current_price,
        )


def isStockMarketTime():
    now = datetime.datetime.now()
    if now.strftime("%A") != "Sunday" and now.strftime("%A") != "Saturday":
        if _start_time <= now.time() or now.time() < _end_time:
            return True
    # elif now.strftime("%A") == "Saturday" and now.time() < _end_time:
    # return True
    return False
