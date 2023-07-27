from django.urls import path
from .views import TaskListApiView, GetTokenView

urlpatterns = [
    path("", TaskListApiView.as_view()),
    path('get_token/', GetTokenView.as_view()),
]
