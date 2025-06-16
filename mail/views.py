from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from mail.forms import MailForm
from mail.models import Mail


class MailListView(ListView):
    model = Mail


class MailDetailView(DetailView):
    model = Mail


class MailCreateView(CreateView):
    model = Mail
    form_class = MailForm


class MailUpdateView(UpdateView):
    model = Mail
    form_class = MailForm
    template_name = "mail/mail_form.html"


class MailDeleteView(DeleteView):
    model = Mail
    # success_url = reverse_lazy("catalog:home")

