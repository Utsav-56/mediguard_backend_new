from rest_framework import serializers
from .models import BloodPressure, BloodSugar, Cholestrol, HeartRate, GenericMetric

class BloodPressureSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodPressure
        fields = '__all__'
        read_only_fields = ('user',)

class BloodSugarSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodSugar
        fields = '__all__'
        read_only_fields = ('user',)

class CholestrolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cholestrol
        fields = '__all__'
        read_only_fields = ('user',)

class HeartRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRate
        fields = '__all__'
        read_only_fields = ('user',)

class GenericMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericMetric
        fields = '__all__'
        read_only_fields = ('user',)
