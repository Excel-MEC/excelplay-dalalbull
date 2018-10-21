from django.conf.urls import url
from django.contrib import admin
from . import views 
app_name='api'
urlpatterns = [
    # url(r'home/$',views.home,name='home'),
    # url(r'home/(?P<code>.*)/$',views.home,name='home'),
    
    # url(r'buy/$',views.buy,name='buy'),
    # url(r'buy/(?P<code>.*)/$',views.buy,name='buy'),
    
    # url(r'sell/$',views.sell,name='sell'),
    # url(r'sell/(?P<code>.*)/$',views.sell,name='sell'),

    # url(r'register/$',views.register,name='register'),
    # url(r'register/(?P<user_id>.*)/$',views.register,name='register'),

    # url(r'logout/$',views.logout,name='logout'),

    url(r'register/$',views.register,name='register'),
    url(r'handShake/$',views.handShake,name='handShake'),
    url(r'logout/$',views.logout,name='logout'),
    url(r'portfolioView/$',views.portfolioView,name='portfolioView'),
    url(r'companydetails/$',views.companyDetails,name='companyDetails'),
    url(r'leaderboard/$',views.leaderboard,name='leaderboard'),
    url(r'stockinfo', views.stockinfo, name='stockinfo'),
    url(r'buy/$',views.buy,name='buy'),
    url(r'sell/$',views.sell,name='sell'),
    url(r'dashboard/$',views.dashboard,name='dashboard'),
    url(r'history/$',views.history,name='history'),
    url(r'currentprice/$',views.currentPrice,name='currentPrice'),
    url(r'ticker', views.ticker, name='ticker'),
    url(r'nifty', views.nifty, name='nifty'),
    url(r'cancels', views.cancels, name='cancels'),
    url(r'pending', views.pending, name='pending'),

]
