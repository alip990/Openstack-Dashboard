from django.urls import path
from django.urls import path
from .views import ProjectView, ImageView, FlavorView

urlpatterns = [
    path('/project/',  ProjectView.as_view()),
    path('/image/', ImageView.as_view()),
    path('/flavor/', FlavorView.as_view())
]
