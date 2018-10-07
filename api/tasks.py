from __future__ import absolute_import, unicode_literals
from celery import shared_task, task

from urllib import request

import urllib
import json

from nsetools import Nse
nse=Nse()

from .models import *

#To get the stock codes of all the companies
all_stock_codes=nse.get_stock_codes()

print("dalalbull tasks")



@shared_task
def stock_update():	
	print("Stock Update");	
	stockdata()
	return 

@shared_task
def leaderboard_update():
	print("Updating Leaderboard")
	ordered_data = Portfolio.objects.order_by('-net_worth')
	rank = 1
	for obj in ordered_data:
		obj.rank = rank
		rank += 1
		obj.save()
	return

@shared_task
def net():
    print("Networth Update");
    networth()
    return

#=========Update details of company========#
# def stockdata():
# 	print("Updating")
# 	for company_code in all_stock_codes:
# 		try:
# 			if(company_code!="SYMBOL" or ""):
# 				data=nse.get_quote(str(company_code))
# 				if(Stock_data.objects.filter(symbol=company_code).exists()):
# 					stock_data=Stock_data.objects.get(symbol=company_code)
# 					stock_data.current_price=data['lastPrice']
# 					stock_data.high=data['dayHigh']
# 					stock_data.low=data['dayLow']
# 					stock_data.open_price=data['open']
# 					stock_data.change=data['change']
# 					stock_data.change_per=data['pChange']
# 					stock_data.trade_Qty=data['deliveryQuantity']
# 					stock_data.trade_Value=data['totalTradedValue']

# 					stock_data.save()
# 				else:
# 					Stock_data.objects.create(
# 						symbol=data['symbol'],
# 						current_price=data['lastPrice'],
# 						high=data['dayHigh'],
# 						low=data['dayLow'],
# 						open_price=data['open'],
# 						change=data['change'],
# 						change_per=data['pChange'],
# 						trade_Qty=data['deliveryQuantity'],
# 						trade_Value=data['totalTradedValue']
# 						)
# 				print("success",end=" ")
# 		except:
# 			print("error")
# 			pass
# 	print("Updating successful")
# 	return JsonResponse({"msg":"success"})

API_KEY="c0e298ec-1912-483a-84f9-20b1a1142e28"
nse_url = 'http://nseindia.com/live_market/dynaContent/live_watch/stock_watch/niftyStockWatch.json'

hdr = {
	'User-Agent': "Mozilla/5.0 (Linux; Android 6.0.1; MotoG3 Build/MPI24.107-55) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.81 Mobile Safari/537.36",
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive'
}

def getRemoteData(url,tries_allowed=3):
	while tries_allowed>0:
		#try:
		req = request.Request(url,headers=hdr)
		page = request.urlopen(req).read()
		data = json.loads(page.decode('utf-8'))
		return data
		#except:
	return None


def getCompanyDetails(symbol):
	url = 'http://nimblerest.lisuns.com:4531/GetLastQuote/?accessKey=%s&xml=false&exchange=NSE&instrumentIdentifier=%s'%(API_KEY,symbol)
	data = getRemoteData(url)
	required_data = {}
	required_data['current_price'] = float(data['SELLPRICE'])
	required_data['high'] = float(data['HIGH'])
	required_data['low'] = float(data['LOW'])
	required_data['open_price'] = float(data['OPEN'])
	required_data['change'] = required_data['current_price'] - float(data['CLOSE']) 
	required_data['change_per'] = float(required_data['change']*100)/float(data['OPEN']) 
	required_data['trade_Qty'] = float(data['TOTALQTYTRADED'])/100000
	required_data['trade_Value'] = float(data['VALUE'])
	return required_data


nifty_top50 = [
	'HCLTECH', 'CIPLA', 'TATAMOTORS', 'SUNPHARMA', 'BOSCHLTD', 'WIPRO', 'ITC', 'TATAMTRDVR', 'TECHM',
	'INFRATEL', 'KOTAKBANK', 'BPCL', 'LUPIN', 'DRREDDY', 'HDFC', 'TCS', 'MARUTI', 'HDFCBANK', 'ONGC',
	'POWERGRID', 'ASIANPAINT', 'COALINDIA', 'AXISBANK', 'BAJAJ-AUTO', 'HINDUNILVR', 'BHARTIARTL', 'SBIN', 'IOC',
	'ADANIPORTS', 'INFY', 'EICHERMOT', 'AUROPHARMA', 'INDUSINDBK', 'NTPC', 'BANKBARODA', 'TATAPOWER', 'RELIANCE', 
	'ZEEL', 'HEROMOTOCO', 'AMBUJACEM', 'LT', 'ACC', 'ICICIBANK', 'IBULHSGFIN', 'TATASTEEL', 'VEDL', 
	'HINDALCO', 'YESBANK', 'ULTRACEMCO', 'GAIL',
]

_first_half_query = '+'.join(nifty_top50[:25])
_second_half_query = '+'.join(nifty_top50[25:])


base_url_formatted = 'http://nimblerest.lisuns.com:4531/GetLastQuoteArray/?accessKey=%s&exchange=NSE&instrumentIdentifiers=%s'
def getBulkData():
	url = base_url_formatted%(API_KEY,_first_half_query)
	data = getRemoteData(url)
	# print(data)
	url = base_url_formatted%(API_KEY,_second_half_query)
	data=data+getRemoteData(url)
	
	formatted_data = []
	count = 0
	for d in data: 
		count += 1
		required_data = {}
		print(d)
		required_data['current_price'] = float(d['SELLPRICE'])
		required_data['high'] = float(d['HIGH'])
		required_data['low'] = float(d['LOW'])
		required_data['open_price'] = float(d['OPEN'])
		required_data['change'] = required_data['current_price'] - float(d['CLOSE']) 
		print(required_data['change'])
		required_data['change_per'] = float(required_data['change']*100)/float(d['OPEN']) 
		required_data['trade_Qty'] = float(d['TOTALQTYTRADED'])/100000
		required_data['trade_Value'] = float(d['VALUE'])

		yield (required_data,d['INSTRUMENTIDENTIFIER'])



#=================================================================================================================


def stockdata():
	print("Stockdata called!!")
	json_data = getRemoteData(nse_url)
	
	company = json_data['latestData'][0]

	#print(company)

	# print(json_data)

	c,__ = Stock_data.objects.get_or_create(symbol='NIFTY 50')
	c.current_price = float(company['ltp'].replace(",",""))
	c.high = float(company['high'].replace(",",""))
	c.low = float(company['low'].replace(",",""))
	c.open_price = float(company['open'].replace(",",""))
	c.change = float(company['ch'].replace(",",""))
	c.change_per = float(company['per'].replace(",",""))
	c.trade_Qty = float(json_data['trdVolumesum'].replace(",",""))
	c.trade_Value = float(json_data['trdValueSum'].replace(",",""))
	c.save()

	company_data_generator = getBulkData()

	for data,symbol in company_data_generator:
		print(' ')
		c,__ = Stock_data.objects.get_or_create(symbol=symbol)
		c.current_price = data['current_price'] 
		c.high = data['high']
		c.low = data['low']
		c.open_price = data['open_price']
		c.change = data['change']
		c.change_per = data['change_per']
		c.trade_Qty = data['trade_Qty']
		c.trade_Value = data['trade_Value']
		c.save()


#========Networth Update========#
def networth():
	u = User.objects.all()
	for k in u:
		try:
			i=Portfolio.objects.get(email=k.email)	
			net_worth=float(i.cash_bal)
			try:
				trans=Transaction.objects.filter(email=i.email	,buy_ss='Buy')
				for j in trans:
					try:
						current_price = float(Stock_data.objects.get(symbol=j.symbol).current_price)
						net_worth+=current_price*float(j.quantity)
					except Stock_data.DoesNotExist:
						print("Company Not Listed")
				i.net_worth = net_worth
				i.save()
			except Transaction.DoesNotExist:
				print("No Transactons")
		except Portfolio.DoesNotExist:
			print("Fail")
	return