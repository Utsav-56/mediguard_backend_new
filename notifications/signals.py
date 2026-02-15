from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Notification

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_welcome_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="Welcome to MediGuard!",
            message="Thank you for joining MediGuard. Your health data is now safe and synced.",
            notification_type='success'
        )

from caretakers.models import CareGivers

@receiver(post_save, sender=CareGivers)
def create_caretaker_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            title="New Caretaker Assigned",
            message=f"{instance.caregiver.email} has been assigned as your caretaker.",
            notification_type='caretaker'
        )

# Add more signals here as needed (e.g. from caretakers or medications)
