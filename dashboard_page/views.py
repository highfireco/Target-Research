from django.shortcuts import render,redirect
from core.firebase_config import db
from collections import Counter

def survey_dashboard_view(request, survey_id):
    uid=request.session.get("uid")
    if not uid:
        return redirect("login")
    
    all_responses = []
    category_list = []
    monthly_counts = [0] * 12
    sample_size = 0

    # ── Security check ──
    survey_ref = db.collection('surveys').document(survey_id)
    survey_doc = survey_ref.get()
    if not survey_doc.exists:
        return render(request, '404.html', status=404)


    # ── current survey สำหรับ dropdown ──
    current_survey = survey_doc.to_dict()
    current_survey['id'] = survey_id

    if current_survey.get('owner_id') != uid:  # username = Firebase UID
        return redirect("home_page")
    
    # ── ดึง surveys ทั้งหมดสำหรับ dropdown ──
    all_surveys = []
    surveys_stream = db.collection('surveys').where('owner_id', '==', uid).stream()
    for doc in surveys_stream:
        data = doc.to_dict()
        data['id'] = doc.id
        all_surveys.append(data)

    # ── ดึง responses ของ survey นี้ ──
    survey_path_string = f"/surveys/{survey_id}"
    docs = db.collection('responses').where('survey_id', '==', survey_path_string).stream()

    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id

        category = data.get('answers', [{}])[0].get('answer')
        if category:
            category_list.append(category)

        ts = data.get('submitted_at')
        if ts and hasattr(ts, 'month'):
            monthly_counts[ts.month - 1] += 1

        all_responses.append(data)

    # ── แปลงข้อมูล Chart ──
    pie_counts = Counter(category_list)

    pie_dict_with_percent = {
        label: {
            'count': count,
            'percent': round((count / sum(pie_counts.values()) * 100), 1) if pie_counts else 0
        }
        for label, count in pie_counts.items()
    }

    latest_answer = '-'
    if all_responses:
        answers = all_responses[0].get('answers', [])
        if answers:
            latest_answer = answers[0].get('answer', '-')

# ── คำนวณ response_rate ──
    project_id_raw = current_survey.get('project_id')
    if project_id_raw:
        if isinstance(project_id_raw, str):
            project_id = project_id_raw.split('/')[-1]
            project_ref = db.collection('projects').document(project_id)
        else:
            project_ref = project_id_raw

        project_doc = project_ref.get()
        if project_doc.exists:
            sample_size = project_doc.to_dict().get('sample_size', 0)

    total_count = len(all_responses)
    response_rate = round((total_count / sample_size * 100), 1) if sample_size > 0 else 0

    context = {
        'latest_responses': all_responses[:5],
        'total_count': len(all_responses),
        'latest_answer': latest_answer,
        'all_surveys': all_surveys,          # ✅ surveys จริงสำหรับ dropdown
        'current_survey': current_survey,    # ✅ survey ที่เลือกอยู่
        'pie_labels': list(pie_counts.keys()),
        'pie_data': list(pie_counts.values()),
        'pie_dict': pie_dict_with_percent,
        'bar_labels': ["ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.",
                       "ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."],
        'bar_data': monthly_counts,
        'response_rate': response_rate  
    }
    return render(request, 'dashboard/dashboard-preview.html', context)