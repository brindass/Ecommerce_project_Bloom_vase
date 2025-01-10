from django.contrib.auth.forms import UserCreationForm
from .models import MyUser, Address
from django import forms



class CreateUserForm(UserCreationForm):
    # Adding status field with custom style
    # status = forms.ChoiceField(
    #     widget=forms.Select(attrs={'class': 'form-control'})
    # )

   class Meta:
        model = MyUser
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # Here we override the widgets for password1 and password2 to ensure the class is applied
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['username','email','first_name','last_name']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street','city','district','state','pincode']
