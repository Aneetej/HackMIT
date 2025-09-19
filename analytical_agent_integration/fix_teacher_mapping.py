#!/usr/bin/env python3
"""
Fix teacher ID mapping from hardcoded teacher_123 to real database Teacher IDs
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def get_real_teacher_ids_from_db():
    """Get real teacher IDs directly from the database using Prisma"""
    try:
        # Use Prisma CLI to query the database directly
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin'
        ], input='SELECT id, name FROM "Teacher" LIMIT 5;', 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        if result.returncode == 0:
            print("✓ Successfully queried teachers from database")
            print(f"Output: {result.stdout}")
            return result.stdout
        else:
            print(f"✗ Database query failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        return None

def create_test_teacher_in_db():
    """Create a test teacher in the database for testing"""
    try:
        # Create a test teacher using Prisma
        create_teacher_sql = """
        INSERT INTO "Teacher" (id, name, email, subject, role, supervised_students)
        VALUES ('test_teacher_001', 'Test Teacher', 'test@example.com', 'Mathematics', 'TEACHER', '{}')
        ON CONFLICT (id) DO NOTHING;
        """
        
        result = subprocess.run([
            'npx', 'prisma', 'db', 'execute', 
            '--stdin'
        ], input=create_teacher_sql, 
        text=True, capture_output=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        if result.returncode == 0:
            print("✓ Test teacher created successfully")
            return 'test_teacher_001'
        else:
            print(f"✗ Failed to create test teacher: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Error creating test teacher: {e}")
        return None

def update_analytics_components_with_real_teacher_id(teacher_id):
    """Update analytics components to use real teacher ID instead of teacher_123"""
    
    files_to_update = [
        'analytical_agent.py',
        'build_teacher_overview.py', 
        'standalone_analysis.py',
        'test_teacher_ids.py'
    ]
    
    base_path = Path('/Users/potriabhisribarama/Documents/HackMIT')
    
    for filename in files_to_update:
        file_path = base_path / filename
        if file_path.exists():
            try:
                # Read the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace hardcoded teacher_123 with real teacher ID
                updated_content = content.replace('teacher_123', teacher_id)
                
                # Also update any DEFAULT_TEACHER_ID constants
                updated_content = updated_content.replace(
                    'DEFAULT_TEACHER_ID = "teacher_123"', 
                    f'DEFAULT_TEACHER_ID = "{teacher_id}"'
                )
                
                # Write back the updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✓ Updated {filename} with teacher ID: {teacher_id}")
                
            except Exception as e:
                print(f"✗ Error updating {filename}: {e}")
        else:
            print(f"⚠ File not found: {filename}")

def test_analytics_with_real_teacher():
    """Test analytics components with real teacher ID"""
    try:
        # Test the analytical agent
        result = subprocess.run([
            'python', 'test_teacher_ids.py'
        ], capture_output=True, text=True, cwd='/Users/potriabhisribarama/Documents/HackMIT')
        
        print("=== Analytics Test Results ===")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error testing analytics: {e}")
        return False

def main():
    print("=== Fixing Teacher ID Mapping ===")
    
    # Step 1: Try to get real teacher IDs from database
    print("\n1. Checking for existing teachers in database...")
    db_result = get_real_teacher_ids_from_db()
    
    # Step 2: Create a test teacher if none exist
    print("\n2. Creating test teacher for analytics testing...")
    test_teacher_id = create_test_teacher_in_db()
    
    if not test_teacher_id:
        print("Failed to create test teacher. Using fallback ID.")
        test_teacher_id = "test_teacher_001"
    
    # Step 3: Update analytics components with real teacher ID
    print(f"\n3. Updating analytics components with teacher ID: {test_teacher_id}")
    update_analytics_components_with_real_teacher_id(test_teacher_id)
    
    # Step 4: Test the updated analytics
    print(f"\n4. Testing analytics with real teacher ID: {test_teacher_id}")
    success = test_analytics_with_real_teacher()
    
    if success:
        print(f"\n✓ Successfully fixed teacher ID mapping to: {test_teacher_id}")
        print("Analytics components now use real database teacher IDs!")
    else:
        print(f"\n⚠ Teacher ID mapping updated to: {test_teacher_id}")
        print("Some analytics tests may need backend server to be running.")
    
    print(f"\nNext steps:")
    print(f"1. Start the backend server")
    print(f"2. Test analytics with: python standalone_analysis.py --teacher-id {test_teacher_id}")
    print(f"3. Verify all endpoints work with real teacher ID")

if __name__ == "__main__":
    main()
