from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect
from .decorators import login_required

#Importing Nse from nse tools (make sure to install the package 'nsetools')
from nsetools import Nse
nse=Nse()


from .models import *


#Data 
data={}

#To get the stock codes of all the companies
all_stock_codes=nse.get_stock_codes()

# #To get the stock codes of top gainer
top_gainers_codes=nse.get_top_gainers()



@login_required
def home(request,code=0):
	
	print (request.session['user'])

	user_obj=user.objects.filter(email=request.session['user']).count()
	if user_obj:
		pass
	else:
		user.objects.create(email=request.session['user'],cash_balance=Decimal(100000),cash_worth=Decimal(0))
	user_obj=user.objects.get(email=request.session['user'])

	#To get all the shares the user bought
	user_shares=user_company.objects.filter(email=request.session['user'])
	
	#To get the rank
	users_rank=user.objects.all().order_by('-cash_balance')

	data={'all_stock_codes':all_stock_codes,'top_gainers_codes':top_gainers_codes}
	data['user_obj']=user_obj
	data['user_shares']=user_shares
	data['users_rank']=users_rank

	if code==0:
		return render(request,'app/home.html',data)
	else:
		get_data=nse.get_quote(code)
		if get_data['pChange'] is None:
				get_data['pChange']=round(((-get_data['previousClose']+get_data['closePrice'])/get_data['previousClose'])*100,2)
		data['get_data']=get_data
		return render(request,'app/home.html',data)

def register(request,user_id=0):
	if user_id==0:
		return HttpResponse('Enter your email id at the end of the URL')
	else :
		request.session['user']=user_id
		return HttpResponseRedirect("/dalalbull/home/")

def logout(request):
	if 'user' in request.session:
		print ('logging out')
		del request.session['user']
	return HttpResponseRedirect("/dalalbull/home/")

@login_required
def buy(request,code=0):
	if code==0:
		return HttpResponse('error')
	else:
		user_obj=user.objects.get(email=request.session['user'])
		get_data=nse.get_quote(code)
		if get_data['lastPrice'] < user_obj.cash_balance:
			user_company.objects.create(email=user_obj.email,company_code=code,no=1,company_name=get_data['companyName'],price_per_stock=get_data['lastPrice'])
			print (round(get_data['lastPrice'],2))
			user_obj.cash_balance=round(user_obj.cash_balance-get_data['lastPrice'],2)
			user_obj.save()
		else :
			return HttpResponse('Not enough money')
		return HttpResponseRedirect("/dalalbull/home/"+code)

@login_required
def sell(request,code=0):
	if code==0:
		return HttpResponse('error');
	else:
		user_obj=user.objects.get(email=request.session['user'])
		get_data=nse.get_quote(code)

		user_company_obj=user_company.objects.filter(email=user_obj.email,company_code=code)
		user_company_obj=user_company_obj[0]
		user_company_obj.delete()
		print (round(get_data['lastPrice'],2))
		user_obj.cash_balance=round(user_obj.cash_balance+get_data['lastPrice'],2)
		user_obj.save()
		return HttpResponseRedirect("/dalalbull/home/"+code)