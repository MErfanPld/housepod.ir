from django.urls import path
from .views import (
    UserLoginView,
    UserRegisterView,
    UserLogoutView,
    ProfileView,
    ProfileCompleteView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/complete/", ProfileCompleteView.as_view(), name="profile_complete"),
]
