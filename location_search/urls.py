from django.urls import path
from . import views, views_google

urlpatterns = [
    path('', views_google.map_get, name='findGas'),
    # Other paths go here
    path('search',views.submit, name='submit'),
    path('searchPage', views.searchPage, name='searchPage'),
    path('updatePrice/<int:gas_station_id>', views.updatePrice, name = 'updatePrice'),

    # Google Paths
    path('search_google', views_google.map_submit, name='submit'),
    path('searchPage_google', views_google.map_get, name='searchPage'),
    path('updatePrice_google/<str:gas_station_location>', views_google.updatePrice, name='updatePrice')
]