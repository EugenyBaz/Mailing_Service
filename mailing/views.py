import smtplib
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, CharField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from clients.models import Client
from mail.models import Mail
from mailing.forms import MailingForm
from mailing.models import AttemptMailing, Mailing


@method_decorator(login_required, name="dispatch")
@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingListView(ListView):
    model = Mailing
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

        if is_manager:
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(owner=user)

        ORDER_STATUSES = [
            When(status="created", then=Value(1)),
            When(status="launched", then=Value(2)),
            When(status="completed", then=Value(3)),
        ]

        sorted_mailings = queryset.annotate(sort_order=Case(*ORDER_STATUSES, output_field=CharField())).order_by(
            "sort_order"
        )
        return sorted_mailings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

        if is_manager:
            # Общую статистику для менеджеров
            context.update(
                {
                    "total_mailings": Mailing.objects.count(),  # Всего рассылок
                    "active_mailings": Mailing.objects.filter(status="launched").count(),  # Активных рассылок
                    "unique_recipients": len(
                        set(Client.objects.values_list("email", flat=True))
                    ),  # Уникальные получатели
                }
            )
        else:
            # Индивидуальную статистику для обычных пользователей
            user_mailings = Mailing.objects.filter(owner=user)
            context.update(
                {
                    "total_mailings": user_mailings.count(),  # Всего рассылок
                    "active_mailings": user_mailings.filter(status="launched").count(),  # Активных рассылок
                    "unique_recipients": len(
                        set(Client.objects.filter(mailing__owner=user).values_list("email", flat=True))
                    ),  # Уникальные получатели
                }
            )

        context["is_manager"] = is_manager
        return context


@method_decorator(login_required, name="dispatch")
class MailingDetailView(DetailView):
    model = Mailing
    context_object_name = "mailing"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attempts"] = self.object.attempts.all()  # Добавляем попытки отправки
        return context


@method_decorator(login_required, name="dispatch")
class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    context_object_name = "mailing"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Назначаем владельца рассылки перед сохранением объекта.
        """
        mailing = form.save(commit=False)
        mailing.owner = self.request.user  # Присваиваем владельца рассылки
        mailing.save()
        return super().form_valid(form)

    def create_mailing(request):
        if request.method == "POST":
            form = MailingForm(request.POST)
            if form.is_valid():
                mailing = form.save(commit=False)
                # Здесь дополнительно обрабатываем сохранение письма, если оно было создано новым
                new_message_subject = request.POST.get("new_message_subject")
                new_message_body = request.POST.get("new_message_body")
                mailing.owner = request.user
                if new_message_subject and new_message_body:
                    new_message = Mail.objects.create(subject_letter=new_message_subject, body_letter=new_message_body)
                    mailing.message = new_message
                mailing.save()
                return redirect("success_url")
        else:
            form = MailingForm()
        return render(request, "mailing/create_mailing.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    context_object_name = "mailing"
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")


@method_decorator(login_required, name="dispatch")
class MailingDeleteView(DeleteView):
    model = Mailing
    context_object_name = "mailing"
    success_url = reverse_lazy("mailing:mailing_list")


@login_required
def manual_launch(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    try:
        result = mailing.send()  # Метод send() должен возвращать True или False
        if result:
            messages.success(request, "Рассылка успешно отправлена!")
        else:
            messages.warning(request, "Рассылка была принята, но возможна задержка доставки.")
    except smtplib.SMTPRecipientsRefused:
        messages.error(request, "Ошибка: Один или несколько адресов получателей являются недействительными.")
    except smtplib.SMTPSenderRefused:
        messages.error(request, "Ошибка: Почтовый сервер отказал в отправителе.")
    except smtplib.SMTPAuthenticationError:
        messages.error(request, "Ошибка: Невозможна авторизация на сервере отправки.")
    except smtplib.SMTPConnectError:
        messages.error(request, "Ошибка: Нет соединения с сервером отправки.")
    except smtplib.SMTPHeloError:
        messages.error(request, "Ошибка: Сервер отказался отвечать на запрос HELO.")
    except smtplib.SMTPDataError:
        messages.error(request, "Ошибка: Недопустимые данные при отправке письма.")
    except Exception as e:
        messages.error(request, f"Общая ошибка при отправке письма: {str(e)}.")
    return redirect("mailing:mailing_list")


@login_required
def update_statuses(request):
    expired_mailings = Mailing.objects.filter(date_and_time_finish_launched__lte=now()).filter(status="launched")
    for mailing in expired_mailings:
        mailing.status = "completed"
        mailing.save()
    return redirect("mailing:mailing_list")


@login_required
def show_statistics(request):
    user = request.user
    is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

    if is_manager:
        # Показывать статистику для всех объектов
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(status="launched").count()
        unique_recipients = len(set(Mailing.objects.values_list("clients__email", flat=True)))
        total_attempts = AttemptMailing.objects.count()
        successful_attempts = AttemptMailing.objects.filter(status="success").count()
        failure_attempts = AttemptMailing.objects.filter(status="failure").count()
    else:
        # Отображаем статистику только для текущих рассылок пользователя
        mailings = Mailing.objects.filter(owner=user)

        total_mailings = mailings.count()
        active_mailings = mailings.filter(status="launched").count()
        total_attempts = AttemptMailing.objects.filter(mailing__in=mailings).count()
        unique_recipients = len(set(mailings.values_list("clients__email", flat=True)))
        successful_attempts = AttemptMailing.objects.filter(mailing__in=mailings, status="success").count()
        failure_attempts = AttemptMailing.objects.filter(mailing__in=mailings, status="failure").count()

    # Создаем словарь контекста и добавляем туда флаг is_manager
    context = {
        "type": "manager" if is_manager else "user",
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
        "total_attempts": total_attempts,
        "successful_attempts": successful_attempts,
        "failure_attempts": failure_attempts,
        "is_manager": is_manager,  # <-- Ключевое изменение
    }

    return render(request, "mailing/show_statistics.html", context)


@login_required
def cancel_mailing(request, mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)
    user = request.user
    is_manager = user.is_staff or user.groups.filter(name="Manager").exists()

    if not is_manager:
        messages.error(request, "Только менеджеры могут отменять рассылки.")
        return redirect("mailing:mailing_list")

    # Устанавливаем статус рассылки как "завершено"
    mailing.status = "completed"
    mailing.save()

    messages.success(request, "Рассылка успешно отменена.")
    return redirect("mailing:mailing_list")
