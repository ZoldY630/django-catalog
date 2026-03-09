from django import forms
from .models import Category

class ProductImportForm(forms.Form):
    file = forms.FileField(label="Файл для импорта (CSV или JSON)")
    file_format = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('json', 'JSON')],
        label="Формат файла"
    )

class ProductExportForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория",
        empty_label="Все категории"
    )
    available = forms.NullBooleanField(
        label="Активность",
        widget=forms.Select(choices=[('', 'Все'), ('1', 'Активные'), ('0', 'Неактивные')]),
        required=False
    )
    price_min = forms.DecimalField(
        required=False,
        label="Цена от",
        min_value=0
    )
    price_max = forms.DecimalField(
        required=False,
        label="Цена до",
        min_value=0
    )
    format = forms.ChoiceField(
        choices=[('csv', 'CSV'), ('json', 'JSON')],
        label="Формат файла",
        initial='csv'
    )
