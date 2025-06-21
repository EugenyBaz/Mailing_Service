from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from mailing.forms import MailingForm
from mailing.models import Mailing
from mail.models import Mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now


class MailingListView(ListView):
    model = Mailing
    context_object_name = 'mailings'


class MailingDetailView(DetailView):
    model = Mailing
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.save()
        return self.object


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    context_object_name = 'mailing'
    success_url = reverse_lazy("mailing:mailing_list")

    def create_mailing(request):
        if request.method == 'POST':
            form = MailingForm(request.POST)
            if form.is_valid():
                mailing = form.save(commit=False)
                # Здесь дополнительно обрабатываем сохранение письма, если оно было создано новым
                new_message_subject = request.POST.get('new_message_subject')
                new_message_body = request.POST.get('new_message_body')
                if new_message_subject and new_message_body:
                    new_message = Mail.objects.create(subject_letter=new_message_subject, body_letter=new_message_body)
                    mailing.message = new_message
                mailing.save()
                return redirect('success_url')
        else:
            form = MailingForm()
        return render(request, 'mailing/create_mailing.html', {'form': form})

class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    context_object_name = 'mailing'
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(DeleteView):
    model = Mailing
    context_object_name = 'mailing'
    success_url = reverse_lazy("mailing:mailing_list")

def manual_launch(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    mailing.send()  # Запускаем отправку вручную
    return redirect('mailing:mailing_list')

def update_statuses(request):
    expired_mailings = Mailing.objects.filter(date_and_time_finish_launched__lte=now()).filter(status="launched")
    for mailing in expired_mailings:
        mailing.status = "completed"
        mailing.save()
    return redirect('mailing:mailing_list')