import secrets

from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import (PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView,
                                       PasswordResetView)
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm
from users.models import User
from django.core.cache import cache


@method_decorator(login_required, name="dispatch")
class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:account_activation_sent")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке, для подтверждения почты. {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


@login_required
def account_activation_sent(request):
    return render(request, "template_success_registration.html")


@login_required
def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    cache.clear()
    return redirect(reverse("users:login"))


@login_required
def custom_logout(request):
    """Пользователь выходит из системы."""
    logout(request)
    messages.success(request, "Вы успешно вышли.")
    cache.clear()
    return HttpResponseRedirect("/users/login/")


@method_decorator(login_required, name="dispatch")
class CustomPasswordResetView(PasswordResetView):
    template_name = "password_reset_form.html"
    email_template_name = "password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")

    def form_valid(self, form):
        result = super().form_valid(form)
        return result


@method_decorator(login_required, name="dispatch")
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "password_reset_done.html"


@method_decorator(login_required, name="dispatch")
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


@method_decorator(login_required, name="dispatch")
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"


User = get_user_model()


@login_required
def users_list_view(request):
    users = User.objects.all()
    is_manager = request.user.is_superuser or request.user.groups.filter(name="Manager").exists()

    # Печать текущих значений для диагностики
    print(f"Request user: {request.user}")
    print(f"User's groups: {request.user.groups.values_list('name', flat=True)}")
    print(f"Is manager: {is_manager}")

    context = {"users": users, "is_manager": is_manager}
    return render(request, "users/users_list.html", context)


@login_required
def update_user_status(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        next_url = request.POST.get("next")
        is_active = "is_active" not in request.POST  # Если чекбокс снят, значит активный, иначе нет

        # Получаем пользователя, чей статус хотим поменять
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
            cache.clear()
            return redirect(next_url)

        # Проверяем, не пытаемся ли мы заблокировать самого себя
        if target_user == request.user:
            messages.warning(request, "Нельзя заблокировать самого себя.")
            cache.clear()
            return redirect(next_url)

        # Если всё хорошо, обновляем статус
        target_user.is_active = is_active
        target_user.save()
        messages.success(request, "Статус пользователя успешно обновлён.")
        cache.clear()
        return redirect(next_url)
    else:
        cache.clear()
        return redirect("users/users_list.html")
