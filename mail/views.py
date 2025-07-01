from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.core.cache import cache
from mail.forms import MailForm
from mail.models import Mail


@method_decorator(login_required, name="dispatch")
@method_decorator(cache_page(60 * 15), name="dispatch")
class MailListView(ListView):
    model = Mail
    context_object_name = "mails"

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

        if is_manager:
            # Менеджеры видят ВСЕ письма
            cache.clear()
            queryset = Mail.objects.all()
        else:
            # Пользователи видят ТОЛЬКО свои письма
            cache.clear()
            queryset = Mail.objects.filter(author=user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_manager = user.is_superuser or user.groups.filter(name="Manager").exists()
        context["is_manager"] = is_manager
        cache.clear()
        return context


@method_decorator(login_required, name="dispatch")
class MailDetailView(DetailView):
    model = Mail
    context_object_name = "mail"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        cache.clear()
        return obj

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

        if is_manager:
            # Менеджеры могут редактировать любое письмо
            cache.clear()
            queryset = Mail.objects.all()
        else:
            # Пользователи могут редактировать только свои письма
            cache.clear()
            queryset = Mail.objects.filter(author=user)
        cache.clear()
        return queryset


@method_decorator(login_required, name="dispatch")
class MailCreateView(CreateView):
    model = Mail
    form_class = MailForm

    def get_success_url(self):
        cache.clear()
        return reverse_lazy("mail:mail_list")

    def form_valid(self, form):
        mail = form.save(commit=False)
        mail.author = self.request.user
        mail.save()
        cache.clear()
        return super().form_valid(form)

    def create_message(request):
        if request.method == "POST":
            form = MailForm(request.POST)
            if form.is_valid():
                mail = form.save(commit=False)
                mail.author = request.user
                mail.save()
                cache.clear()
                return redirect("mail:mail_list")  # перенаправляем на страницу создания рассылки
        else:
            form = MailForm()
        cache.clear()
        return render(request, "mail/mail_form.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class MailUpdateView(UpdateView):
    model = Mail
    context_object_name = "mail"
    form_class = MailForm
    template_name = "mail/mail_form.html"
    success_url = reverse_lazy("mail:mail_list")

    def is_manager(self):
        cache.clear()
        return self.request.user.is_staff or self.request.user.groups.filter(name="Manager").exists()

    def dispatch(self, request, *args, **kwargs):
        # Менеджеры могут читать, но не редактировать
        if self.is_manager:
            cache.clear()
            return HttpResponseForbidden("Вам запрещено редактировать это сообщение.")
        cache.clear()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Обычные пользователи могут редактировать только свои письма
        cache.clear()
        return Mail.objects.filter(author=self.request.user)


@method_decorator(login_required, name="dispatch")
class MailDeleteView(DeleteView):
    model = Mail
    context_object_name = "mail"
    success_url = reverse_lazy("mail:mail_list")

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

        if is_manager:
            # Менеджеры могут удалить любое письмо

            queryset = Mail.objects.all()
        else:
            # Пользователи могут удалить только свои письма

            queryset = Mail.objects.filter(author=user)
        cache.clear()
        return queryset
