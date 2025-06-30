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

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят всех клиентов
            queryset = Client.objects.all()
        else:
            # Пользователь видит только своих клиентов
            queryset = Client.objects.filter(owner=user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_manager = user.is_superuser or user.groups.filter(name='Manager').exists()
        context['is_manager'] = is_manager
        return context

@method_decorator(login_required, name='dispatch')
class ClientDetailView(DetailView):
    model = Client
    context_object_name = 'client'

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят всех клиентов
            queryset = Client.objects.all()
        else:
            # Пользователь видит только своих клиентов
            queryset = Client.objects.filter(owner=user)

        return queryset


@method_decorator(login_required, name='dispatch')
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем текущего пользователя в форму
        return kwargs

    def form_valid(self, form):
        # Создаем экземпляр клиента, но пока не сохраняем
        client = form.save(commit=False)
        # Устанавливаем автором текущего пользователя
        client.owner = self.request.user
        # Сохраняем клиента
        client.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clients:client_list')



@method_decorator(login_required, name='dispatch')
class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    context_object_name = 'client'
    success_url = reverse_lazy("clients:client_list")

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят всех клиентов
            queryset = Client.objects.all()
        else:
            # Пользователь видит только своих клиентов
            queryset = Client.objects.filter(owner=user)

        return queryset

@method_decorator(login_required, name='dispatch')
class ClientDeleteView(DeleteView):
    model = Client
    context_object_name = 'client'
    success_url = reverse_lazy("clients:client_list")

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят всех клиентов
            queryset = Client.objects.all()
        else:
            # Пользователь видит только своих клиентов
            queryset = Client.objects.filter(owner=user)

        return queryset