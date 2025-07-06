from django.contrib import admin

from .models import AttemptMailing, Mailing


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_and_time_first_launched",
        "date_and_time_finish_launched",
        "status",
        "message",
        "client_names",
    )
    ordering = ("id",)


@admin.register(AttemptMailing)
class AttemptMailingAdmin(admin.ModelAdmin):
    list_display = ("datetime_attempt", "status", "mailing")
