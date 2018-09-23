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
	try:
		del request.session['user']
		return JsonResponse({'success':True})
	except:
		return JsonResponse({'success':False})

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
	return JsonResponse({"msg":"success"})

#========BUY========#
'''
POST format
{
	'quantity':<qty>,
	'company':<company>,
	'b_ss':<"buy"/"short sell">
}
'''
@csrf_exempt
@login_required
def buy(request):
	data=request.POST
	quantity=Decimal(data['quantity'])
	company=data['company']
	b_ss=data['b_ss']

	#Checking if the Company exists
	stock_data=companyCheck(company)
	current_price=stock_data.current_price

	#Checking if the quantity is an integer	
	quantityCheck(quantity)

	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans
	margin=(user_portfolio.margin)

	#Brokerage
	brokerage=calculateBrokerage(no_trans,quantity,current_price)

	#Checking if the user has enough cash balance
	user_cash_balance=user_portfolio.cash_bal
	if((b_ss=="buy" and user_cash_balance-(quantity*current_price)-margin-brokerage<0) or (b_ss=="short sell" and user_cash_balance-margin-(quantity*current_price)/2-brokerage<0)):
		return JsonResponse({'msg':'Not enough balance'})

	#===Executed only if the user has enough cash balance===#
	msg=''
	if Transaction.objects.filter(email=request.session['user'],symbol=company,buy_ss=b_ss).exists():
		transaction=Transaction.objects.get(email=request.session['user'],symbol=company,buy_ss=b_ss)
		transaction.quantity+=int(quantity)
		transaction.value=current_price
		transaction.time=now=datetime.datetime.now()
		transaction.save()
	else:	
		Transaction.objects.create(
			email=request.session['user'],
			symbol=company,
			buy_ss=b_ss,
			quantity=quantity,
			value=current_price,
			)
	if(b_ss=="buy"):
		user_portfolio.cash_bal=user_cash_balance-(quantity*current_price)
		msg+="You have succcessfully bought {1} quantities of {2}".format(request.session['user'],quantity,company)
	else:
		user_portfolio.margin=(user_portfolio.margin)+(quantity*current_price)/2
		msg+="You have succcessfully short sold {1} quantities of {2}".format(request.session['user'],quantity,company)

	user_portfolio.cash_bal-=brokerage
	user_portfolio.no_trans+=1
	user_portfolio.save()

	return JsonResponse({'msg':msg})

#=======SELL========#
'''
POST format
{
	'quantity':<qty>,
	'company':<company>,
	's_sc':<"sell"/"short cover">
}
'''
@csrf_exempt
@login_required
def sell(request):
	data=request.POST
	company=data['company']
	quantity=Decimal(data['quantity'])
	s_sc=data['s_sc']
	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans

	b_ss="buy" if s_sc=="sell" else "short sell"

	#Checking if the Company exists
	stock_data=companyCheck(company)
	current_price=Decimal(stock_data.current_price)

	#Checking if the quantity is an integer	
	quantityCheck(quantity)

	#Checking if the user has any share of the company
	if not Transaction.objects.filter(email=request.session['user'],symbol=data['company'],buy_ss=b_ss).exists():
		return JsonResponse({'msg':'No quantity to sell'})

	transaction=Transaction.objects.get(email=request.session['user'],symbol=data['company'],buy_ss=b_ss)

	#Checking if the posted quantity is greater than the quantity user owns
	if(transaction.quantity-quantity<0):
		return JsonResponse({'msg':'Quantity error'})

	#SELL
	brokerage=calculateBrokerage(user_portfolio.no_trans,quantity,current_price)

	if s_sc=="sell":
		user_portfolio.cash_bal+=stock_data.current_price*quantity
	else:
		user_portfolio.margin=user_portfolio.margin-(quantity*transaction.value)/2
		user_portfolio.cash_bal=user_portfolio.cash_bal-(transaction.value-stock_data.current_price)*quantity

	if(transaction.quantity==quantity):
		transaction.delete()
	else:
		transaction.quantity-=quantity
		transaction.save()

	user_portfolio.cash_bal-=brokerage
	user_portfolio.no_trans+=1
	user_portfolio.save()

	return JsonResponse({'msg':'Success'})




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
		'margin':user_portfolio.margin
	}
	return data_to_send

def stock_symbols():  
    data_to_send = {
        'companies' :all_stock_codes,
        }
    return data_to_send

def leaderboardData():
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

def companyCheck(company):
	try:
		stock_data=Stock_data.objects.get(symbol=company)
	except:
		return JsonResponse({'msg':'Company does exist'})
	return stock_data

def quantityCheck(quantity):
	if int(quantity)-quantity==0 and int(quantity)!=0:
		pass
	else:
		return JsonResponse({'msg':'Quantity error'})
	return

def calculateBrokerage(no_trans,quantity,current_price):
	if(no_trans+1<=100):
		brokerage=(Decimal(0.5/100)*current_price)*(quantity) 
	elif(no_trans+1<=1000):                     
		brokerage=(Decimal(1/100)*current_price)*(quantity)
	else :                      
		brokerage=(Decimal(1.5/100)*current_price)*(quantity)
	return Decimal(brokerage)