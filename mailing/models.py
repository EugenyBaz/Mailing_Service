from django.core.mail import send_mail
from django.db import models
from django.shortcuts import redirect
from django.utils.timezone import now
from clients.models import Client
from mail.models import Mail
from config.settings import EMAIL_HOST_USER
from django.conf import settings


class Mailing(models.Model):

    STATUS_CHOICES = (("created", "Cоздана"), ("launched", "Запущена"), ("completed", "Завершена"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=2, verbose_name="Владелец")
    date_and_time_first_launched = models.DateTimeField(verbose_name="Дата и время первой отправки", blank=True, null=True)
    date_and_time_finish_launched = models.DateTimeField(verbose_name="Дата и время окончания отправки", blank = True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default = "created", verbose_name="Статус")
    message = models.ForeignKey(Mail, on_delete=models.CASCADE, verbose_name="Сообщение")
    clients = models.ManyToManyField(Client, verbose_name="Получатели")

    def client_names(self):
        return ", ".join([client.name for client in self.clients.all()])

    client_names.short_description = "Получатели"


    def __str__(self):
        return f"Рассылка '{self.message.subject_letter}' ({self.status})"

    def send(self):
        if self.status == "completed":  # Блокируем повторный запуск только завершённых успешных рассылок
            raise Exception("Рассылка уже успешно завершена и не может быть запущена повторно!")

        elif self.status == "launched":  # Если рассылка запущена, делаем предупреждение
            print("Рассылка уже запущена, но возможна повторная попытка...")

        else:  # Во всех остальных случаях разрешаем отправку
            self.date_and_time_first_launched = now()
            self.status = "launched"
            self.save()
            self._send_email()

    def check_expiration(self):
        if self.date_and_time_finish_launched and self.date_and_time_finish_launched <= now() and self.status != "completed":
            self.status = "completed"
            self.save()

    def _send_email(self):
        """Реализует отправку письма и сохраняет результат"""
        subject = self.message.subject_letter
        body = self.message.body_letter
        sender_email = EMAIL_HOST_USER  # Почта отправителя
        recipient_emails = list(self.clients.values_list('email', flat=True))  # Получатели

        try:
            result = send_mail(subject, body, sender_email, recipient_emails)
            if result > 0:
                status = 'success'
                server_response = "Сообщение успешно доставлено."
            else:
                status = 'failure'
                server_response = "Сообщение не удалось доставить."
        except Exception as e:
            status = 'failure'
            server_response = str(e)

        # Сохраняем результат отправки
        attempt = AttemptMailing.objects.create(
            status=status,
            server_response=server_response,
            mailing=self
        )

        return attempt


    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class AttemptMailing(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно' ),
        ('failure', 'Не успешно')
    ]

    datetime_attempt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    server_response = models.TextField(blank= True, null= True)
    mailing = models.ForeignKey(Mailing, related_name= 'attempts', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.mailing} - {self.status}'

