# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, task

from nsetools import Nse
nse=Nse()

from .models import *

#To get the stock codes of all the companies
all_stock_codes=nse.get_stock_codes()

print("dalalbull task")



@shared_task
def tq():	
	print("Stock Update");	
	stockdata()
	print("Orders");	
	orders()
	return 

@task(name="sum_two_numbers")
def add(x, y):
    return x + y

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
