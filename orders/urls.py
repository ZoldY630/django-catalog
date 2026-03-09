# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'  # ← Add this line
urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('my/', views.my_orders, name='my_orders'),
]
