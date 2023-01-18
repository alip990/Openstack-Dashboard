from django.urls import path
from django.urls import path
from .views import ProjectView, ImageView, FlavorView, KeypairView, VmView

urlpatterns = [
    path('/project/',  ProjectView.as_view()),
    path('/image/', ImageView.as_view()),
    path('/flavor/', FlavorView.as_view()),
    path('/<str:project_id>/keypair', KeypairView.as_view()),
    path('/<str:project_id>/vm/', VmView.as_view())
]
