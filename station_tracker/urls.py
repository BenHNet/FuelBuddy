from django.urls import path, include
from location_search import views as searchViews
from .views import index, main
from . import views
from django.contrib import admin

urlpatterns = [
   path('', views.index, name='home'),
   path('index/', index, name='index'),
   path('main/', main, name='main'),
   path('login/', views.user_login, name='login'),
   path('signup/', views.user_signup, name='signup'),
   path('logout/', views.user_logout, name='logout'),
   path('update_gas_prices/', views.update_gas_prices, name="update_gas_prices"),
   path('location_search/', searchViews.map_view, name = "findGas"),
   path('location_search/', include('location_search.urls')),
   path('feedback/', views.render_feedback_form, name="feedback"),
   path('station-tracker/', views.map_view, name="station-tracker"),
   path('about/', views.user_about, name="about"),
   path('fueldemand/', views.user_fueldemand, name="fueldemand"),
   path('stationowner/', views.user_stationowner, name="stationowner"),
   #path('create_checkout_session/', views.create_checkout_session, name="checkout"),
   path('payment/', views.user_payment, name='payment'),
   path('map/', views.map_view, name='map_view'),
   path('payment/', views.user_payment, name='user_payment'),



]

