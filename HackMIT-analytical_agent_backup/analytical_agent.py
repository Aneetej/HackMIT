import requests
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

class AnalyticalAgent:
    """
    Analytics agent specialized in fetching and analyzing teacher analytics data
    from the Express API endpoints.
    """
    
    def __init__(self, api_base_url: str = None, use_mock_data: bool = True):
        self.role = "Analytics Specialist"
        self.goal = "Fetch and analyze educational analytics data for teachers"
        self.backstory = """You are an expert data analyst specializing in educational metrics. 
        You excel at interpreting student engagement data, learning patterns, and 
        providing actionable insights for teachers to improve their instruction."""
        self.api_base_url = api_base_url.rstrip('/') if api_base_url else None
        self.use_mock_data = use_mock_data
        
        # Initialize database connection if not using mock data
        if not self.use_mock_data:
            try:
                from prisma import Prisma
                self.db = Prisma()
            except ImportError:
                print("Prisma client not available, falling back to mock data")
                self.use_mock_data = True
    
    async def fetch_teacher_overview(
        self, 
        teacher_id: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive overview analytics for a teacher's cohort.
        
        Args:
            teacher_id: The teacher's unique identifier
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary containing teacher overview analytics or None if error
        """
        if self.use_mock_data:
            print("Using mock data for teacher overview")
            return self._generate_mock_overview(teacher_id, start_date, end_date)
        
        try:
            # Connect to database and fetch real data
            await self.db.connect()
            
            # Get teacher and supervised students
            teacher = await self.db.teacher.find_unique(where={"id": teacher_id})
            if not teacher:
                print(f"Teacher {teacher_id} not found")
                return None
            
            # Get students supervised by this teacher
            students = await self.db.student.find_many(
                where={"id": {"in": teacher.supervised_students}}
            )
            
            # Get sessions in date range
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date + "T23:59:59")
            
            sessions = await self.db.chatsession.find_many(
                where={
                    "student_id": {"in": [s.id for s in students]},
                    "started_at": {"gte": start_dt, "lte": end_dt}
                },
                include={"messages": True, "student": True}
            )
            
            # Calculate real metrics
            overview_data = await self._calculate_overview_metrics(
                teacher, students, sessions, start_date, end_date
            )
            
            await self.db.disconnect()
            return overview_data
            
        except Exception as e:
            print(f"Error fetching real data: {e}")
            print("Falling back to mock data...")
            return self._generate_mock_overview(teacher_id, start_date, end_date)
    
    async def _calculate_overview_metrics(self, teacher, students, sessions, start_date, end_date):
        """Calculate real analytics metrics from database data"""
        total_students = len(students)
        total_sessions = len(sessions)
        
        # Calculate session metrics
        completed_sessions = [s for s in sessions if s.status == "completed"]
        completion_rate = (len(completed_sessions) / total_sessions * 100) if total_sessions > 0 else 0
        
        # Calculate average session duration
        durations = []
        for session in sessions:
            if session.ended_at and session.started_at:
                duration = (session.ended_at - session.started_at).total_seconds() / 60
                durations.append(duration)
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate message metrics
        all_messages = []
        for session in sessions:
            all_messages.extend(session.messages)
        
        total_messages = len(all_messages)
        avg_messages_per_student = total_messages / total_students if total_students > 0 else 0
        
        # Get student activity
        student_activity = {}
        for session in sessions:
            student_id = session.student_id
            student_activity[student_id] = student_activity.get(student_id, 0) + 1
        
        # Get most active students
        most_active = sorted(
            [(student_id, count) for student_id, count in student_activity.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        # Map student IDs to names
        student_names = {s.id: s.name for s in students}
        most_active_with_names = [
            {"name": student_names.get(student_id, "Unknown"), "sessions": count}
            for student_id, count in most_active
        ]
        
        # Calculate hourly distribution
        hourly_counts = {}
        for message in all_messages:
            hour = message.timestamp.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (0, 0)
        
        # Get learning challenges from concepts covered in sessions
        all_concepts = []
        for session in sessions:
            all_concepts.extend(session.concepts_covered or [])
        
        concept_counts = {}
        for concept in all_concepts:
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        top_challenges = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "teacherId": teacher.id,
            "dateRange": {"start": start_date, "end": end_date},
            "summary": {
                "totalStudents": total_students,
                "activeStudents": len([s for s in students if s.id in student_activity]),
                "totalSessions": total_sessions,
                "completionRate": round(completion_rate, 1),
                "avgSessionDuration": round(avg_duration, 1)
            },
            "engagement": {
                "avgMessagesPerStudent": round(avg_messages_per_student, 1),
                "totalMessages": total_messages,
                "peakHour": f"{peak_hour[0]:02d}:00",
                "peakMessages": peak_hour[1]
            },
            "studentActivity": most_active_with_names,
            "topChallenges": [{"concept": concept, "frequency": count} for concept, count in top_challenges],
            "generatedAt": datetime.now().isoformat()
        }
    
    async def fetch_faqs(self, teacher_id: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Fetch FAQ data from database"""
        if self.use_mock_data:
            from mock_data_generator import MockDataGenerator
            mock_gen = MockDataGenerator()
            return {"faqs": mock_gen.generate_faqs(limit)}
        
        try:
            await self.db.connect()
            
            faqs = await self.db.frequentlyaskedquestion.find_many(
                order_by={"frequency_count": "desc"},
                take=limit
            )
            
            faq_data = [
                {
                    "questionText": faq.question_text,
                    "category": faq.category,
                    "frequencyCount": faq.frequency_count,
                    "successRate": faq.success_rate
                }
                for faq in faqs
            ]
            
            await self.db.disconnect()
            return {"faqs": faq_data}
            
        except Exception as e:
            print(f"Error fetching FAQs: {e}")
            from mock_data_generator import MockDataGenerator
            mock_gen = MockDataGenerator()
            return {"faqs": mock_gen.generate_faqs(limit)}

    async def fetch_hourly_distribution(
        self, 
        teacher_id: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch hourly message distribution for a teacher's cohort.
        
        Args:
            teacher_id: The teacher's unique identifier
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary containing hourly distribution data or None if error
        """
        if not self.api_base_url:
            print("No API URL configured. Use StandaloneAnalytics for mock data instead.")
            return None
            
        try:
            url = f"{self.api_base_url}/teacher/{teacher_id}/hourly"
            params = {
                'start': start_date,
                'end': end_date
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching hourly distribution: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def fetch_faqs_and_misconceptions(
        self, 
        teacher_id: str, 
        start_date: str, 
        end_date: str,
        limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch top FAQs and misconceptions for a teacher's cohort.
        
        Args:
            teacher_id: The teacher's unique identifier
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            limit: Maximum number of FAQs to return (1-50)
            
        Returns:
            Dictionary containing FAQs and misconceptions or None if error
        """
        if not self.api_base_url:
            print("No API URL configured. Use StandaloneAnalytics for mock data instead.")
            return None
            
        try:
            url = f"{self.api_base_url}/teacher/{teacher_id}/faqs"
            params = {
                'start': start_date,
                'end': end_date,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FAQs and misconceptions: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def analyze_engagement_trends(self, overview_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze engagement trends from overview data and provide insights.
        
        Args:
            overview_data: Overview analytics data from API
            
        Returns:
            Dictionary containing analysis insights
        """
        insights = {}
        
        if not overview_data or 'engagementMetrics' not in overview_data:
            return {"error": "Invalid or missing engagement data"}
        
        engagement = overview_data['engagementMetrics']
        session_metrics = overview_data.get('sessionMetrics', {})
        
        # Analyze message activity
        avg_messages = engagement.get('avgMessagesPerStudent', 0)
        if avg_messages > 50:
            insights['message_activity'] = "High engagement - students are very active in conversations"
        elif avg_messages > 20:
            insights['message_activity'] = "Moderate engagement - good level of student participation"
        elif avg_messages > 5:
            insights['message_activity'] = "Low engagement - consider strategies to increase participation"
        else:
            insights['message_activity'] = "Very low engagement - immediate attention needed"
        
        # Analyze session completion
        completion_rate = session_metrics.get('completionRate', 0)
        if completion_rate > 80:
            insights['completion_trend'] = "Excellent session completion rate - students are staying engaged"
        elif completion_rate > 60:
            insights['completion_trend'] = "Good completion rate with room for improvement"
        elif completion_rate > 40:
            insights['completion_trend'] = "Moderate completion rate - investigate dropout causes"
        else:
            insights['completion_trend'] = "Low completion rate - urgent intervention needed"
        
        # Analyze session duration
        avg_duration = session_metrics.get('avgDurationMinutes', 0)
        if avg_duration > 30:
            insights['session_length'] = "Long sessions indicate deep engagement or potential confusion"
        elif avg_duration > 15:
            insights['session_length'] = "Optimal session length for focused learning"
        elif avg_duration > 5:
            insights['session_length'] = "Short sessions - check if students are getting adequate help"
        else:
            insights['session_length'] = "Very short sessions may indicate technical issues or lack of engagement"
        
        return insights
    
    def check_api_health(self) -> bool:
        """
        Check if the analytics API is healthy and responding.
        
        Returns:
            True if API is healthy, False otherwise
        """
        if not self.api_base_url:
            print("No API URL configured.")
            return False
            
        try:
            url = f"{self.api_base_url}/health"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            health_data = response.json()
            return health_data.get('status') == 'healthy'
            
        except Exception as e:
            print(f"API health check failed: {e}")
            return False
    
    def get_date_range_last_week(self) -> tuple[str, str]:
        """
        Get date range for the last 7 days.
        
        Returns:
            Tuple of (start_date, end_date) in ISO format
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        return (
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    
    def get_date_range_last_month(self) -> tuple[str, str]:
        """
        Get date range for the last 30 days.
        
        Returns:
            Tuple of (start_date, end_date) in ISO format
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        return (
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

# Factory function to create analytical agent
def create_analytical_agent(api_base_url: str = None) -> AnalyticalAgent:
    """
    Factory function to create and configure an AnalyticalAgent.
    
    Args:
        api_base_url: Base URL for the analytics API (optional, for real API calls)
        
    Returns:
        Configured AnalyticalAgent instance
    """
    return AnalyticalAgent(api_base_url=api_base_url)
