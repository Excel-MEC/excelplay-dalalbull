from django.contrib import admin
from .models import User, Portfolio, TransactionBuy, TransactionShortSell, Stock_data

# Register your models here.
admin.site.register(User)
admin.site.register(Portfolio)
admin.site.register(TransactionBuy)
admin.site.register(TransactionShortSell)
admin.site.register(Stock_data)
