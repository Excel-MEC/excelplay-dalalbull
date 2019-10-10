import datetime
from decimal import Decimal

from api.models import (
    Portfolio,
    TransactionBuy,
    TransactionShortSell,
    Stock_data,
    History,
    Pending,
)


def submit_buy_fun(user_id, quantity, company, pending_price=None):

    #Checking if the Company exists
    stock_data_response = companyCheck(company)
    if stock_data_response['error']:
        return stock_data_response
    stock_data = stock_data_response['stock_data']
    current_price=stock_data.current_price
    user_portfolio=Portfolio.objects.get(user_id=user_id)
    no_trans=user_portfolio.no_trans
    margin=(user_portfolio.margin)

    if(quantity == 0):
        return {'msg': 'Quantity cannot be 0'}

    if(pending_price!=None):
        if pending_price==current_price:  
            return {'msg':'Pending price error'}
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))
        t=current_price-percentager
        l=current_price+percentager
        q=False
        if (pending_price > current_price or pending_price <= t ):
            q=True

        if (q):
            msg='Pending Price for Buying should be less than and maximum of 5% below Current Price'
            return {'msg': msg}
        # elif r:
        # 	return JsonResponse({'msg':'Pending Price for Short Selling should be greater than and maximum of 5% above Current Price'})
        else:
            p = Pending(
                user_id=user_id,
                symbol=company,
                buy_ss="BUY",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg = "You have made a Pending Order to "+"buy"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return {'msg': msg}


    #Brokerage
    brokerage=calculateBrokerage(no_trans,quantity,current_price)

    #Checking if the user has enough cash balance
    user_cash_balance=user_portfolio.cash_bal
    if(user_cash_balance-(quantity*current_price)-margin-brokerage<0):
        msg="Not enough balance"
        return {'msg': msg}

    #===Executed only if the user has enough cash balance===#
    if TransactionBuy.objects.filter(user_id=user_id,symbol=company).exists():
        transaction=TransactionBuy.objects.get(user_id=user_id,symbol=company)
        transaction.value=(current_price*quantity + transaction.value*transaction.quantity)/(quantity+transaction.quantity)
        transaction.quantity+=int(quantity)
        transaction.time=now=datetime.datetime.now()
        transaction.save()
    else:	
        TransactionBuy.objects.create(
            user_id=user_id,
            symbol=company,
            quantity=quantity,
            value=current_price,
        )
    user_portfolio.cash_bal=user_cash_balance-(quantity*current_price)
    msg="You have successfully bought {1} quantities of {2}".format(user_id,quantity,company)

    user_portfolio.cash_bal-=brokerage
    user_portfolio.no_trans+=1
    user_portfolio.save()

    history=History(
        user_id=user_id,
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="BUY",
        quantity=quantity,
        price=stock_data.current_price
    )
    history.save()

    return {'msg': msg}


def submit_shortSell_fun(user_id, quantity, company, pending_price):

    #Checking if the Company exists
    stock_data_response = companyCheck(company)
    if stock_data_response['error']:
        return stock_data_response
    stock_data = stock_data_response['stock_data']
    current_price = stock_data.current_price

    user_portfolio = Portfolio.objects.get(user_id=user_id)
    no_trans = user_portfolio.no_trans
    margin = (user_portfolio.margin)

    if(quantity == 0):
        return {'msg': 'Quantity cannot be 0'}

    if(pending_price!=None):
        if pending_price==current_price:  
            return {'msg':'Pending price error'}
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))
        t = current_price-percentager
        l = current_price+percentager

        r = False
        if(pending_price < current_price or pending_price >= l ):
            r=True

        if r:
            msg='Pending Price for Short Selling should be greater than and maximum of 5% above Current Price'
            return {'msg': msg}
        else:
            p = Pending(
                user_id=user_id,
                symbol=company,
                buy_ss="SHORT SELL",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg= "You have made a Pending Order to "+"short sell"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return {'msg': msg}

    #Brokerage
    brokerage=calculateBrokerage(no_trans,quantity,current_price)

    #Checking if the user has enough cash balance
    user_cash_balance=user_portfolio.cash_bal
    if(user_cash_balance-margin-(quantity*current_price)/2-brokerage<0):
        msg="Not enough balance"
        return {'msg': msg}

    #===Executed only if the user has enough cash balance===#
    if TransactionShortSell.objects.filter(user_id=user_id,symbol=company).exists():
        transaction=TransactionShortSell.objects.get(user_id=user_id,symbol=company)
        transaction.value=(current_price*quantity + transaction.value*transaction.quantity)/(quantity+transaction.quantity)
        transaction.quantity+=int(quantity)
        transaction.time=now=datetime.datetime.now()
        transaction.save()
    else:	
        TransactionShortSell.objects.create(
            user_id=user_id,
            symbol=company,
            quantity=quantity,
            value=current_price,
        )
    user_portfolio.margin=(user_portfolio.margin)+(quantity*current_price)/2
    msg="You have succcessfully short sold {1} quantities of {2}".format(user_id,quantity,company)

    user_portfolio.cash_bal-=brokerage
    user_portfolio.no_trans+=1
    user_portfolio.save()

    history = History(
        user_id=user_id,
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="SHORT SELL",
        quantity=quantity,
        price=stock_data.current_price
    )
    history.save()

    return {'msg': msg}


def submit_sell_fun(user_id, quantity, company, pending_price=None):

    user_portfolio=Portfolio.objects.get(user_id=user_id)
    no_trans=user_portfolio.no_trans

    #Checking if the Company exists
    stock_data_response = companyCheck(company)
    if stock_data_response['error']:
        return stock_data_response
    stock_data = stock_data_response['stock_data']
    current_price=Decimal(stock_data.current_price)

    #Checking if the user has any share of the company
    if (not TransactionBuy.objects.filter(user_id=user_id,symbol=company).exists()):
        msg="No quantity to sell"
        return {'msg': msg}

    transaction = TransactionBuy.objects.get(user_id=user_id,symbol=company)

    #Checking if the posted quantity is greater than the quantity user owns
    if(quantity == 0 or transaction.quantity-quantity<0):
        msg="Quantity error"
        return {'msg': msg}

    if(pending_price!=None):
        if pending_price==current_price:  
            return JsonResponse({'msg':'Pending price error'})
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))

        if(pending_price<current_price):
            msg='Pending Price for selling should be greater current price'
            return {'msg': msg}
        else:
            p=Pending(
                user_id=user_id,
                symbol=company,
                buy_ss="SELL",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg = "You have made a Pending Order to "+"sell"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return {'msg': msg}

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
        user_id=user_id,
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="SELL",
        quantity=quantity,
        price=stock_data.current_price
        )
    history.save()

    return {'msg': msg}

def submit_shortCover_fun(user_id, quantity, company, pending_price=None):

    user_portfolio=Portfolio.objects.get(user_id=user_id)
    no_trans=user_portfolio.no_trans

    #Checking if the Company exists
    stock_data_response = companyCheck(company)
    if stock_data_response['error']:
        return stock_data_response
    stock_data = stock_data_response['stock_data']
    current_price=Decimal(stock_data.current_price)

    #Checking if the user has any share of the company
    if (not TransactionShortSell.objects.filter(user_id=user_id,symbol=company).exists()):
        msg="No quantity to Short cover"
        return {'msg': msg}

    transaction=TransactionShortSell.objects.get(user_id=user_id,symbol=company)

    #Checking if the posted quantity is greater than the quantity user owns
    if(quantity == 0 or transaction.quantity-quantity<0):
        msg="Quantity error"
        return {'msg': msg}

    if(pending_price!=None):
        if pending_price==current_price:  
            msg='Pending price error'
            return {'msg': msg}
        pending_price=Decimal(pending_price)
        percentager = Decimal(0.05 * float(current_price))

        if(pending_price>current_price):
            msg='Pending Price for short cover should be less than current price'
            return {'msg': msg}
        else:
            p=Pending(
                user_id=user_id,
                symbol=company,
                buy_ss="SHORT COVER",
                quantity=quantity,
                value=pending_price,
                time=datetime.datetime.now().time()
            )
            p.save()
            msg= "You have made a Pending Order to "+"short cover"+" "+str(quantity)+" shares of '"+company+"' at a Desired Price of'"+'RS. '+str(pending_price)
            return {'msg': msg}

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
        user_id=user_id,
        time=datetime.datetime.now().time(),
        symbol=company,
        buy_ss="SHORT COVER",
        quantity=quantity,
        price=stock_data.current_price
        )
    history.save()

    return {'msg': msg}


def calculateBrokerage(no_trans,quantity,current_price):
    if(no_trans+1<=100):
        brokerage=(Decimal(0.5/100)*current_price)*(quantity) 
    elif(no_trans+1<=1000):                     
        brokerage=(Decimal(1/100)*current_price)*(quantity)
    else :                      
        brokerage=(Decimal(1.5/100)*current_price)*(quantity)
    return Decimal(brokerage)


def companyCheck(company):
    if company =="" or company =="NIFTY 50":
        return {'msg':'Error', 'error': True}
    try:
        stock_data=Stock_data.objects.get(symbol=company)
    except:
        return {'msg':'Company does not exist', 'error': True}
    return {'stock_data': stock_data, 'error': False}


def quantityCheck(quantity):
    if int(quantity)-quantity==0 and int(quantity)!=0:
        return {'error': False}
    else:
        return {'msg':'Quantity error', 'error': True}
