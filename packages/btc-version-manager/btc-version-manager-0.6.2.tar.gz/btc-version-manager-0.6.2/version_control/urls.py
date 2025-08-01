from django.urls import path

from . import views

app_name = "version_control"

urlpatterns = [
    path(
        "update_vcs_relation_tree/<int:pk>",
        views.VCSRelationTreeUpdateView.as_view(),
        name="update_vcs_relation_tree",
    ),
]
