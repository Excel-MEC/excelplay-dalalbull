import datetime
from django.test import TestCase
from .models import User,Portfolio,Stock_data

class UserCase(TestCase):
    def setUp(self):
        User.objects.create(user_id="111")
        User.objects.create(user_id="231")
		Portfolio.objects.create(user_id="342",
        cash_bal=100000, net_worth=23113212
        rank=1, no_trans=3, margin=342)
		Portfolio.objects.create(user_id="12",
        cash_bal=10, net_worth=24343
        rank=12, no_trans=4, margin=2)
		Stock_data.objects.create(symbol="INF", start=231, end=342,
		current_price=271, change=40, change_model=34, trade_Qty=1000, trade_price=10000)
		Stock_data.objects.create(symbol="AIR",start=2310,end=2500,		
		current_price=2380,change=400, change_model=33, trade_Qty=10324, trade_price=10002310)
        TransactionBuy.objects.create(user_id="32", symbol="AIR",
        quantity=25,value=10000,time=datetime.now())
        TransactionBuy.objects.create(user_id="32", symbol="TCS",
        quantity=130,value=243423,time=datetime.now())
        TransactionShortSell.objects.create(user_id="32", symbol="AIR",
        quantity=25,value=10000,time=datetime.now())
        TransactionShortSell.objects.create(user_id="32", symbol="TCS",
        quantity=130,value=243423,time=datetime.now())   
        History.objects.create(user_id="342",time=datetime.now(),symbol="TCS",
        buy_ss="safd",quantity=34,price=2323)     
        History.objects.create(user_id="111",time=datetime.now(),symbol="DLF",
        buy_ss="safd",quantity=11,price=42) 
        Pending.objects.create(user_id="342",time=datetime.now(),symbol="TCS",
        buy_ss="safd",quantity=34,value=2323)  
        Pending.objects.create(user_id="111",time=datetime.now(),symbol="DLF",
        buy_ss="safd",quantity=11,value=42)    
        StockDataHistory.objects.create(symbol="tcs",current_price=3243,time=datetime.now())
        StockDataHistory.objects.create(symbol="DLF",current_price=1111,time=datetime.now())
