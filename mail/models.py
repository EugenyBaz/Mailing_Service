from django.db import models


class Mail(models.Model):
    subject_letter = models.CharField(max_length=100, verbose_name="Тема письма")
    body_letter = models.TextField(verbose_name="Тело письма")


    def __str__(self):
        return self.subject_letter

    class Meta:
        verbose_name = "Почтовое сообщение"
        verbose_name_plural = "Почтовые сообщения"


