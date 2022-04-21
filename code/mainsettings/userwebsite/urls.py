from django.urls import path
from . import views

urlpatterns = [
    path('',views.Home, name='Home'),
    path('home',views.Home2, name='Home2'),
    path('get_report',views.get_report, name='get_report'),
]