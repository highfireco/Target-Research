from django.urls import path
from . import views

urlpatterns = [
    path("create-project/",                views.create_project_view,  name="create_project"),
    path("create-project-api/",            views.create_project_api,   name="create_project_api"),
    path("drafts/",                        views.draft_history_view,   name="draft_history"),
    path("drafts/<int:draft_id>/convert/", views.convert_to_project,   name="convert_to_project"),
    path("drafts/<int:draft_id>/delete/",  views.delete_draft,         name="delete_draft"),
    path("my-projects/",                   views.my_projects_view,     name="my_projects"),
    path("project-list/",                  views.project_list_view,    name="project_list"),
]
