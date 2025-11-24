# coupons/views.py (создай папку coupons и файл views.py)
from django.shortcuts import redirect
from django.utils import timezone
from .models import Coupon

def coupon_apply(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code__iexact=code,
                                        valid_from__lte=timezone.now(),
                                        valid_to__gte=timezone.now(),
                                        active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('cart:cart_detail')
