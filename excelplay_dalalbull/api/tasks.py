from __future__ import absolute_import, unicode_literals
import requests
import json
from celery import shared_task, task
import os
import datetime
from currency_converter import CurrencyConverter
from redis_leaderboard.wrapper import RedisLeaderboard

from excelplay_dalalbull import settings
from .models import *
from .consumers import (
	graphDataPush,
	tickerDataPush,
	portfolioDataPush
)

currency_converter = CurrencyConverter()
rdb = RedisLeaderboard('redis', 6379, 0)
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
		ordered_data = Portfolio.objects.order_by('-net_worth')
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


#=================================================================================================================

api_token_key = 'HodrBJaddlZmkQiWn4wOBv44snyZIpAMUn58Ef5oPfUiME1lv8ojl2lwV4A1'
root_url = 'https://api.worldtradingdata.com/api/v1/stock?symbol={}&api_token={}'
company_symbols = ['AAPL', 'GOOGL', 'MSFT', 'FB', 'SNAP', 'NFLX', 'AMZN', 'ADBE', 'ORCL', 'TSLA', 'INTC', 'AMD', 'NVDA', 'IBM', 'QCOM', 'CSCO', 'TXN', 'ACN', 'UBER', 'CRM', 'CTSH', 'SNE', 'INFY', 'BIDU', 'BABA', 'NOW', 'DIS', 'SPOT', 'HPQ', 'DELL', 'PYPL', 'EBAY', 'SAP', 'TM', 'TWTR', 'T', 'VZ', 'PEP', 'SBUX', 'MAR', 'WDC', 'ADSK', 'AKAM', 'ANSS', 'APA', 'JPM', 'PAAS', 'MVIS', 'SPPI', 'SNPS']
no_companies_at_a_time = 50
def stockdata():
	company_data_generator = []
	for i in range(0, len(company_symbols), no_companies_at_a_time):
		symbols = company_symbols[i:i+no_companies_at_a_time]
		url = root_url.format(','.join(symbols), api_token_key)
		r = requests.get(url)
		try:
			data = r.json()['data']
		except KeyError:
			print(f"Failed to fetch stock data. The data returned is: {r.content}")
			break
		company_data_generator += data

	for data in company_data_generator:
		data['price']  = float(data['price'])
		data['day_high'] = float(data['day_high'])
		data['day_low'] = float(data['day_low'])
		data['price_open'] = float(data['price_open'])
		data['day_change'] = float(data['day_change'])
		if(data['currency'] != 'USD'):
			multiplier = currency_converter.convert(1, data['currency'], 'USD')
			data['currency'] = 'USD'
			data['price'] = data['price'] * multiplier
			data['day_high'] = data['day_high'] * multiplier
			data['day_low'] = data['day_low'] * multiplier
			data['price_open'] = data['price_open'] * multiplier
			data['day_change'] = data['day_change'] * multiplier

		symbol = data['symbol']
		c,__ = Stock_data.objects.get_or_create(symbol=symbol)
		c.name = data['name']
		c.current_price = data['price']
		c.high = data['day_high']
		c.low = data['day_low']
		c.open_price = data['price_open']
		c.change = data['day_change']
		c.change_per = data['change_pct']
		c.trade_Qty = data['volume']
		c.trade_Value = 0 #data['trade_Value']
		c.save()


#========Networth Update========#
def networth():
	u = User.objects.all()
	for k in u:
		try:
			i=Portfolio.objects.get(user_id=k.user_id)	
			net_worth=float(i.cash_bal)
			try:
				trans=TransactionBuy.objects.filter(user_id=i.user_id)
				for j in trans:
					try:
						current_price = float(Stock_data.objects.get(symbol=j.symbol).current_price)
						net_worth += current_price * float(j.quantity)
						rdb.add('dalalbull', i.user_id, net_worth)
					except Stock_data.DoesNotExist:
						print("Company Not Listed")
				i.net_worth = net_worth
				i.save()
			except TransactionBuy.DoesNotExist:
				print("No Transactons")
		except Portfolio.DoesNotExist:
			print("Fail")
	return


#==========Sell/Short-Cover========#        
def sell_sc(username,symbol,quantity,typ):
	qnty=float(quantity)
	try:
		price = float(Stock_data.objects.get(symbol=symbol).current_price)
		port = Portfolio.objects.get(user_id=username)
		cash_bal = float(port.cash_bal)
		no_trans = float(port.no_trans)
		margin = float(port.margin)
		
		if(typ == "SELL"):
			b_ss = "BUY"
			t=TransactionBuy.objects.get(symbol=symbol,user_id=username)
		else:
			b_ss = "SHORT SELL"
			t=TransactionShortSell.objects.get(symbol=symbol,user_id=username)
		try:
			old_quantity = float(t.quantity)
			old_value = float(t.value)
			
			if(quantity <= old_quantity):
				new_quantity = old_quantity-qnty
				old_total = old_value
				new_value = old_value
				if(new_quantity == 0):
					t.delete()
				else:
					t.quantity = new_quantity
					t.value = new_value
					t.save()
				try:
					port = Portfolio.objects.get(user_id = username)
					old_cash_bal = float(port.cash_bal)
					margin = float(port.margin)
					no_trans = float(port.no_trans)
					if(typ == "SHORT COVER"):
						sc_profit = (old_total-price)*qnty
						cash_bal = old_cash_bal+sc_profit
						margin = (margin-(old_value/2)*qnty)+(new_value/2)*qnty
					elif(typ == "SELL"):
						cash_bal = old_cash_bal+(qnty*price)
					no_trans = no_trans+1
					if(no_trans <= 100):
						brokerage = ((0.5/100)*price)*qnty
					elif(no_trans <= 1000):
						brokerage = ((1/100)*price)*qnty
					else:
						brokerage = ((1.5/100)*price)*qnty
					
					print("\nupdating portfolio")
					cash_bal-=brokerage
					port.cash_bal = cash_bal
					port.margin = margin
					port.no_trans = no_trans
					port.save()
					print("Pending order completed")
					history = History(user_id = username,time = datetime.datetime.now(),symbol = symbol,buy_ss = typ,quantity = qnty,price = price)
					history.save()
					return True
				except Portfolio.DoesNotExist:
					print("Error fetching portfolio")
		except:
			print("Error fetching from transactions ")
			return False
	except Stock_data.DoesNotExist:
		return False
	return False


#==========Buy/Short-Sell========#
def buy_ss(username,symbol,quantity,typ):	
	qnty=float(quantity)
	try:
		price = float(Stock_data.objects.get(symbol = symbol).current_price)
		port = Portfolio.objects.get(user_id = username)
		cash_bal = float(port.cash_bal)
		no_trans = float(port.no_trans)
		margin = float(port.margin)
		if(no_trans+1 <= 100):
			brokerage=((0.5/100)*price)*qnty
		else:
			if(no_trans+1 <= 1000):
				brokerage = ((1/100)*price)*qnty
			else:
				brokerage = ((1.5/100)*price)*qnty
		if(((cash_bal-margin-brokerage)>0 and (cash_bal-margin-brokerage)>=(price*qnty) and typ == "BUY") or ((cash_bal-margin-brokerage)>=((price*qnty)/2) and typ == "SHORT SELL")):
			try:
				if typ == "BUY":
					trans = TransactionBuy.objects.get(user_id=username,symbol=symbol)
				else :
					trans= TransactionShortSell.objects.get(user_id=username,symbol=symbol)

				old_qnty = float(trans.quantity)
				value = float(trans.value)
				new_qnty = old_qnty + qnty
				trans.quantity = new_qnty
				trans.value = value
				trans.save()
				print("Pending order completed")
			except :
				value = price
				if typ == "BUY":
					trans = TransactionBuy(user_id=username,symbol=symbol,quantity=qnty,value=value)
				else:
					trans = TransactionShortSell(user_id=username,symbol=symbol,quantity=qnty,value=value)
				trans.save()
				print("Pending order completed")  					
			if(typ == "BUY"):
				cash_bal_up = cash_bal-(qnty*price)
				margin_up = margin
			else:
				if(typ == "SHORT SELL"): 
					cash_bal_up = cash_bal
					margin_up = margin+(qnty*price)/2
			cash_bal_up -= brokerage
			no_trans += 1
			port.cash_bal = cash_bal_up
			port.margin = margin_up
			port.no_trans = no_trans
			port.save()
			history = History(user_id = username,time = datetime.datetime.now(),symbol = symbol,buy_ss = typ,quantity = qnty,price = price)
			history.save()
			return True
	except Stock_data.DoesNotExist:
		return False	
	return False


#===============Orders=================#
def orders():
	ret=False
	if isStockMarketTime():
		try:
			pending_ord = Pending.objects.all()
			for i in pending_ord :
				idn = i.id
				username = i.user_id
				symbol = i.symbol
				typ = i.buy_ss
				quantity = i.quantity
				price = i.value
				try:
					stock_qry = Stock_data.objects.get(symbol=symbol)
					current_price  = stock_qry.current_price
					if(current_price > 0):
						if(current_price<=price):
							if(typ == "BUY"):
								ret= buy_ss(username,symbol,quantity,typ)
							else:
								if(typ == "SHORT COVER"):
									ret=sell_sc(username,symbol,quantity,typ)
						else:
							if(current_price >= price):
								if(typ == "SELL"):
									ret = sell_sc(username,symbol,quantity,typ)
								else:
									if(typ == "SHORT SELL"):
										ret = buy_ss(username,symbol,quantity,typ)
						if(ret == True):
							ret = False
							del_query = Pending.objects.get(id=idn,user_id=username,symbol=symbol,buy_ss=typ,quantity=quantity,value=price)
							del_query.delete()
				except Stock_data.DoesNotExist:
					print("Company Not Listed")
		except Pending.DoesNotExist:
			print("No Pending Orders")		 	
	else:
		try:
			day_endq=TransactionShortSell.objects.all()
			for i in day_endq :
				username = i.user_id
				symbol = i.symbol
				quantity = i.quantity
				type_temp = "SHORT COVER"
				print("Short Cover")
				ret = sell_sc(username,symbol,quantity,type_temp)
		except:
			print("No Transactions")
		Pending.objects.all().delete()

#========= Store company data in History ===========#
def updateGraphData():
	latest_stock_data = Stock_data.objects.all()

	for stock in latest_stock_data:
		StockDataHistory.objects.create(
			symbol = stock.symbol,
			current_price = stock.current_price,
		)


# _start_time = datetime.time(hour=9,minute=15,second=30)#,second=00)
# _end_time = datetime.time(hour=15,minute=29,second=30)#,minute=30,second=00)

# _start_time = datetime.time(hour=19,minute=30,second=30)#,second=00)
# _end_time = datetime.time(hour=1,minute=29,second=30)#,minute=30,second=00)
def isStockMarketTime():
	now = datetime.datetime.now()
	if(now.strftime("%A")!='Sunday' and now.strftime("%A")!='Saturday'):		
		if( _start_time <= now.time() or now.time() < _end_time):
			return True
	return False
