from django.contrib import admin

from .models import Mail


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ("subject_letter", "body_letter")
