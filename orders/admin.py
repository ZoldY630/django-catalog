from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'phone', 'created', 'paid', 'status']
    list_filter = ['paid', 'created', 'status']
    list_editable = ['status']
    inlines = [OrderItemInline]
