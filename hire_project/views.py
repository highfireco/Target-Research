from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ResearchProject
import json
from django.http import HttpResponse


def create_project_view(request):
    return render(request, "hire/create_project.html")


def survey_page(request):
    return render(request, "hire/create_survey.html")


@csrf_exempt
def create_project_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        project = ResearchProject.objects.create(
            title=data.get("title"),
            objective=data.get("objective"),
            description=data.get("description"),
            age_range=data.get("age_range"),
            gender=data.get("gender"),
            location=data.get("location"),
            sample_size=int(data.get("sample_size", 0)),
            status=data.get("status", "draft"),
            owner_id="demo_user_001"
        )

        return JsonResponse({
            "status": "success",
            "project_id": project.id
        })

    return JsonResponse({"error": "POST only"}, status=405)


def draft_history_page(request):
    return HttpResponse("Draft history page (temp)")
