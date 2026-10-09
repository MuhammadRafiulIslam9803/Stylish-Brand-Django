from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth import password_validation
from . models import Customer, Product

#Registration
class CustomerRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget = forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget = forms.PasswordInput(attrs={'class':'form-control'}))
    email = forms.CharField(required=True, widget= forms.EmailInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'email':'Email'}
        widget = {'username': forms.TextInput(attrs={'class':'form-control'})}



#login
class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus':True,'class':'form-control' }))
    password = forms.CharField(label=_('Password'),strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current_password','class':'form-control' }))


#Password Change
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_('Old Password'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'autofocus': True, 'class':'form-control'}))

    new_password1 = forms.CharField(label=_('New Password'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new password', 'class':'form-control'}), help_text=password_validation.password_validators_help_text_html())

    new_password2 = forms.CharField(label=_('Confirm New Password'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new password', 'class':'form-control'}))


#Reset
class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=50, widget=forms.EmailInput(attrs={'autocomplete':'email', 'class':'form_control'}))


#Set passwordform
class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_('New Password'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new password', 'class':'form-control'}), help_text=password_validation.password_validators_help_text_html())

    new_password2 = forms.CharField(label=_('Confirm New Password'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new password', 'class':'form-control'}))


#profile
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','division','district','thana','villorroad','zipcode']
        widgets = {'name':forms.TextInput(attrs={'class':'form-control'}), 'division':forms.Select(attrs={'class':'form-control'}), 'district':forms.TextInput(attrs={'class':'form-control'}), 'thana':forms.TextInput(attrs={'class':'form-control'}), 'villorroad':forms.TextInput(attrs={'class':'form-control'}), 'zipcode':forms.NumberInput(attrs={'class':'form-control'})} 



# store admin form

    


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "selling_price",
            "discounted_price",
            "description",
            "brand",
            "category",
            "product_image",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name",
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
            }),
            "discounted_price": forms.NumberInput(attrs={
                "class": "form-control",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
            }),
            "brand": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter brand",
            }),
            "category": forms.Select(attrs={
                "class": "form-select",
            }),
            "product_image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }