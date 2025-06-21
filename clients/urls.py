from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from clients.apps import ClientsConfig
from clients.views import ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, ClientDeleteView

app_name = ClientsConfig.name

urlpatterns = [
    path("", ClientListView.as_view(), name="client_list"),
    path("<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("create/", ClientCreateView.as_view(), name="client_create"),
    path("<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)