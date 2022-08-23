from django.urls import path
from . import views

urlpatterns = [
    path('',views.Home2, name='Home2'),
    path('home',views.Home2, name='Home2'),
    path('get_report',views.get_report, name='get_report'),
    path('filterbybbox',views.filter_by_bbox, name='filterbybbox'),
    path('mock_shape_extent',views.mock_shape_extent, name='mock_shape_extent'),
]
