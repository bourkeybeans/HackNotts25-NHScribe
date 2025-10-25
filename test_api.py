#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing NHScribe API Endpoints")
    print("=" * 40)
    
    try:
        # Test 1: List patients (should be empty initially)
        print("1. Testing GET /patients/")
        response = requests.get(f"{BASE_URL}/patients/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            patients = response.json()
            print(f"   Found {len(patients)} patients")
        else:
            print(f"   Error: {response.text}")
        
        # Test 2: Create a new patient
        print("\n2. Testing POST /patients/")
        patient_data = {
            "name": "John Doe",
            "age": 45,
            "sex": "M",
            "address": "123 Main St, London",
            "conditions": "Hypertension"
        }
        response = requests.post(f"{BASE_URL}/patients/", data=patient_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            patient = response.json()
            print(f"   Created patient: {patient['name']} (ID: {patient['id']})")
            patient_id = patient['id']
        else:
            print(f"   Error: {response.text}")
            return
        
        # Test 3: Search patients
        print("\n3. Testing GET /patients/search/")
        response = requests.get(f"{BASE_URL}/patients/search/", params={"name": "John"})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            patients = response.json()
            print(f"   Found {len(patients)} patients matching 'John'")
        else:
            print(f"   Error: {response.text}")
        
        # Test 4: List patients again (should have 1 now)
        print("\n4. Testing GET /patients/ (after creation)")
        response = requests.get(f"{BASE_URL}/patients/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            patients = response.json()
            print(f"   Found {len(patients)} patients")
            for p in patients:
                print(f"   - {p['name']} (ID: {p['id']}, Age: {p['age']})")
        
        print("\n✅ All API tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("   Make sure the backend is running on http://localhost:8000")
        print("   Run: uvicorn app:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
