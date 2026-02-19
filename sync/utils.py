from django.utils import timezone
from django.db import transaction
from medications.models import Medicine, Intake
from medications.serializers import MedicineSerializer, IntakeSerializer
from reminders.models import Alarm
from reminders.serializers import AlarmSerializer
from health.models import (
    BloodPressure,
    BloodSugar,
    Cholestrol,
    HeartRate,
    GenericMetric,
)
from health.serializers import (
    BloodPressureSerializer,
    BloodSugarSerializer,
    CholestrolSerializer,
    HeartRateSerializer,
    GenericMetricSerializer,
)

SYNC_MAP = {
    "medication": (Medicine, MedicineSerializer),
    "intake": (Intake, IntakeSerializer),
    "alarm": (Alarm, AlarmSerializer),
    "blood_pressure": (BloodPressure, BloodPressureSerializer),
    "blood_sugar": (BloodSugar, BloodSugarSerializer),
    "cholestrol": (Cholestrol, CholestrolSerializer),
    "heart_rate": (HeartRate, HeartRateSerializer),
    "generic_metric": (GenericMetric, GenericMetricSerializer),
}

def get_user_group_name(email):
    """
    Generates a valid Channels group name from an email.
    Channels only allows alphanumerics, hyphens, underscores, or periods.
    """
    sanitized = email.replace("@", "_at_").replace(".", "_")
    return f"user_{sanitized}"

def process_item(user, entity, item_data, item_success_callback=None):
    if entity not in SYNC_MAP:
        return None

    model_class, serializer_class = SYNC_MAP[entity]
    item_id = item_data.get("id")

    try:
        instance = model_class.objects.get(id=item_id, user=user)
        client_updated_at = item_data.get("updated_at")
        if client_updated_at:
            try:
                client_dt = timezone.datetime.fromisoformat(
                    client_updated_at.replace("Z", "+00:00")
                )
                if instance.updated_at and client_dt <= instance.updated_at:
                    return instance  # No update needed, server version is newer or same
            except ValueError:
                pass
        serializer = serializer_class(instance, data=item_data, partial=True)
    except model_class.DoesNotExist:
        serializer = serializer_class(data=item_data)

    if serializer.is_valid():
        if item_id:
            saved_instance = serializer.save(user=user, id=item_id)
        else:
            saved_instance = serializer.save(user=user)

        if item_success_callback and saved_instance:
            item_success_callback(entity, saved_instance, serializer.data)
        return saved_instance
    else:
        print(f"Sync validation error for {entity}: {serializer.errors}")
        return None


def perform_sync(
    user, client_payload, progress_callback=None, item_success_callback=None
):
    since = client_payload.get("since")
    server_response_payload = {}
    sync_start_time = timezone.now()

    with transaction.atomic():
        # 1. Process Pushes (Client -> Server)
        payload_data = client_payload.get("payload", {})
        if isinstance(payload_data, dict):
            total_keys = len(payload_data)
            for idx, (key, items) in enumerate(payload_data.items()):
                if key not in SYNC_MAP:
                    continue

                if progress_callback:
                    progress_callback(
                        f"Processing {key}...", 0.1 + (idx / total_keys) * 0.4
                    )

                total_items = len(items)
                for idx_item, item_data in enumerate(items):
                    if progress_callback:
                        progress_callback(
                            status=f"Pushing {key}...",
                            progress=(idx_item + 1) / total_items
                            if total_items > 0
                            else 1.0,
                            entity=key,
                            current=idx_item + 1,
                            total=total_items,
                            mode="push",
                        )
                    process_item(user, key, item_data, item_success_callback)

        # 2. Process Pulls (Server -> Client)
        if progress_callback:
            progress_callback("Fetching updates...", 0.6)

        pull_ids_map = client_payload.get("pull_ids", {})
        total_models = len(SYNC_MAP)
        for idx, (key, (model_class, serializer_class)) in enumerate(SYNC_MAP.items()):
            if progress_callback:
                progress_callback(
                    f"Preparing {key} updates...", 0.6 + (idx / total_models) * 0.3
                )

            # Targeted pull based on IDs if provided, otherwise fallback to since_dt
            pull_ids = pull_ids_map.get(key, [])
            if pull_ids:
                queryset = model_class.objects.filter(user=user, id__in=pull_ids)
            else:
                queryset = model_class.objects.filter(user=user)
                if since:
                    try:
                        since_dt = timezone.datetime.fromisoformat(
                            since.replace("Z", "+00:00")
                        )
                        queryset = queryset.filter(updated_at__gt=since_dt)
                    except ValueError:
                        pass

            serializer = serializer_class(queryset, many=True)
            server_response_payload[key] = serializer.data

    if progress_callback:
        progress_callback("Sync complete", 1.0)

    # Create a notification for the user
    try:
        from notifications.models import Notification

        Notification.objects.create(
            user=user,
            title="Data Synced",
            message=f"Sync completed at {sync_start_time.strftime('%H:%M:%S')}. Your health data is up to date.",
            notification_type="sync",
        )
    except Exception as e:
        print(f"Error creating sync notification: {e}")

    return {
        "last_sync": sync_start_time.isoformat().replace("+00:00", "Z"),
        "payload": server_response_payload,
    }
