import uuid
from django.db import models
from django.conf import settings

class Medicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="medicines")
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock_left = models.IntegerField(blank=True, null=True)
    photo_path = models.CharField(max_length=512, blank=True, null=True) # Paths might be local to phone
    medicine_type = models.CharField(max_length=50, blank=True, null=True) # Store enum as string
    strength = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    dose_per_intake = models.IntegerField(default=1)
    
    # Schedule as JSON or comma-separated
    intake_times = models.JSONField(default=list) # List of minutes from midnight
    days_of_week = models.JSONField(default=list) # List of ints 0-6
    
    # Alarm settings
    schedule_alarms = models.BooleanField(default=True)
    alarm_vibrate = models.BooleanField(default=True)
    alarm_snooze_minutes = models.IntegerField(default=5)
    alarm_audio_path = models.CharField(max_length=512, blank=True, null=True)
    
    # Sync Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class Intake(models.Model):
    STATUS_CHOICES = (
        ("taken", "Taken"),
        ("missed", "Missed"),
        ("skipped", "Skipped"),
        ("unknown", "Unknown"),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="intakes")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="intake_records")
    
    scheduled_time = models.DateTimeField()
    actual_taken_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    notes = models.TextField(blank=True, null=True)
    dosage_taken = models.FloatField(null=True, blank=True)
    date = models.DateField()
    
    # Sync Metadata
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Intake of {self.medicine.name} at {self.scheduled_time} ({self.status})"
