from django.db import models

from clients.models import Client
from mail.models import Mail


class Mailing(models.Model):

    STATUS_CHOICES = (("created", "Cоздана"), ("launched", "Запущена"), ("completed", "Завершена"))

    date_and_time_first_launched = models.DateTimeField(verbose_name="Дата и время первой отправки", auto_now_add=True)
    date_and_time_finish_launched = models.DateTimeField(verbose_name="Дата и время окончания отправки", blank = True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, verbose_name="Статус")
    message = models.ForeignKey(Mail, on_delete=models.CASCADE, verbose_name="Сообщение")
    clients = models.ManyToManyField(Client, verbose_name="Получатели")

    def __str__(self):
        return f"Рассылка '{self.message.subject_letter}' ({self.status})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
