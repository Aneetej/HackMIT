import asyncio
from studentagents.prisma_client import PrismaClient

def run_async(coro):
    """Helper function to run async code in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def create_default_student_context():
    """Create default student context when database is unavailable"""
    return {
        'learning_style': 'visual',
        'student_name': 'Student',
        'grade': '10',
        'subject_focus': 'algebra',
        'preferred_content': 'interactive',
        'concepts_mastered': 'basic arithmetic',
        'improvement_areas': 'word problems',
        'total_sessions': 1,
        'total_messages': 0,
        'total_time_spent': 0,
        'average_engagement': 75,
        'teacher_name': 'Teacher',
        'class_name': 'Demo Class',
        'teaching_style': 'interactive'
    }

def map_student_data_to_context(student_data):
    """Map comprehensive student data from Prisma to crew context"""
    current_class = student_data.get('current_class', {})
    statistics = student_data.get('statistics', {})
    learning_analytics = student_data.get('learning_analytics', [])
    
    # Get improvement areas from latest analytics
    improvement_areas = 'word problems'
    if learning_analytics and learning_analytics[0].get('improvement_areas'):
        improvement_areas = ', '.join(learning_analytics[0]['improvement_areas'])
    
    return {
        'learning_style': student_data.get('learning_style', 'visual'),
        'student_name': student_data.get('name', 'Student'),
        'grade': str(student_data.get('grade', '10')),
        'subject_focus': student_data.get('subject_focus', 'algebra'),
        'preferred_content': student_data.get('preferred_content', 'interactive'),
        'concepts_mastered': str(statistics.get('total_concepts_mastered', 'basic concepts')),
        'improvement_areas': improvement_areas,
        'total_sessions': statistics.get('total_sessions', 1),
        'total_messages': statistics.get('total_messages', 0),
        'total_time_spent': statistics.get('total_time_spent', 0),
        'average_engagement': int(statistics.get('average_engagement', 75)),
        'teacher_name': current_class.get('teacher', {}).get('name', 'Teacher'),
        'class_name': current_class.get('name', 'Demo Class'),
        'teaching_style': current_class.get('teaching_style', 'interactive')
    }

def get_student_data():
    """Get student data from database"""
    print("\n=== Student Login ===")
    
    # For demo purposes, you can hardcode these or get from input
    student_id = input("Enter your student ID (or press Enter for demo): ").strip()
    class_id = input("Enter your class ID (or press Enter for demo): ").strip()
    
    # Use demo values if not provided
    if not student_id:
        student_id = "demo_student_123"
    if not class_id:
        class_id = "demo_class_456"
    
    # Initialize Prisma client
    prisma_client = PrismaClient()
    
    try:
        # Connect to database
        connected = run_async(prisma_client.connect())
        if not connected:
            print("⚠️ Database connection failed. Using default settings.")
            return create_default_student_context()
        
        # Get student data with class context
        student_data = run_async(prisma_client.get_student_by_id_and_class(student_id, class_id))
        
        if student_data:
            print(f"✅ Welcome back, {student_data.get('name', 'Student')}!")
            print(f"📚 Class: {student_data.get('current_class', {}).get('name', 'Demo Class')}")
            print(f"🎯 Learning Style: {student_data.get('learning_style', 'visual')}")
            
            return map_student_data_to_context(student_data)
        else:
            print("⚠️ Student not found in database. Using default settings.")
            return create_default_student_context()
            
    except Exception as e:
        print(f"⚠️ Database error: {e}. Using default settings.")
        return create_default_student_context()
    finally:
        # Disconnect from database
        try:
            run_async(prisma_client.disconnect())
        except:
            pass
