from django.db import models
from decimal import Decimal

#Details of the user
class user(models.Model):
	email=models.CharField(max_length=100,null=True,blank=True)
	cash_balance=models.FloatField(null=True)
	cash_worth=models.FloatField(null=True)
	def __str__(self):
		return self.email 

#Details of the company user owns
class user_company(models.Model):
	email=models.CharField(max_length=100,null=True,blank=True)
	company_code=models.CharField(max_length=100,null=True,blank=True)
	company_name=models.CharField(max_length=100,null=True,blank=True)
	price_per_stock=models.FloatField(null=True)
	no=models.IntegerField(null=True)
	def __str__(self):
		return self.email +' '+ self.company_code