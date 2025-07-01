from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар")
    phone_number = models.CharField(max_length=50, verbose_name="Телефон", help_text="Введите номер телефона")
    country = models.CharField(max_length=50, verbose_name="Страна")
    token = models.CharField(max_length=100, verbose_name="Токен", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Statistic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    successful_deliveries = models.PositiveIntegerField(default=0)
    unsuccessful_attempts = models.PositiveIntegerField(default=0)
    total_messages_sent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Statistics for {self.user.username}"
