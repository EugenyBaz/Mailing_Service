from django.contrib import admin
from .models import Mailing


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "date_and_time_first_launched", "date_and_time_finish_launched", "status", "message", "client_names")
    ordering = ("id",)

