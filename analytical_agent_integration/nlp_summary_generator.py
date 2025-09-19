#!/usr/bin/env python3
"""
NLP Summary Generator

This module generates comprehensive class summaries using NLP techniques
and real student data from the backend API.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter
import re

# Try to import NLP libraries, fall back gracefully if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    NLP_AVAILABLE = True
except ImportError:
    print("NLP libraries not available. Using basic text processing.")
    NLP_AVAILABLE = False

class NLPSummaryGenerator:
    """Generates comprehensive class summaries using NLP and real backend data."""
    
    def __init__(self, api_base_url: str = "http://localhost:4000/api"):
        """
        Initialize the NLP summary generator.
        
        Args:
            api_base_url: Base URL for the analytics API
        """
        self.api_base_url = api_base_url.rstrip('/') if api_base_url else "http://localhost:4000/api"
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.claude_available = bool(self.anthropic_api_key)
        
        if not self.claude_available:
            print("ANTHROPIC_API_KEY not found. Using basic NLP processing.")
    
    def generate_class_summary(
        self,
        teacher_id: str,
        start_date: str = None,
        end_date: str = None,
        include_sentiment: bool = True,
        include_topics: bool = True,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive class summary using real student data.
        
        Args:
            teacher_id: Teacher's unique identifier
            start_date: Start date for summary period
            end_date: End date for summary period
            include_sentiment: Whether to include sentiment analysis
            include_topics: Whether to include topic modeling
            include_recommendations: Whether to include AI recommendations
            
        Returns:
            Dictionary containing comprehensive class summary
        """
        print(f"Generating class summary for teacher {teacher_id}")
        
        # Fetch real student data from backend
        student_data = self._fetch_student_data(teacher_id, start_date, end_date)
        if not student_data:
            return self._generate_default_summary(teacher_id)
        
        # Process the data
        summary = {
            "teacher_id": teacher_id,
            "period": {"start": start_date, "end": end_date},
            "generated_at": datetime.now().isoformat(),
            "data_source": "backend_api"
        }
        
        # Basic statistics
        summary.update(self._calculate_basic_stats(student_data))
        
        # Extract text content for NLP processing
        text_content = self._extract_text_content(student_data)
        
        if include_topics and text_content:
            summary["topics"] = self._analyze_topics(text_content)
        
        if include_sentiment and text_content:
            summary["sentiment"] = self._analyze_sentiment(text_content)
        
        # Extract learning patterns
        summary["learning_patterns"] = self._analyze_learning_patterns(student_data)
        
        # Generate insights
        summary["insights"] = self._generate_insights(student_data, summary)
        
        if include_recommendations:
            summary["recommendations"] = self._generate_recommendations(summary)
        
        return summary
    
    def _fetch_student_data(
        self, 
        teacher_id: str, 
        start_date: str = None, 
        end_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch student data from backend API."""
        try:
            # Fetch student summaries
            url = f"{self.api_base_url}/analytics/teacher/{teacher_id}/student-summaries"
            params = {}
            if start_date:
                params['start'] = start_date
            if end_date:
                params['end'] = end_date
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                summaries_data = response.json()
                
                # Also fetch session data for more detailed analysis
                session_url = f"{self.api_base_url}/analytics/teacher/{teacher_id}/overview"
                session_response = requests.get(session_url, params=params, timeout=30)
                
                session_data = {}
                if session_response.status_code == 200:
                    session_data = session_response.json()
                
                return {
                    "summaries": summaries_data.get('summaries', []),
                    "overview": session_data
                }
            else:
                print(f"Failed to fetch student data: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching student data: {e}")
            return None
    
    def _calculate_basic_stats(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic statistics from student data."""
        summaries = student_data.get('summaries', [])
        overview = student_data.get('overview', {})
        
        stats = {
            "total_students": len(summaries),
            "total_sessions": overview.get('summary', {}).get('totalSessions', 0),
            "completion_rate": overview.get('summary', {}).get('completionRate', 0),
            "avg_session_duration": overview.get('summary', {}).get('avgSessionDuration', 0),
            "total_messages": overview.get('engagement', {}).get('totalMessages', 0)
        }
        
        if stats["total_students"] > 0:
            stats["avg_sessions_per_student"] = stats["total_sessions"] / stats["total_students"]
            stats["avg_messages_per_student"] = stats["total_messages"] / stats["total_students"]
        else:
            stats["avg_sessions_per_student"] = 0
            stats["avg_messages_per_student"] = 0
        
        return stats
    
    def _extract_text_content(self, student_data: Dict[str, Any]) -> List[str]:
        """Extract text content from student data for NLP processing."""
        text_content = []
        
        summaries = student_data.get('summaries', [])
        for summary in summaries:
            # Extract summary text
            if summary.get('summary_text'):
                text_content.append(summary['summary_text'])
            
            # Extract challenges and strengths
            challenges = summary.get('challenges', [])
            strengths = summary.get('strengths', [])
            
            text_content.extend(challenges)
            text_content.extend(strengths)
        
        # Also extract from overview data
        overview = student_data.get('overview', {})
        top_challenges = overview.get('topChallenges', [])
        for challenge in top_challenges:
            if challenge.get('concept'):
                text_content.append(challenge['concept'])
        
        return [text for text in text_content if text and len(text.strip()) > 10]
    
    def _analyze_topics(self, text_content: List[str]) -> Dict[str, Any]:
        """Analyze topics using NLP techniques."""
        if not text_content or not NLP_AVAILABLE:
            return self._basic_topic_analysis(text_content)
        
        try:
            # Use TF-IDF for topic extraction
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            tfidf_matrix = vectorizer.fit_transform(text_content)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top terms
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            top_indices = mean_scores.argsort()[-20:][::-1]
            top_topics = [feature_names[i] for i in top_indices]
            
            # Cluster topics if we have enough content
            topics_by_cluster = []
            if len(text_content) >= 5:
                try:
                    n_clusters = min(5, len(text_content) // 2)
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    clusters = kmeans.fit_predict(tfidf_matrix)
                    
                    for cluster_id in range(n_clusters):
                        cluster_docs = [text_content[i] for i, c in enumerate(clusters) if c == cluster_id]
                        if cluster_docs:
                            cluster_terms = self._extract_cluster_terms(cluster_docs, vectorizer, tfidf_matrix, clusters, cluster_id)
                            topics_by_cluster.append({
                                "cluster_id": cluster_id,
                                "documents": len(cluster_docs),
                                "key_terms": cluster_terms[:5]
                            })
                except Exception as e:
                    print(f"Clustering failed: {e}")
            
            return {
                "method": "tfidf_clustering",
                "top_topics": top_topics[:10],
                "topic_clusters": topics_by_cluster,
                "total_documents": len(text_content)
            }
            
        except Exception as e:
            print(f"Advanced topic analysis failed: {e}")
            return self._basic_topic_analysis(text_content)
    
    def _extract_cluster_terms(self, cluster_docs, vectorizer, tfidf_matrix, clusters, cluster_id):
        """Extract key terms for a specific cluster."""
        cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]
        cluster_tfidf = tfidf_matrix[cluster_indices]
        
        mean_scores = np.mean(cluster_tfidf.toarray(), axis=0)
        feature_names = vectorizer.get_feature_names_out()
        
        top_indices = mean_scores.argsort()[-10:][::-1]
        return [feature_names[i] for i in top_indices]
    
    def _basic_topic_analysis(self, text_content: List[str]) -> Dict[str, Any]:
        """Basic topic analysis using word frequency."""
        if not text_content:
            return {"method": "basic", "top_topics": [], "total_documents": 0}
        
        # Simple word frequency analysis
        all_words = []
        for text in text_content:
            # Basic text cleaning
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            all_words.extend(words)
        
        # Remove common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those'}
        filtered_words = [word for word in all_words if word not in stop_words]
        
        # Get top words
        word_counts = Counter(filtered_words)
        top_topics = [word for word, count in word_counts.most_common(15)]
        
        return {
            "method": "basic_frequency",
            "top_topics": top_topics,
            "total_documents": len(text_content),
            "total_words": len(filtered_words)
        }
    
    def _analyze_sentiment(self, text_content: List[str]) -> Dict[str, Any]:
        """Analyze sentiment of text content."""
        if not text_content:
            return {"method": "none", "overall_sentiment": "neutral"}
        
        if self.claude_available:
            return self._ai_sentiment_analysis(text_content)
        else:
            return self._basic_sentiment_analysis(text_content)
    
    def _ai_sentiment_analysis(self, text_content: List[str]) -> Dict[str, Any]:
        """Use AI for sentiment analysis."""
        try:
            # Sample a subset of content for analysis
            sample_content = text_content[:10] if len(text_content) > 10 else text_content
            combined_text = " ".join(sample_content)
            
            # Call Claude API for sentiment analysis
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Authorization": f"Bearer {self.anthropic_api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 200,
                    "messages": [{
                        "role": "user",
                        "content": f"Analyze the sentiment of this educational content and provide a brief summary. Content: {combined_text[:1000]}"
                    }]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_analysis = result.get('content', [{}])[0].get('text', '')
                
                # Extract sentiment from AI response
                sentiment = "neutral"
                if "positive" in ai_analysis.lower():
                    sentiment = "positive"
                elif "negative" in ai_analysis.lower():
                    sentiment = "negative"
                
                return {
                    "method": "ai_analysis",
                    "overall_sentiment": sentiment,
                    "ai_summary": ai_analysis,
                    "analyzed_documents": len(sample_content)
                }
            else:
                print(f"AI sentiment analysis failed: {response.status_code}")
                return self._basic_sentiment_analysis(text_content)
                
        except Exception as e:
            print(f"AI sentiment analysis error: {e}")
            return self._basic_sentiment_analysis(text_content)
    
    def _basic_sentiment_analysis(self, text_content: List[str]) -> Dict[str, Any]:
        """Basic sentiment analysis using keyword matching."""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'enjoy', 'happy', 'success', 'understand', 'clear', 'helpful', 'easy'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'dislike', 'difficult', 'hard', 'confusing', 'frustrated', 'struggle', 'problem', 'issue', 'error', 'wrong', 'fail'}
        
        positive_count = 0
        negative_count = 0
        
        for text in text_content:
            words = text.lower().split()
            positive_count += sum(1 for word in words if word in positive_words)
            negative_count += sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "method": "keyword_matching",
            "overall_sentiment": sentiment,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "analyzed_documents": len(text_content)
        }
    
    def _analyze_learning_patterns(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning patterns from student data."""
        summaries = student_data.get('summaries', [])
        overview = student_data.get('overview', {})
        
        patterns = {
            "engagement_levels": self._categorize_engagement(summaries, overview),
            "common_challenges": self._extract_common_challenges(summaries),
            "learning_preferences": self._analyze_learning_preferences(summaries),
            "progress_indicators": self._analyze_progress(summaries)
        }
        
        return patterns
    
    def _categorize_engagement(self, summaries: List[Dict], overview: Dict) -> Dict[str, Any]:
        """Categorize student engagement levels."""
        total_students = len(summaries)
        if total_students == 0:
            return {"high": 0, "medium": 0, "low": 0}
        
        avg_sessions = overview.get('summary', {}).get('totalSessions', 0) / total_students if total_students > 0 else 0
        
        high_engagement = 0
        medium_engagement = 0
        low_engagement = 0
        
        for summary in summaries:
            session_count = summary.get('session_count', 0)
            if session_count > avg_sessions * 1.2:
                high_engagement += 1
            elif session_count > avg_sessions * 0.8:
                medium_engagement += 1
            else:
                low_engagement += 1
        
        return {
            "high": high_engagement,
            "medium": medium_engagement,
            "low": low_engagement,
            "high_percentage": (high_engagement / total_students * 100) if total_students > 0 else 0
        }
    
    def _extract_common_challenges(self, summaries: List[Dict]) -> List[Dict[str, Any]]:
        """Extract and rank common challenges."""
        all_challenges = []
        for summary in summaries:
            challenges = summary.get('challenges', [])
            all_challenges.extend(challenges)
        
        challenge_counts = Counter(all_challenges)
        return [
            {"challenge": challenge, "frequency": count}
            for challenge, count in challenge_counts.most_common(10)
        ]
    
    def _analyze_learning_preferences(self, summaries: List[Dict]) -> Dict[str, Any]:
        """Analyze learning preferences from student data."""
        # This is a simplified analysis - in a real system, you'd have more detailed preference data
        preferences = {
            "visual_learners": 0,
            "auditory_learners": 0,
            "kinesthetic_learners": 0,
            "reading_writing_learners": 0
        }
        
        # Basic heuristics based on summary content
        for summary in summaries:
            summary_text = summary.get('summary_text', '').lower()
            if any(word in summary_text for word in ['visual', 'diagram', 'chart', 'graph', 'image']):
                preferences["visual_learners"] += 1
            if any(word in summary_text for word in ['discussion', 'explain', 'talk', 'listen']):
                preferences["auditory_learners"] += 1
            if any(word in summary_text for word in ['practice', 'hands-on', 'activity', 'exercise']):
                preferences["kinesthetic_learners"] += 1
            if any(word in summary_text for word in ['read', 'write', 'text', 'notes']):
                preferences["reading_writing_learners"] += 1
        
        return preferences
    
    def _analyze_progress(self, summaries: List[Dict]) -> Dict[str, Any]:
        """Analyze student progress indicators."""
        total_students = len(summaries)
        if total_students == 0:
            return {"improving": 0, "stable": 0, "declining": 0}
        
        # Simplified progress analysis based on available data
        improving = 0
        stable = 0
        declining = 0
        
        for summary in summaries:
            # Use session count and strengths as progress indicators
            session_count = summary.get('session_count', 0)
            strengths = len(summary.get('strengths', []))
            challenges = len(summary.get('challenges', []))
            
            if session_count > 5 and strengths > challenges:
                improving += 1
            elif session_count > 2 and strengths >= challenges:
                stable += 1
            else:
                declining += 1
        
        return {
            "improving": improving,
            "stable": stable,
            "declining": declining,
            "improvement_rate": (improving / total_students * 100) if total_students > 0 else 0
        }
    
    def _generate_insights(self, student_data: Dict[str, Any], summary: Dict[str, Any]) -> List[str]:
        """Generate insights from the analysis."""
        insights = []
        
        # Engagement insights
        engagement = summary.get("learning_patterns", {}).get("engagement_levels", {})
        high_engagement_pct = engagement.get("high_percentage", 0)
        
        if high_engagement_pct > 70:
            insights.append("Excellent student engagement - most students are highly active")
        elif high_engagement_pct > 40:
            insights.append("Good student engagement with room for improvement")
        else:
            insights.append("Low student engagement - consider strategies to increase participation")
        
        # Completion rate insights
        completion_rate = summary.get("completion_rate", 0)
        if completion_rate > 80:
            insights.append("High session completion rate indicates good content pacing")
        elif completion_rate < 60:
            insights.append("Low completion rate suggests content may be too challenging or lengthy")
        
        # Challenge insights
        common_challenges = summary.get("learning_patterns", {}).get("common_challenges", [])
        if common_challenges:
            top_challenge = common_challenges[0]["challenge"]
            insights.append(f"Most common challenge: '{top_challenge}' - consider targeted interventions")
        
        # Sentiment insights
        sentiment = summary.get("sentiment", {}).get("overall_sentiment", "neutral")
        if sentiment == "positive":
            insights.append("Positive student sentiment indicates good learning experience")
        elif sentiment == "negative":
            insights.append("Negative sentiment detected - may need to address student concerns")
        
        return insights
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Based on engagement
        engagement = summary.get("learning_patterns", {}).get("engagement_levels", {})
        if engagement.get("low", 0) > engagement.get("high", 0):
            recommendations.append("Implement more interactive activities to boost engagement")
        
        # Based on completion rate
        completion_rate = summary.get("completion_rate", 0)
        if completion_rate < 70:
            recommendations.append("Consider breaking sessions into shorter segments")
        
        # Based on common challenges
        common_challenges = summary.get("learning_patterns", {}).get("common_challenges", [])
        if common_challenges:
            recommendations.append(f"Create additional resources for '{common_challenges[0]['challenge']}'")
        
        # Based on progress
        progress = summary.get("learning_patterns", {}).get("progress_indicators", {})
        declining = progress.get("declining", 0)
        total = progress.get("improving", 0) + progress.get("stable", 0) + declining
        
        if total > 0 and declining / total > 0.3:
            recommendations.append("Provide additional support for struggling students")
        
        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "Continue monitoring student progress regularly",
                "Maintain current successful teaching strategies",
                "Consider periodic student feedback collection"
            ])
        
        return recommendations
    
    def _generate_default_summary(self, teacher_id: str) -> Dict[str, Any]:
        """Generate default summary when no data is available."""
        return {
            "teacher_id": teacher_id,
            "generated_at": datetime.now().isoformat(),
            "data_source": "default",
            "error": "No student data available",
            "total_students": 0,
            "total_sessions": 0,
            "insights": ["No data available for analysis"],
            "recommendations": ["Ensure students are actively using the system"]
        }

def main():
    """Main function for testing the NLP summary generator."""
    generator = NLPSummaryGenerator()
    
    # Test summary generation
    summary = generator.generate_class_summary(
        teacher_id="teacher_123",
        include_sentiment=True,
        include_topics=True,
        include_recommendations=True
    )
    
    print("Generated Class Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
