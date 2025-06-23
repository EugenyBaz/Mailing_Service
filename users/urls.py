from django.contrib.auth.views import LoginView, LogoutView
from users.apps import UsersConfig
from django.urls import path

from users.views import UserCreateView, email_verification, account_activation_sent, custom_logout
from users.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>", email_verification, name="email-confirm"),
    path('account_activation_sent/', account_activation_sent, name='account_activation_sent'),
    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]