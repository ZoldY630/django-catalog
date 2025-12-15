# orders/views.py
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        order = Order.objects.create(
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
    return render(request, 'orders/create.html')
