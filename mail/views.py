from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from mail.forms import MailForm
from mail.models import Mail
from django.shortcuts import render, redirect


class MailListView(ListView):
    model = Mail
    context_object_name = 'mails'


class MailDetailView(DetailView):
    model = Mail
    context_object_name = 'mail'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.save()
        return self.object



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



class MailUpdateView(UpdateView):
    model = Mail
    context_object_name = 'mail'
    form_class = MailForm
    template_name = "mail/mail_form.html"
    success_url = reverse_lazy("mail:mail_list")


class MailDeleteView(DeleteView):
    model = Mail
    context_object_name = 'mail'
    success_url = reverse_lazy("mail:mail_list")

