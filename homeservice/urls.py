from django.conf.urls import url
from django.urls import path
from homeservice import views

urlpatterns = [
    url('', views.homepage, name='home')
]