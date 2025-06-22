from django.contrib.auth.views import LoginView, LogoutView
from users.apps import UsersConfig
from django.urls import path

from users.views import UserCreateView, email_verification, account_activation_sent

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page='/users/login/'), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>", email_verification, name="email-confirm"),
    path('account_activation_sent/', account_activation_sent, name='account_activation_sent'),
]