from django.conf.urls import url,include
from django.contrib import admin
app_name='excelplay_dalalbull'
urlpatterns = [
    url(r'^admin/',admin.site.urls),
    url(r'^dalalbull/',include('excelplay_dalalbull.urls'),name='excelplay_dalalbull'),
]
