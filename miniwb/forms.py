# miniwb/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False, label="Имя")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')
