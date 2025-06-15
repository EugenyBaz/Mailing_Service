from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from mailing.forms import MailingForm
from mailing.models import Mailing




class MailingListView(ListView):
    model = Mailing


class MailingDetailView(DetailView):
    model = Mailing


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm


class UpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"


class DeleteView(DeleteView):
    model = Mailing
    # success_url = reverse_lazy("catalog:home")


