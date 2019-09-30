from django.shortcuts import render,HttpResponse
from django.http import HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt

from redis_leaderboard.wrapper import RedisLeaderboard

import numbers
import datetime

from .decorators import login_required
from pytz import timezone
from excelplay_dalalbull import settings
from .models import *

#========Register users========#
'''

POST FORMAT

    {
        'user':<user_id>
    }

'''
rdb = RedisLeaderboard('redis', 6379, 0)

#========Create User object if (not created========)#
@login_required
def handShake(request):
    try:
        user_id = request.session['user']
        total_users = Portfolio.objects.count()
        print(user_id)
    
        if (not isinstance(total_users,int)):
            total_users=1
    
        if (not User.objects.filter(user_id=user_id).exists()):
            User.objects.create(
                user_id=user_id
            )

        if (not Portfolio.objects.filter(user_id=user_id).exists()):
            initial = 1000000.00
            Portfolio.objects.create(
                user_id=user_id,
                cash_bal=initial,
                no_trans=0,
                net_worth=initial,
                rank=total_users,
            )
            rdb.add('dalalbull', user_id, initial)

    except Exception as e:
        print(e)
        pass

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
    'pending':<null or price>,
    'b_ss':<"buy"/"short sell">,
}
'''


def sell(request):
    data_to_send = sell_data(request.session['user'])
    return JsonResponse(data_to_send)


@csrf_exempt
@login_required
def submit_buy(request):
    data=request.POST
    
    cclose = isWrongTime()
    if(cclose):
        return JsonResponse({'cclose': True})

    if(data['b_ss']=="buy"):
        msg=submit_buy_fun(request)
    else:
        msg=submit_shortSell_fun(request)

    print(msg)

    return JsonResponse({'msg':msg})


def submit_buy_fun(request):

    data=request.POST
    quantity=Decimal(data['quantity'])
    company=data['company']

    #Checking if the Company exists
    stock_data=companyCheck(company)
    current_price=stock_data.current_price

    user_portfolio=Portfolio.objects.get(user_id=request.session['user'])
    no_trans=user_portfolio.no_trans
    margin=(user_portfolio.margin)

    try:
        pending_price=data['pending']
    except:
        pending_price=''

    if(pending_price!=''):
        if pending_price==current_price:  
            return JsonResponse({'msg':'Pending price error'})
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))
        t=current_price-percentager
        l=current_price+percentager
        q=False
        if (pending_price > current_price or pending_price <= t ):
            q=True

        if (q):
            msg='Pending Price for Buying should be less than and maximum of 5% below Current Price'
            return msg
        # elif r:
        # 	return JsonResponse({'msg':'Pending Price for Short Selling should be greater than and maximum of 5% above Current Price'})
        else:
            p = Pending(
                user_id=request.session['user'],
                symbol=company,
                buy_ss="BUY",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg = "You have made a Pending Order to "+"buy"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return msg


    #Brokerage
    brokerage=calculateBrokerage(no_trans,quantity,current_price)

    #Checking if the user has enough cash balance
    user_cash_balance=user_portfolio.cash_bal
    if(user_cash_balance-(quantity*current_price)-margin-brokerage<0):
        msg="Not enough balance"
        return msg

    #===Executed only if the user has enough cash balance===#
    if TransactionBuy.objects.filter(user_id=request.session['user'],symbol=company).exists():
        transaction=TransactionBuy.objects.get(user_id=request.session['user'],symbol=company)
        transaction.quantity+=int(quantity)
        transaction.value=current_price
        transaction.time=now=datetime.datetime.now()
        transaction.save()
    else:	
        TransactionBuy.objects.create(
            user_id=request.session['user'],
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
        user_id=request.session['user'],
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="BUY",
        quantity=quantity,
        price=stock_data.current_price
    )
    history.save()

    return msg

def submit_shortSell_fun(request):
    data = request.POST
    quantity = Decimal(data['quantity'])
    company = data['company']

    #Checking if the Company exists
    stock_data = companyCheck(company)
    current_price = stock_data.current_price

    user_portfolio = Portfolio.objects.get(user_id=request.session['user'])
    no_trans = user_portfolio.no_trans
    margin = (user_portfolio.margin)

    try:
        pending_price=data['pending']
    except:
        pending_price=''

    if(pending_price!=''):
        if pending_price==current_price:  
            return JsonResponse({'msg':'Pending price error'})
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))
        t = current_price-percentager
        l = current_price+percentager

        r = False
        if(pending_price < current_price or pending_price >= l ):
            r=True

        if r:
            msg='Pending Price for Short Selling should be greater than and maximum of 5% above Current Price'
            return msg
        else:
            p = Pending(
                user_id=request.session['user'],
                symbol=company,
                buy_ss="SHORT SELL",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg= "You have made a Pending Order to "+"short sell"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return msg

    #Brokerage
    brokerage=calculateBrokerage(no_trans,quantity,current_price)

    #Checking if the user has enough cash balance
    user_cash_balance=user_portfolio.cash_bal
    if(user_cash_balance-margin-(quantity*current_price)/2-brokerage<0):
        msg="Not enough balance"
        return msg

    #===Executed only if the user has enough cash balance===#
    if TransactionShortSell.objects.filter(user_id=request.session['user'],symbol=company).exists():
        transaction=TransactionShortSell.objects.get(user_id=request.session['user'],symbol=company)
        transaction.quantity+=int(quantity)
        transaction.value=current_price
        transaction.time=now=datetime.datetime.now()
        transaction.save()
    else:	
        TransactionShortSell.objects.create(
            user_id=request.session['user'],
            symbol=company,
            quantity=quantity,
            value=current_price,
        )
    user_portfolio.margin=(user_portfolio.margin)+(quantity*current_price)/2
    msg="You have succcessfully short sold {1} quantities of {2}".format(request.session['user'],quantity,company)

    user_portfolio.cash_bal-=brokerage
    user_portfolio.no_trans+=1
    user_portfolio.save()

    history = History(
        user_id=request.session['user'],
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="SHORT SELL",
        quantity=quantity,
        price=stock_data.current_price
    )
    history.save()

    return msg

#=======SELL========#
'''
POST format
{
    'quantity':<qty>,
    'company':<company>,
    's_sc':<"sell"/"short cover">,
    'pending':<null or price>,
}
'''
@csrf_exempt
@login_required
def submit_sell(request):
    data=request.POST

    cclose = isWrongTime()
    if(cclose):
        return JsonResponse({'cclose': True})

    if data['s_sc']=="sell":
        msg=submit_sell_fun(request)
    else:
        msg=submit_shortCover_fun(request)

    return JsonResponse({'msg':msg})


def submit_sell_fun(request):
    data=request.POST
    company=data['company']
    quantity=Decimal(data['quantity'])
    user_portfolio=Portfolio.objects.get(user_id=request.session['user'])
    no_trans=user_portfolio.no_trans


    #Checking if the Company exists
    stock_data=companyCheck(company)
    current_price=Decimal(stock_data.current_price)

    #Checking if the user has any share of the company
    if (not TransactionBuy.objects.filter(user_id=request.session['user'],symbol=data['company']).exists()):
        msg="No quantity to sell"
        return msg

    transaction = TransactionBuy.objects.get(user_id=request.session['user'],symbol=data['company'])

    #Checking if the posted quantity is greater than the quantity user owns
    if(transaction.quantity-quantity<0):
        msg="Quantity error"
        return msg

    try:
        pending_price=data['pending']
    except:
        pending_price=''

    if(pending_price!=''):
        if pending_price==current_price:  
            return JsonResponse({'msg':'Pending price error'})
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))

        if(pending_price<current_price):
            msg='Pending Price for selling should be greater current price'
            return msg
        else:
            p=Pending(
                user_id=request.session['user'],
                symbol=company,
                buy_ss="SELL",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg = "You have made a Pending Order to "+"sell"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return msg

    #SELL

    brokerage = calculateBrokerage(user_portfolio.no_trans,quantity,current_price)

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

    history=History(
        user_id=request.session['user'],
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="SELL",
        quantity=quantity,
        price=stock_data.current_price
        )
    history.save()

    return msg

def submit_shortCover_fun(request):
    data=request.POST
    company=data['company']
    quantity=Decimal(data['quantity'])
    user_portfolio=Portfolio.objects.get(user_id=request.session['user'])
    no_trans=user_portfolio.no_trans


    #Checking if the Company exists
    stock_data=companyCheck(company)
    current_price=Decimal(stock_data.current_price)

    #Checking if the user has any share of the company
    if (not TransactionShortSell.objects.filter(user_id=request.session['user'],symbol=data['company']).exists()):
        msg="No quantity to sell"
        return msg

    transaction=TransactionShortSell.objects.get(user_id=request.session['user'],symbol=data['company'])

    #Checking if the posted quantity is greater than the quantity user owns
    if(transaction.quantity-quantity<0):
        msg="Quantity error"
        return msg


    try:
        pending_price=data['pending']
    except:
        pending_price=''

    if(pending_price!=''):
        if pending_price==current_price:  
            msg='Pending price error'
            return msg
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))

        if(pending_price>current_price):
            msg='Pending Price for short cover should be less than current price'
            return msg
        else:
            p=Pending(
                user_id=request.session['user'],
                symbol=company,
                buy_ss="SHORT COVER",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg= "You have made a Pending Order to "+"short cover"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return msg

    #SHORT COVER

    brokerage=calculateBrokerage(user_portfolio.no_trans,quantity,current_price)

    user_portfolio.margin=user_portfolio.margin-(quantity*transaction.value)/2
    user_portfolio.cash_bal=user_portfolio.cash_bal+(transaction.value-stock_data.current_price)*quantity

    if(transaction.quantity==quantity):
        transaction.delete()
    else:
        transaction.quantity-=quantity
        transaction.save()

    user_portfolio.cash_bal-=brokerage
    user_portfolio.no_trans+=1
    user_portfolio.save()
    
    msg="Success"

    history=History(
        user_id=request.session['user'],
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="SHORT COVER",
        quantity=quantity,
        price=stock_data.current_price
        )
    history.save()

    return msg

@csrf_exempt
@login_required
def pending(request):      
    
    no_stock=False

    try:
        t = Pending.objects.filter(user_id=request.session['user'])
        row=[]
        for i in t:
            print(i.symbol)
            temp={}
            temp['quantity']=float(i.quantity)
            temp['value']=float(i.value)
            temp['type']=i.buy_ss
            temp['symbol']=i.symbol
            try:
                s=Stock_data.objects.get(symbol=temp['symbol'])
                temp['current_price']=(str(s.current_price))
            except Stock_data.DoesNotExist:
                temp['current_price']='Not Listed'
                temp['id']=i.id
            row.append(temp)
    except Pending.DoesNotExist:
        no_stock=True

    data = {
        'pending':row,
    }

    return JsonResponse(data)

'''
POST DATA Format:
{
'iddel' : <id>, 
'company' : <company code>,
}

'''
@login_required
def cancels(request):
    cclose = isWrongTime()
    if(cclose):
        return JsonResponse({'cclose': True})

    iddel=request.POST['iddel']
    company=request.POST['company']
    username=request.session['user']
    msg=""
    if(iddel!="" and company !=""):
        try:
            p=Pending.objects.get(user_id=username,
            id=iddel,
            symbol=company,
            )
            p.delete()
            msg = "Specified pending order has been cancelled"

        except Pending.DoesNotExist:
            msg="Error Cancelling"
    else:
        msg="Invalid Data"

    data_to_send = {
    'msg' : msg,
    }

    return JsonResponse(data_to_send)

#======STOCKINFO======#
'''
Page stock information.
List of all companies.
'''
def stock_symbols():  
    stocks=Stock_data.objects.all()    
    companies =[]                      
    for c in stocks:
        companies.append(c.symbol)

    data_to_send = {
        'companies' : companies,
        }
    return data_to_send


@login_required
def stockinfo(request):                           
    data_to_send = stock_symbols()
    return JsonResponse(data_to_send)


#=======History========#
'''
    Details of all transactions.
'''
@login_required
def history(request):
    hist = History.objects.filter(user_id=request.session['user'])

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

@login_required
def graphView(request):
    return JsonResponse( graph('NIFTY 50')) 

#======To Get Current Price======#

'''
This is called when user selects the company
in buy/short sell,
UI performs the required calculations

POST format
    {
        'company':<company code>,
    }
'''
@csrf_exempt
@login_required
def currentPrice(request):
    user_id=request.session['user']
    company = request.POST['company']
    curr_price = Stock_data.objects.get(symbol=company).current_price
    portfo = Portfolio.objects.get(user_id=user_id)
    cash_bal = portfo.cash_bal
    margin = portfo.margin
    no_trans = portfo.no_trans

    data = {
        'curr_price' : curr_price,
        'cash_bal': cash_bal,
        'margin' : margin,
        'no_trans' : no_trans
    }                    

    return JsonResponse(data)


def portfolio(user_id):
    print("User ID: ", user_id)
    user_portfolio = Portfolio.objects.get(user_id=user_id)
    total_no=User.objects.count()
    data_to_send = {
        'cash_bal' : float(user_portfolio.cash_bal),
        'net_worth': float(user_portfolio.net_worth),
        'rank': float(user_portfolio.rank),
        'total_users' : float(total_no),
        'total_transactions' : float(user_portfolio.no_trans),
        'margin':float(user_portfolio.margin),
    }
    return data_to_send

@login_required
def ticker(request):
    return JsonResponse(ticker_data())

def ticker_data():
    stocks = Stock_data.objects.all()
    tickerData = []
    for stock in stocks:
        tickerData.append({
            'name': stock.symbol,
            'current_price' : stock.current_price,
            'change_per' : stock.change_per,
        })
    return {
        'tickerData': tickerData,
    }

@login_required
def nifty(request):
    return JsonResponse(niftyData())

def niftyData():

    nifty= Stock_data.objects.get(symbol='NIFTY 50')

    data_to_send = {
        'current_price': float(nifty.current_price),
        'change' : float(nifty.change) , 
    }
    
    return data_to_send

def leaderboardData():
    p=Portfolio.objects.all().order_by('-net_worth')[:100]
    i=1
    l=[]
    for t in p:
        user = {
            'user_id': t.user_id,
            'cash_bal': float(t.cash_bal),
            'no_trans': float(t.no_trans),
        }      
        l.append(user)
    data_to_send = {
        'leaderboard_data' : l,
    }
    return data_to_send

def companyCheck(company):
    if company =="" or company =="NIFTY 50":
        return JsonResponse({'msg':'Error'})
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

def getStockHoldings(user_id):
    stock_holdings=[]
    transactions=TransactionBuy.objects.filter(user_id=user_id)
    for i in transactions:
        stock={}
        stock['company']=i.symbol
        stock['number']=i.quantity
        stock['type']="BUY"
        stock['purchase']=(i.value)
        stock['current']=(Stock_data.objects.get(symbol=i.symbol).current_price)
        stock_holdings.append(stock)

    transactions=TransactionShortSell.objects.filter(user_id=user_id)
    for i in transactions:
        stock={}
        stock['company']=i.symbol
        stock['number']=i.quantity
        stock['type']="SHORT SELL"
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

def graph(company):
    graph_values=Old_Stock_data.objects.filter(symbol=company).order_by('time')
    graph_data=[]
    for i in graph_values:
        temp=[]
        timez=timezone(settings.TIME_ZONE)
        time=i.time.astimezone(timez)
        temp.append( (time.hour-9)*60 + time.minute -15 )
        temp.append( i.current_price )
        graph_data.append(temp)

    data_to_send = {
        'graph_data' : graph_data,
    }
    return data_to_send

def sell_data(user_id):                      
    no_stock=False
    transactions=[]
    data={}
    data_array={}
    d=[]
    k=0
    s =set()
    cclose = isWrongTime()
    if (not isWrongTime()):
        try:
            t1 = TransactionBuy.objects.filter(user_id=user_id)

            for i in t1:
                temp={}

                temp['old_quantity']=float(i.quantity)
                temp['old_value']=float(i.value)

                temp['buy_ss']="BUY"
                temp['symbol']=i.symbol

                try:
                    s = Stock_data.objects.get(symbol=temp['symbol'])
                except:
                    continue

                temp['profit']=float(s.current_price)-(temp['old_value'])
                   
                temp['prof_per']=(temp['profit']/(temp['old_value']))*100
                                               
                temp['disp']='Sell'


                transactions.append(
                    {
                        'company' : temp['symbol'],
                        'type_of_trade' : temp['buy_ss'],
                        'share_in_hand' : temp['old_quantity'],
                        'current_price' : str(s.current_price),
                        'gain' : temp['prof_per'],
                        'type_of_trans' : temp['disp']
                    })

            t2 = TransactionShortSell.objects.filter(user_id=user_id)

            for i in t2:
                temp={}

                temp['old_quantity']=float(i.quantity)
                temp['old_value']=float(i.value)

                temp['buy_ss']="SHORT SELL"
                temp['symbol']=i.symbol

                try:
                    s = Stock_data.objects.get(symbol=temp['symbol'])
                except:
                    continue
                   
                temp['profit']=temp['old_value']-float(s.current_price)

                temp['disp']='SHORT COVER'

                temp['prof_per']=(temp['profit']/(temp['old_value']))*100


                transactions.append(
                    {
                        'company' : temp['symbol'],
                        'type_of_trade' : temp['buy_ss'],
                        'share_in_hand' : temp['old_quantity'],
                        'current_price' : str(s.current_price),
                        'gain' : temp['prof_per'],
                        'type_of_trans' : temp['disp']
                    })


                if(len(transactions)==0):
                    no_stock=True
        except:
            no_stock=True 

    data = {
        'cclose' : cclose,
        'no_stock': no_stock,
        'trans':transactions,
    }
    
    return data

# _start_time = datetime.time(hour=9,minute=15,second=30)#,second=00)
# _end_time = datetime.time(hour=15,minute=29,second=30)#,minute=30,second=00)

_start_time = datetime.time(hour=19,minute=30,second=30)#,second=00)
_end_time = datetime.time(hour=1,minute=29,second=30)#,minute=30,second=00)
def isWrongTime():
    cclose = True
    now = datetime.datetime.now()
    if (now.strftime("%A")!='Sunday' and now.strftime("%A")!='Saturday'):
        now = datetime.datetime.now()
        if(_start_time <= now.time() or now.time() < _end_time):
            cclose = False
    return cclose
