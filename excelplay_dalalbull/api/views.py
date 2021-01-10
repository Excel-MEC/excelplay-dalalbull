from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

# from redis_leaderboard.wrapper import RedisLeaderboard

import numbers
import datetime
import requests

from decimal import Decimal

from .decorators import login_required
from pytz import timezone
from excelplay_dalalbull import settings
from .models import (
    User,
    Portfolio,
    TransactionBuy,
    TransactionShortSell,
    Stock_data,
    StockDataHistory,
    History,
    Pending,
)
from .utils import (
    submit_buy_fun,
    submit_sell_fun,
    submit_shortSell_fun,
    submit_shortCover_fun,
)


_start_time, _end_time = [settings._start_time, settings._end_time]


# ========Register users========#
"""

POST FORMAT

    {
        'user':<user_id>
    }

"""
# rdb = RedisLeaderboard('redis', 6379, 0)

# ========Create User object if (not created========)#
@login_required
def handShake(request):
    try:
        user_id = request.session["user"]
        total_users = Portfolio.objects.count()
        print(user_id)

        if not isinstance(total_users, int):
            total_users = 1

        if not User.objects.filter(user_id=user_id).exists():
            r = requests.post(
                settings.USER_DETAIL_API_ENDPOINT, json={"user_id": user_id}
            )
            details = r.json()
            if details["userid"] == -1:
                return JsonResponse({"Error": "User does not exist in auth service"})
            else:
                User.objects.create(
                    user_id=user_id,
                    name=details["name"],
                    email=details["email"],
                    profile_picture=details["picture"],
                )

        if not Portfolio.objects.filter(user_id=user_id).exists():
            initial = 100000.00
            Portfolio.objects.create(
                user_id=user_id,
                cash_bal=initial,
                no_trans=0,
                net_worth=initial,
                rank=total_users,
            )
            # rdb.add('dalalbull', user_id, initial)

    except Exception as e:
        print(e)
        pass

    return JsonResponse({"success": True})


# ======Dashboard======#
@login_required
@csrf_exempt
def dashboard(request):
    total_users = User.objects.count()

    data_to_send = {
        "total_users": total_users,
        "stockholdings": getStockHoldings(request.session["user"]),
        "topGainers": getTopGainers(),
        "topLosers": getTopLosers(),
        "mostActiveVol": getMostActiveVolume(),
        "mostActiveVal": getMostActiveValue(),
    }

    return JsonResponse(data_to_send)


# ========Logout (Delete 'user' from session)========#
@login_required
def logout(request):
    try:
        del request.session["user"]
        return JsonResponse({"success": True})
    except:
        return JsonResponse({"success": False})


# ========Details of user=========#
@login_required
def portfolioView(request):
    return JsonResponse(portfolio(request.session["user"]))


# ========Leaderboard========#
@login_required
def leaderboard(request):
    return JsonResponse(leaderboardData())


# ========GetRank============#
@login_required
def getrank(request):
    curr_id = request.session["user"]
    all_users = Portfolio.objects.all().order_by(
        "-net_worth", "last_networth_update_time"
    )
    rank = 1
    for user in all_users:
        if user.user_id == curr_id:
            return JsonResponse({"rank": rank})
        rank += 1
    # If user is not found in portfolio
    return JsonResponse({"rank": -1})


# ========Company Info=====#
"""

Information about each company.
Post data format:

    {
        'company' :<company code>,
    }

"""


@csrf_exempt
@login_required
def companyDetails(request):
    try:
        company = request.POST["company"]
    except:
        return JsonResponse({"msg": "error"})
    try:
        data_to_send = Stock_data.objects.get(symbol=company).as_dict()
        return JsonResponse(data_to_send)
    except:
        return JsonResponse({"result": "wrong company name!"})


# ========BUY========#
"""
POST format
{
    'quantity':<qty>,
    'company':<company>,
    'pending':<null or price>,
    'b_ss':<"buy"/"short sell">,
}
"""


def sell(request):
    data_to_send = sell_data(request.session["user"])
    return JsonResponse(data_to_send)


@csrf_exempt
@login_required
def submit_buy(request):
    data = request.POST
    user_id = request.session["user"]
    quantity = Decimal(data["quantity"])
    company = data["company"]
    try:
        pending_price = None if data["pending"] == "" else data["pending"]
    except:
        pending_price = None

    cclose = isWrongTime()
    if cclose:
        return JsonResponse({"cclose": True})

    if data["b_ss"] == "buy":
        response = submit_buy_fun(user_id, quantity, company, pending_price)
    else:
        response = submit_shortSell_fun(user_id, quantity, company, pending_price)

    print(response["msg"])

    return JsonResponse({"msg": response["msg"]})


# =======SELL========#
"""
POST format
{
    'quantity':<qty>,
    'company':<company>,
    's_sc':<"sell"/"short cover">,
    'pending':<'' or price>,
}
"""


@csrf_exempt
@login_required
def submit_sell(request):
    data = request.POST
    user_id = request.session["user"]
    quantity = Decimal(data["quantity"])
    company = data["company"]
    try:
        pending_price = None if data["pending"] == "" else data["pending"]
    except:
        pending_price = None

    cclose = isWrongTime()
    if cclose:
        return JsonResponse({"cclose": True})

    if data["s_sc"] == "sell":
        response = submit_sell_fun(user_id, quantity, company, pending_price)
    else:
        response = submit_shortCover_fun(user_id, quantity, company, pending_price)

    msg = response["msg"]

    return JsonResponse({"msg": msg})


@csrf_exempt
@login_required
def pending(request):

    no_stock = False

    try:
        t = Pending.objects.filter(user_id=request.session["user"])
        row = []
        for i in t:
            print(i.symbol)
            temp = {}
            temp["id"] = i.id
            temp["quantity"] = float(i.quantity)
            temp["value"] = float(i.value)
            temp["type"] = i.buy_ss
            temp["symbol"] = i.symbol
            try:
                s = Stock_data.objects.get(symbol=temp["symbol"])
                temp["current_price"] = str(s.current_price)
            except Stock_data.DoesNotExist:
                temp["current_price"] = "Not Listed"
            row.append(temp)
    except Pending.DoesNotExist:
        no_stock = True

    data = {
        "pending": row,
    }

    return JsonResponse(data)


"""
POST DATA Format:
    {
        'p_id' : <id>,
    }
"""


@csrf_exempt
@login_required
def cancel_pending(request):
    cclose = isWrongTime()
    if cclose:
        return JsonResponse({"cclose": True})

    p_id = request.POST["p_id"]
    user_id = request.session["user"]
    try:
        p = Pending.objects.get(user_id=user_id, id=p_id)
        p.delete()
        msg = "Specified pending order has been cancelled"
    except Pending.DoesNotExist:
        msg = "Error Cancelling"

    data_to_send = {"msg": msg}

    return JsonResponse(data_to_send)


# ======STOCKINFO======#
"""
Page stock information.
List of all companies.
"""


def stock_symbols():
    stocks = Stock_data.objects.all()
    companies = []
    for c in stocks:
        companies.append(c.symbol)

    data_to_send = {
        "companies": companies,
    }
    return data_to_send


@login_required
def stockinfo(request):
    data_to_send = stock_symbols()
    return JsonResponse(data_to_send)


# =======History========#
"""
    Details of all transactions.
"""


@login_required
def history(request):
    hist = History.objects.filter(user_id=request.session["user"])

    hf = []
    for i in hist:
        h = i.as_dict()
        h["time"] = h["time"].strftime("%a  %d %b %I:%M:%S %p")
        h["total"] = float(i.quantity) * float(i.price)
        hf.append(h)

    data = {
        "history": hf,
    }

    return JsonResponse(data)


"""
Returns Company stock History

POST format
    {
        'company':<company code>,
    }
"""


@csrf_exempt
@login_required
def graphView(request):

    company_symbol = request.POST["company"]
    return JsonResponse(graph(company_symbol))


# ======To Get Current Price======#

"""
This is called when user selects the company
in buy/short sell,
UI performs the required calculations

POST format
    {
        'company':<company code>,
    }
"""


@csrf_exempt
@login_required
def currentPrice(request):
    user_id = request.session["user"]
    company = request.POST["company"]
    curr_price = Stock_data.objects.get(symbol=company).current_price
    portfo = Portfolio.objects.get(user_id=user_id)
    cash_bal = portfo.cash_bal
    margin = portfo.margin
    no_trans = portfo.no_trans

    data = {
        "curr_price": curr_price,
        "cash_bal": cash_bal,
        "margin": margin,
        "no_trans": no_trans,
    }

    return JsonResponse(data)


def portfolio(user_id):
    print("User ID: ", user_id)
    user_portfolio = Portfolio.objects.get(user_id=user_id)
    total_no = User.objects.count()
    data_to_send = {
        "cash_bal": float(user_portfolio.cash_bal),
        "net_worth": float(user_portfolio.net_worth),
        "rank": float(user_portfolio.rank),
        "total_users": float(total_no),
        "total_transactions": float(user_portfolio.no_trans),
        "margin": float(user_portfolio.margin),
    }
    return data_to_send


@login_required
def ticker(request):
    return JsonResponse(ticker_data())


def ticker_data():
    stocks = Stock_data.objects.all().order_by("symbol")
    tickerData = []
    for stock in stocks:
        tickerData.append(
            {
                "name": stock.name,
                "symbol": stock.symbol,
                "current_price": stock.current_price,
                "change_per": stock.change_per,
            }
        )
    return {
        "tickerData": tickerData,
    }


@login_required
def nifty(request):
    return JsonResponse(niftyData())


def niftyData():

    nifty = Stock_data.objects.get(symbol="NIFTY 50")

    data_to_send = {
        "current_price": float(nifty.current_price),
        "change": float(nifty.change),
    }

    return data_to_send


# @login_required
def is_share_market_open(request):
    return JsonResponse({"response": not isWrongTime()})


def leaderboardData():
    p = Portfolio.objects.all().order_by("-net_worth", "last_networth_update_time")
    all_users = User.objects.values()
    users_dict = {}
    for u in all_users:
        users_dict[u["user_id"]] = u

    i = 1
    l = []
    for t in p:
        user = {
            "user_id": t.user_id,
            "name": users_dict[t.user_id]["name"],
            "email": users_dict[t.user_id]["email"],
            "picture": users_dict[t.user_id]["profile_picture"],
            "net_worth": t.net_worth,
            "cash_bal": float(t.cash_bal),
            "no_trans": float(t.no_trans),
        }
        l.append(user)
    data_to_send = {
        "leaderboard_data": l,
    }
    return data_to_send


def getStockHoldings(user_id):
    stock_holdings = []
    transactions = TransactionBuy.objects.filter(user_id=user_id)
    for i in transactions:
        stock = {}
        stock["company"] = i.symbol
        stock["number"] = i.quantity
        stock["type"] = "BUY"
        stock["purchase"] = i.value
        stock["current"] = Stock_data.objects.get(symbol=i.symbol).current_price
        stock_holdings.append(stock)

    transactions = TransactionShortSell.objects.filter(user_id=user_id)
    for i in transactions:
        stock = {}
        stock["company"] = i.symbol
        stock["number"] = i.quantity
        stock["type"] = "SHORT SELL"
        stock["purchase"] = i.value
        stock["current"] = Stock_data.objects.get(symbol=i.symbol).current_price
        stock_holdings.append(stock)
    return stock_holdings


def getTopGainers():
    gainers = []
    stocks = Stock_data.objects.all().order_by("-change_per")[:5]
    for stock in stocks:
        gainers.append(
            {
                "name": stock.symbol,
                "change_per": stock.change_per,
            }
        )
    return gainers


def getTopLosers():
    losers = []
    stocks = Stock_data.objects.all().order_by("change_per")[:5]
    for stock in stocks:
        losers.append(
            {
                "name": stock.symbol,
                "change_per": stock.change_per,
            }
        )
    return losers


def getMostActiveVolume():
    mostActiveVol = []
    stocks = Stock_data.objects.all().order_by("-trade_Qty")[:5]
    for stock in stocks:
        mostActiveVol.append(
            {
                "name": stock.symbol,
                "trade_Qty": stock.trade_Qty,
            }
        )
    return mostActiveVol


def getMostActiveValue():
    mostActiveVal = []
    stocks = Stock_data.objects.all().order_by("-trade_Value")[:5]
    for stock in stocks:
        mostActiveVal.append(
            {
                "name": stock.symbol,
                "trade_value": stock.trade_Value,
            }
        )
    return mostActiveVal


def graph(company):
    graph_values = reversed(
        StockDataHistory.objects.filter(symbol=company).order_by("-time")[:20]
    )
    graph_data = []
    for i in graph_values:
        temp = []
        timez = timezone(settings.TIME_ZONE)
        time = i.time.astimezone(timez)
        temp.append((time.hour) * 60 + time.minute)
        temp.append(i.current_price)
        graph_data.append(temp)

    data_to_send = {
        "graph_data": graph_data,
    }
    return data_to_send


def sell_data(user_id):
    no_stock = False
    transactions = []
    data = {}
    data_array = {}
    d = []
    k = 0
    s = set()
    cclose = isWrongTime()
    if not isWrongTime():
        try:
            t1 = TransactionBuy.objects.filter(user_id=user_id)

            for i in t1:
                temp = {}

                temp["old_quantity"] = float(i.quantity)
                temp["old_value"] = float(i.value)

                temp["buy_ss"] = "BUY"
                temp["symbol"] = i.symbol

                try:
                    s = Stock_data.objects.get(symbol=temp["symbol"])
                except:
                    continue

                temp["profit"] = float(s.current_price) - (temp["old_value"])

                temp["prof_per"] = (temp["profit"] / (temp["old_value"])) * 100

                temp["disp"] = "Sell"

                transactions.append(
                    {
                        "company": temp["symbol"],
                        "type_of_trade": temp["buy_ss"],
                        "share_in_hand": temp["old_quantity"],
                        "current_price": str(s.current_price),
                        "gain": temp["prof_per"],
                        "type_of_trans": temp["disp"],
                    }
                )

            t2 = TransactionShortSell.objects.filter(user_id=user_id)

            for i in t2:
                temp = {}

                temp["old_quantity"] = float(i.quantity)
                temp["old_value"] = float(i.value)

                temp["buy_ss"] = "SHORT SELL"
                temp["symbol"] = i.symbol

                try:
                    s = Stock_data.objects.get(symbol=temp["symbol"])
                except:
                    continue

                temp["profit"] = temp["old_value"] - float(s.current_price)

                temp["disp"] = "SHORT COVER"

                temp["prof_per"] = (temp["profit"] / (temp["old_value"])) * 100

                transactions.append(
                    {
                        "company": temp["symbol"],
                        "type_of_trade": temp["buy_ss"],
                        "share_in_hand": temp["old_quantity"],
                        "current_price": str(s.current_price),
                        "gain": temp["prof_per"],
                        "type_of_trans": temp["disp"],
                    }
                )

                if len(transactions) == 0:
                    no_stock = True
        except:
            no_stock = True

    data = {
        "cclose": cclose,
        "no_stock": no_stock,
        "trans": transactions,
    }

    return data


# _start_time = datetime.time(hour=9,minute=15,second=30)#,second=00)
# _end_time = datetime.time(hour=15,minute=29,second=30)#,minute=30,second=00)

# _start_time = datetime.time(hour=19,minute=30,second=30)#,second=00)
# _end_time = datetime.time(hour=1,minute=29,second=30)#,minute=30,second=00)
def isWrongTime():
    cclose = True
    now = datetime.datetime.now()
    if now.strftime("%A") != "Sunday" and now.strftime("%A") != "Saturday":
        now = datetime.datetime.now()
        if _start_time <= now.time() or now.time() < _end_time:
            cclose = False
    elif now.strftime("%A") == "Saturday" and now.time() < _end_time:
        cclose = False
    return cclose
