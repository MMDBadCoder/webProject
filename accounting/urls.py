# account/urls.py
from django.conf.urls import url
from django.urls import path

from accounting import views


app_name = 'accounting'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
    url(r'^signup/$', views.signup_view, name='signup'),
    url(r'^login/$', views.login_view, name='login'),
    path('activate/<str:username>/<str:code>', views.activate, name='activate'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('reset/<str:code>', views.reset_password_view, name='reset-password'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^edit/$', views.edit_profile, name='edit'),
    url(r'^forgot/$', views.forget_password_view, name='forgot'),
    url(r'^myprofile/$', views.my_profile, name='my-profile')
]
