from django.urls import path

from users.api.views import LoginView, RegisterView, LogoutView, RefreshTokenView, UserProfileView, VerifyTokenView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("refresh-token/", RefreshTokenView.as_view()),
    path("user-profile/", UserProfileView.as_view()),
    path("verify-token/", VerifyTokenView.as_view())
]
