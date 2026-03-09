from django.utils.text import slugify
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import csv
import json
import logging
from io import StringIO

from .models import Product, Category
from .forms import ProductImportForm, ProductExportForm

logger = logging.getLogger(__name__)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'old_price', 'stock', 'available', 'created']
    list_editable = ['price', 'old_price', 'stock', 'available']
    list_filter = ['available', 'created', 'category']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_view), name='shop_product_export'),
            path('do-export/', self.admin_site.admin_view(self.export_products), name='shop_product_do_export'),
            path('import/', self.admin_site.admin_view(self.import_view), name='shop_product_import'),
        ]
        return custom_urls + urls

    # ---------- Экспорт (страница с фильтрами) ----------
    def export_view(self, request):
        if request.method == 'POST':
            form = ProductExportForm(request.POST)
            if form.is_valid():
                params = {}
                if form.cleaned_data['category']:
                    params['category'] = form.cleaned_data['category'].id
                if form.cleaned_data['available'] is not None:
                    params['available'] = '1' if form.cleaned_data['available'] else '0'
                if form.cleaned_data['price_min'] is not None:
                    params['price_min'] = form.cleaned_data['price_min']
                if form.cleaned_data['price_max'] is not None:
                    params['price_max'] = form.cleaned_data['price_max']
                params['format'] = form.cleaned_data['format']
                return redirect(f"{request.path}do-export/?{self._build_query(params)}")
        else:
            form = ProductExportForm()
        return render(request, 'admin/shop/product/export.html', {'form': form, 'title': 'Экспорт товаров'})

    def _build_query(self, params):
        return '&'.join([f"{k}={v}" for k, v in params.items()])

    # ---------- Экспорт (генерация файла) ----------
    def export_products(self, request):
        if not request.user.is_staff:
            messages.error(request, "Нет прав")
            return redirect('admin:shop_product_changelist')

        queryset = Product.objects.all()
        if 'category' in request.GET:
            queryset = queryset.filter(category__id=request.GET['category'])
        if 'available' in request.GET:
            queryset = queryset.filter(available=(request.GET['available'] == '1'))
        if 'price_min' in request.GET:
            queryset = queryset.filter(price__gte=request.GET['price_min'])
        if 'price_max' in request.GET:
            queryset = queryset.filter(price__lte=request.GET['price_max'])

        format_type = request.GET.get('format', 'csv')
        count = queryset.count()

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="products.csv"'
            writer = csv.writer(response, delimiter=';')
            writer.writerow(['id', 'name', 'price', 'stock', 'category', 'available'])
            for p in queryset:
                writer.writerow([p.id, p.name, p.price, p.stock, p.category.name, p.available])
            logger.info(f"Экспорт CSV: {count} товаров пользователем {request.user}")
            return response
        else:  # json
            data = [{
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'stock': p.stock,
                'category': p.category.name,
                'available': p.available
            } for p in queryset]
            response = HttpResponse(
                json.dumps(data, ensure_ascii=False, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = 'attachment; filename="products.json"'
            logger.info(f"Экспорт JSON: {count} товаров пользователем {request.user}")
            return response

    # ---------- Импорт (страница с формой) ----------
    def import_view(self, request):
        if request.method == 'POST':
            form = ProductImportForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                file_format = form.cleaned_data['file_format']
                added = updated = skipped = 0
                errors = []

                try:
                    if file_format == 'csv':
                        decoded = file.read().decode('utf-8')
                        io_string = StringIO(decoded)
                        reader = csv.DictReader(io_string, delimiter=';')
                        for row_num, row in enumerate(reader, start=1):
                            try:
                                result = self._process_row(row, row_num)
                                if result == 'added':
                                    added += 1
                                elif result == 'updated':
                                    updated += 1
                                else:
                                    skipped += 1
                            except Exception as e:
                                errors.append(f"Строка {row_num}: {str(e)}")
                                skipped += 1
                    else:  # json
                        data = json.load(file)
                        for row_num, row in enumerate(data, start=1):
                            try:
                                result = self._process_row(row, row_num)
                                if result == 'added':
                                    added += 1
                                elif result == 'updated':
                                    updated += 1
                                else:
                                    skipped += 1
                            except Exception as e:
                                errors.append(f"Объект {row_num}: {str(e)}")
                                skipped += 1

                    messages.success(request, f"Импорт завершён: добавлено {added}, обновлено {updated}, пропущено {skipped}")
                    if errors:
                        messages.warning(request, f"Ошибок: {len(errors)} (первые 10):")
                        for err in errors[:10]:
                            messages.error(request, err)

                    logger.info(f"Импорт: добавлено {added}, обновлено {updated}, ошибок {len(errors)} пользователем {request.user}")
                except Exception as e:
                    messages.error(request, f"Ошибка чтения файла: {str(e)}")

                return redirect('admin:shop_product_changelist')
        else:
            form = ProductImportForm()
        return render(request, 'admin/shop/product/import.html', {'form': form, 'title': 'Импорт товаров'})

    # ---------- Обработка одной записи ----------
    def _process_row(self, row, row_num):
        if not row.get('name'):
            raise ValueError("Отсутствует название товара")
        if not row.get('price'):
            raise ValueError("Отсутствует цена")

        try:
            price = float(row['price'])
            if price < 0:
                raise ValueError("Цена не может быть отрицательной")
        except (ValueError, TypeError):
            raise ValueError("Некорректное значение цены")

        stock = row.get('stock', 0)
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError("Остаток не может быть отрицательным")
        except (ValueError, TypeError):
            raise ValueError("Некорректное значение остатка")

        available = row.get('available', True)
        if isinstance(available, str):
            available = available.lower() in ('true', '1', 'yes', 'да')

        category_name = row.get('category', '').strip()
        if not category_name:
            raise ValueError("Не указана категория")

        # --- Генерация уникального slug для категории ---
        from django.utils.text import slugify
        base_slug = slugify(category_name)
        if not base_slug:
            base_slug = f"category-{row_num}"  # запасной вариант, если имя не дало slug
        cat_slug = base_slug
        counter = 1
        while Category.objects.filter(slug=cat_slug).exists():
            cat_slug = f"{base_slug}-{counter}"
            counter += 1

        # Пытаемся найти категорию по имени, если нет — создаём с нужным slug
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'slug': cat_slug}
        )
        # Если категория существовала, но slug у неё отличается (или пустой) — обновляем
        if not created and category.slug != cat_slug:
            # Проверяем, не занят ли новый slug другой категорией (маловероятно, но для безопасности)
            if not Category.objects.filter(slug=cat_slug).exclude(id=category.id).exists():
                category.slug = cat_slug
                category.save()
        # -------------------------------------------------

        product_id = row.get('id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                created_product = False
            except Product.DoesNotExist:
                product = Product(category=category)
                created_product = True
        else:
            product = Product(category=category)
            created_product = True

        product.name = row['name']
        product.price = price
        product.stock = stock
        product.category = category
        product.available = available

        # Обработка slug товара (как было ранее)
        if 'slug' in row and row['slug']:
            product.slug = row['slug']
        else:
            base_slug_product = slugify(product.name)
            if not base_slug_product:
                base_slug_product = f"product-{product_id or 'new'}"
            slug_product = base_slug_product
            counter_product = 1
            while Product.objects.filter(slug=slug_product).exclude(id=product.id).exists():
                slug_product = f"{base_slug_product}-{counter_product}"
                counter_product += 1
            product.slug = slug_product

        if 'old_price' in row and row['old_price']:
            try:
                product.old_price = float(row['old_price'])
            except:
                pass
        if 'description' in row:
            product.description = row['description']

        product.save()
        return 'added' if created_product else 'updated'

    # ---------- Кнопки на странице списка ----------
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_export_import'] = True
        return super().changelist_view(request, extra_context)
