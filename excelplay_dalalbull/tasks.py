from __future__ import absolute_import, unicode_literals
from celery import shared_task, task

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
def stockdata():
	print("Updating")
	for company_code in all_stock_codes:
		try:
			if(company_code!="SYMBOL" or ""):
				data=nse.get_quote(str(company_code))
				if(Stock_data.objects.filter(symbol=company_code).exists()):
					stock_data=Stock_data.objects.get(symbol=company_code)
					stock_data.current_price=data['lastPrice']
					stock_data.high=data['dayHigh']
					stock_data.low=data['dayLow']
					stock_data.open_price=data['open']
					stock_data.change=data['change']
					stock_data.change_per=data['pChange']
					stock_data.trade_Qty=data['deliveryQuantity']
					stock_data.trade_Value=data['totalTradedValue']

					stock_data.save()
				else:
					Stock_data.objects.create(
						symbol=data['symbol'],
						current_price=data['lastPrice'],
						high=data['dayHigh'],
						low=data['dayLow'],
						open_price=data['open'],
						change=data['change'],
						change_per=data['pChange'],
						trade_Qty=data['deliveryQuantity'],
						trade_Value=data['totalTradedValue']
						)
				print("success",end=" ")
		except:
			print("error")
			pass
	print("Updating successful")
	return JsonResponse({"msg":"success"})


#========Networth Update========#
def networth():
	u = User.objects.all()
	for k in u:
		try:
			i=Portfolio.objects.get(email=k.email)	
			net_worth=float(i.cash_bal)
			try:
				trans=Transaction.objects.filter(user_id=i.user_id,buy_ss='Buy')
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