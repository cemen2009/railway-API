from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import CreateUserView


app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("token/verify/", TokenVerifyView.as_view(), name="verify_token"),
    # path("me/", ManageUserView.as_view(), name="profile"),
]
