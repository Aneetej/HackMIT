import requests
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

class AnalyticalAgent:
    """
    Analytics agent specialized in fetching and analyzing teacher analytics data
    from the Express API endpoints.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:4000/api"):
        self.role = "Analytics Specialist"
        self.goal = "Fetch and analyze educational analytics data for teachers"
        self.backstory = """You are an expert data analyst specializing in educational metrics. 
        You excel at interpreting student engagement data, learning patterns, and 
        providing actionable insights for teachers to improve their instruction."""
        self.api_base_url = api_base_url.rstrip('/') if api_base_url else "http://localhost:4000/api"
    
    def fetch_teacher_overview(
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
        try:
            url = f"{self.api_base_url}/teacher/{teacher_id}/overview"
            params = {
                'start': start_date,
                'end': end_date
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching teacher overview: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None

    def fetch_faqs(self, teacher_id: str, start_date: str, end_date: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Fetch FAQ data from the backend API.
        
        Args:
            teacher_id: The teacher's unique identifier
            start_date: Start date for the query
            end_date: End date for the query
            limit: Maximum number of FAQs to return
            
        Returns:
            Dictionary containing FAQ data or None if error
        """
        try:
            url = f"{self.api_base_url}/teacher/{teacher_id}/faqs"
            params = {"start": start_date, "end": end_date, "limit": limit}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FAQs: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None

    def fetch_hourly_distribution(
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
        
        if not overview_data:
            return {"error": "Invalid or missing overview data"}
        
        # Handle different response formats
        engagement = overview_data.get('engagement', {})
        summary = overview_data.get('summary', {})
        
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
        completion_rate = summary.get('completionRate', 0)
        if completion_rate > 80:
            insights['completion_trend'] = "Excellent session completion rate - students are staying engaged"
        elif completion_rate > 60:
            insights['completion_trend'] = "Good completion rate with room for improvement"
        elif completion_rate > 40:
            insights['completion_trend'] = "Moderate completion rate - investigate dropout causes"
        else:
            insights['completion_trend'] = "Low completion rate - urgent intervention needed"
        
        # Analyze session duration
        avg_duration = summary.get('avgSessionDuration', 0)
        if avg_duration > 30:
            insights['session_length'] = "Long sessions indicate deep engagement or potential confusion"
        elif avg_duration > 15:
            insights['session_length'] = "Optimal session length for focused learning"
        elif avg_duration > 5:
            insights['session_length'] = "Short sessions - check if students are getting adequate help"
        else:
            insights['session_length'] = "Very short sessions - students may not be getting sufficient support"
        
        return insights
    
    def fetch_engagement_analysis(
        self, 
        teacher_id: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch and analyze engagement data for a teacher's cohort.
        
        Args:
            teacher_id: The teacher's unique identifier
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary containing engagement analysis or None if error
        """
        try:
            # Get overview data for engagement analysis
            overview_data = self.fetch_teacher_overview(teacher_id, start_date, end_date)
            if not overview_data:
                return {"error": "Failed to fetch overview data for engagement analysis"}
            
            # Analyze engagement trends using the correct field names from API response
            engagement_metrics = overview_data.get('engagementMetrics', {})
            session_metrics = overview_data.get('sessionMetrics', {})
            
            # Create insights based on actual API response structure
            insights = {}
            
            # Analyze message activity
            avg_messages = engagement_metrics.get('avgMessagesPerStudent', 0)
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
                insights['session_length'] = "Very short sessions - students may not be getting sufficient support"
            
            # Get hourly distribution for activity patterns
            hourly_data = self.fetch_hourly_distribution(teacher_id, start_date, end_date)
            
            # Combine all engagement data
            engagement_analysis = {
                "teacherId": teacher_id,
                "dateRange": {
                    "start": start_date,
                    "end": end_date
                },
                "engagementMetrics": engagement_metrics,
                "sessionMetrics": session_metrics,
                "insights": insights,
                "activityPatterns": hourly_data.get('summary', {}) if hourly_data else {},
                "studentActivity": overview_data.get('studentActivity', [])
            }
            
            return engagement_analysis
            
        except Exception as e:
            print(f"Error in engagement analysis: {e}")
            return {"error": f"Engagement analysis failed: {str(e)}"}
    
    def fetch_topic_performance(
        self, 
        teacher_id: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch topic performance data from backend API.
        """
        try:
            url = f"{self.api_base_url}/teacher/{teacher_id}/topic-performance"
            params = {"start": start_date, "end": end_date}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching topic performance: {e}")
            return {
                "successfulTopics": [],
                "strugglingTopics": [],
                "summary": {
                    "totalSuccessfulTopics": 0,
                    "totalStrugglingTopics": 0
                }
            }

    def fetch_analytics_summary(self, teacher_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch analytics summary from backend API.
        """
        try:
            url = f"{self.api_base_url}/teacher/{teacher_id}/analytics-summary"
            params = {"start": start_date, "end": end_date}
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching analytics summary: {e}")
            return {
                "summary": "Unable to generate summary due to data unavailability.",
                "keyInsights": [],
                "recommendations": []
            }
    
    def check_api_health(self) -> bool:
        """
        Check if the analytics API is healthy and responding.
        
        Returns:
            True if API is healthy, False otherwise
        """
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
def create_analytical_agent(api_base_url: str = "http://localhost:4000/api") -> AnalyticalAgent:
    """
    Factory function to create and configure an AnalyticalAgent.
    
    Args:
        api_base_url: Base URL for the analytics API
        
    Returns:
        Configured AnalyticalAgent instance
    """
    return AnalyticalAgent(api_base_url=api_base_url)
