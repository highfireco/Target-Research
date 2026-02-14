from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from firebase_admin import firestore 
from collections import Counter

def survey_dashboard_view(request, survey_id):
    db = firestore.client()

    # ── Security check ──
    survey_ref = db.collection('surveys').document(survey_id)
    survey_doc = survey_ref.get()
    if not survey_doc.exists:
        return render(request, '404.html', status=404)
    
    # if survey_doc.to_dict().get('owner_id') != str(request.user.id):
    #     return render(request, '403.html', status=403)

    # ── ดึง responses ทั้งหมดของ survey นี้ ──
    docs = db.collection('responses') \
             .where('survey_id', '==', survey_ref) \
             .stream()

    all_responses = []
    category_list = []
    monthly_counts = [0] * 12  # ม.ค. - ธ.ค.

    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        

        # เตรียมข้อมูล Pie Chart
        category = data.get('answers', [{}])[0].get('answer')  # สมมติว่า category อยู่ในคำตอบแรก
        if category:
            category_list.append(category)

        # เตรียมข้อมูล Bar Chart
        print("keys:", data.keys())
        print("submitted_at:", data.get('submitted_at'))
        ts = data.get('submitted_at')
        if ts and hasattr(ts, 'month'):
            monthly_counts[ts.month - 1] += 1
            print(f"Response ID {doc.id} submitted at month {ts.month}, updated monthly_counts: {monthly_counts}")
        else:
            print(f"Warning: 'submitted_at' is missing or not a timestamp for response ID {doc.id}")
        all_responses.append(data)

    # ── แปลงข้อมูลสำหรับ Chart ──
    pie_counts = Counter(category_list)
    total=len(all_responses)

    pie_dict_with_percent = {
        label: {
            'count': count,
            'percent': round((count / sum(pie_counts.values()) * 100), 1) if sum(pie_counts.values()) > 0 else 0
        }
        for label, count in pie_counts.items()
    }
    latest_answer = None
    if all_responses:
        latest = all_responses[0]
        answers = latest.get('answers', [])
    
    # debug ดูว่า answers มีอะไร
    print("answers:", answers)
    print("answers type:", type(answers))
    if answers:
        print("answers[0]:", answers[0])
        print("answers[0] type:", type(answers[0]))
    
    if answers:
        latest_answer = answers[0].get('answer', '-')

    context = {
        # ตาราง (ได้ top 5 )
        'latest_responses': all_responses[:5],
        'total_count': len(all_responses),
        'latest_answer': latest_answer or '-',

        # Pie Chart
        'pie_labels': list(pie_counts.keys()),
        'pie_data': list(pie_counts.values()),
        'pie_dict': pie_dict_with_percent,           # สำหรับ progress bar ใน template

        # Bar Chart
        'bar_labels': ["ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.",
                       "ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."],
        'bar_data': monthly_counts,
    }
    return render(request, 'dashboard/dashboard-preview.html', context)