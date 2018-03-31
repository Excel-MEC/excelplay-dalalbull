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


# class alumni(models.Model):
#     fname=models.CharField(max_length=200,null=True)
#     lname=models.CharField(max_length=200,null=True)
#     year_pass=models.IntegerField(null=True)
#     id = models.IntegerField(primary_key=True)
#     #student=models.CharField(max_length=2,null=True)#y or N
#     #inst_name=models.CharField(max_length=200,null=True)
#     phno=models.CharField(max_length=15,null=True)
#     email=models.CharField(max_length=100,null=True,blank=True)
#     #dob=models.DateField
#     # address info
#     #a_street = models.CharField(max_length=200,null=True)
#     #a_city = models.CharField(max_length=200,null=True)
#     #a_state = models.CharField(max_length=200,null=True)
#     #a_country = models.CharField(max_length=200,null=True)
#     #a_pin = models.CharField(max_length=50,null=True)
#     #event info
#     #event=models.CharField(max_length=30,default='none')

#     no_attending=models.IntegerField(default=0)
#     attend=models.IntegerField(default=0)
#     registration_fee=models.IntegerField(default=0)

    # def __str__(self):