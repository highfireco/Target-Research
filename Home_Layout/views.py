from django.shortcuts import render
from firebase_admin import firestore

def home_page(request):
    db = firestore.client()
    surveys = []
    for doc in db.collection('surveys').stream():
        data = doc.to_dict()
        data['id'] = doc.id
        surveys.append(data)
    
    # ✅ ส่งแค่ survey แรก
    first_survey = surveys[0] if surveys else None
    
    return render(request, 'home/home_preview.html', {
        'surveys': surveys,
        'first_survey': first_survey
    })
def setting_page(request):
    return render(request, 'home/settings.html')

def profile_page(request):
    return render(request, 'home/edit_profile.html')