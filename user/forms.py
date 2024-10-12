from django.contrib.auth.forms import UserCreationForm
from .models import MyUser
from django import forms

class CreateUserForm(UserCreationForm):
    # Adding status field with custom style
    # status = forms.ChoiceField(
    #     widget=forms.Select(attrs={'class': 'form-control'})
    # )

   class Meta:
        model = MyUser
        fields = ['name', 'email', 'password1', 'password2']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # Here we override the widgets for password1 and password2 to ensure the class is applied
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

