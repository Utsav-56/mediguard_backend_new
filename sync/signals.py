import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from medications.models import Medicine, Intake
from reminders.models import Alarm
from health.models import (
    BloodPressure,
    BloodSugar,
    Cholestrol,
    HeartRate,
    GenericMetric,
)

SYNC_MODELS = [
    Medicine,
    Intake,
    Alarm,
    BloodPressure,
    BloodSugar,
    Cholestrol,
    HeartRate,
    GenericMetric,
]


def get_entity_name(instance):
    # Map model to entity name used in SYNC_MAP
    from .utils import SYNC_MAP

    model_name = instance.__class__.__name__
    mapping = {
        "Medicine": "medication",
        "Intake": "intake",
        "Alarm": "alarm",
        "BloodPressure": "blood_pressure",
        "BloodSugar": "blood_sugar",
        "Cholestrol": "cholestrol",
        "HeartRate": "heart_rate",
        "GenericMetric": "generic_metric",
    }
    return mapping.get(model_name)


@receiver(post_save)
def broadcast_update(sender, instance, created, **kwargs):
    if sender in SYNC_MODELS:
        try:
            channel_layer = get_channel_layer()
            from .utils import get_user_group_name
            group_name = get_user_group_name(instance.user.email)

            # Get the serializer for this model
            from .utils import SYNC_MAP

            entity_name = get_entity_name(instance)
            if not entity_name:
                return

            _, serializer_class = SYNC_MAP.get(entity_name, (None, None))

            if serializer_class:
                data = serializer_class(instance).data

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "sync_event",
                        "event": "item_update",
                        "entity": entity_name,
                        "data": data,
                        "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
                    },
                )
        except Exception as e:
            print(f"Error in broadcast_update signal: {e}")


@receiver(post_delete)
def broadcast_delete(sender, instance, **kwargs):
    if sender in SYNC_MODELS:
        try:
            channel_layer = get_channel_layer()
            from .utils import get_user_group_name
            group_name = get_user_group_name(instance.user.email)

            entity_name = get_entity_name(instance)
            if not entity_name:
                return

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "sync_event",
                    "event": "item_delete",
                    "entity": entity_name,
                    "data": {"id": str(instance.id)},
                    "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
                },
            )
        except Exception as e:
            print(f"Error in broadcast_delete signal: {e}")
