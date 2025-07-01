from django.contrib.auth import get_user_model
from django.forms import BooleanField, ModelForm

from clients.models import Client

User = get_user_model()


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class ClientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "comment"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Получаем текущего пользователя из аргументов
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.instance.owner = user
