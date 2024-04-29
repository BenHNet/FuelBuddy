from django.urls import path, include

from location_search import views as searchViews
from . import views
from .views import index, render_feedback_form, delete_feedback,feedback_success, admin_manage

urlpatterns = [
    path('', index, name='home'),
    path('index/', index, name='index'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('update_gas_prices/', views.update_gas_prices, name="update_gas_prices"),
    path('location_search/', include('location_search.urls')),
    path('feedback/', views.render_feedback_form, name="feedback"),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
    path('feedback/delete/<int:id>/', delete_feedback, name='delete_feedback'),
    path('feedback/success/<int:id>/', feedback_success, name='feedback_success'),
    path('station-tracker/', views.map_view, name="station-tracker"),
    path('about/', views.user_about, name="about"),
    path('fueldemand/', views.user_fueldemand, name="fueldemand"),
    path('stationowner/', views.user_stationowner, name="stationowner"),
    # path('create_checkout_session/', views.create_checkout_session, name="checkout"),
    path('payment/', views.user_payment, name='payment'),
    path('map/', views.map_view, name='map_view'),
    path('payment/', views.user_payment, name='user_payment'),
    path('admin_manage/', views.admin_manage, name='admin_manage'),
]
