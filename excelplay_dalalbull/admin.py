from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Portfolio)
admin.site.register(Transaction)
admin.site.register(Stock_data)
