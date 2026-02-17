import os
import django
import random
import json
from django.utils import timezone
from datetime import datetime, timedelta
from faker import Faker

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile, HealthInfo
from medications.models import Medicine, Intake
from reminders.models import Alarm
from caretakers.models import CareGivers
from health.models import BloodPressure, BloodSugar, Cholestrol, HeartRate, GenericMetric

User = get_user_model()
fake = Faker()

DEFAULT_PASSWORD = "asdfghjkl;'"

def clear_data():
    print("Clearing existing data...")
    User.objects.exclude(is_superuser=True).delete()
    # Cascading deletes will handle most, but let's be sure
    CareGivers.objects.all().delete()
    Medicine.objects.all().delete()
    Intake.objects.all().delete()
    Alarm.objects.all().delete()
    BloodPressure.objects.all().delete()
    BloodSugar.objects.all().delete()
    Cholestrol.objects.all().delete()
    HeartRate.objects.all().delete()
    GenericMetric.objects.all().delete()

def create_user(email, first_name, last_name, is_caretaker_for=None, emergency_email=None):
    user = User.objects.create_user(email=email, password=DEFAULT_PASSWORD)
    
    dob = fake.date_of_birth(minimum_age=20, maximum_age=80)
    age = (timezone.now().date() - dob).days // 365
    
    profile = UserProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        age=age,
        gender=random.choice(['male', 'female']),
        dob=dob,
        phone_number=fake.phone_number(),
        address=fake.address(),
        contact_email=emergency_email
    )
    
    HealthInfo.objects.create(
        user=user,
        blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
        weight=random.uniform(50.0, 100.0),
        height=random.uniform(150.0, 200.0),
        allergies=random.choice(['None', 'Peanuts', 'Penicillin', 'Dust', 'Pollen']),
        chronic_conditions=random.choice(['None', 'Diabetes', 'Hypertension', 'Asthma'])
    )
    
    return user

def seed_user_data(user):
    # Create some medicines
    medicines_list = [
        ("Metformin", "Diabetes management", "500mg", 2),
        ("Lisinopril", "Blood pressure", "10mg", 1),
        ("Atorvastatin", "Cholesterol", "20mg", 1),
        ("Aspirin", "Heart health", "81mg", 1),
        ("Sertraline", "Antidepressant", "50mg", 1),
    ]
    
    for name, desc, strength, dose in random.sample(medicines_list, random.randint(2, 4)):
        medicine = Medicine.objects.create(
            user=user,
            name=name,
            description=desc,
            strength=strength,
            dose_per_intake=dose,
            stock_left=random.randint(10, 50),
            type=random.randint(0, 4),
            intake_times=[480, 1200] if dose == 2 else [480],
            days_of_week=[0, 1, 2, 3, 4, 5, 6]
        )
        
        # Create Alarms
        for time in medicine.intake_times:
            Alarm.objects.create(
                user=user,
                medicine=medicine,
                time_in_minutes=time,
                is_enabled=True
            )
            
        # Create some intakes for the last 3 days
        for i in range(3):
            date = timezone.now().date() - timedelta(days=i)
            for time in medicine.intake_times:
                Intake.objects.create(
                    user=user,
                    medicine=medicine,
                    scheduled_time=time,
                    actual_taken_time=time + random.randint(-10, 10),
                    status=1, # Taken
                    date=date
                )

    # Create Health Metrics
    for i in range(5):
        timestamp = timezone.now() - timedelta(days=i, hours=random.randint(0, 23))
        
        BloodPressure.objects.create(
            user=user,
            timestamp=timestamp,
            systolic=random.randint(110, 140),
            diastolic=random.randint(70, 90),
            pulse=random.randint(60, 100),
            heart_rate=random.randint(60, 100)
        )
        
        BloodSugar.objects.create(
            user=user,
            timestamp=timestamp,
            concentration=random.uniform(80, 150),
            meal_context=random.choice(["Before Breakfast", "After Lunch", "Random"])
        )
        
        HeartRate.objects.create(
            user=user,
            timestamp=timestamp,
            rate=random.randint(60, 100)
        )

def main():
    clear_data()
    
    caretaker_email = "caretaker@mediguard.com"
    
    # 1. Create Caretaker
    caretaker = create_user(
        email=caretaker_email,
        first_name="Samuel",
        last_name="Caretaker"
    )
    print(f"Created Caretaker: {caretaker.email}")
    
    # 2. Create 4 users
    users_info = [
        ("Alice", "Johnson", "alice@test.com"),
        ("Bob", "Smith", "bob@test.com"),
        ("Charlie", "Davis", "charlie@test.com"),
        ("Diana", "Prince", "diana@test.com"),
    ]
    
    details = []
    details.append({
        "role": "Caretaker",
        "email": caretaker.email,
        "password": DEFAULT_PASSWORD,
        "name": "Samuel Caretaker"
    })
    
    for first, last, email in users_info:
        # Relationship established if user's emergency email matches caretaker's login email
        user = create_user(
            email=email,
            first_name=first,
            last_name=last,
            emergency_email=caretaker_email
        )
        seed_user_data(user)
        
        # Explicitly establish relationship in CareGivers model as requested
        CareGivers.objects.create(
            user=user,
            caregiver=caretaker,
            email=caretaker_email,
            nick_name="",
            contact_number=caretaker.profile.phone_number
        )
        
        print(f"Created User: {user.email} (Relation with caretaker established)")
        
        details.append({
            "role": "User",
            "email": user.email,
            "password": DEFAULT_PASSWORD,
            "name": f"{first} {last}",
            "caretaker": caretaker_email
        })
        
    # Write details to user_details.py
    with open('user_details.py', 'w') as f:
        f.write("# MediGuard User Login Details\n")
        f.write("# Generated by create_dummy_data.py\n\n")
        f.write("USERS = " + json.dumps(details, indent=4) + "\n")
    
    print("\nDummy data generation complete!")
    print("User details saved to user_details.py")

if __name__ == "__main__":
    main()
