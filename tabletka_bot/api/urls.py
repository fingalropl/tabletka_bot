from django.urls import path
from .views import ReminderView

urlpatterns = [
    # path("user/", ChatView.as_view(), name="user"),
    # path("reminder_list/", ReminderListView.as_view(), name="reminder"),
    path("reminder/", ReminderView.as_view(), name="reminder"),
]