from django.urls import path
from .views import (
    create_project_view,
    create_project_api,
    convert_to_project,
    draft_history_view,   # ⬅ เพิ่มตัวนี้
)

urlpatterns = [
    path('create-project/', create_project_view, name='create_project'),
    path('create-project-api/', create_project_api, name='create_project_api'),
    path('convert/<int:draft_id>/', convert_to_project, name='convert_project'),
    path('drafts/', draft_history_view, name='draft_history'),  # ⬅ เพิ่มบรรทัดนี้
]
