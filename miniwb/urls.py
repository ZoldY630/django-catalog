from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ←←← ВАЖНО! cart, order, coupon ДОЛЖНЫ БЫТЬ ВЫШЕ shop! ←←←
    path('cart/', include('cart.urls')),
    path('order/', include('orders.urls')),
    path('coupon/', include('coupons.urls')),

    # shop должен быть ПОСЛЕДНИМ, потому что у него жадный <slug:slug>/
    path('', include('shop.urls')),
]

# Чтобы фотки товаров показывались
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
