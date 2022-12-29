from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Order


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'

    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control rounded-0'}))

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'buying_type', 'order_date', 'comment'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'phone': forms.TextInput(attrs={'class': 'form-control rounded-0'}),
            'address': forms.Textarea(attrs={'class': 'form-control rounded-0'}),
            'buying_type': forms.Select(attrs={'class': 'form-select rounded-0'}),
            'comment': forms.Textarea(attrs={'class': 'form-control rounded-0'}),
        }


class RegisterUserForm(UserCreationForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email')

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'inputEmailAddress',
                'placeholder': 'user@example.com'
            }),
        }


class LoginUserForm(AuthenticationForm):

    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))



