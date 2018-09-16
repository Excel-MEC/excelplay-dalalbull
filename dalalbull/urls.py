from django.conf.urls import url,include
from django.contrib import admin
app_name='app'
urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^dalalbull/',include('app.urls'),name='app'),
]
