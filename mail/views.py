from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from mail.forms import MailForm
from mail.models import Mail
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class MailListView(ListView):
    model = Mail
    context_object_name = 'mails'

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят ВСЕ письма
            queryset = Mail.objects.all()
        else:
            # Пользователи видят ТОЛЬКО свои письма
            queryset = Mail.objects.filter(author=user)

        return queryset



@method_decorator(login_required, name='dispatch')
class MailDetailView(DetailView):
    model = Mail
    context_object_name = 'mail'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.save()
        return self.object

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры могут редактировать любое письмо
            queryset = Mail.objects.all()
        else:
            # Пользователи могут редактировать только свои письма
            queryset = Mail.objects.filter(author=user)

        return queryset


@method_decorator(login_required, name='dispatch')
class MailCreateView(CreateView):
    model = Mail
    form_class = MailForm

    def get_success_url(self):
        return reverse_lazy('mail:mail_list')


    def create_message(request):
        if request.method == 'POST':
            form = MailForm(request.POST)
            if form.is_valid():
                mail=form.save()
                return redirect('mailing:mail_detail', pk=mail.id)  # перенаправляем на страницу создания рассылки
        else:
            form = MailForm()
        return render(request, 'mail/mail_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class MailUpdateView(UpdateView):
    model = Mail
    context_object_name = 'mail'
    form_class = MailForm
    template_name = "mail/mail_form.html"
    success_url = reverse_lazy("mail:mail_list")

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры могут редактировать любое письмо
            queryset = Mail.objects.all()
        else:
            # Пользователи могут редактировать только свои письма
            queryset = Mail.objects.filter(author=user)

        return queryset


@method_decorator(login_required, name='dispatch')
class MailDeleteView(DeleteView):
    model = Mail
    context_object_name = 'mail'
    success_url = reverse_lazy("mail:mail_list")

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры могут удалить любое письмо
            queryset = Mail.objects.all()
        else:
            # Пользователи могут удалить только свои письма
            queryset = Mail.objects.filter(author=user)

        return queryset

