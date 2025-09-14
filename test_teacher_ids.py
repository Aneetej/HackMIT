#!/usr/bin/env python3
"""
Test script to check real teacher IDs in the database and test analytics integration
"""

import requests
import json
from analytical_agent import AnalyticalAgent

def test_backend_connection():
    """Test if backend is running and accessible"""
    try:
        response = requests.get("http://localhost:4000/", timeout=5)
        if response.status_code == 200:
            print("✓ Backend server is running")
            return True
        else:
            print(f"✗ Backend server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend server connection failed: {e}")
        return False

def get_real_teacher_ids():
    """Get real teacher IDs from the database"""
    try:
        response = requests.get("http://localhost:4000/teachers", timeout=10)
        if response.status_code == 200:
            teachers = response.json()
            print(f"✓ Found {len(teachers)} teachers in database:")
            for teacher in teachers[:5]:  # Show first 5 teachers
                print(f"  - ID: {teacher.get('id', 'N/A')}, Name: {teacher.get('name', 'N/A')}")
            return [teacher.get('id') for teacher in teachers if teacher.get('id')]
        else:
            print(f"✗ Failed to fetch teachers: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Error fetching teachers: {e}")
        return []

def test_analytics_with_real_teacher_id(teacher_id):
    """Test analytics agent with a real teacher ID"""
    print(f"\n=== Testing Analytics with Teacher ID: {teacher_id} ===")
    
    agent = AnalyticalAgent(api_base_url="http://localhost:4000/api")
    
    # Test teacher overview
    print("Testing teacher overview...")
    try:
        overview = agent.fetch_teacher_overview(teacher_id, "2024-01-01", "2024-12-31")
        if overview:
            print("✓ Teacher overview fetched successfully")
            print(f"  Summary: {overview.get('summary', {})}")
        else:
            print("✗ Teacher overview returned None")
    except Exception as e:
        print(f"✗ Teacher overview failed: {e}")
    
    # Test FAQs
    print("Testing FAQs...")
    try:
        faqs = agent.fetch_faqs(teacher_id, limit=5)
        if faqs:
            print("✓ FAQs fetched successfully")
            print(f"  FAQ count: {len(faqs.get('faqs', []))}")
        else:
            print("✗ FAQs returned None")
    except Exception as e:
        print(f"✗ FAQs failed: {e}")
    
    # Test hourly distribution
    print("Testing hourly distribution...")
    try:
        hourly = agent.fetch_hourly_distribution(teacher_id, "2024-01-01", "2024-12-31")
        if hourly:
            print("✓ Hourly distribution fetched successfully")
        else:
            print("✗ Hourly distribution returned None")
    except Exception as e:
        print(f"✗ Hourly distribution failed: {e}")

def test_analytics_endpoints_directly():
    """Test analytics endpoints directly"""
    print("\n=== Testing Analytics Endpoints Directly ===")
    
    # Test if analytics endpoints are mounted
    test_urls = [
        "http://localhost:4000/api/teacher/test_teacher/overview?start=2024-01-01&end=2024-12-31",
        "http://localhost:4000/api/teacher/test_teacher/faqs?limit=5",
        "http://localhost:4000/api/teacher/test_teacher/hourly?start=2024-01-01&end=2024-12-31"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            endpoint_name = url.split('/')[-1].split('?')[0]
            if response.status_code == 200:
                print(f"✓ {endpoint_name} endpoint is accessible")
            else:
                print(f"✗ {endpoint_name} endpoint returned {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"✗ {endpoint_name} endpoint failed: {e}")

def main():
    print("=== Teacher ID Mapping Test ===")
    
    # Test backend connection
    if not test_backend_connection():
        print("Backend server is not running. Please start it first.")
        return
    
    # Test analytics endpoints
    test_analytics_endpoints_directly()
    
    # Get real teacher IDs
    teacher_ids = get_real_teacher_ids()
    
    if teacher_ids:
        # Test with first real teacher ID
        test_analytics_with_real_teacher_id(teacher_ids[0])
    else:
        print("No teacher IDs found in database. Testing with mock ID...")
        test_analytics_with_real_teacher_id("test_teacher_001")

if __name__ == "__main__":
    main()
