from django.urls import path
from .views import *

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutContactView.as_view(), name="about"),
    path("contact/", AboutContactView.as_view(), name="contact"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("shipping/", ShippingView.as_view(), name="shipping"),
]
