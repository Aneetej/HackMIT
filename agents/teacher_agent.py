from crewai import Agent
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from database.models import ChatSession, FrequentlyAskedQuestion, LearningAnalytics

class TeacherAgent:
    """
    Teacher Agent - Top level of the hierarchy
    
    Responsibilities:
    - Monitor all student interactions
    - Generate analytics and insights
    - Track frequently asked questions
    - Provide oversight and recommendations
    - Identify learning patterns across students
    """
    
    def __init__(self, tools: List = None):
        self.tools = tools or []
        self.monitored_sessions = {}
        self.faq_tracker = {}
        
        # Initialize the crewAI agent
        self.agent = Agent(
            role="Mathematics Education Supervisor",
            goal="""Monitor and analyze all student learning interactions to provide 
                   comprehensive insights, track learning patterns, and identify 
                   frequently asked questions to improve the overall learning experience.""",
            backstory="""You are an experienced mathematics educator with expertise in 
                        learning analytics and educational technology. You have the ability 
                        to observe all student-tutor interactions and extract meaningful 
                        insights about learning patterns, common difficulties, and 
                        effective teaching methods.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
    
    def get_crewai_agent(self) -> Agent:
        """Return the crewAI agent instance"""
        return self.agent
    
    async def notify_interaction(
        self, 
        student_id: str, 
        session_id: str, 
        summary: str
    ):
        """
        Receive notification of student interaction
        
        Args:
            student_id: The student involved in the interaction
            session_id: The session ID
            summary: Summary of the interaction
        """
        
        # Track the interaction
        if session_id not in self.monitored_sessions:
            self.monitored_sessions[session_id] = {
                'student_id': student_id,
                'start_time': datetime.utcnow(),
                'interactions': [],
                'concepts_covered': set(),
                'questions_asked': 0
            }
        
        # Add interaction summary
        self.monitored_sessions[session_id]['interactions'].append({
            'timestamp': datetime.utcnow(),
            'summary': summary
        })
        
        # Extract and track questions for FAQ analysis
        await self._extract_and_track_questions(summary, session_id)
    
    async def generate_individual_analytics(
        self, 
        student_id: str, 
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate analytics for an individual student
        
        Args:
            student_id: The student to analyze
            time_period: Time period for analysis (day, week, month)
            
        Returns:
            Dict containing individual student analytics
        """
        
        # Calculate time range
        end_date = datetime.utcnow()
        if time_period == "day":
            start_date = end_date - timedelta(days=1)
        elif time_period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(weeks=1)
        
        # Gather session data for the student
        student_sessions = [
            session for session in self.monitored_sessions.values()
            if session['student_id'] == student_id and 
            session['start_time'] >= start_date
        ]
        
        # Calculate metrics
        total_sessions = len(student_sessions)
        total_interactions = sum(len(session['interactions']) for session in student_sessions)
        
        # Engagement metrics
        avg_session_length = self._calculate_avg_session_length(student_sessions)
        concepts_covered = set()
        for session in student_sessions:
            concepts_covered.update(session.get('concepts_covered', set()))
        
        # Learning progress indicators
        progress_trend = self._analyze_progress_trend(student_sessions)
        
        return {
            'student_id': student_id,
            'time_period': time_period,
            'metrics': {
                'total_sessions': total_sessions,
                'total_interactions': total_interactions,
                'avg_session_length_minutes': avg_session_length,
                'concepts_covered': list(concepts_covered),
                'concepts_count': len(concepts_covered)
            },
            'engagement': {
                'trend': progress_trend,
                'consistency': self._calculate_consistency_score(student_sessions),
                'response_quality': self._assess_response_quality(student_sessions)
            },
            'recommendations': self._generate_recommendations(student_sessions),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def generate_class_overview(
        self, 
        student_ids: List[str], 
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate overview analytics for a class/group of students
        
        Args:
            student_ids: List of student IDs to include
            time_period: Time period for analysis
            
        Returns:
            Dict containing class overview analytics
        """
        
        class_analytics = []
        
        # Generate individual analytics for each student
        for student_id in student_ids:
            student_analytics = await self.generate_individual_analytics(
                student_id, time_period
            )
            class_analytics.append(student_analytics)
        
        # Aggregate class-level metrics
        total_sessions = sum(a['metrics']['total_sessions'] for a in class_analytics)
        total_concepts = set()
        for analytics in class_analytics:
            total_concepts.update(analytics['metrics']['concepts_covered'])
        
        # Identify common challenges
        common_concepts = self._identify_common_concepts(class_analytics)
        engagement_distribution = self._analyze_engagement_distribution(class_analytics)
        
        return {
            'class_overview': {
                'total_students': len(student_ids),
                'total_sessions': total_sessions,
                'unique_concepts_covered': len(total_concepts),
                'avg_sessions_per_student': total_sessions / len(student_ids) if student_ids else 0
            },
            'engagement_analysis': engagement_distribution,
            'common_concepts': common_concepts,
            'class_recommendations': self._generate_class_recommendations(class_analytics),
            'individual_analytics': class_analytics,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def get_faqs(
        self, 
        category: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get frequently asked questions
        
        Args:
            category: Optional category filter
            limit: Maximum number of FAQs to return
            
        Returns:
            List of FAQ data
        """
        
        # Sort FAQs by frequency
        sorted_faqs = sorted(
            self.faq_tracker.items(),
            key=lambda x: x[1]['frequency'],
            reverse=True
        )
        
        # Filter by category if specified
        if category:
            sorted_faqs = [
                (q, data) for q, data in sorted_faqs
                if data.get('category', '').lower() == category.lower()
            ]
        
        # Format and return top FAQs
        faqs = []
        for question, data in sorted_faqs[:limit]:
            faqs.append({
                'question': question,
                'frequency': data['frequency'],
                'category': data.get('category', 'general'),
                'last_asked': data.get('last_asked', ''),
                'common_answers': data.get('common_answers', []),
                'success_rate': data.get('success_rate', 0.0)
            })
        
        return faqs
    
    async def _extract_and_track_questions(self, summary: str, session_id: str):
        """Extract questions from interaction summary and track for FAQ analysis"""
        
        # Simple question extraction (in production, use NLP)
        sentences = summary.split('.')
        questions = [s.strip() + '?' for s in sentences if '?' in s]
        
        for question in questions:
            question = question.strip()
            if len(question) > 10:  # Filter out very short questions
                
                # Normalize question for tracking
                normalized_q = self._normalize_question(question)
                
                if normalized_q not in self.faq_tracker:
                    self.faq_tracker[normalized_q] = {
                        'frequency': 0,
                        'category': self._categorize_question(question),
                        'first_asked': datetime.utcnow().isoformat(),
                        'common_answers': [],
                        'success_rate': 0.0
                    }
                
                self.faq_tracker[normalized_q]['frequency'] += 1
                self.faq_tracker[normalized_q]['last_asked'] = datetime.utcnow().isoformat()
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question text for better matching"""
        # Remove extra whitespace, convert to lowercase
        normalized = ' '.join(question.lower().split())
        
        # Remove common variations
        replacements = {
            "how do i": "how to",
            "can you": "how to",
            "what is": "what's",
            "how does": "how do"
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    def _categorize_question(self, question: str) -> str:
        """Categorize question by mathematical topic"""
        question_lower = question.lower()
        
        categories = {
            'algebra': ['variable', 'equation', 'solve', 'x', 'linear', 'quadratic'],
            'geometry': ['triangle', 'circle', 'area', 'perimeter', 'angle', 'shape'],
            'calculus': ['derivative', 'integral', 'limit', 'function', 'rate'],
            'statistics': ['mean', 'median', 'probability', 'data', 'graph'],
            'arithmetic': ['add', 'subtract', 'multiply', 'divide', 'fraction']
        }
        
        for category, keywords in categories.items():
            if any(keyword in question_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _calculate_avg_session_length(self, sessions: List[Dict]) -> float:
        """Calculate average session length in minutes"""
        if not sessions:
            return 0.0
        
        total_minutes = 0
        valid_sessions = 0
        
        for session in sessions:
            if session['interactions']:
                # Estimate session length based on interaction timestamps
                start_time = session['start_time']
                last_interaction = session['interactions'][-1]['timestamp']
                duration = (last_interaction - start_time).total_seconds() / 60
                total_minutes += duration
                valid_sessions += 1
        
        return total_minutes / valid_sessions if valid_sessions > 0 else 0.0
    
    def _analyze_progress_trend(self, sessions: List[Dict]) -> str:
        """Analyze learning progress trend"""
        if len(sessions) < 2:
            return "insufficient_data"
        
        # Simple trend analysis based on session frequency and interaction count
        recent_sessions = sessions[-3:] if len(sessions) >= 3 else sessions
        older_sessions = sessions[:-3] if len(sessions) >= 3 else []
        
        if not older_sessions:
            return "new_learner"
        
        recent_avg_interactions = sum(len(s['interactions']) for s in recent_sessions) / len(recent_sessions)
        older_avg_interactions = sum(len(s['interactions']) for s in older_sessions) / len(older_sessions)
        
        if recent_avg_interactions > older_avg_interactions * 1.1:
            return "improving"
        elif recent_avg_interactions < older_avg_interactions * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _calculate_consistency_score(self, sessions: List[Dict]) -> float:
        """Calculate learning consistency score (0.0 to 1.0)"""
        if len(sessions) < 2:
            return 0.5
        
        # Calculate based on regular session intervals
        session_dates = [s['start_time'].date() for s in sessions]
        unique_dates = set(session_dates)
        
        # More unique dates = more consistent learning
        consistency = len(unique_dates) / len(sessions)
        return min(consistency, 1.0)
    
    def _assess_response_quality(self, sessions: List[Dict]) -> str:
        """Assess the quality of student responses"""
        if not sessions:
            return "unknown"
        
        total_interactions = sum(len(s['interactions']) for s in sessions)
        
        # Simple heuristic based on interaction count
        if total_interactions > 20:
            return "high_engagement"
        elif total_interactions > 10:
            return "moderate_engagement"
        else:
            return "low_engagement"
    
    def _generate_recommendations(self, sessions: List[Dict]) -> List[str]:
        """Generate personalized recommendations based on session analysis"""
        recommendations = []
        
        if not sessions:
            return ["Start with regular practice sessions to build momentum"]
        
        avg_length = self._calculate_avg_session_length(sessions)
        trend = self._analyze_progress_trend(sessions)
        
        if avg_length < 5:
            recommendations.append("Consider longer study sessions for deeper understanding")
        
        if trend == "declining":
            recommendations.append("Review fundamental concepts to strengthen foundation")
            recommendations.append("Consider adjusting difficulty level or pacing")
        elif trend == "improving":
            recommendations.append("Great progress! Consider tackling more challenging problems")
        
        consistency = self._calculate_consistency_score(sessions)
        if consistency < 0.3:
            recommendations.append("Try to maintain more regular study schedule")
        
        return recommendations
    
    def _identify_common_concepts(self, class_analytics: List[Dict]) -> List[Dict]:
        """Identify concepts that appear frequently across students"""
        concept_frequency = {}
        
        for analytics in class_analytics:
            for concept in analytics['metrics']['concepts_covered']:
                concept_frequency[concept] = concept_frequency.get(concept, 0) + 1
        
        # Sort by frequency and return top concepts
        sorted_concepts = sorted(
            concept_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'concept': concept, 'frequency': freq}
            for concept, freq in sorted_concepts[:10]
        ]
    
    def _analyze_engagement_distribution(self, class_analytics: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement distribution across the class"""
        engagement_levels = [a['engagement']['response_quality'] for a in class_analytics]
        
        distribution = {
            'high_engagement': engagement_levels.count('high_engagement'),
            'moderate_engagement': engagement_levels.count('moderate_engagement'),
            'low_engagement': engagement_levels.count('low_engagement')
        }
        
        total_students = len(class_analytics)
        percentages = {
            level: (count / total_students * 100) if total_students > 0 else 0
            for level, count in distribution.items()
        }
        
        return {
            'distribution': distribution,
            'percentages': percentages,
            'total_students': total_students
        }
    
    def _generate_class_recommendations(self, class_analytics: List[Dict]) -> List[str]:
        """Generate recommendations for the entire class"""
        recommendations = []
        
        # Analyze common patterns
        low_engagement_count = sum(
            1 for a in class_analytics 
            if a['engagement']['response_quality'] == 'low_engagement'
        )
        
        if low_engagement_count > len(class_analytics) * 0.3:
            recommendations.append("Consider reviewing teaching methods to increase engagement")
        
        # Check for common struggling concepts
        common_concepts = self._identify_common_concepts(class_analytics)
        if common_concepts:
            top_concept = common_concepts[0]['concept']
            recommendations.append(f"Focus on '{top_concept}' - appears challenging for many students")
        
        return recommendations
