from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mailing.apps import MailingConfig
from mailing.views import MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView,  manual_launch, update_statuses

app_name = MailingConfig.name

urlpatterns = [
    path("", MailingListView.as_view(), name="mailing_list"),
    path("<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("create/", MailingCreateView.as_view(), name="mailing_create"),
    path("<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path('manual-launch/<int:mailing_id>/', manual_launch, name='manual_launch'),
    path('update-status/', update_statuses, name='update_statuses'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
