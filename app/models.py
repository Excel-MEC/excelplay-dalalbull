from django.db import models
from decimal import Decimal

#Details of the user
class User(models.Model):
	email=models.CharField(primary_key=True,max_length=100)
	def __str__(self):
		return self.email

class Portfolio(models.Model):
	email=models.CharField(primary_key=True,max_length=100)
	cash_bal = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('100000'))
	no_trans = models.DecimalField(max_digits=19, decimal_places=0, default=Decimal('0'))
	def __str__(self):
		return ' %10s | %10s | %10s '%(self.email,
			self.cash_bal,
			self.no_trans,
			)

#Details of the company user owns
class User_company(models.Model):
	email=models.CharField(max_length=100,null=True,blank=True)
	company_code=models.CharField(max_length=100,null=True,blank=True)
	company_name=models.CharField(max_length=100,null=True,blank=True)
	price_per_stock=models.FloatField(null=True)
	no=models.IntegerField(null=True)
	def __str__(self):
		return self.email +' '+ self.company_code

class Stock_data(models.Model):
    symbol=models.CharField(max_length=30, primary_key=True)
    current_price=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    high=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    low=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    open_price=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    change=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    change_per=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    trade_Qty=models.DecimalField(max_digits=19, decimal_places=2,null=True)
    trade_Value=models.DecimalField(max_digits=19, decimal_places=2,null=True)

    def __str__(self):
    	return '%10s    |   %10s '%(self.symbol,
			self.current_price,
			)

    def as_dict(self):
    	return {
    	'symbol' : self.symbol,
    	'current_price' : float(self.current_price),
    	'high' : float(self.high),
    	'low' : float(self.low),
    	'open_price' : float(self.open_price),
    	'change' : float(self.change),
    	'change_per' : float(self.change_per),
    	'trade_Qty' : float(self.trade_Qty),
    	'trade_Value' : float(self.trade_Value),
    	}