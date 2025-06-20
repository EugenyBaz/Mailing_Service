from django.urls import reverse_lazy
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

    def get_success_url(self):
        return reverse_lazy('mail:mail_detail', kwargs={'pk': self.object.pk})


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
    form_class = MailForm
    template_name = "mail/mail_form.html"


class MailDeleteView(DeleteView):
    model = Mail
    # success_url = reverse_lazy("catalog:home")

