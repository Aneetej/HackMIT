"""
Prisma database client for student agents system.
Handles database connections and student data retrieval using the existing Prisma schema.
"""

import os
import asyncio
from typing import Optional, Dict, List, Any
from prisma import Prisma
from prisma.models import Student, Class, ChatSession, StudentPreference, LearningAnalytics

class PrismaClient:
    """Manages Prisma database connections and student data operations"""
    
    def __init__(self):
        self.client = Prisma()
        self._connected = False
    
    async def connect(self) -> bool:
        """Establish connection to the database"""
        try:
            await self.client.connect()
            self._connected = True
            print(" Connected to Prisma database")
            return True
        except Exception as e:
            print(f" Database connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close database connection"""
        if self._connected:
            await self.client.disconnect()
            self._connected = False
            print("🔌 Database connection closed")
    
    
    async def get_student_by_id_and_class(self, student_id: str, class_id: str) -> Optional[Dict]:
        """Retrieve ALL student information by ID filtered for specific class context"""
        if not self._connected:
            return None
        
        try:
            # First verify student is enrolled in the specified class
            student = await self.client.student.find_unique(
                where={'id': student_id},
                include={
                    'classes': {
                        'where': {'id': class_id}
                    }
                }
            )
            
            if not student or not student.classes:
                print(f" Student {student_id} not found or not enrolled in class {class_id}")
                return None
            
            # Get comprehensive student data with ALL related information
            student_data = await self.client.student.find_unique(
                where={'id': student_id},
                include={
                    # Get the specific class with full details
                    'classes': {
                        'where': {'id': class_id},
                        'include': {
                            'teacher': True,  # Include teacher information
                            'students': {
                                'select': {'id': True, 'name': True}  # Other students in class
                            }
                        }
                    },
                    # Get ALL student preferences
                    'preferences': {
                        'order_by': {'created_at': 'desc'}
                    },
                    # Get ALL learning analytics
                    'learning_analytics': {
                        'order_by': {'date': 'desc'},
                        'take': 1
                    },
                    # Get ALL chat sessions for this class
                    'chat_sessions': {
                        'where': {
                            'classId': class_id
                        },
                        'include': {
                            'messages': {
                                'order_by': {'timestamp': 'asc'}
                            },
                            'takeaways': True
                        },
                        'order_by': {'started_at': 'desc'}
                    },
                    # Get student's enrollment details for this class
                    'enrollments': {
                        'where': {'classId': class_id},
                        'include': {
                            'class': True
                        }
                    }
                }
            )
            
            if student_data:
                # Get the specific class data
                current_class = student_data.classes[0] if student_data.classes else None
                
                # Format comprehensive student information
                return {
                    # Basic student information
                    'id': student_data.id,
                    'name': student_data.name,
                    'email': student_data.email,
                    'grade': student_data.grade,
                    'subject_focus': student_data.subject_focus,
                    'learning_style': student_data.learning_style,
                    'preferred_content': student_data.preferred_content,
                    'created_at': student_data.created_at.isoformat() if student_data.created_at else None,
                    'updated_at': student_data.updated_at.isoformat() if student_data.updated_at else None,
                    
                    # Current class information
                    'current_class': {
                        'id': current_class.id,
                        'name': current_class.name,
                        'subject': current_class.subject,
                        'grade_level': current_class.grade_level,
                        'teaching_style': current_class.teachingStyle,
                        'description': current_class.description,
                        'teacher': {
                            'id': current_class.teacher.id,
                            'name': current_class.teacher.name,
                            'email': current_class.teacher.email
                        } if current_class.teacher else None,
                        'total_students': len(current_class.students),
                        'classmates': [
                            {'id': s.id, 'name': s.name} 
                            for s in current_class.students 
                            if s.id != student_id
                        ]
                    } if current_class else None,
                    
                    # All student preferences
                    'preferences': [
                        {
                            'id': pref.id,
                            'type': pref.preference_type,
                            'value': pref.preference_value,
                            'confidence': pref.confidence_score,
                            'created_at': pref.created_at.isoformat() if pref.created_at else None
                        } 
                        for pref in student_data.preferences
                    ],
                    
                    # All learning analytics
                    'learning_analytics': [
                        {
                            'id': analytics.id,
                            'date': analytics.date.isoformat() if analytics.date else None,
                            'engagement_score': analytics.engagement_score,
                            'concepts_mastered': analytics.concepts_mastered,
                            'time_spent_minutes': analytics.time_spent_minutes,
                            'questions_asked': analytics.questions_asked,
                            'correct_answers': analytics.correct_answers,
                            'improvement_areas': analytics.improvement_areas
                        }
                        for analytics in student_data.learning_analytics
                    ],
                    
                    # All chat sessions in this class
                    'chat_sessions': [
                        {
                            'id': session.id,
                            'topic': session.topic,
                            'status': session.status,
                            'started_at': session.started_at.isoformat() if session.started_at else None,
                            'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                            'concepts_covered': session.concepts_covered,
                            'session_summary': session.session_summary,
                            'message_count': len(session.messages),
                            'messages': [
                                {
                                    'id': msg.id,
                                    'sender': msg.sender,
                                    'content': msg.content,
                                    'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
                                }
                                for msg in session.messages
                            ],
                            'takeaways': [
                                {
                                    'id': takeaway.id,
                                    'concept': takeaway.concept,
                                    'understanding_level': takeaway.understanding_level,
                                    'notes': takeaway.notes
                                }
                                for takeaway in session.takeaways
                            ]
                        }
                        for session in student_data.chat_sessions
                    ],
                    
                    # Enrollment information
                    'enrollment': {
                        'enrolled_at': student_data.enrollments[0].enrolled_at.isoformat() if student_data.enrollments and student_data.enrollments[0].enrolled_at else None,
                        'status': 'active'  # Assuming active since they're found in the class
                    } if student_data.enrollments else None,
                    
                    # Summary statistics
                    'statistics': {
                        'total_sessions': len(student_data.chat_sessions),
                        'completed_sessions': len([s for s in student_data.chat_sessions if s.status == 'completed']),
                        'total_messages': sum(len(s.messages) for s in student_data.chat_sessions),
                        'total_time_spent': sum(a.time_spent_minutes or 0 for a in student_data.learning_analytics),
                        'average_engagement': sum(a.engagement_score or 0 for a in student_data.learning_analytics) / len(student_data.learning_analytics) if student_data.learning_analytics else 0,
                        'total_concepts_mastered': len(set().union(*[a.concepts_mastered or [] for a in student_data.learning_analytics])),
                        'last_activity': max([s.started_at for s in student_data.chat_sessions if s.started_at], default=None)
                    },
                    
                    # Context for current request
                    'current_class_id': class_id,
                    'data_fetched_at': student_data.updated_at.isoformat() if student_data.updated_at else None
                }
            return None
            
        except Exception as e:
            print(f"❌ Error fetching comprehensive student data: {e}")
            return None
    
    async def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Retrieve student information by ID with all classes (for general use)"""
        if not self._connected:
            return None
        
        try:
            student = await self.client.student.find_unique(
                where={'id': student_id},
                include={
                    'classes': True,
                    'preferences': True,
                    'learning_analytics': {
                        'order_by': {'date': 'desc'},
                        'take': 1
                    }
                }
            )
            
            if student:
                return {
                    'id': student.id,
                    'name': student.name,
                    'email': student.email,
                    'grade': student.grade,
                    'subject_focus': student.subject_focus,
                    'learning_style': student.learning_style,
                    'preferred_content': student.preferred_content,
                    'classes': [{'id': cls.id, 'name': cls.name, 'teaching_style': cls.teachingStyle} for cls in student.classes],
                    'preferences': [{'type': pref.preference_type, 'value': pref.preference_value, 'confidence': pref.confidence_score} for pref in student.preferences],
                    'recent_analytics': student.learning_analytics[0].__dict__ if student.learning_analytics else None
                }
            return None
            
        except Exception as e:
            print(f" Error fetching student by ID: {e}")
            return None
    
    async def get_class_info(self, class_id: str) -> Optional[Dict]:
        """Get class information including teaching style and restrictions"""
        if not self._connected:
            return None
        
        try:
            class_info = await self.client.class_.find_unique(
                where={'id': class_id},
                include={
                    'teacher': True,
                    'students': True
                }
            )
            
            if class_info:
                return {
                    'id': class_info.id,
                    'name': class_info.name,
                    'restrictions': class_info.restrictions,
                    'teaching_style': class_info.teachingStyle,
                    'teacher': class_info.teacher.__dict__ if class_info.teacher else None,
                    'student_count': len(class_info.students)
                }
            return None
            
        except Exception as e:
            print(f" Error fetching class info: {e}")
            return None
    
    async def start_chat_session(self, student_id: str, session_type: str = "tutoring", class_id: str = None) -> Optional[str]:
        """Start a new chat session for a student in a specific class"""
        if not self._connected:
            return None
        
        try:
            # Verify student is enrolled in the class if class_id is provided
            if class_id:
                enrollment_check = await self.client.student.find_first(
                    where={
                        'id': student_id,
                        'classes': {
                            'some': {'id': class_id}
                        }
                    }
                )
                
                if not enrollment_check:
                    print(f" Student {student_id} not enrolled in class {class_id}")
                    return None
            
            session = await self.client.chatsession.create(
                data={
                    'student_id': student_id,
                    'session_type': session_type,
                    'classId': class_id,
                    'status': 'active'
                }
            )
            
            print(f" Started chat session: {session.id} for class {class_id}")
            return session.id
            
        except Exception as e:
            print(f" Error starting chat session: {e}")
            return None
    
    async def add_chat_message(self, session_id: str, sender_type: str, content: str, 
                              agent_type: str = None, message_type: str = "text") -> bool:
        """Add a message to a chat session"""
        if not self._connected:
            return False
        
        try:
            await self.client.chatmessage.create(
                data={
                    'session_id': session_id,
                    'sender_type': sender_type,
                    'agent_type': agent_type,
                    'content': content,
                    'message_type': message_type
                }
            )
            return True
            
        except Exception as e:
            print(f" Error adding chat message: {e}")
            return False
    
    async def end_chat_session(self, session_id: str, concepts_covered: List[str] = None) -> bool:
        """End a chat session and update metrics"""
        if not self._connected:
            return False
        
        try:
            # Get message count for this session
            messages = await self.client.chatmessage.find_many(
                where={'session_id': session_id}
            )
            
            questions_asked = len([msg for msg in messages if msg.sender_type == 'student'])
            
            await self.client.chatsession.update(
                where={'id': session_id},
                data={
                    'status': 'completed',
                    'ended_at': None,  # Will use database default (now())
                    'questions_asked': questions_asked,
                    'concepts_covered': concepts_covered or []
                }
            )
            
            print(f" Ended chat session: {session_id}")
            return True
            
        except Exception as e:
            print(f" Error ending chat session: {e}")
            return False
    
    async def get_student_preferences_for_class(self, student_id: str, class_id: str) -> Dict[str, Any]:
        """Get student preferences filtered for specific class context"""
        if not self._connected:
            return {}
        
        try:
            # Verify student is in the class
            enrollment_check = await self.client.student.find_first(
                where={
                    'id': student_id,
                    'classes': {
                        'some': {'id': class_id}
                    }
                }
            )
            
            if not enrollment_check:
                print(f" Student {student_id} not enrolled in class {class_id}")
                return {}
            
            preferences = await self.client.studentpreference.find_many(
                where={'student_id': student_id},
                order_by={'confidence_score': 'desc'}
            )
            
            pref_dict = {}
            for pref in preferences:
                pref_dict[pref.preference_type] = {
                    'value': pref.preference_value,
                    'confidence': pref.confidence_score,
                    'method': pref.detection_method
                }
            
            return pref_dict
            
        except Exception as e:
            print(f" Error fetching student preferences: {e}")
            return {}
    
    async def get_class_specific_analytics(self, student_id: str, class_id: str) -> List[Dict]:
        """Get learning analytics for a student in a specific class"""
        if not self._connected:
            return []
        
        try:
            # Get sessions for this student in this class
            sessions = await self.client.chatsession.find_many(
                where={
                    'student_id': student_id,
                    'classId': class_id,
                    'status': 'completed'
                },
                order_by={'started_at': 'desc'},
                take=10
            )
            
            # Get analytics for these sessions
            analytics = await self.client.learninganalytics.find_many(
                where={'student_id': student_id},
                order_by={'date': 'desc'},
                take=5
            )
            
            return [
                {
                    'session_count_in_class': len(sessions),
                    'recent_analytics': [analytics_item.__dict__ for analytics_item in analytics],
                    'class_id': class_id
                }
            ]
            
        except Exception as e:
            print(f" Error fetching class-specific analytics: {e}")
            return []
    
    async def update_student_analytics(self, student_id: str, session_duration: int, 
                                     concepts_mastered: List[str], success_rate: float) -> bool:
        """Update learning analytics for a student"""
        if not self._connected:
            return False
        
        try:
            await self.client.learninganalytics.create(
                data={
                    'student_id': student_id,
                    'session_duration': session_duration,
                    'concepts_mastered': concepts_mastered,
                    'success_rate': success_rate,
                    'questions_per_session': 0.0,  # Will be calculated
                    'response_time_avg': 0.0,  # Will be calculated
                    'difficulty_progression': 'stable'  # Default
                }
            )
            
            return True
            
        except Exception as e:
            print(f" Error updating student analytics: {e}")
            return False

# Global client instance
prisma_client = PrismaClient()

# Synchronous wrapper functions for easier integration
def run_async(coro):
    """Helper function to run async functions synchronously"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def connect_to_database() -> bool:
    """Synchronous wrapper for database connection"""
    return run_async(prisma_client.connect())

def get_student_data_for_class(student_id: str, class_id: str) -> Optional[Dict]:
    """Synchronous wrapper for getting student data filtered by class"""
    return run_async(prisma_client.get_student_by_id_and_class(student_id, class_id))

def get_class_data(class_id: str) -> Optional[Dict]:
    """Synchronous wrapper for getting class data"""
    return run_async(prisma_client.get_class_info(class_id))

def start_session(student_id: str, session_type: str = "tutoring", class_id: str = None) -> Optional[str]:
    """Synchronous wrapper for starting a chat session"""
    return run_async(prisma_client.start_chat_session(student_id, session_type, class_id))

def add_message(session_id: str, sender_type: str, content: str, agent_type: str = None) -> bool:
    """Synchronous wrapper for adding a chat message"""
    return run_async(prisma_client.add_chat_message(session_id, sender_type, content, agent_type))

def end_session(session_id: str, concepts_covered: List[str] = None) -> bool:
    """Synchronous wrapper for ending a chat session"""
    return run_async(prisma_client.end_chat_session(session_id, concepts_covered))

def get_class_specific_preferences(student_id: str, class_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for getting class-specific student preferences"""
    return run_async(prisma_client.get_student_preferences_for_class(student_id, class_id))

def get_class_analytics(student_id: str, class_id: str) -> List[Dict]:
    """Synchronous wrapper for getting class-specific analytics"""
    return run_async(prisma_client.get_class_specific_analytics(student_id, class_id))

def disconnect_from_database():
    """Synchronous wrapper for database disconnection"""
    return run_async(prisma_client.disconnect())
