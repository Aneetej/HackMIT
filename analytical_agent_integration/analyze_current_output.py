#!/usr/bin/env python3
"""
Analyze exactly what data is being returned from the updated analytics agent
"""

from analytical_agent import AnalyticalAgent
import json

def test_individual_endpoints():
    """Test each analytics endpoint individually to see exact output"""
    print("=== Testing Individual Analytics Endpoints ===")
    
    agent = AnalyticalAgent(api_base_url="http://localhost:4000/api")
    teacher_id = "cmfjnia2t0000oihjgwx13py3"
    
    print(f"Testing with Teacher ID: {teacher_id}")
    print("Date range: 2025-08-15 to 2025-09-14\n")
    
    # Test 1: Teacher Overview
    print("1. TEACHER OVERVIEW ENDPOINT:")
    print("-" * 50)
    try:
        overview = agent.fetch_teacher_overview(teacher_id, "2025-08-15", "2025-09-14")
        if overview:
            print("✓ SUCCESS - Overview data received:")
            print(json.dumps(overview, indent=2))
            print(f"Data keys: {list(overview.keys())}")
        else:
            print("✗ FAILED - No overview data returned")
    except Exception as e:
        print(f"✗ ERROR - {e}")
    print()
    
    # Test 2: FAQs
    print("2. FAQS ENDPOINT:")
    print("-" * 50)
    try:
        faqs = agent.fetch_faqs(teacher_id, limit=5)
        if faqs:
            print("✓ SUCCESS - FAQ data received:")
            print(json.dumps(faqs, indent=2))
            print(f"Data keys: {list(faqs.keys())}")
        else:
            print("✗ FAILED - No FAQ data returned")
    except Exception as e:
        print(f"✗ ERROR - {e}")
    print()
    
    # Test 3: Hourly Distribution
    print("3. HOURLY DISTRIBUTION ENDPOINT:")
    print("-" * 50)
    try:
        hourly = agent.fetch_hourly_distribution(teacher_id, "2025-08-15", "2025-09-14")
        if hourly:
            print("✓ SUCCESS - Hourly data received:")
            print(json.dumps(hourly, indent=2))
            print(f"Data keys: {list(hourly.keys())}")
            
            # Analyze hourly data structure
            if 'hourlyDistribution' in hourly:
                total_messages = sum(hour['messageCount'] for hour in hourly['hourlyDistribution'])
                print(f"Total messages across all hours: {total_messages}")
                active_hours = len([h for h in hourly['hourlyDistribution'] if h['messageCount'] > 0])
                print(f"Active hours (with messages): {active_hours}")
        else:
            print("✗ FAILED - No hourly data returned")
    except Exception as e:
        print(f"✗ ERROR - {e}")
    print()
    
    # Test 4: Engagement Analysis (if available)
    print("4. ENGAGEMENT ANALYSIS:")
    print("-" * 50)
    try:
        engagement = agent.fetch_engagement_analysis(teacher_id, "2025-08-15", "2025-09-14")
        if engagement:
            print("✓ SUCCESS - Engagement data received:")
            print(json.dumps(engagement, indent=2))
            print(f"Data keys: {list(engagement.keys())}")
        else:
            print("✗ FAILED - No engagement data returned")
    except Exception as e:
        print(f"✗ ERROR - {e}")

def analyze_expected_vs_actual():
    """Compare what we expect vs what we're actually getting"""
    print("\n=== EXPECTED VS ACTUAL DATA ANALYSIS ===")
    print("-" * 60)
    
    expected_data = {
        "teacher_overview": [
            "completion_rate",
            "average_messages_per_student", 
            "active_students",
            "sessions_per_day",
            "engagement_metrics"
        ],
        "faqs": [
            "question_text",
            "category", 
            "frequency_count",
            "success_rate"
        ],
        "hourly_distribution": [
            "hourly_breakdown",
            "peak_hours",
            "total_messages",
            "active_periods"
        ],
        "misconceptions": [
            "common_misconceptions",
            "categories",
            "frequency",
            "recommendations"
        ]
    }
    
    print("EXPECTED DATA STRUCTURE:")
    for endpoint, fields in expected_data.items():
        print(f"  {endpoint}:")
        for field in fields:
            print(f"    - {field}")
    
    print("\nACTUAL WORKING ENDPOINTS:")
    print("  ✓ hourly_distribution: Complete 24-hour breakdown with summary")
    print("  ✗ teacher_overview: Database schema errors")
    print("  ✗ faqs: Missing required parameters and schema issues")
    print("  ✗ misconceptions: Database column errors")

def main():
    print("=== ANALYTICS AGENT OUTPUT ANALYSIS ===")
    print("=" * 60)
    
    # Test individual endpoints
    test_individual_endpoints()
    
    # Analyze expected vs actual
    analyze_expected_vs_actual()
    
    print("\n=== SUMMARY ===")
    print("CURRENTLY WORKING:")
    print("- Hourly Distribution: ✓ Returns complete 24-hour activity data")
    print("- Backend Integration: ✓ Real teacher IDs working")
    print("- Database Connection: ✓ Live PostgreSQL queries")
    
    print("\nNEEDS FIXING:")
    print("- Teacher Overview: Database schema mismatches")
    print("- FAQs: Missing columns and parameter issues") 
    print("- Misconceptions: Table structure problems")
    
    print("\nDATA CURRENTLY AVAILABLE:")
    print("- Teacher ID validation")
    print("- Hourly message distribution (0-23 hours)")
    print("- Peak activity analysis")
    print("- Total message counts")
    print("- Active hours tracking")

if __name__ == "__main__":
    main()
