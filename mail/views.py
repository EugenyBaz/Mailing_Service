from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from mail.forms import MailForm
from mail.models import Mail
from django.shortcuts import render, redirect


class MailListView(ListView):
    model = Mail


class MailDetailView(DetailView):
    model = Mail


class MailCreateView(CreateView):
    model = Mail
    form_class = MailForm

    def create_message(request):
        if request.method == 'POST':
            form = MailForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('mailing:mailing_create')  # перенаправляем на страницу создания рассылки
        else:
            form = MailForm()
        return render(request, 'mail/create_message.html', {'form': form})


class MailUpdateView(UpdateView):
    model = Mail
    form_class = MailForm
    template_name = "mail/mail_form.html"


class MailDeleteView(DeleteView):
    model = Mail
    # success_url = reverse_lazy("catalog:home")

