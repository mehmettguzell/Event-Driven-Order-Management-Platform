from django.urls import path

from users.api.views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),
]
