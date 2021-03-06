# account/urls.py
from django.conf.urls import url
from django.urls import path

from twitting import views

# SET THE NAMESPACE!
app_name = 'twitting'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
    url(r'^newpost/$', views.new_post, name='newpost'),
    url(r'^reply/$', views.reply, name='replypost'),
    url(r'^edit/$', views.edit, name='editpost'),
    url(r'^delete/$', views.delete, name='deletepost'),
    path('info/<str:page_id>', views.info, name='info'),
]
