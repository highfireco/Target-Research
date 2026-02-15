from django.db import models


class ResearchProject(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('active',    'Active'),
        ('completed', 'Completed'),
        ('closed',    'Closed'),
    ]

    # ── ข้อมูลโครงการ ──────────────────────────
    title       = models.CharField(max_length=255)
    objective   = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # ── ข้อมูลองค์กร ────────────────────────────
    org_name = models.CharField(max_length=255, null=True, blank=True)
    org_type = models.CharField(max_length=50,  null=True, blank=True)
    org_dept = models.CharField(max_length=255, null=True, blank=True)

    # ── ระยะเวลา ────────────────────────────────
    start_date = models.CharField(max_length=20, null=True, blank=True)
    deadline   = models.CharField(max_length=20, null=True, blank=True)

    # ── กลุ่มตัวอย่าง ───────────────────────────
    age_range   = models.CharField(max_length=50,  null=True, blank=True)
    gender      = models.CharField(max_length=20,  null=True, blank=True)
    occupations = models.JSONField(default=list,   blank=True)
    location    = models.CharField(max_length=100, null=True, blank=True)
    sample_size = models.IntegerField(default=0)

    # ── แบบสอบถาม ───────────────────────────────
    question_count = models.IntegerField(null=True, blank=True)
    est_minutes    = models.IntegerField(null=True, blank=True)

    # ── meta ────────────────────────────────────
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    owner_id   = models.CharField(max_length=100, default='anonymous')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ResearchDraft(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('submitted', 'Submitted'),
    ]

    # ── ข้อมูลโครงการ ──────────────────────────
    title       = models.CharField(max_length=255)
    objective   = models.TextField(null=True, blank=True)
    description = models.TextField(blank=True)

    # ── ข้อมูลองค์กร ────────────────────────────
    org_name = models.CharField(max_length=255, null=True, blank=True)
    org_type = models.CharField(max_length=50,  null=True, blank=True)
    org_dept = models.CharField(max_length=255, null=True, blank=True)

    # ── ระยะเวลา ────────────────────────────────
    start_date = models.CharField(max_length=20, null=True, blank=True)
    deadline   = models.CharField(max_length=20, null=True, blank=True)

    # ── กลุ่มตัวอย่าง ───────────────────────────
    age_range   = models.CharField(max_length=50,  null=True, blank=True)
    gender      = models.CharField(max_length=20,  null=True, blank=True)
    occupations = models.JSONField(default=list,   blank=True)
    location    = models.CharField(max_length=100, null=True, blank=True)
    sample_size = models.IntegerField(default=0)

    # ── แบบสอบถาม ───────────────────────────────
    question_count = models.IntegerField(null=True, blank=True)
    est_minutes    = models.IntegerField(null=True, blank=True)

    # ── meta ────────────────────────────────────
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    owner_id   = models.CharField(max_length=100, default='anonymous')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
