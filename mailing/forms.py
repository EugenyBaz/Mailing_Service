from django.forms import BooleanField, ModelForm

from mailing.models import Mail, Mailing


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        exclude = ["owner"]
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Передаем пользователя из view
        super().__init__(*args, **kwargs)
        if user:
            self.fields["message"].queryset = Mail.objects.filter(author=user)
