from django.urls import path
from .views import ChatView

urlpatterns = [
    path("user/", ChatView.as_view(), name="user"),
]