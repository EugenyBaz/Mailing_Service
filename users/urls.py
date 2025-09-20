from django.contrib.auth.views import LoginView
from django.urls import path

from users.apps import UsersConfig
from users.views import (CustomPasswordResetCompleteView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView,
                         CustomPasswordResetView, UserCreateView, account_activation_sent, custom_logout,
                         email_verification, update_user_status, users_list_view)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>", email_verification, name="email-confirm"),
    path("account_activation_sent/", account_activation_sent, name="account_activation_sent"),
    path("reset-password/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("reset-done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset-complete/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("users_list/", users_list_view, name="users_list"),
    path("update-status/", update_user_status, name="update_user_status"),
]
