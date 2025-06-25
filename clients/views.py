from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from clients.forms import ClientForm
from clients.models import Client
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class ClientListView(ListView):
    model = Client
    context_object_name = 'clients'

@method_decorator(login_required, name='dispatch')
class ClientDetailView(DetailView):
    model = Client
    context_object_name = 'client'


@method_decorator(login_required, name='dispatch')
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm

    def get_success_url(self):
        return reverse_lazy('clients:client_list')



@method_decorator(login_required, name='dispatch')
class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    context_object_name = 'client'
    success_url = reverse_lazy("clients:client_list")

@method_decorator(login_required, name='dispatch')
class ClientDeleteView(DeleteView):
    model = Client
    context_object_name = 'client'
    success_url = reverse_lazy("clients:client_list")