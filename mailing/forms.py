from django.forms import ModelForm, BooleanField
from mailing.models import Mailing



class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = "__all__"