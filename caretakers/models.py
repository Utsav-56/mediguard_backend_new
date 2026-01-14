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
    caretaker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cared_users"
    )

    contact_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # full name assumed
    address = models.TextField(blank=True, null=True)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "caretaker")

    def __str__(self):
        return f"{self.caretaker.email} is a caretaker for {self.user.email}"
