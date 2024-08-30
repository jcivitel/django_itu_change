from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start-scraping/', views.start_scraping, name='start_scraping'),
    path('get-progress/', views.get_progress, name='get_progress'),
]