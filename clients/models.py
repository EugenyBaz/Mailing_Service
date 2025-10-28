from django.conf import settings
from django.db import models

from users.models import User


class Client(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=2, verbose_name="Владелец")
    name = models.CharField(max_length=100, verbose_name="Ф.И.О")
    email = models.EmailField(unique=True, verbose_name="Email")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
