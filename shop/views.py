# reports/views.py — полный исправленный вариант (замени свой файл на этот)

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from shop.models import Product
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay, TruncMonth

@staff_member_required
def sales_by_period(request):
    period = request.GET.get('period', 'day')
    start_date = request.GET.get('start', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end', timezone.now().date())

    orders = Order.objects.filter(created__date__gte=start_date, created__date__lte=end_date)

    cost_expression = ExpressionWrapper(
        F('items__price') * F('items__quantity'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )

    if period == 'day':
        data = orders.annotate(
            date=TruncDay('created'),
            item_cost=cost_expression
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('item_cost'),
            avg_check=Avg('item_cost'),
            paid=Count('id', filter=Q(paid=True)),
            cancelled=Count('id', filter=Q(status='отменён'))
        ).order_by('date')
    else:
        data = orders.annotate(
            date=TruncMonth('created'),
            item_cost=cost_expression
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('item_cost'),
            avg_check=Avg('item_cost'),
            paid=Count('id', filter=Q(paid=True)),
            cancelled=Count('id', filter=Q(status='отменён'))
        ).order_by('date')

    return render(request, 'reports/sales_by_period.html', {
        'data': data, 'period': period, 'start': start_date, 'end': end_date
    })

@staff_member_required
def order_statuses(request):
    start_date = request.GET.get('start', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end', timezone.now().date())

    orders = Order.objects.filter(created__date__gte=start_date, created__date__lte=end_date)
    data = orders.values('status').annotate(count=Count('id')).order_by('status')

    return render(request, 'reports/order_statuses.html', {
        'data': data, 'start': start_date, 'end': end_date
    })

@staff_member_required
def stock_remains(request):
    products = Product.objects.all().order_by('-stock')
    return render(request, 'reports/stock_remains.html', {'products': products})

@staff_member_required
def new_clients(request):
    start_date = request.GET.get('start', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end', timezone.now().date())

    new_users = User.objects.filter(date_joined__date__gte=start_date, date_joined__date__lte=end_date).count()

    return render(request, 'reports/new_clients.html', {
        'new_users': new_users, 'start': start_date, 'end': end_date
    })

@staff_member_required
def best_clients(request):
    from django.db.models import F, ExpressionWrapper, DecimalField, Sum, Count

    cost_expression = ExpressionWrapper(
        F('items__price') * F('items__quantity'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )

    data = Order.objects.annotate(
        item_total=cost_expression
    ).values('user__username').annotate(
        total_sum=Sum('item_total'),
        count=Count('id')
    ).order_by('-total_sum')[:10]  # топ-10

    return render(request, 'reports/best_clients.html', {'data': data})
