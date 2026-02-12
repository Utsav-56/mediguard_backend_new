from django.db import models
from utils.models import SyncableModel

class Medicine(SyncableModel):
    MEDICINE_TYPES = (
        (0, 'Tablet'),
        (1, 'Capsule'),
        (2, 'Syrup'),
        (3, 'Injection'),
        (4, 'Other'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock_left = models.IntegerField(blank=True, null=True)
    photo = models.ImageField(upload_to='medicine_photos/', blank=True, null=True)
    
    type = models.IntegerField(choices=MEDICINE_TYPES, default=0)
    strength = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    dose_per_intake = models.IntegerField(default=1)
    
    # Store lists as JSON or comma-separated strings. JSON is better for DRF.
    intake_times = models.JSONField(default=list) # List of minutes from midnight
    days_of_week = models.JSONField(default=list) # List of ints 0-6
    
    schedule_alarms = models.BooleanField(default=True)
    alarm_vibrate = models.BooleanField(default=True)
    alarm_snooze_minutes = models.IntegerField(default=5)
    alarm_audio_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class Intake(SyncableModel):
    STATUS_CHOICES = (
        (0, 'Unknown'),
        (1, 'Taken'),
        (2, 'Skipped'),
        (3, 'Missed'),
    )

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='intakes')
    alarm_id = models.UUIDField(blank=True, null=True) # ID of the Alarm model (reminders app)
    
    scheduled_time = models.IntegerField() # minutes from midnight
    actual_taken_time = models.IntegerField(blank=True, null=True)
    
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    notes = models.TextField(blank=True, null=True)
    dosage_taken = models.FloatField(blank=True, null=True)
    
    date = models.DateField()

    def __str__(self):
        return f"Intake of {self.medicine.name} by {self.user.email} on {self.date}"
