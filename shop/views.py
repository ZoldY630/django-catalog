# shop/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    return render(request, 'shop/list.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/detail.html', {'product': product})
