from django.db import models

class ResearchProject(models.Model):
    title = models.CharField(max_length=255)
    objective = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    age_range = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    sample_size = models.IntegerField(default=0)

    status = models.CharField(max_length=20, default="draft")  
    owner_id = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
