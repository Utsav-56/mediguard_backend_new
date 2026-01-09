import uuid
from django.db import models
from django.conf import settings

class BaseMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.BigIntegerField() # Unix timestamp as stored in Flutter
    note = models.TextField(blank=True, null=True)
    
    # Sync Metadata
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-timestamp']

class BloodPressure(BaseMetric):
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    pulse = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"BP {self.systolic}/{self.diastolic} - {self.user.email}"

class BloodSugar(BaseMetric):
    concentration = models.FloatField()
    meal_context = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Sugar {self.concentration} - {self.user.email}"

class Cholestrol(BaseMetric):
    total_cholesterol = models.FloatField()
    ldl = models.FloatField(null=True, blank=True)
    hdl = models.FloatField(null=True, blank=True)
    triglycerides = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Cholesterol {self.total_cholesterol} - {self.user.email}"

class HeartRate(BaseMetric):
    rate = models.IntegerField()

    def __str__(self):
        return f"Heart Rate {self.rate} - {self.user.email}"

class GenericMetric(BaseMetric):
    metric_name = models.CharField(max_length=255)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit or ''} - {self.user.email}"
