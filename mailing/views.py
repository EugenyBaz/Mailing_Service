from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from mailing.forms import MailingForm
from mailing.models import Mailing, AttemptMailing
from mail.models import Mail
from clients.models import Client
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib import messages
from django.db.models import Case, When, CharField, Value
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class MailingListView(ListView):
    model = Mailing
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят ВСЕ рассылки
            queryset = Mailing.objects.all()
        else:
            # Пользователи видят ТОЛЬКО свои рассылки
            queryset = Mailing.objects.filter(owner=user)

        ORDER_STATUSES = [
            When(status='created', then=Value(1)),
            When(status='launched', then=Value(2)),
            When(status='completed', then=Value(3)),
        ]

        # Применяем сортировку
        sorted_mailings = queryset.annotate(sort_order=Case(*ORDER_STATUSES, output_field=CharField())).order_by(
            'sort_order')
        return sorted_mailings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

        if is_manager:
            # Менеджеры видят всю статистику
            context.update({
                'total_mailings': Mailing.objects.count(),
                'active_mailings': Mailing.objects.filter(status='launched').count(),
                'unique_recipients': len(set(Mailing.objects.values_list('clients__email', flat=True))),
            })
        else:
            # Пользователи видят только статистику по своим рассылкам
            user_mailings = Mailing.objects.filter(owner=user)
            context.update({
                'total_mailings': user_mailings.count(),
                'active_mailings': user_mailings.filter(status='launched').count(),
                'unique_recipients': len(set(user_mailings.values_list('clients__email', flat=True))),
            })

        return context

@method_decorator(login_required, name='dispatch')
class MailingDetailView(DetailView):
    model = Mailing
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.all()  # Добавляем попытки отправки
        return context


@method_decorator(login_required, name='dispatch')
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
                mailing.owner = request.user
                if new_message_subject and new_message_body:
                    new_message = Mail.objects.create(subject_letter=new_message_subject, body_letter=new_message_body)
                    mailing.message = new_message
                mailing.save()
                return redirect('success_url')
        else:
            form = MailingForm()
        return render(request, 'mailing/create_mailing.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    context_object_name = 'mailing'
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


@method_decorator(login_required, name='dispatch')
class MailingDeleteView(DeleteView):
    model = Mailing
    context_object_name = 'mailing'
    success_url = reverse_lazy("mailing:mailing_list")

@login_required
def manual_launch(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    try:
        mailing.send()  # Пробуем отправить рассылку
        messages.success(request, 'Рассылка успешно запущена!')
    except Exception as e:
        messages.error(request, f'Ошибка при запуске рассылки: {str(e)}')
    return redirect('mailing:mailing_list')

@login_required
def update_statuses(request):
    expired_mailings = Mailing.objects.filter(date_and_time_finish_launched__lte=now()).filter(status="launched")
    for mailing in expired_mailings:
        mailing.status = "completed"
        mailing.save()
    return redirect('mailing:mailing_list')



@login_required
def show_statistics(request):
    user = request.user
    is_manager = user.is_staff or user.groups.filter(name='Manager').exists()

    if is_manager:
        # Показывать статистику для всех объектов
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status='launched').count()
        unique_recipients = len(set(Mailing.objects.values_list('clients__email', flat=True)))
        total_attempts = AttemptMailing.objects.count()
        successful_attempts = AttemptMailing.objects.filter(status='success').count()
        failure_attempts = AttemptMailing.objects.filter(status='failure').count()
    else:
        # Отображаем статистику только для текущих рассылок пользователя
        mailings = Mailing.objects.filter(owner=user)

        total_mailings = mailings.count()
        active_mailings = mailings.filter(status='launched').count()
        total_attempts = AttemptMailing.objects.filter(mailing__in=mailings).count()
        unique_recipients = len(set(mailings.values_list('clients__email', flat=True)))
        successful_attempts = AttemptMailing.objects.filter(mailing__in=mailings, status='success').count()
        failure_attempts = AttemptMailing.objects.filter(mailing__in=mailings, status='failure').count()

    context = {
        'type': 'manager' if is_manager else 'user',
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'failure_attempts': failure_attempts,
    }

    return render(request, 'mailing/show_statistics.html', context)