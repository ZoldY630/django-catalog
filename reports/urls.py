from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('sales-by-period/', views.sales_by_period, name='sales_by_period'),
    path('order-statuses/',  views.order_statuses,  name='order_statuses'),
    path('stock-remains/',   views.stock_remains,   name='stock_remains'),
    path('new-clients/',     views.new_clients,     name='new_clients'),
    path('best-clients/',    views.best_clients,    name='best_clients'),
]
