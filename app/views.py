from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt
import numbers
import datetime
from .decorators import login_required

from nsetools import Nse
nse=Nse()

from .models import *

#To get the stock codes of all the companies
all_stock_codes=nse.get_stock_codes()

#========Register users========#
'''

POST FORMAT

	{
		'user':<email>
	}

'''
@csrf_exempt
def register(request):
	try:
		request.session['user']=request.POST['user']
		return JsonResponse({'success':True})
	except:
		return JsonResponse({'success':False})

#========Create User object if not created========#
@login_required
def handShake(request):
	email = request.session['user']
	print(email)
	if not User.objects.filter(email=email).exists():
		User.objects.create(
			email=email,
		)
		print("new user................")
	if not Portfolio.objects.filter(email=email).exists():
		Portfolio.objects.create(
				email=email,
				cash_bal=1000000.00,
				no_trans=0,
			)
	return JsonResponse({'success':True})

#========Logout (Delete 'user' from session)========#
@login_required
def logout(request):
	del request.session['user']
	return JsonResponse({'success':True})

#========Details of user=========#
@login_required
def portfolioView(request):
    return JsonResponse(portfolio(request.session['user'] )) 

#========Leaderboard========#
@login_required
def leaderboard(request):
    return JsonResponse(leaderboardData()) 

#========Company Info=====#
'''

Information about each company.
Post data format:

    {
        'company' :<company code>,
    }

'''
@csrf_exempt
@login_required
def companyDetails(request):                          
    company = request.POST['company']
    try:
        data_to_send = Stock_data.objects.get(symbol=company).as_dict()
        return JsonResponse(data_to_send)
    except:
        return JsonResponse({ 
            'result' : 'wrong company name!'}
            )

#=========Update details of company========#
def newCompanyDetails(request):
	for company_code in all_stock_codes:
		try:
			if(company_code!="SYMBOL" or ""):
				data=nse.get_quote(str(company_code))
				if(Stock_data.objects.get(symbol=company_code)):
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
	return JsonResponse({"msg":"success"})

#========BUY========#
'''
POST format
{
	'quantity':<qty>,
	'company':<company>
}
'''
@csrf_exempt
@login_required
def buy(request):
	data=request.POST
	quantity=float(data['quantity'])
	company=data['company']
	try:
		stock_data=Stock_data.objects.get(symbol=company)
	except:
		return JsonResponse({'msg':'Company does exist'})
	if int(quantity)-quantity==0:
		pass
	else:
		return JsonResponse({'msg':'Quantity error'})
	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans
	current_price=float(stock_data.current_price)
	if(no_trans+1<=100):
	        brokerage=((0.5/100)*current_price)*float(quantity) 
	elif(no_trans+1<=1000):                     
	        brokerage=((1/100)*current_price)*float(quantity)
	else :                      
	        brokerage=((1.5/100)*current_price)*float(quantity)
	user_cash_balance=float(user_portfolio.cash_bal)
	if(user_cash_balance-(quantity*current_price)-brokerage<0):
		return JsonResponse({'msg':'Not enough balance'})
	msg=''
	if Transaction.objects.filter(email=request.session['user'],symbol=company).exists():
		transaction=Transaction.objects.get(email=request.session['user'],symbol=company)
		transaction.quantity+=int(quantity)
		transaction.value=current_price
		transaction.time=now=datetime.datetime.now()
		transaction.save()
	else:	
		Transaction.objects.create(
			email=request.session['user'],
			symbol=company,
			buy_ss="buy",
			quantity=quantity,
			value=current_price,
			)
	user_portfolio.cash_bal=user_cash_balance-(quantity*current_price)-brokerage
	user_portfolio.no_trans+=1
	user_portfolio.save()
	msg+="{0} just bought {1} quantities of {2}".format(request.session['user'],quantity,company)
	return JsonResponse({'msg':msg})



#=================================#
#       NON REQUEST FUNCTIONS     #
#=================================#

def portfolio(email):
	user_portfolio=Portfolio.objects.get(email=email)
	total_no=User.objects.count()
	data_to_send = {
		'cash_bal' : user_portfolio.cash_bal,
		'total_users' : total_no,
		'total_transactions' : user_portfolio.no_trans,
	}
	return data_to_send

def stock_symbols():  
    data_to_send = {
        'companies' :all_stock_codes,
        }
    return data_to_send

def leaderboardData():
    #p=Portfolio.objects.all().order_by('-net_worth')[:100]
    p=Portfolio.objects.all().order_by('-cash_bal')[:100]
    i=1
    l=[]
    for t in p:
        user = {
        'name': t.email,
        'cash_bal': t.cash_bal,
        'no_trans':t.no_trans,
        }      

        l.append(user)
    data_to_send = {
    'leaderboard_data' : l,
    }
    return data_to_send