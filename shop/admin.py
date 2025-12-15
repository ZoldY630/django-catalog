from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'old_price', 'stock', 'available', 'created']
    list_editable = ['price', 'old_price', 'stock', 'available']  # ← менять прямо в списке!
    list_filter = ['available', 'created']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
