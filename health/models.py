from django.db import models
from utils.models import SyncableModel

class BaseHealthMetric(SyncableModel):
    timestamp = models.DateTimeField()
    note = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

class BloodPressure(BaseHealthMetric):
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    pulse = models.IntegerField(blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)

class BloodSugar(BaseHealthMetric):
    concentration = models.FloatField() # mg/dL
    meal_context = models.CharField(max_length=100, blank=True, null=True)

class Cholestrol(BaseHealthMetric):
    total_cholesterol = models.FloatField()
    ldl = models.FloatField(blank=True, null=True)
    hdl = models.FloatField(blank=True, null=True)
    triglycerides = models.FloatField(blank=True, null=True)

class HeartRate(BaseHealthMetric):
    rate = models.IntegerField()

class GenericMetric(BaseHealthMetric):
    metric_name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
