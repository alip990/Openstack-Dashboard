from django.urls import path, re_path
from django.urls import path
from .views import ProjectsView, ImageView, FlavorView, KeypairView, VmView, ProjectView, SecurityGroupsView, VmOperation, SecurityGroupRuleView

urlpatterns = [
    path('/projects/',  ProjectsView.as_view()),
    path('/project/<str:id>',  ProjectView.as_view()),
    path('/image/', ImageView.as_view()),
    path('/flavor/', FlavorView.as_view()),
    path('/keypair', KeypairView.as_view()),
    path('/vm/', VmView.as_view()),
    path('/security-groups/', SecurityGroupsView.as_view()),
    path('/security-group-rule/', SecurityGroupRuleView.as_view()),
    path('/vm/operation/', VmOperation.as_view())

]
