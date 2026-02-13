from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db import transaction

from medications.models import Medicine, Intake
from medications.serializers import MedicineSerializer, IntakeSerializer
from reminders.models import Alarm
from reminders.serializers import AlarmSerializer
from health.models import BloodPressure, BloodSugar, Cholestrol, HeartRate, GenericMetric
from health.serializers import (
    BloodPressureSerializer, BloodSugarSerializer, CholestrolSerializer,
    HeartRateSerializer, GenericMetricSerializer
)

class GlobalSyncView(APIView):
    permission_classes = [IsAuthenticated]

    # Map frontend keys to (Model, Serializer)
    SYNC_MAP = {
        'medicine': (Medicine, MedicineSerializer),
        'intake': (Intake, IntakeSerializer),
        'alarm': (Alarm, AlarmSerializer),
        'blood_pressure': (BloodPressure, BloodPressureSerializer),
        'blood_sugar': (BloodSugar, BloodSugarSerializer),
        'cholestrol': (Cholestrol, CholestrolSerializer),
        'heart_rate': (HeartRate, HeartRateSerializer),
        'generic_metric': (GenericMetric, GenericMetricSerializer),
    }

    def post(self, request):
        since = request.data.get('since')
        client_payload = request.data
        
        print(f"DEBUG: Sync request from {request.user.email}")
        print(f"DEBUG: Since: {since}")
        print(f"DEBUG: Payload : {client_payload}")
        
        server_response_payload = {}
        sync_start_time = timezone.now()

        with transaction.atomic():
            # 1. Process Pushes (Client -> Server)
            payload_data = client_payload.get('payload', {})
            if isinstance(payload_data, dict):
                for key, items in payload_data.items():
                    if key not in self.SYNC_MAP:
                        continue
                    
                    model_class, serializer_class = self.SYNC_MAP[key]
                    
                    for item_data in items:
                        item_id = item_data.get('id')
                        # if not item_id: continue # Validated by serializer or created new

                        try:
                            instance = model_class.objects.get(id=item_id, user=request.user)
                            # Last Write Wins (LWW)
                            client_updated_at = item_data.get('updated_at')
                            if client_updated_at:
                                try:
                                    client_dt = timezone.datetime.fromisoformat(client_updated_at.replace('Z', '+00:00'))
                                    if instance.updated_at and client_dt <= instance.updated_at:
                                        # Server has newer or same data, skip push for this item
                                        continue
                                except ValueError:
                                    pass
                            
                            serializer = serializer_class(instance, data=item_data, partial=True)
                        except model_class.DoesNotExist:
                            # Create new
                            serializer = serializer_class(data=item_data)
                        
                        if serializer.is_valid():
                            if item_id:
                                 # Force creation with the specific UUID provided by client
                                 serializer.save(user=request.user, id=item_id)
                            else:
                                 serializer.save(user=request.user)
                        else:
                            print(f"Sync validation error for {key}: {serializer.errors}")

            # 2. Process Pulls (Server -> Client)
            for key, (model_class, serializer_class) in self.SYNC_MAP.items():
                queryset = model_class.objects.filter(user=request.user)
                if since:
                    try:
                        since_dt = timezone.datetime.fromisoformat(since.replace('Z', '+00:00'))
                        queryset = queryset.filter(updated_at__gt=since_dt)
                    except ValueError:
                        pass
                
                serializer = serializer_class(queryset, many=True)
                server_response_payload[key] = serializer.data

        print(f"DEBUG: Successfully synced data for {request.user.email}")

        return Response({
            'last_sync': sync_start_time.isoformat(),
            'payload': server_response_payload
        }, status=status.HTTP_200_OK)
