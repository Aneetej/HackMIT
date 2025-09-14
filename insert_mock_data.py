#!/usr/bin/env python3
"""
Mock Data Insertion Script

Inserts test data into the database for the 3 core analytics metrics:
1. Frequently Asked Questions
2. Learning Analytics (successful topics)
3. Session Takeaways (struggling topics)
"""

import os
import sys
from datetime import datetime, timedelta
import subprocess
import json

def run_prisma_command(command):
    """Execute a Prisma CLI command."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def insert_faq_data():
    """Insert sample FAQ data."""
    print("Inserting FAQ data...")
    
    faqs = [
        {
            "question_text": "How do I solve quadratic equations?",
            "category": "algebra",
            "frequency_count": 25,
            "success_rate": 0.78
        },
        {
            "question_text": "What is the Pythagorean theorem?",
            "category": "geometry",
            "frequency_count": 18,
            "success_rate": 0.85
        },
        {
            "question_text": "How do I find the derivative of a function?",
            "category": "calculus",
            "frequency_count": 22,
            "success_rate": 0.65
        },
        {
            "question_text": "What are prime numbers?",
            "category": "number_theory",
            "frequency_count": 12,
            "success_rate": 0.92
        },
        {
            "question_text": "How do I solve systems of equations?",
            "category": "algebra",
            "frequency_count": 20,
            "success_rate": 0.70
        },
        {
            "question_text": "What is the area of a circle?",
            "category": "geometry",
            "frequency_count": 15,
            "success_rate": 0.88
        },
        {
            "question_text": "How do I factor polynomials?",
            "category": "algebra",
            "frequency_count": 28,
            "success_rate": 0.62
        }
    ]
    
    for faq in faqs:
        command = f"""npx prisma db execute --stdin <<EOF
INSERT INTO "frequently_asked_questions" (id, question_text, category, frequency_count, success_rate, first_asked, last_asked, keywords)
VALUES (
    '{generate_cuid()}',
    '{faq["question_text"]}',
    '{faq["category"]}',
    {faq["frequency_count"]},
    {faq["success_rate"]},
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '1 day',
    ARRAY['{faq["category"]}', 'math']
);
EOF"""
        run_prisma_command(command)
    
    print("✓ FAQ data inserted")

def insert_learning_analytics_data():
    """Insert sample learning analytics data for successful topics."""
    print("Inserting learning analytics data...")
    
    # Get the test student ID
    student_id = "cmfjniab50001oihjqsfvi427"
    
    analytics_data = [
        {
            "concepts_mastered": ["quadratic_equations", "linear_equations", "factoring"],
            "success_rate": 0.85,
            "session_duration": 45
        },
        {
            "concepts_mastered": ["geometry_basics", "area_calculation", "perimeter"],
            "success_rate": 0.92,
            "session_duration": 38
        },
        {
            "concepts_mastered": ["prime_numbers", "divisibility", "factors"],
            "success_rate": 0.88,
            "session_duration": 32
        },
        {
            "concepts_mastered": ["fractions", "decimals", "percentages"],
            "success_rate": 0.79,
            "session_duration": 42
        },
        {
            "concepts_mastered": ["basic_algebra", "variables", "expressions"],
            "success_rate": 0.83,
            "session_duration": 40
        }
    ]
    
    for i, data in enumerate(analytics_data):
        concepts_array = "{" + ",".join([f'"{c}"' for c in data["concepts_mastered"]]) + "}"
        date_offset = i * 5  # Spread over different days
        
        command = f"""npx prisma db execute --stdin <<EOF
INSERT INTO "learning_analytics" (
    id, student_id, date, session_duration, questions_per_session, 
    response_time_avg, concepts_mastered, difficulty_progression, success_rate
)
VALUES (
    '{generate_cuid()}',
    '{student_id}',
    NOW() - INTERVAL '{date_offset} days',
    {data["session_duration"]},
    8.5,
    12.3,
    ARRAY{concepts_array},
    'progressive',
    {data["success_rate"]}
);
EOF"""
        run_prisma_command(command)
    
    print("✓ Learning analytics data inserted")

def insert_session_takeaways_data():
    """Insert sample session takeaways data for struggling topics."""
    print("Inserting session takeaways data...")
    
    # First, we need to get or create a chat session
    session_id = "test_session_001"
    student_id = "cmfjniab50001oihjqsfvi427"
    
    # Create a test chat session first
    command = f"""npx prisma db execute --stdin <<EOF
INSERT INTO "chat_sessions" (id, student_id, started_at, ended_at, message_count)
VALUES (
    '{session_id}',
    '{student_id}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '45 minutes',
    15
) ON CONFLICT (id) DO NOTHING;
EOF"""
    run_prisma_command(command)
    
    takeaways_data = [
        {
            "takeaway_type": "difficulty_calculus",
            "summary": "Student struggled with derivative concepts",
            "key_concepts": ["derivatives", "calculus", "chain_rule"],
        },
        {
            "takeaway_type": "confusion_trigonometry",
            "summary": "Student had trouble with trigonometric identities",
            "key_concepts": ["trigonometry", "identities", "sine_cosine"],
        },
        {
            "takeaway_type": "struggle_word_problems",
            "summary": "Student needs help translating word problems to equations",
            "key_concepts": ["word_problems", "translation", "problem_solving"],
        },
        {
            "takeaway_type": "difficulty_graphing",
            "summary": "Student confused about graphing linear functions",
            "key_concepts": ["graphing", "linear_functions", "slope"],
        },
        {
            "takeaway_type": "confusion_fractions",
            "summary": "Student struggled with complex fraction operations",
            "key_concepts": ["fractions", "operations", "complex_fractions"],
        }
    ]
    
    for i, data in enumerate(takeaways_data):
        concepts_array = "{" + ",".join([f'"{c}"' for c in data["key_concepts"]]) + "}"
        
        command = f"""npx prisma db execute --stdin <<EOF
INSERT INTO "session_takeaways" (
    id, session_id, takeaway_type, summary, key_concepts, 
    effective_methods, created_at, relevance_score
)
VALUES (
    '{generate_cuid()}',
    '{session_id}',
    '{data["takeaway_type"]}',
    '{data["summary"]}',
    ARRAY{concepts_array},
    '{{"visual_aids": true, "practice_problems": true}}',
    NOW() - INTERVAL '{i * 2} days',
    0.8
);
EOF"""
        run_prisma_command(command)
    
    print("✓ Session takeaways data inserted")

def generate_cuid():
    """Generate a simple CUID-like string for testing."""
    import random
    import string
    return 'test' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def main():
    print("=== Mock Data Insertion for Analytics Testing ===")
    print("Inserting test data for the 3 core metrics...")
    print()
    
    # Insert data for each metric
    insert_faq_data()
    insert_learning_analytics_data()
    insert_session_takeaways_data()
    
    print()
    print("✅ All mock data inserted successfully!")
    print()
    print("You can now test the analytics with:")
    print("python build_teacher_overview.py --teacher-id cmfjnia2t0000oihjgwx13py3")

if __name__ == "__main__":
    main()
