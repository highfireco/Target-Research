from django.shortcuts import render
from core.firebase_config import db
from datetime import datetime, timedelta, timezone
from django.http import HttpResponse, JsonResponse

# ------------------- SURVEY NOTIFICATION -------------------
def survey_notification(request):
    surveys_ref = db.collection("surveys")
    docs = surveys_ref.stream()

    now = datetime.now(tz=timezone.utc)
    survey_list = []

    AVG_TIME_PER_QUESTION = 5  # นาทีต่อคำถาม
    POINTS_PER_MINUTE = 1      # คะแนนต่อ 1 นาที

    for doc in docs:
        data = doc.to_dict()

        created_at_obj = data.get("created_at")
        if not created_at_obj:
            continue

        created_at = created_at_obj  # datetime with tzinfo
        days_diff = (now - created_at).days
        is_new = days_diff <= 3

        expire_date = created_at + timedelta(days=10)
        days_left = max((expire_date - now).days, 0)
        is_ending = 0 <= days_left <= 2

        # --- คำนวณเวลาและคะแนนจากจำนวน question ---
        questions_ref = db.collection("surveys").document(doc.id).collection("questions")
        question_docs = list(questions_ref.stream())
        num_questions = len(question_docs)

        total_time = num_questions * AVG_TIME_PER_QUESTION
        total_points = total_time * POINTS_PER_MINUTE

        survey_list.append({
            "id": doc.id,
            "title": data.get("title"),
            "description": data.get("description"),
            "objective": data.get("objective"),
            "sample_size": data.get("sample_size"),
            "created_at": created_at,
            "is_new": is_new,
            "is_ending": is_ending,
            "days_left": days_left,
            "total_time": total_time,
            "total_points": total_points,
        })

    return render(request, "notifications/survey_notification.html", {
        "surveys": survey_list
    })


# ------------------- PROJECT PROGRESS -------------------
def project_progress_notification(request):
    now = datetime.now(tz=timezone.utc)
    project_data_list = []

    # ดึง projects ทั้งหมด
    projects_ref = db.collection("projects")
    project_docs = projects_ref.stream()

    for project_doc in project_docs:
        project = project_doc.to_dict()
        project_id = project_doc.id
        sample_size = project.get("sample_size", 0)

        # --- ดึง survey ของ project ---
        survey_ref = db.collection("surveys").where(
            field_path="project_id",
            op_string="==",
            value=db.document(f"projects/{project_id}")
        )
        survey_docs = list(survey_ref.stream())

        if not survey_docs:
            continue  # ข้าม project ที่ยังไม่มี survey

        survey_doc = survey_docs[0]
        survey = survey_doc.to_dict()

        start_date = survey.get("start_date")
        end_date = survey.get("end_date")

        print(f"Survey ID: {survey_doc.id}")
        print("Subcollections:", [col.id for col in db.collection("surveys").document(survey_doc.id).collections()])


        # --- นับจำนวน responses ---
        responses_ref = db.collection("responses").where(
            "survey_id", "==", db.document(f"surveys/{survey_doc.id}")
    )
        response_docs = list(responses_ref.stream())
        num_responds = len(response_docs)
        print(f"Survey ID: {survey_doc.id}, Responses found: {num_responds}")


        # --- คำนวณความคืบหน้าเป็น %
        progress_percentage = 0
        if sample_size > 0:
            progress_percentage = min(int((num_responds / sample_size) * 100), 100)

        # --- กำหนดสถานะโครงการ ---
        if num_responds >= sample_size or (end_date and end_date < now):
            status = "completed"
        else:
            status = "in-progress"


        project_data_list.append({
            "survey_title": survey.get("title"),
            "survey_description": survey.get("description"),
            "start_date": start_date,
            "end_date": end_date,
            "num_responds": num_responds,
            "sample_size": sample_size,
            "progress_percentage": progress_percentage,
            "status": status,
        })
    print(project_data_list)

    return render(request, "notifications/project_progress_notification.html", {
        "projects": project_data_list
    })

# ------------------- OTHER NOTIFICATIONS -------------------
def notification_home(request):
    return render(request, "notifications/notification_home.html")

def payment_notification(request):
    return render(request, "notifications/payment_notification.html")