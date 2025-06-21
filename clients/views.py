from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from clients.forms import ClientForm
from clients.models import Client


class ClientListView(ListView):
    model = Client
    context_object_name = 'clients'


class ClientDetailView(DetailView):
    model = Client
    context_object_name = 'client'



class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm

    def get_success_url(self):
        return reverse_lazy('clients:client_list')




class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    context_object_name = 'client'
    success_url = reverse_lazy("clients:client_list")


class ClientDeleteView(DeleteView):
    model = Client
    context_object_name = 'client'
    success_url = reverse_lazy("clients:client_list")