from django.urls import path

from . import views

urlpatterns = [
    path("preview/<int:pk>/<slug:key>/", views.preview),
]
