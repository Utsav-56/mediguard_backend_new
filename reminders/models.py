from django.db import models
from utils.models import SyncableModel

class Alarm(SyncableModel):
    is_enabled = models.BooleanField(default=True)
    time_in_minutes = models.IntegerField() # 0-1439
    
    medicine = models.ForeignKey('medications.Medicine', on_delete=models.CASCADE, related_name='alarms')
    
    audio_file_path = models.CharField(max_length=255, blank=True, null=True)
    vibrate = models.BooleanField(default=True)
    snooze_minutes = models.IntegerField(default=5)

    def __str__(self):
        return f"Alarm for {self.medicine.name} at {self.time_in_minutes} ({self.user.email})"
