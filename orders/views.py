# orders/views.py
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'first_name': request.user.first_name or '',
            'phone': request.user.username or '',  # Или добавьте поле phone в User модель, если нужно
        }

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,  # ← добавьте user
            first_name=request.POST['first_name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            comment=request.POST.get('comment', ''),
            discount=cart.coupon.discount if cart.coupon else 0
        )
        for item in cart:
            OrderItem.objects.create(order=order,
                                     product=item['product'],
                                     price=item['price'],
                                     quantity=item['quantity'])
        cart.clear()
        return render(request, 'orders/created.html', {'order': order})
    return render(request, 'orders/create.html', {'initial_data': initial_data})

def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/my_orders.html', {'orders': orders})
