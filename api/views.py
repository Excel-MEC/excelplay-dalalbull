from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt
import numbers
import datetime
from .decorators import login_required

from .models import *
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
				net_worth=1000000.00,
				rank=Portfolio.objects.count
			)
	return JsonResponse({'success':True})

#======Dashboard======#
@login_required
@csrf_exempt
def dashboard(request):
    total_users = User.objects.count()

    data_to_send = {
        'total_users' : total_users,
        'stockholdings':getStockHoldings(request.session['user']),
        'topGainers' : getTopGainers(),
        'topLosers' : getTopLosers(),
        'mostActiveVol' : getMostActiveVolume(),
        'mostActiveVal' : getMostActiveValue(),
    }

    return JsonResponse(data_to_send)

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
	try:
		company = request.POST['company']
	except:
		return JsonResponse({ 
		    'msg' : 'error'}
		    )
	try:
	    data_to_send = Stock_data.objects.get(symbol=company).as_dict()
	    return JsonResponse(data_to_send)
	except:
	    return JsonResponse({ 
	        'result' : 'wrong company name!'}
	        )

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
	
	if(data['b_ss']=="buy"):
		msg=submit_buy(request)
	else:
		msg=submit_shortSell(request)

	print(msg)

	return JsonResponse({'msg':msg})

def submit_buy(request):
	data=request.POST
	quantity=Decimal(data['quantity'])
	company=data['company']

	#Checking if the Company exists
	stock_data=companyCheck(company)
	current_price=stock_data.current_price

	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans
	margin=(user_portfolio.margin)

	#Brokerage
	brokerage=calculateBrokerage(no_trans,quantity,current_price)

	#Checking if the user has enough cash balance
	user_cash_balance=user_portfolio.cash_bal
	if(user_cash_balance-(quantity*current_price)-margin-brokerage<0):
		msg="Not enough balance"
		return msg

	#===Executed only if the user has enough cash balance===#
	if TransactionBuy.objects.filter(email=request.session['user'],symbol=company).exists():
		transaction=TransactionBuy.objects.get(email=request.session['user'],symbol=company)
		transaction.quantity+=int(quantity)
		transaction.value=current_price
		transaction.time=now=datetime.datetime.now()
		transaction.save()
	else:	
		TransactionBuy.objects.create(
			email=request.session['user'],
			symbol=company,
			quantity=quantity,
			value=current_price,
			)
	user_portfolio.cash_bal=user_cash_balance-(quantity*current_price)
	msg="You have succcessfully bought {1} quantities of {2}".format(request.session['user'],quantity,company)

	user_portfolio.cash_bal-=brokerage
	user_portfolio.no_trans+=1
	user_portfolio.save()

	history=History(
		email=request.session['user'],
		time=datetime.datetime.now().time(),
		symbol=company,
		buy_ss="BUY",
		quantity=quantity,
		price=stocks.current_price
		)
	history.save()

	return msg

def submit_shortSell(request):
	data=request.POST
	quantity=Decimal(data['quantity'])
	company=data['company']

	#Checking if the Company exists
	stock_data=companyCheck(company)
	current_price=stock_data.current_price

	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans
	margin=(user_portfolio.margin)

	#Brokerage
	brokerage=calculateBrokerage(no_trans,quantity,current_price)

	#Checking if the user has enough cash balance
	user_cash_balance=user_portfolio.cash_bal
	if(user_cash_balance-margin-(quantity*current_price)/2-brokerage<0):
		msg="Not enough balance"
		return msg

	#===Executed only if the user has enough cash balance===#
	if TransactionShortSell.objects.filter(email=request.session['user'],symbol=company).exists():
		transaction=TransactionShortSell.objects.get(email=request.session['user'],symbol=company)
		transaction.quantity+=int(quantity)
		transaction.value=current_price
		transaction.time=now=datetime.datetime.now()
		transaction.save()
	else:	
		TransactionShortSell.objects.create(
			email=request.session['user'],
			symbol=company,
			quantity=quantity,
			value=current_price,
			)
	user_portfolio.margin=(user_portfolio.margin)+(quantity*current_price)/2
	msg="You have succcessfully short sold {1} quantities of {2}".format(request.session['user'],quantity,company)

	user_portfolio.cash_bal-=brokerage
	user_portfolio.no_trans+=1
	user_portfolio.save()

	history=History(
		email=request.session['user'],
		time=datetime.datetime.now().time(),
		symbol=company,
		buy_ss="SHORT SELL",
		quantity=quantity,
		price=stocks.current_price
	)
	history.save()

	return msg

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

	if data['s_sc']=="sell":
		msg=submit_sell(request)
	else:
		msg=submit_shortCover(request)

	return JsonResponse({'msg':msg})

def submit_sell(request):
	data=request.POST
	company=data['company']
	quantity=Decimal(data['quantity'])
	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans


	#Checking if the Company exists
	stock_data=companyCheck(company)
	current_price=Decimal(stock_data.current_price)

	#Checking if the user has any share of the company
	if not TransactionBuy.objects.filter(email=request.session['user'],symbol=data['company']).exists():
		msg="No quantity to sell"
		return msg

	transaction=TransactionBuy.objects.get(email=request.session['user'],symbol=data['company'])

	#Checking if the posted quantity is greater than the quantity user owns
	if(transaction.quantity-quantity<0):
		msg="Quantity error"
		return msg

	#SELL

	brokerage=calculateBrokerage(user_portfolio.no_trans,quantity,current_price)

	user_portfolio.cash_bal+=stock_data.current_price*quantity

	if(transaction.quantity==quantity):
		transaction.delete()
	else:
		transaction.quantity-=quantity
		transaction.save()

	user_portfolio.cash_bal-=brokerage
	user_portfolio.no_trans+=1
	user_portfolio.save()

	msg="Success"
	return msg

def submit_shortCover(request):
	data=request.POST
	company=data['company']
	quantity=Decimal(data['quantity'])
	user_portfolio=Portfolio.objects.get(email=request.session['user'])
	no_trans=user_portfolio.no_trans


	#Checking if the Company exists
	stock_data=companyCheck(company)
	current_price=Decimal(stock_data.current_price)

	#Checking if the user has any share of the company
	if not TransactionShortSell.objects.filter(email=request.session['user'],symbol=data['company']).exists():
		msg="No quantity to sell"
		return msg

	transaction=TransactionShortSell.objects.get(email=request.session['user'],symbol=data['company'])

	#Checking if the posted quantity is greater than the quantity user owns
	if(transaction.quantity-quantity<0):
		msg="Quantity error"
		return msg

	#SHORT COVER

	brokerage=calculateBrokerage(user_portfolio.no_trans,quantity,current_price)

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
	
	msg="Success"

	return msg

#=======History========#
'''
    Details of all transactions.
'''
@login_required
def history(request):
    hist = History.objects.filter(email=request.session['user'])

    hf = []
    for i in hist:
        h = i.as_dict()
        h['time'] = h['time'].strftime("%a  %d %b %I:%M:%S %p")
        h['total']= (float(i.quantity) * float(i.price))
        hf.append(h)

    data = {
    'history' : hf,
    }

    return JsonResponse(data)


def portfolio(email):
	user_portfolio=Portfolio.objects.get(email=email)
	total_no=User.objects.count()
	data_to_send = {
		'cash_bal' : user_portfolio.cash_bal,
		'net_worth': user_portfolio.net_worth,
		'rank': user_portfolio.rank,
		'total_users' : total_no,
		'total_transactions' : user_portfolio.no_trans,
		'margin':user_portfolio.margin,
	}
	return data_to_send

def stock_symbols():  
    data_to_send = {
        'companies' :all_stock_codes,
        }
    return data_to_send

def leaderboardData():
    p=Portfolio.objects.all().order_by('-net_worth')[:100]
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

def getStockHoldings(email):
	stock_holdings=[]
	transactions=TransactionBuy.objects.filter(email=email)
	for i in transactions:
		stock={}
		stock['company']=i.symbol
		stock['number']=i.quantity
		stock['type']="Buy"
		stock['purchase']=(i.value)
		stock['current']=(Stock_data.objects.get(symbol=i.symbol).current_price)
		stock_holdings.append(stock)

	transactions=TransactionShortSell.objects.filter(email=email)
	for i in transactions:
		stock={}
		stock['company']=i.symbol
		stock['number']=i.quantity
		stock['type']="Short Sell"
		stock['purchase']=(i.value)
		stock['current']=(Stock_data.objects.get(symbol=i.symbol).current_price)
		stock_holdings.append(stock)
	return stock_holdings

def getTopGainers():
    gainers=[]
    stocks=Stock_data.objects.all().order_by('-change_per')[:5]
    for stock in stocks:
        gainers.append({
            'name' : stock.symbol,
            'change_per' : stock.change_per,
            })
    return gainers

def getTopLosers():
    losers=[]
    stocks=Stock_data.objects.all().order_by('change_per')[:5]
    for stock in stocks:
        losers.append({
            'name' : stock.symbol,
            'change_per' : stock.change_per,
            })
    return losers

def getMostActiveVolume():
    mostActiveVol=[]
    stocks=Stock_data.objects.all().order_by('-trade_Qty')[:5]
    for stock in stocks:
        mostActiveVol.append({
            'name' : stock.symbol,
            'trade_Qty' : stock.trade_Qty,
            })
    return mostActiveVol

def getMostActiveValue():
    mostActiveVal=[]
    stocks=Stock_data.objects.all().order_by('-trade_Value')[:5]
    for stock in stocks:
        mostActiveVal.append({
            'name' : stock.symbol,
            'trade_value' : stock.trade_Value,
            })
    return mostActiveVal