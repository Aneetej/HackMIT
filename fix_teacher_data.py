#!/usr/bin/env python3
"""
Fix teacher data to include supervised students for analytics testing
"""

import subprocess
import json

def update_teacher_supervised_students():
    """Update teacher to include supervised students"""
    try:
        # First get the student ID we created
        get_student_sql = """
        SELECT id FROM "students" WHERE email = 'test.student@example.com' LIMIT 1;
        """
        
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin', '--schema', 'prisma/schema.prisma'
        ], input=get_student_sql, 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        print("Student query result:", result.stdout)
        print("Student query error:", result.stderr)
        
        # Update teacher to supervise the test student
        update_teacher_sql = """
        UPDATE "teachers" 
        SET supervised_students = ARRAY['cmfjniab50001oihjqsfvi427']
        WHERE email = 'test.teacher@example.com';
        """
        
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin', '--schema', 'prisma/schema.prisma'
        ], input=update_teacher_sql, 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        if result.returncode == 0:
            print("✓ Updated teacher supervised_students")
            return True
        else:
            print(f"✗ Failed to update teacher: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating teacher data: {e}")
        return False

def create_sample_chat_data():
    """Create sample chat sessions and messages for testing"""
    try:
        # Create a chat session
        create_session_sql = """
        INSERT INTO "chat_sessions" (id, student_id, session_type, started_at, questions_asked, "classId")
        VALUES ('test_session_001', 'cmfjniab50001oihjqsfvi427', 'tutoring', NOW() - INTERVAL '1 day', 5, '100938')
        ON CONFLICT (id) DO NOTHING;
        """
        
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin', '--schema', 'prisma/schema.prisma'
        ], input=create_session_sql, 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        if result.returncode == 0:
            print("✓ Created test chat session")
        else:
            print(f"✗ Failed to create chat session: {result.stderr}")
        
        # Create sample messages
        create_messages_sql = """
        INSERT INTO "chat_messages" (id, session_id, sender_type, content, message_type, timestamp)
        VALUES 
        ('msg_001', 'test_session_001', 'student', 'What is algebra?', 'text', NOW() - INTERVAL '1 day'),
        ('msg_002', 'test_session_001', 'agent', 'Algebra is a branch of mathematics...', 'text', NOW() - INTERVAL '1 day'),
        ('msg_003', 'test_session_001', 'student', 'Can you explain quadratic equations?', 'text', NOW() - INTERVAL '1 day'),
        ('msg_004', 'test_session_001', 'agent', 'A quadratic equation is...', 'text', NOW() - INTERVAL '1 day')
        ON CONFLICT (id) DO NOTHING;
        """
        
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin', '--schema', 'prisma/schema.prisma'
        ], input=create_messages_sql, 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        if result.returncode == 0:
            print("✓ Created test chat messages")
        else:
            print(f"✗ Failed to create chat messages: {result.stderr}")
        
        # Create sample FAQs
        create_faqs_sql = """
        INSERT INTO "frequently_asked_questions" (id, question_text, category, frequency_count, first_asked, last_asked, success_rate)
        VALUES 
        ('faq_001', 'What is algebra?', 'algebra_basics', 15, NOW() - INTERVAL '7 days', NOW() - INTERVAL '1 day', 0.85),
        ('faq_002', 'How do I solve quadratic equations?', 'quadratic_equations', 12, NOW() - INTERVAL '5 days', NOW() - INTERVAL '2 hours', 0.75),
        ('faq_003', 'What are linear functions?', 'linear_algebra', 8, NOW() - INTERVAL '3 days', NOW() - INTERVAL '1 hour', 0.90)
        ON CONFLICT (id) DO NOTHING;
        """
        
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin', '--schema', 'prisma/schema.prisma'
        ], input=create_faqs_sql, 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        if result.returncode == 0:
            print("✓ Created test FAQs")
            return True
        else:
            print(f"✗ Failed to create FAQs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False

def main():
    print("=== Fixing Teacher Data for Analytics Testing ===")
    
    # Update teacher supervised students
    update_teacher_supervised_students()
    
    # Create sample chat data
    create_sample_chat_data()
    
    print("\n=== Teacher Data Fix Complete ===")
    print("Teacher should now have supervised students and sample data for analytics testing")

if __name__ == "__main__":
    main()
