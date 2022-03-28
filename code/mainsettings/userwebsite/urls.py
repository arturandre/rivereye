from django.urls import path, re_path
from . import views
from django.contrib.staticfiles import views as sviews

urlpatterns = [
    path('',views.Home, name='Home'),
    path('home',views.Home2, name='Home2'),
    re_path(r'^static/(?P<path>.*)$', sviews.serve),
]