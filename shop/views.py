# shop/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login   # если ещё не импортировано
from .models import Product, Category
from miniwb.forms import RegisterForm

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    return render(request, 'shop/list.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/detail.html', {'product': product})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
