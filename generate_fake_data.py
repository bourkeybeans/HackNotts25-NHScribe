#!/usr/bin/env python3
"""
Generate fake patients and letters for testing the NHScribe application
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random

# Fake data pools
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green"
]

STREETS = [
    "Main Street", "High Street", "Park Avenue", "Church Road", "Station Road",
    "London Road", "Victoria Street", "Green Lane", "Manor Road", "Church Street",
    "Park Road", "Queens Road", "King Street", "New Road", "Mill Lane",
    "Springfield Road", "Oak Avenue", "The Avenue", "School Lane", "York Road"
]

CITIES = [
    "London", "Manchester", "Birmingham", "Leeds", "Liverpool", "Sheffield",
    "Bristol", "Newcastle", "Nottingham", "Southampton", "Leicester", "Coventry",
    "Bradford", "Edinburgh", "Cardiff", "Belfast", "Glasgow", "Brighton", "Oxford"
]

CONDITIONS = [
    "Hypertension", "Type 2 Diabetes", "Asthma", "Arthritis", "Depression",
    "Anxiety", "Migraine", "COPD", "Eczema", "Hypothyroidism",
    "High Cholesterol", "Osteoporosis", "GERD", "Sleep Apnea", "None"
]

DOCTOR_NAMES = [
    "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Williams", "Dr. James Patel",
    "Dr. Rachel Thompson", "Dr. David Kumar", "Dr. Lisa Anderson", "Dr. Robert Singh",
    "Dr. Amanda Taylor", "Dr. Christopher Lee", "Dr. Jennifer Brown", "Dr. Daniel White",
    "Dr. Maria Garcia", "Dr. Thomas Wilson", "Dr. Jessica Martinez"
]

TEST_TYPES = [
    "Full Blood Count", "Haemoglobin", "Cholesterol Panel", "Thyroid Function",
    "Liver Function", "Kidney Function", "HbA1c (Diabetes)", "Vitamin D",
    "Iron Studies", "PSA Test", "Glucose Test", "Urine Analysis"
]

LETTER_TEMPLATES = [
    """Full Blood Count Results

Your recent full blood count test has been completed. The results show:

White Blood Cell Count: {wbc} x10^9/L (Reference: 4.0-11.0)
Red Blood Cell Count: {rbc} x10^12/L (Reference: 4.5-5.5)
Haemoglobin: {hb} g/L (Reference: 115-165)
Platelets: {plt} x10^9/L (Reference: 150-400)

{interpretation}

If you have any concerns or questions about these results, please contact your GP surgery to arrange a follow-up appointment.

Please note that these results are for medical use only and should be discussed with your healthcare provider.""",

    """Cholesterol Test Results

Your cholesterol panel has been analyzed with the following results:

Total Cholesterol: {tc} mmol/L (Reference: <5.0)
LDL Cholesterol: {ldl} mmol/L (Reference: <3.0)
HDL Cholesterol: {hdl} mmol/L (Reference: >1.0)
Triglycerides: {tg} mmol/L (Reference: <1.7)

{interpretation}

We recommend maintaining a healthy diet, regular exercise, and following any prescribed medication regimen. Please schedule a follow-up appointment if you have any concerns.

These results should be reviewed with your healthcare provider for personalized advice.""",

    """Thyroid Function Test Results

Your thyroid function test has been completed. The results are:

TSH (Thyroid Stimulating Hormone): {tsh} mU/L (Reference: 0.4-4.0)
Free T4: {ft4} pmol/L (Reference: 9-25)
Free T3: {ft3} pmol/L (Reference: 3.5-6.5)

{interpretation}

Your thyroid plays a crucial role in regulating metabolism. If you experience symptoms such as fatigue, weight changes, or temperature sensitivity, please discuss with your doctor.

Please keep this letter for your medical records.""",

    """HbA1c Diabetes Monitoring Results

Your HbA1c test, which measures average blood sugar control over the past 2-3 months, shows:

HbA1c: {hba1c} mmol/mol (Reference: <42 non-diabetic, <53 good control)
Equivalent Average Glucose: {avg_glucose} mmol/L

{interpretation}

Continue monitoring your blood glucose levels regularly and maintain your current treatment plan. Lifestyle factors including diet, exercise, and medication adherence are important for optimal control.

Please contact your diabetes care team if you have any questions or concerns.""",

    """Liver Function Test Results

Your liver function tests have been analyzed:

ALT (Alanine Aminotransferase): {alt} U/L (Reference: 10-40)
AST (Aspartate Aminotransferase): {ast} U/L (Reference: 10-40)
Alkaline Phosphatase: {alp} U/L (Reference: 30-130)
Bilirubin: {bili} μmol/L (Reference: 3-17)
Albumin: {alb} g/L (Reference: 35-50)

{interpretation}

Your liver performs many vital functions. If you have concerns about liver health, alcohol consumption, or medications, please discuss with your healthcare provider.

Keep this letter with your medical records.""",

    """Kidney Function Test Results

Your kidney (renal) function has been assessed:

Creatinine: {creat} μmol/L (Reference: 60-110)
eGFR: {egfr} mL/min/1.73m² (Reference: >60)
Urea: {urea} mmol/L (Reference: 2.5-7.8)
Sodium: {na} mmol/L (Reference: 135-145)
Potassium: {k} mmol/L (Reference: 3.5-5.0)

{interpretation}

Your kidneys filter waste from your blood and regulate fluid balance. Staying well-hydrated and managing blood pressure are important for kidney health.

Please retain this letter for your records."""
]

INTERPRETATIONS = {
    "normal": [
        "All results are within the normal reference range. No immediate action is required.",
        "Your results appear normal and satisfactory. Continue with your current health management plan.",
        "These results are within expected limits. No concerns noted at this time.",
        "All values fall within the normal range. Maintain your current lifestyle and medication regimen."
    ],
    "borderline": [
        "Some results are slightly outside the normal range but not significantly concerning. We recommend monitoring and a follow-up test in 3-6 months.",
        "Your results show borderline values. Please consider lifestyle modifications and schedule a follow-up appointment.",
        "While most results are normal, some values warrant attention. Please discuss with your GP at your next appointment.",
        "Results are mostly satisfactory with minor variations. Continue current treatment and retest as recommended."
    ],
    "abnormal": [
        "Some results are outside the normal range and require attention. Please contact your GP surgery to arrange a follow-up appointment within the next 2 weeks.",
        "Your results show values that need medical review. Please schedule an appointment with your healthcare provider to discuss treatment options.",
        "These results indicate that further investigation or treatment adjustment may be necessary. Please contact your doctor promptly.",
        "Abnormal values detected that require medical attention. Please arrange to see your GP as soon as possible to discuss these findings."
    ]
}

def generate_patient():
    """Generate a fake patient"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    
    street_num = random.randint(1, 999)
    street = random.choice(STREETS)
    city = random.choice(CITIES)
    postcode = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1,9)} {random.randint(1,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
    
    address = f"{street_num} {street}, {city}, {postcode}"
    age = random.randint(18, 90)
    sex = random.choice(['M', 'F', 'Other'])
    conditions = random.choice(CONDITIONS)
    
    return {
        'name': name,
        'address': address,
        'age': age,
        'sex': sex,
        'conditions': conditions
    }

def generate_letter_content(test_type):
    """Generate fake letter content based on test type"""
    template_idx = random.randint(0, len(LETTER_TEMPLATES) - 1)
    template = LETTER_TEMPLATES[template_idx]
    
    # Generate random test values
    values = {
        'wbc': round(random.uniform(3.5, 12.0), 1),
        'rbc': round(random.uniform(4.0, 6.0), 2),
        'hb': random.randint(110, 170),
        'plt': random.randint(140, 420),
        'tc': round(random.uniform(3.5, 7.0), 1),
        'ldl': round(random.uniform(2.0, 5.0), 1),
        'hdl': round(random.uniform(0.8, 2.5), 1),
        'tg': round(random.uniform(0.5, 3.0), 1),
        'tsh': round(random.uniform(0.3, 5.0), 2),
        'ft4': round(random.uniform(8, 28), 1),
        'ft3': round(random.uniform(3.0, 7.0), 1),
        'hba1c': random.randint(35, 75),
        'avg_glucose': round(random.uniform(5.0, 12.0), 1),
        'alt': random.randint(8, 60),
        'ast': random.randint(8, 55),
        'alp': random.randint(25, 150),
        'bili': random.randint(2, 22),
        'alb': random.randint(32, 52),
        'creat': random.randint(55, 120),
        'egfr': random.randint(50, 120),
        'urea': round(random.uniform(2.0, 9.0), 1),
        'na': random.randint(133, 147),
        'k': round(random.uniform(3.3, 5.3), 1)
    }
    
    # Determine interpretation based on values
    result_category = random.choices(['normal', 'borderline', 'abnormal'], weights=[60, 30, 10])[0]
    interpretation = random.choice(INTERPRETATIONS[result_category])
    values['interpretation'] = interpretation
    
    try:
        content = template.format(**values)
    except KeyError:
        # If template doesn't match, use a generic one
        content = f"{test_type} Results\n\nYour recent {test_type.lower()} test has been completed.\n\n{interpretation}\n\nPlease contact your GP if you have any questions."
    
    return content

def create_fake_data(num_patients=10, letters_per_patient_range=(1, 3)):
    """Create fake patients and letters in the database"""
    conn = sqlite3.connect('scribe.db')
    cursor = conn.cursor()
    
    print(f"Generating {num_patients} fake patients with letters...")
    print("=" * 60)
    
    total_letters = 0
    
    for i in range(num_patients):
        # Create patient
        patient = generate_patient()
        
        cursor.execute("""
            INSERT INTO patients (name, address, age, sex, conditions)
            VALUES (?, ?, ?, ?, ?)
        """, (patient['name'], patient['address'], patient['age'], 
              patient['sex'], patient['conditions']))
        
        patient_id = cursor.lastrowid
        print(f"\n✓ Created Patient {patient_id}: {patient['name']}")
        print(f"  Age: {patient['age']}, Sex: {patient['sex']}")
        print(f"  Address: {patient['address']}")
        print(f"  Conditions: {patient['conditions']}")
        
        # Create random number of letters for this patient
        num_letters = random.randint(*letters_per_patient_range)
        
        for j in range(num_letters):
            # Generate letter
            letter_uid = str(uuid.uuid4())
            doctor_name = random.choice(DOCTOR_NAMES)
            test_type = random.choice(TEST_TYPES)
            status = random.choices(
                ['Draft', 'Approved', 'Rejected'],
                weights=[50, 40, 10]
            )[0]
            
            # Random date in the last 30 days
            days_ago = random.randint(0, 30)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            # If approved, set approved_at to a few hours after created_at
            approved_at = None
            if status == 'Approved':
                hours_later = random.randint(1, 24)
                approved_at = created_at + timedelta(hours=hours_later)
            
            # Generate letter content
            content = generate_letter_content(test_type)
            
            cursor.execute("""
                INSERT INTO letters (patient_id, doctor_name, details, status, 
                                   letter_uid, created_at, approved_at, content, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, doctor_name, test_type, status, letter_uid,
                  created_at.isoformat(), 
                  approved_at.isoformat() if approved_at else None,
                  content, None))
            
            letter_id = cursor.lastrowid
            total_letters += 1
            
            print(f"  → Letter {letter_id}: {test_type} ({status})")
            print(f"     Doctor: {doctor_name}")
            print(f"     Created: {created_at.strftime('%Y-%m-%d %H:%M')}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✓ Successfully created {num_patients} patients and {total_letters} letters!")
    print("=" * 60)

def clear_fake_data():
    """Clear all data from the database (use with caution!)"""
    response = input("⚠️  WARNING: This will delete ALL patients and letters from the database.\nType 'YES' to confirm: ")
    
    if response != 'YES':
        print("Cancelled.")
        return
    
    conn = sqlite3.connect('scribe.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM letters")
    cursor.execute("DELETE FROM patients")
    
    conn.commit()
    conn.close()
    
    print("✓ All data cleared from database.")

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_fake_data()
        return
    
    # Default: create 10 patients with 1-3 letters each
    num_patients = 10
    
    if len(sys.argv) > 1:
        try:
            num_patients = int(sys.argv[1])
        except ValueError:
            print("Usage: python generate_fake_data.py [num_patients]")
            print("       python generate_fake_data.py --clear  (to clear all data)")
            return
    
    create_fake_data(num_patients=num_patients, letters_per_patient_range=(1, 3))
    
    print("\n💡 Tip: Run 'python generate_fake_data.py --clear' to remove all data")
    print("💡 Tip: Run 'python generate_fake_data.py 20' to create 20 patients")

if __name__ == "__main__":
    main()

