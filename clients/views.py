from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from clients.forms import ClientForm
from clients.models import Client


class ClientListView(ListView):
    model = Client


class ClientDetailView(DetailView):
    model = Client



class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm



class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"


class ClientDeleteView(DeleteView):
    model = Client
    # success_url = reverse_lazy("catalog:home")