from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('call-model/', views.call_model, name='call_model'),
]