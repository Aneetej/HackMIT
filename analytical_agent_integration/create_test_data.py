#!/usr/bin/env python3
"""
Create test data for analytics integration testing
"""

import requests
import json
from datetime import datetime, timedelta

def create_test_teacher():
    """Create a test teacher with proper data relationships"""
    try:
        # Create teacher
        teacher_data = {
            "email": "test.teacher@example.com",
            "name": "Test Analytics Teacher",
            "subject": "Mathematics"
        }
        
        response = requests.post("http://localhost:4000/api/teacher/register", 
                               json=teacher_data, timeout=10)
        
        if response.status_code == 201:
            teacher = response.json()
            teacher_id = teacher['teacherId']
            print(f"✓ Created test teacher: {teacher_id}")
            return teacher_id
        elif response.status_code == 409:
            # Teacher already exists
            teacher = response.json()
            teacher_id = teacher['teacherId']
            print(f"✓ Using existing test teacher: {teacher_id}")
            return teacher_id
        else:
            print(f"✗ Failed to create teacher: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating teacher: {e}")
        return None

def create_test_student():
    """Create a test student"""
    try:
        student_data = {
            "email": "test.student@example.com",
            "name": "Test Student",
            "grade": 10,
            "subject_focus": "algebra",
            "learning_style": "visual"
        }
        
        response = requests.post("http://localhost:4000/api/student/register", 
                               json=student_data, timeout=10)
        
        if response.status_code == 201:
            student = response.json()
            student_id = student['studentId']
            print(f"✓ Created test student: {student_id}")
            return student_id
        elif response.status_code == 409:
            # Student already exists
            student = response.json()
            student_id = student['studentId']
            print(f"✓ Using existing test student: {student_id}")
            return student_id
        else:
            print(f"✗ Failed to create student: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating student: {e}")
        return None

def create_test_class(teacher_id):
    """Create a test class for the teacher"""
    try:
        class_data = {
            "name": "Test Analytics Class",
            "restrictions": "None",
            "teachingStyle": "Interactive",
            "studentGrade": "10",
            "subject": "Mathematics",
            "otherNotes": "Test class for analytics"
        }
        
        response = requests.post(f"http://localhost:4000/api/teacher/{teacher_id}/class", 
                               json=class_data, timeout=10)
        
        if response.status_code == 200:
            class_data = response.json()
            class_id = class_data['class']['id']
            print(f"✓ Created test class: {class_id}")
            return class_id
        else:
            print(f"✗ Failed to create class: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating class: {e}")
        return None

def test_analytics_with_test_teacher(teacher_id):
    """Test analytics endpoints with the test teacher"""
    print(f"\n=== Testing Analytics with Test Teacher: {teacher_id} ===")
    
    # Test overview endpoint
    try:
        url = f"http://localhost:4000/api/teacher/{teacher_id}/overview"
        params = {'start': '2024-01-01', 'end': '2024-12-31'}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✓ Overview endpoint working")
            data = response.json()
            print(f"  Overview data keys: {list(data.keys())}")
        else:
            print(f"✗ Overview endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Overview endpoint error: {e}")
    
    # Test FAQs endpoint
    try:
        url = f"http://localhost:4000/api/teacher/{teacher_id}/faqs"
        params = {'limit': 5}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✓ FAQs endpoint working")
            data = response.json()
            print(f"  FAQs data keys: {list(data.keys())}")
        else:
            print(f"✗ FAQs endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ FAQs endpoint error: {e}")
    
    # Test hourly endpoint
    try:
        url = f"http://localhost:4000/api/teacher/{teacher_id}/hourly"
        params = {'start': '2024-01-01', 'end': '2024-12-31'}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✓ Hourly endpoint working")
            data = response.json()
            print(f"  Hourly data keys: {list(data.keys())}")
        else:
            print(f"✗ Hourly endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Hourly endpoint error: {e}")

def test_analytical_agent_integration(teacher_id):
    """Test the analytical agent with the test teacher"""
    print(f"\n=== Testing Analytical Agent Integration ===")
    
    try:
        from analytical_agent import AnalyticalAgent
        
        agent = AnalyticalAgent(api_base_url="http://localhost:4000/api")
        
        # Test overview
        overview = agent.fetch_teacher_overview(teacher_id, "2024-01-01", "2024-12-31")
        if overview:
            print("✓ Analytical agent overview working")
        else:
            print("✗ Analytical agent overview failed")
        
        # Test FAQs
        faqs = agent.fetch_faqs(teacher_id, limit=5)
        if faqs:
            print("✓ Analytical agent FAQs working")
        else:
            print("✗ Analytical agent FAQs failed")
        
        # Test hourly distribution
        hourly = agent.fetch_hourly_distribution(teacher_id, "2024-01-01", "2024-12-31")
        if hourly:
            print("✓ Analytical agent hourly distribution working")
        else:
            print("✗ Analytical agent hourly distribution failed")
            
    except Exception as e:
        print(f"✗ Analytical agent integration error: {e}")

def main():
    print("=== Creating Test Data for Analytics Integration ===")
    
    # Create test teacher
    teacher_id = create_test_teacher()
    if not teacher_id:
        print("Failed to create test teacher. Exiting.")
        return
    
    # Create test student
    student_id = create_test_student()
    if not student_id:
        print("Failed to create test student. Continuing with teacher tests.")
    
    # Create test class
    class_id = create_test_class(teacher_id)
    if not class_id:
        print("Failed to create test class. Continuing with basic tests.")
    
    # Test analytics endpoints
    test_analytics_with_test_teacher(teacher_id)
    
    # Test analytical agent integration
    test_analytical_agent_integration(teacher_id)
    
    print(f"\n=== Integration Test Complete ===")
    print(f"Test Teacher ID: {teacher_id}")
    print(f"You can now run: python standalone_analysis.py --teacher-id {teacher_id}")

if __name__ == "__main__":
    main()
