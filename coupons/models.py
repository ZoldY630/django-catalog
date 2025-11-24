# coupons/models.py
from django.db import models

class Coupon(models.Model):
    code = models.CharField("Код", max_length=50, unique=True)
    discount = models.IntegerField("Скидка %", default=10)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
