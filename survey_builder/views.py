from django.shortcuts import render

def survey_page(request):
    return render(request, 'survey/survey_preview.html')
# Create your views here.
