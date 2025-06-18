from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from mailing.forms import MailingForm
from mailing.models import Mailing
from django.shortcuts import render, redirect




class MailingListView(ListView):
    model = Mailing


class MailingDetailView(DetailView):
    model = Mailing

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views_count += 1
        self.object.save()
        return self.object


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm

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
    template_name = "mailing/mailing_form.html"


class MailingDeleteView(DeleteView):
    model = Mailing
    # success_url = reverse_lazy("catalog:home")


