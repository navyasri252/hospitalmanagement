import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
myproject_dir = project_root / 'myproject'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append(str(myproject_dir))
sys.path.append(str(project_root))

import django
django.setup()

from hospital.models import Doctor

def seed():
    doctors = [
        # ─── CARDIOLOGY ───────────────────────────────────────────────────
        {
            "name": "James Harrington",
            "department": "CARDIO",
            "specialization": "Interventional Cardiology & Heart Failure",
            "consultation_fee": 220.00,
            "available_days": "Mon - Wed",
        },
        {
            "name": "Priya Mehta",
            "department": "CARDIO",
            "specialization": "Electrophysiology & Cardiac Arrhythmia",
            "consultation_fee": 200.00,
            "available_days": "Tue, Thu, Fri",
        },
        {
            "name": "Nathan Cole",
            "department": "CARDIO",
            "specialization": "Preventive Cardiology & Lipid Management",
            "consultation_fee": 175.00,
            "available_days": "Mon, Wed, Fri",
        },

        # ─── PEDIATRICS ───────────────────────────────────────────────────
        {
            "name": "Sarah Okonkwo",
            "department": "PEDIA",
            "specialization": "Neonatology & Premature Infant Care",
            "consultation_fee": 155.00,
            "available_days": "Tue - Fri",
        },
        {
            "name": "David Kim",
            "department": "PEDIA",
            "specialization": "Pediatric Infectious Diseases",
            "consultation_fee": 140.00,
            "available_days": "Mon - Thu",
        },
        {
            "name": "Amelia Foster",
            "department": "PEDIA",
            "specialization": "Pediatric Neurodevelopment & Autism",
            "consultation_fee": 165.00,
            "available_days": "Mon, Wed, Fri",
        },

        # ─── ORTHOPEDICS ──────────────────────────────────────────────────
        {
            "name": "Marcus Reeves",
            "department": "ORTHO",
            "specialization": "Total Knee & Hip Replacement Surgery",
            "consultation_fee": 180.00,
            "available_days": "Mon, Wed, Fri",
        },
        {
            "name": "Fatima Al-Rashid",
            "department": "ORTHO",
            "specialization": "Spine Surgery & Disc Disorders",
            "consultation_fee": 195.00,
            "available_days": "Tue - Thu",
        },
        {
            "name": "Ryan O'Brien",
            "department": "ORTHO",
            "specialization": "Sports Medicine & Arthroscopy",
            "consultation_fee": 160.00,
            "available_days": "Mon - Wed",
        },

        # ─── NEUROLOGY ────────────────────────────────────────────────────
        {
            "name": "Dana Scully",
            "department": "NEURO",
            "specialization": "Clinical Neurology & Epilepsy",
            "consultation_fee": 210.00,
            "available_days": "Mon - Thu",
        },
        {
            "name": "Arjun Sharma",
            "department": "NEURO",
            "specialization": "Stroke Medicine & Cerebrovascular Disease",
            "consultation_fee": 230.00,
            "available_days": "Mon, Tue, Thu",
        },
        {
            "name": "Helena Voss",
            "department": "NEURO",
            "specialization": "Movement Disorders & Parkinson's Disease",
            "consultation_fee": 195.00,
            "available_days": "Wed - Fri",
        },
    ]

    created_count = 0
    skipped_count = 0
    for d in doctors:
        obj, created = Doctor.objects.get_or_create(
            name=d["name"],
            defaults={
                "department": d["department"],
                "specialization": d["specialization"],
                "consultation_fee": d["consultation_fee"],
                "available_days": d["available_days"],
                "is_active": True,
            }
        )
        if created:
            created_count += 1
            print(f"  [+] Created Dr. {obj.name} ({obj.get_department_display()})")
        else:
            skipped_count += 1
            print(f"  [~] Skipped Dr. {obj.name} (already exists)")

    print(f"\n[DONE] Seeding complete: {created_count} created, {skipped_count} already existed.")

if __name__ == '__main__':
    print("\n[*] Seeding Hospital Database...\n")
    seed()
