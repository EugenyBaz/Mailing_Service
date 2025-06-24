import secrets

from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView

from mailing.models import Mailing, AttemptMailing
from users.forms import UserRegisterForm
from users.models import User
from config.settings import EMAIL_HOST_USER
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import EmailMessage
from django.conf import settings
from users.models import Statistic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib import messages


@login_required
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
    return render(request, 'template_success_registration.html')


@login_required
def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


@login_required
def custom_logout(request):
    """Пользователь выходит из системы."""
    logout(request)
    messages.success(request, 'Вы успешно вышли.')
    return HttpResponseRedirect('/users/login/')


@login_required
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        result = super().form_valid(form)
        return result


@login_required
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


@login_required
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


@login_required
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

@login_required
def user_statistics(request):
    # Получаем статистику только для текущего пользователя
    current_user = request.user
    user_stats = Statistic.objects.filter(user=current_user).first()

    # Рассчитываем статистику по собственным рассылкам пользователя
    mailings = Mailing.objects.filter(owner=current_user)
    total_mailings = mailings.count()
    active_mailings = mailings.filter(status='active').count()
    attempts = AttemptMailing.objects.filter(mailing__owner=current_user)
    total_attempts = attempts.count()
    successful_attempts = attempts.filter(status='success').count()
    failure_attempts = attempts.filter(status='failure').count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'failure_attempts': failure_attempts,
        'user_stats': user_stats,
    }

    return render(request, 'users/user_statistics.html', context)