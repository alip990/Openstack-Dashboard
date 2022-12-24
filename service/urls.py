from django.urls import path
from django.urls import path
from .views import ProjectView , ImageView

urlpatterns = [
    path('/project/',  ProjectView.as_view()),
    path('/image/', ImageView.as_view())
]
