from django.shortcuts import render
from core.firebase_config import db
from datetime import datetime, timedelta, timezone

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


def project_progress_notification(request):
    now = datetime.now(tz=timezone.utc)
    project_data_list = []

    projects_ref = db.collection("projects")
    project_docs = projects_ref.stream()

    for project_doc in project_docs:
        project = project_doc.to_dict()
        project_id = project_doc.id

        # --- เช็ค status active ---
        if project.get("status") != "active":
            print(f"Skipping project {project_id}: status is {project.get('status')}")
            continue

        sample_size = project.get("sample_size", 0)
        start_date = project.get("start_date")
        end_date = project.get("deadline")

        # --- เช็ค datetime ---
        if not isinstance(start_date, datetime):
            print(f"Skipping project {project_id}: start_date is not datetime ({start_date})")
            continue
        if not isinstance(end_date, datetime):
            print(f"Skipping project {project_id}: deadline is not datetime ({end_date})")
            continue

        # --- ดึง survey ของ project ---
        survey_ref = db.collection("surveys").where(
            "project_id", "==", db.document(f"projects/{project_id}")
        )
        survey_docs = list(survey_ref.stream())

        if not survey_docs:
            print(f"No survey found for project {project_id}")
            continue

        survey_doc = survey_docs[0]
        survey = survey_doc.to_dict()

        # --- นับจำนวนคำถามจาก subcollection questions ---
        questions_ref = db.collection("surveys") \
            .document(survey_doc.id) \
            .collection("questions")
        question_count = len(list(questions_ref.stream()))
        print(f"Survey {survey_doc.id} has {question_count} questions")

        # --- นับ responses ---
        responses_ref = db.collection("responses").where(
            "survey_id", "==", db.document(f"surveys/{survey_doc.id}")
        )
        response_docs = list(responses_ref.stream())
        num_responds = len(response_docs)
        print(f"Survey {survey_doc.id} has {num_responds} responses")

        # --- คำนวณ progress ---
        progress_percentage = 0
        if sample_size > 0:
            progress_percentage = min(int((num_responds / sample_size) * 100), 100)

        # --- กำหนดสถานะ ---
        if num_responds >= sample_size or end_date < now:
            status = "completed"
        else:
            status = "in-progress"

        # --- เพิ่มเข้า list ---
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

    print("Final project_data_list:", project_data_list)
    return render(request, "notifications/project_progress_notification.html", {
        "projects": project_data_list
    })

# ------------------- OTHER NOTIFICATIONS -------------------
def notification_home(request):
    return render(request, "notifications/notification_home.html")

def payment_notification(request):
    return render(request, "notifications/payment_notification.html")

