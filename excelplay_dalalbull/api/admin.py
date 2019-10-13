from django.contrib import admin
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

class PortfolioAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'cash_bal', 'net_worth', 'no_trans', 'margin')
	search_fields = ('user_id',)


class TransactionBuyAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'symbol', 'quantity', 'value', 'time')
	search_fields = ('user_id', 'symbol')


class TransactionShortSellAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'symbol', 'quantity', 'value', 'time')
	search_fields = ('user_id', 'symbol')


class Stock_dataAdmin(admin.ModelAdmin):
	list_display = ('symbol', 'name', 'current_price', 'high', 'low', 'open_price', 'change', 'change_per')
	search_fields = ('symbo', 'name')


class StockDataHistoryAdmin(admin.ModelAdmin):
	list_display = ('symbol', 'current_price', 'time')
	search_fields = ('symbol',)


class HistoryAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'time', 'symbol', 'buy_ss', 'quantity', 'price')
	search_fields = ('user_id',)


class PendingAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'symbol', 'buy_ss', 'quantity', 'value', 'time')
	search_fields = ('user_id',)


# Register your models here.
admin.site.register(User)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(TransactionBuy, TransactionBuyAdmin)
admin.site.register(TransactionShortSell, TransactionShortSellAdmin)
admin.site.register(Stock_data, Stock_dataAdmin)
admin.site.register(StockDataHistory, StockDataHistoryAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Pending, PendingAdmin)
