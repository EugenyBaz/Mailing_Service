from django.db import models
from django.shortcuts import redirect
from django.utils.timezone import now
from clients.models import Client
from mail.models import Mail


class Mailing(models.Model):

    STATUS_CHOICES = (("created", "Cоздана"), ("launched", "Запущена"), ("completed", "Завершена"))

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
        if self.status == "completed" or self.status == "created":
            self.date_and_time_first_launched = now()
            self.status = "launched"
            self.save()
        else:
            raise Exception("Рассылка уже запущена и не может быть запущена повторно!")

    def check_expiration(self):
        if self.date_and_time_finish_launched and self.date_and_time_finish_launched <= now() and self.status != "completed":
            self.status = "completed"
            self.save()




    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
