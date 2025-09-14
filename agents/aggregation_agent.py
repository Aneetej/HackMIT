from crewai import Agent
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class AggregationAgent:
    """
    Aggregation Agent - Data collection and analysis
    
    Responsibilities:
    - Collect and aggregate interaction data
    - Generate statistical insights
    - Track learning patterns across students
    - Provide data for teacher analytics
    - Monitor system performance metrics
    """
    
    def __init__(self):
        self.interaction_logs = []
        self.student_metrics = defaultdict(dict)
        self.system_metrics = defaultdict(list)
        self.learning_patterns = defaultdict(list)
        
        # Initialize the crewAI agent
        self.agent = Agent(
            role="Data Analytics and Aggregation Specialist",
            goal="""Collect, process, and analyze all educational interaction data to 
                   provide comprehensive insights about learning patterns, student 
                   engagement, and system performance for continuous improvement.""",
            backstory="""You are an expert data analyst specializing in educational 
                        technology and learning analytics. You have extensive experience 
                        in processing large volumes of educational interaction data, 
                        identifying meaningful patterns, and generating actionable 
                        insights for educators and system optimization.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
    
    def get_crewai_agent(self) -> Agent:
        """Return the crewAI agent instance"""
        return self.agent
    
    async def log_interaction(
        self,
        student_id: str,
        message: str,
        response: Dict[str, Any],
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a student-agent interaction for analysis
        
        Args:
            student_id: The student involved
            message: Student's message
            response: Agent's response data
            session_id: Session identifier
            metadata: Additional metadata
        """
        
        interaction_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'student_id': student_id,
            'session_id': session_id,
            'message_length': len(message),
            'response_length': len(response.get('response', '')),
            'concepts_covered': response.get('concepts_covered', []),
            'difficulty_level': response.get('difficulty_level', 'medium'),
            'response_type': response.get('response_type', 'text'),
            'engagement_indicators': self._extract_engagement_indicators(message, response),
            'learning_indicators': response.get('preference_indicators', {}),
            'metadata': metadata or {}
        }
        
        # Store interaction
        self.interaction_logs.append(interaction_data)
        
        # Update student metrics
        await self._update_student_metrics(student_id, interaction_data)
        
        # Update learning patterns
        await self._update_learning_patterns(student_id, interaction_data)
        
        # Update system metrics
        await self._update_system_metrics(interaction_data)
        
        # Cleanup old data (keep last 1000 interactions)
        if len(self.interaction_logs) > 1000:
            self.interaction_logs = self.interaction_logs[-1000:]
    
    async def generate_student_analytics(
        self, 
        student_id: str, 
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics for a specific student
        
        Args:
            student_id: The student to analyze
            time_period: Time period for analysis
            
        Returns:
            Dict containing detailed student analytics
        """
        
        # Filter interactions for this student and time period
        student_interactions = await self._get_student_interactions(student_id, time_period)
        
        if not student_interactions:
            return {
                'student_id': student_id,
                'time_period': time_period,
                'message': 'No interactions found for this period',
                'analytics': {}
            }
        
        # Calculate engagement metrics
        engagement_metrics = await self._calculate_engagement_metrics(student_interactions)
        
        # Calculate learning progress
        learning_progress = await self._calculate_learning_progress(student_interactions)
        
        # Analyze interaction patterns
        interaction_patterns = await self._analyze_interaction_patterns(student_interactions)
        
        # Generate recommendations
        recommendations = await self._generate_student_recommendations(
            student_interactions, engagement_metrics, learning_progress
        )
        
        return {
            'student_id': student_id,
            'time_period': time_period,
            'analytics': {
                'engagement': engagement_metrics,
                'learning_progress': learning_progress,
                'interaction_patterns': interaction_patterns,
                'recommendations': recommendations
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def generate_class_analytics(
        self, 
        student_ids: List[str], 
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate analytics for a class/group of students
        
        Args:
            student_ids: List of student IDs
            time_period: Time period for analysis
            
        Returns:
            Dict containing class-level analytics
        """
        
        class_interactions = []
        student_analytics = {}
        
        # Collect data for all students
        for student_id in student_ids:
            student_data = await self.generate_student_analytics(student_id, time_period)
            student_analytics[student_id] = student_data
            
            student_interactions = await self._get_student_interactions(student_id, time_period)
            class_interactions.extend(student_interactions)
        
        if not class_interactions:
            return {
                'class_analytics': {
                    'message': 'No interactions found for this class and period'
                }
            }
        
        # Calculate class-level metrics
        class_engagement = await self._calculate_class_engagement(class_interactions)
        concept_distribution = await self._analyze_concept_distribution(class_interactions)
        difficulty_analysis = await self._analyze_difficulty_distribution(class_interactions)
        common_patterns = await self._identify_common_patterns(class_interactions)
        
        return {
            'class_analytics': {
                'total_students': len(student_ids),
                'total_interactions': len(class_interactions),
                'time_period': time_period,
                'engagement_overview': class_engagement,
                'concept_distribution': concept_distribution,
                'difficulty_analysis': difficulty_analysis,
                'common_patterns': common_patterns
            },
            'individual_analytics': student_analytics,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def get_frequently_asked_questions(
        self, 
        limit: int = 10, 
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze interactions to identify frequently asked questions
        
        Args:
            limit: Maximum number of FAQs to return
            category: Optional category filter
            
        Returns:
            List of FAQ data with frequency and patterns
        """
        
        # Extract questions from interactions
        questions = []
        for interaction in self.interaction_logs:
            message = interaction.get('message', '')
            if '?' in message and len(message) > 10:
                questions.append({
                    'question': message,
                    'concepts': interaction.get('concepts_covered', []),
                    'timestamp': interaction['timestamp'],
                    'student_id': interaction['student_id']
                })
        
        # Group similar questions
        question_groups = await self._group_similar_questions(questions)
        
        # Calculate frequencies and rank
        faq_data = []
        for group_key, group_questions in question_groups.items():
            if category and not any(category.lower() in concept.lower() 
                                  for q in group_questions 
                                  for concept in q.get('concepts', [])):
                continue
            
            faq_data.append({
                'representative_question': group_questions[0]['question'],
                'frequency': len(group_questions),
                'concepts': list(set(concept for q in group_questions 
                                   for concept in q.get('concepts', []))),
                'first_asked': min(q['timestamp'] for q in group_questions),
                'last_asked': max(q['timestamp'] for q in group_questions),
                'unique_students': len(set(q['student_id'] for q in group_questions))
            })
        
        # Sort by frequency and return top results
        faq_data.sort(key=lambda x: x['frequency'], reverse=True)
        return faq_data[:limit]
    
    async def get_system_performance_metrics(self) -> Dict[str, Any]:
        """
        Get system performance and usage metrics
        
        Returns:
            Dict containing system performance data
        """
        
        current_time = datetime.utcnow()
        
        # Calculate metrics for different time periods
        metrics = {}
        
        for period_name, hours in [('last_hour', 1), ('last_day', 24), ('last_week', 168)]:
            period_start = current_time - timedelta(hours=hours)
            period_interactions = [
                i for i in self.interaction_logs 
                if datetime.fromisoformat(i['timestamp']) >= period_start
            ]
            
            if period_interactions:
                metrics[period_name] = {
                    'total_interactions': len(period_interactions),
                    'unique_students': len(set(i['student_id'] for i in period_interactions)),
                    'unique_sessions': len(set(i['session_id'] for i in period_interactions)),
                    'avg_response_length': statistics.mean(i['response_length'] for i in period_interactions),
                    'concept_coverage': len(set(concept for i in period_interactions 
                                              for concept in i.get('concepts_covered', []))),
                    'engagement_score': await self._calculate_period_engagement(period_interactions)
                }
            else:
                metrics[period_name] = {
                    'total_interactions': 0,
                    'message': 'No interactions in this period'
                }
        
        return {
            'performance_metrics': metrics,
            'system_health': await self._assess_system_health(),
            'generated_at': current_time.isoformat()
        }
    
    async def _get_student_interactions(self, student_id: str, time_period: str) -> List[Dict[str, Any]]:
        """Get interactions for a specific student within time period"""
        
        end_time = datetime.utcnow()
        
        if time_period == "day":
            start_time = end_time - timedelta(days=1)
        elif time_period == "week":
            start_time = end_time - timedelta(weeks=1)
        elif time_period == "month":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(weeks=1)
        
        return [
            interaction for interaction in self.interaction_logs
            if (interaction['student_id'] == student_id and 
                datetime.fromisoformat(interaction['timestamp']) >= start_time)
        ]
    
    async def _calculate_engagement_metrics(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement metrics from interactions"""
        
        if not interactions:
            return {'message': 'No interactions to analyze'}
        
        # Calculate various engagement indicators
        message_lengths = [i['message_length'] for i in interactions]
        response_lengths = [i['response_length'] for i in interactions]
        
        # Session analysis
        sessions = set(i['session_id'] for i in interactions)
        interactions_per_session = len(interactions) / len(sessions) if sessions else 0
        
        # Concept engagement
        all_concepts = [concept for i in interactions for concept in i.get('concepts_covered', [])]
        unique_concepts = set(all_concepts)
        
        return {
            'total_interactions': len(interactions),
            'unique_sessions': len(sessions),
            'avg_interactions_per_session': round(interactions_per_session, 2),
            'avg_message_length': round(statistics.mean(message_lengths), 2) if message_lengths else 0,
            'avg_response_length': round(statistics.mean(response_lengths), 2) if response_lengths else 0,
            'concepts_explored': len(unique_concepts),
            'concept_diversity': round(len(unique_concepts) / len(all_concepts), 2) if all_concepts else 0,
            'engagement_score': await self._calculate_engagement_score(interactions)
        }
    
    async def _calculate_learning_progress(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate learning progress indicators"""
        
        if len(interactions) < 2:
            return {'message': 'Insufficient data for progress analysis'}
        
        # Sort interactions by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x['timestamp'])
        
        # Analyze difficulty progression
        difficulty_levels = {'easy': 1, 'medium': 2, 'hard': 3}
        difficulty_progression = [
            difficulty_levels.get(i.get('difficulty_level', 'medium'), 2) 
            for i in sorted_interactions
        ]
        
        # Calculate trend
        if len(difficulty_progression) >= 3:
            recent_avg = statistics.mean(difficulty_progression[-3:])
            earlier_avg = statistics.mean(difficulty_progression[:-3]) if len(difficulty_progression) > 3 else difficulty_progression[0]
            
            if recent_avg > earlier_avg * 1.1:
                progress_trend = 'advancing'
            elif recent_avg < earlier_avg * 0.9:
                progress_trend = 'reviewing'
            else:
                progress_trend = 'stable'
        else:
            progress_trend = 'insufficient_data'
        
        # Concept mastery analysis
        concept_frequency = defaultdict(int)
        for interaction in sorted_interactions:
            for concept in interaction.get('concepts_covered', []):
                concept_frequency[concept] += 1
        
        return {
            'progress_trend': progress_trend,
            'difficulty_progression': difficulty_progression,
            'avg_difficulty': round(statistics.mean(difficulty_progression), 2),
            'concept_mastery': dict(concept_frequency),
            'learning_velocity': len(set(concept for i in sorted_interactions 
                                       for concept in i.get('concepts_covered', []))) / len(sorted_interactions)
        }
    
    async def _analyze_interaction_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in student interactions"""
        
        if not interactions:
            return {}
        
        # Time-based patterns
        timestamps = [datetime.fromisoformat(i['timestamp']) for i in interactions]
        hours = [t.hour for t in timestamps]
        days = [t.weekday() for t in timestamps]
        
        # Response type patterns
        response_types = [i.get('response_type', 'text') for i in interactions]
        response_type_counts = defaultdict(int)
        for rt in response_types:
            response_type_counts[rt] += 1
        
        return {
            'preferred_hours': self._find_most_common(hours),
            'preferred_days': self._find_most_common(days),
            'response_type_preferences': dict(response_type_counts),
            'session_patterns': await self._analyze_session_patterns(interactions),
            'consistency_score': await self._calculate_consistency_score(timestamps)
        }
    
    async def _generate_student_recommendations(
        self, 
        interactions: List[Dict[str, Any]], 
        engagement: Dict[str, Any], 
        progress: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized recommendations for student"""
        
        recommendations = []
        
        # Engagement-based recommendations
        if engagement.get('avg_interactions_per_session', 0) < 3:
            recommendations.append("Encourage longer study sessions for deeper learning")
        
        if engagement.get('concept_diversity', 0) < 0.3:
            recommendations.append("Explore a wider variety of mathematical concepts")
        
        # Progress-based recommendations
        progress_trend = progress.get('progress_trend', 'stable')
        if progress_trend == 'reviewing':
            recommendations.append("Focus on strengthening fundamental concepts")
        elif progress_trend == 'advancing':
            recommendations.append("Continue challenging yourself with advanced topics")
        
        # Pattern-based recommendations
        if len(interactions) > 0:
            avg_message_length = engagement.get('avg_message_length', 0)
            if avg_message_length < 20:
                recommendations.append("Try asking more detailed questions for better help")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _extract_engagement_indicators(self, message: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract engagement indicators from interaction"""
        
        indicators = {}
        
        # Message engagement indicators
        message_lower = message.lower()
        if any(word in message_lower for word in ['help', 'please', 'can you']):
            indicators['politeness'] = True
        
        if '?' in message:
            indicators['asks_questions'] = True
        
        if any(word in message_lower for word in ['understand', 'get it', 'clear']):
            indicators['seeks_understanding'] = True
        
        # Response engagement indicators
        response_length = len(response.get('response', ''))
        if response_length > 100:
            indicators['detailed_response'] = True
        
        return indicators
    
    async def _update_student_metrics(self, student_id: str, interaction_data: Dict[str, Any]):
        """Update running metrics for a student"""
        
        if student_id not in self.student_metrics:
            self.student_metrics[student_id] = {
                'total_interactions': 0,
                'total_concepts': set(),
                'session_count': set(),
                'first_interaction': interaction_data['timestamp'],
                'last_interaction': interaction_data['timestamp']
            }
        
        metrics = self.student_metrics[student_id]
        metrics['total_interactions'] += 1
        metrics['total_concepts'].update(interaction_data.get('concepts_covered', []))
        metrics['session_count'].add(interaction_data['session_id'])
        metrics['last_interaction'] = interaction_data['timestamp']
    
    async def _update_learning_patterns(self, student_id: str, interaction_data: Dict[str, Any]):
        """Update learning patterns for a student"""
        
        pattern_data = {
            'timestamp': interaction_data['timestamp'],
            'concepts': interaction_data.get('concepts_covered', []),
            'difficulty': interaction_data.get('difficulty_level', 'medium'),
            'engagement': interaction_data.get('engagement_indicators', {})
        }
        
        self.learning_patterns[student_id].append(pattern_data)
        
        # Keep only recent patterns (last 50)
        if len(self.learning_patterns[student_id]) > 50:
            self.learning_patterns[student_id] = self.learning_patterns[student_id][-50:]
    
    async def _update_system_metrics(self, interaction_data: Dict[str, Any]):
        """Update system-wide metrics"""
        
        timestamp = interaction_data['timestamp']
        hour_key = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d-%H')
        
        self.system_metrics[hour_key].append({
            'interaction_count': 1,
            'concepts_covered': len(interaction_data.get('concepts_covered', [])),
            'response_length': interaction_data.get('response_length', 0)
        })
    
    async def _calculate_engagement_score(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate overall engagement score (0.0 to 1.0)"""
        
        if not interactions:
            return 0.0
        
        score_components = []
        
        # Message quality score
        avg_message_length = statistics.mean(i['message_length'] for i in interactions)
        message_score = min(avg_message_length / 50, 1.0)  # Normalize to 50 chars
        score_components.append(message_score)
        
        # Interaction frequency score
        sessions = set(i['session_id'] for i in interactions)
        interactions_per_session = len(interactions) / len(sessions) if sessions else 0
        frequency_score = min(interactions_per_session / 10, 1.0)  # Normalize to 10 interactions
        score_components.append(frequency_score)
        
        # Concept diversity score
        all_concepts = [concept for i in interactions for concept in i.get('concepts_covered', [])]
        unique_concepts = set(all_concepts)
        diversity_score = min(len(unique_concepts) / 5, 1.0) if all_concepts else 0  # Normalize to 5 concepts
        score_components.append(diversity_score)
        
        return round(statistics.mean(score_components), 2)
    
    def _find_most_common(self, items: List) -> List:
        """Find most common items in a list"""
        if not items:
            return []
        
        counts = defaultdict(int)
        for item in items:
            counts[item] += 1
        
        max_count = max(counts.values())
        return [item for item, count in counts.items() if count == max_count]
    
    async def _analyze_session_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns within sessions"""
        
        session_data = defaultdict(list)
        for interaction in interactions:
            session_data[interaction['session_id']].append(interaction)
        
        session_lengths = [len(session_interactions) for session_interactions in session_data.values()]
        
        return {
            'avg_session_length': round(statistics.mean(session_lengths), 2) if session_lengths else 0,
            'total_sessions': len(session_data),
            'session_length_distribution': {
                'short': len([s for s in session_lengths if s <= 3]),
                'medium': len([s for s in session_lengths if 4 <= s <= 7]),
                'long': len([s for s in session_lengths if s >= 8])
            }
        }
    
    async def _calculate_consistency_score(self, timestamps: List[datetime]) -> float:
        """Calculate learning consistency score based on timestamp patterns"""
        
        if len(timestamps) < 2:
            return 0.0
        
        # Calculate intervals between interactions
        sorted_timestamps = sorted(timestamps)
        intervals = []
        for i in range(1, len(sorted_timestamps)):
            interval = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds() / 3600  # hours
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Consistency is higher when intervals are more regular
        avg_interval = statistics.mean(intervals)
        interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        
        # Normalize consistency score (lower variance = higher consistency)
        consistency = 1.0 / (1.0 + interval_variance / (avg_interval ** 2)) if avg_interval > 0 else 0.0
        
        return round(consistency, 2)
    
    async def _calculate_class_engagement(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate class-level engagement metrics"""
        
        if not interactions:
            return {}
        
        students = set(i['student_id'] for i in interactions)
        sessions = set(i['session_id'] for i in interactions)
        
        return {
            'total_students': len(students),
            'total_sessions': len(sessions),
            'total_interactions': len(interactions),
            'avg_interactions_per_student': round(len(interactions) / len(students), 2),
            'avg_sessions_per_student': round(len(sessions) / len(students), 2),
            'class_engagement_score': await self._calculate_engagement_score(interactions)
        }
    
    async def _analyze_concept_distribution(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of mathematical concepts across class"""
        
        concept_counts = defaultdict(int)
        for interaction in interactions:
            for concept in interaction.get('concepts_covered', []):
                concept_counts[concept] += 1
        
        total_concepts = sum(concept_counts.values())
        
        return {
            'total_concept_instances': total_concepts,
            'unique_concepts': len(concept_counts),
            'concept_distribution': dict(concept_counts),
            'top_concepts': sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    async def _analyze_difficulty_distribution(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze difficulty level distribution"""
        
        difficulty_counts = defaultdict(int)
        for interaction in interactions:
            difficulty = interaction.get('difficulty_level', 'medium')
            difficulty_counts[difficulty] += 1
        
        total = sum(difficulty_counts.values())
        
        return {
            'distribution': dict(difficulty_counts),
            'percentages': {
                level: round(count / total * 100, 1) if total > 0 else 0
                for level, count in difficulty_counts.items()
            }
        }
    
    async def _identify_common_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify common patterns across the class"""
        
        # Time patterns
        hours = [datetime.fromisoformat(i['timestamp']).hour for i in interactions]
        peak_hours = self._find_most_common(hours)
        
        # Response type patterns
        response_types = [i.get('response_type', 'text') for i in interactions]
        common_response_types = self._find_most_common(response_types)
        
        return {
            'peak_learning_hours': peak_hours,
            'preferred_response_types': common_response_types,
            'common_concepts': await self._find_common_concept_sequences(interactions)
        }
    
    async def _find_common_concept_sequences(self, interactions: List[Dict[str, Any]]) -> List[List[str]]:
        """Find common sequences of concepts studied"""
        
        # Group by session and extract concept sequences
        session_sequences = defaultdict(list)
        for interaction in sorted(interactions, key=lambda x: x['timestamp']):
            session_id = interaction['session_id']
            concepts = interaction.get('concepts_covered', [])
            if concepts:
                session_sequences[session_id].extend(concepts)
        
        # Find common subsequences (simplified approach)
        all_sequences = list(session_sequences.values())
        common_sequences = []
        
        # Look for sequences of length 2-3 that appear multiple times
        for seq_length in [2, 3]:
            sequence_counts = defaultdict(int)
            for sequence in all_sequences:
                for i in range(len(sequence) - seq_length + 1):
                    subseq = tuple(sequence[i:i + seq_length])
                    sequence_counts[subseq] += 1
            
            # Add sequences that appear more than once
            for seq, count in sequence_counts.items():
                if count > 1:
                    common_sequences.append(list(seq))
        
        return common_sequences[:5]  # Return top 5
    
    async def _group_similar_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group similar questions together for FAQ analysis"""
        
        # Simple grouping based on key terms and concepts
        groups = defaultdict(list)
        
        for question in questions:
            # Create a key based on concepts and key terms
            concepts = question.get('concepts', [])
            question_text = question['question'].lower()
            
            # Extract key terms
            key_terms = []
            for word in question_text.split():
                if len(word) > 3 and word not in ['what', 'how', 'why', 'when', 'where', 'does', 'this', 'that']:
                    key_terms.append(word)
            
            # Create group key
            group_key = tuple(sorted(concepts + key_terms[:3]))  # Use top 3 key terms
            groups[group_key].append(question)
        
        return dict(groups)
    
    async def _calculate_period_engagement(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate engagement score for a specific time period"""
        return await self._calculate_engagement_score(interactions)
    
    async def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health based on metrics"""
        
        current_time = datetime.utcnow()
        recent_interactions = [
            i for i in self.interaction_logs
            if datetime.fromisoformat(i['timestamp']) >= current_time - timedelta(hours=1)
        ]
        
        health_status = "healthy"
        issues = []
        
        # Check interaction volume
        if len(recent_interactions) == 0:
            health_status = "warning"
            issues.append("No recent interactions")
        elif len(recent_interactions) > 100:
            health_status = "warning"
            issues.append("High interaction volume")
        
        # Check for error patterns
        error_indicators = [
            i for i in recent_interactions
            if i.get('metadata', {}).get('errors', False)
        ]
        
        if len(error_indicators) > len(recent_interactions) * 0.1:  # More than 10% errors
            health_status = "critical"
            issues.append("High error rate")
        
        return {
            'status': health_status,
            'issues': issues,
            'recent_interaction_count': len(recent_interactions),
            'error_rate': len(error_indicators) / len(recent_interactions) if recent_interactions else 0
        }
