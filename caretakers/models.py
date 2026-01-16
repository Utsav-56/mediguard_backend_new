from accounts.models import User
from django.db import models


"""
Important to understand::
Caregivers are those who will give care to the user in emergencies.
caretakers are those to whom we give care in emergencies.

"""


# Those are the emergency caretakers for a user
# if user gets admitted, these caretakers will be notified
# and will have access to certain info of the user
# one user can have multiple caretakers
# one caretaker can care for multiple users
# many to many relationship through this model
class CareGivers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="caretakers")

    # The user who provides care
    caregiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cared_for_users",  # caregiver.cared_for_users → all users this person cares for
        help_text="The user who provides care",
    )

    # this will be the actual contact number of the caregiver where we can call or send regular SMS
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    # number where we can send whatsapp messages if needed
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    # email of the caregiver where we can send email notifications if needed,  can be diffrent from user email
    email = models.EmailField(blank=True, null=True)

    # name of the caregiver is derived from user profile but can be overridden here
    # nickname means the name by which user knows the caregiver can be different from the actual name
    nick_name = models.CharField(
        max_length=100, blank=True, null=True
    )  # full name assumed

    # where this caretaker lives,  if nothing is given then is derived from user profile
    address = models.TextField(blank=True, null=True)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "caregiver")

    def __str__(self):
        return f"{self.caregiver.email} is a caretaker for {self.user.email}"

    # filter those who are caretakers for a given user
    @staticmethod
    def get_caregivers_for_user(user):
        """Get all caregivers for a given user"""
        return CareGivers.objects.filter(user=user)

    # filter those users for whom this user is a caregiver
    @staticmethod
    def get_users_cared_by(caregiver):
        """Get all users for whom this user is a caregiver"""
        return CareGivers.objects.filter(caregiver=caregiver)
