from django.urls import path
from . import views

urlpatterns = [
    path("", views.nerUI, name="Name Entity Recognition"),
    path("result/", views.resultView, name="Test")
]