from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User, UserProfile
from caretakers.models import CareGivers

@receiver(post_save, sender=UserProfile)
def create_caretaker_from_profile(sender, instance, created, **kwargs):
    """
    When UserProfile is saved, check emergency_contact_email.
    If it matches an existing User, create a CareGivers entry.
    """
    email = instance.emergency_contact_email
    if email:
        try:
            caregiver_user = User.objects.get(email=email)
            # Create link: patient=instance.user, caregiver=caregiver_user
            if caregiver_user != instance.user: # Prevent self-care loop
                CareGivers.objects.get_or_create(
                    user=instance.user,
                    caregiver=caregiver_user,
                    defaults={
                        'nick_name': f"Emergency Contact ({email})",
                        'email': email
                    }
                )
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def create_caretaker_from_user_registration(sender, instance, created, **kwargs):
    """
    When a new User is created (or updated), check if any existing Profiles listed this email as emergency contact.
    If so, create CareGivers entries.
    """
    # Find all profiles where emergency_contact_email == instance.email
    profiles = UserProfile.objects.filter(emergency_contact_email=instance.email)
    
    for profile in profiles:
        if profile.user != instance:
             CareGivers.objects.get_or_create(
                user=profile.user,
                caregiver=instance,
                defaults={
                    'nick_name': f"Emergency Contact ({instance.email})",
                    'email': instance.email
                }
            )
