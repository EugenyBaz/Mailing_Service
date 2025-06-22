from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from mailing.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "avatar", "phone_number", "country", "password1", "password2")



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email Address")