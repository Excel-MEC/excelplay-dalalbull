from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt

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
			if(company_code!="SYMBOL"):
				data=nse.get_quote(str(company_code))
				Stock_data.objects.update_or_create(
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