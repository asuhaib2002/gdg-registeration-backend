from django.urls import include
from django.urls import path

app_name = "api"
urlpatterns = [
    path("v1/registration/", include("gdg_registration_backend.apps.gdg_registration.urls")),
]
