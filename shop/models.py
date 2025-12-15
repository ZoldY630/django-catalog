# shop/models.py
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField("Категория", max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField("Фото", upload_to='products/', blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    old_price = models.DecimalField("Старая цена", max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField("Остаток", default=0)
    available = models.BooleanField("В наличии", default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])
