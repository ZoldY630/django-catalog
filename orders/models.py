# orders/models.py
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    address = models.CharField("Адрес", max_length=255)
    comment = models.TextField("Комментарий", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey('coupons.Coupon', null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0)
    paid = models.BooleanField("Оплачен", default=False)

    def __str__(self):
        return f'Заказ {self.id}'

    def get_total_cost(self):
        total = sum(item.get_cost() for item in self.items.all())
        if self.discount:
            total -= total * self.discount / 100
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('shop.Product', on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def get_cost(self):
        return self.price * self.quantity
