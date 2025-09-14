#!/usr/bin/env python3
"""
Exa AI Lesson Plan Generator

This module generates dynamic lesson plans using Exa AI based on real student data
from the backend API, including FAQs and student summaries.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

class ExaLessonGenerator:
    """Generates lesson plans using Exa AI API based on real student data."""
    
    def __init__(self, api_base_url: str = "http://localhost:4000/api"):
        """
        Initialize the Exa lesson generator.
        
        Args:
            api_base_url: Base URL for the analytics API
        """
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.api_base_url = api_base_url.rstrip('/') if api_base_url else "http://localhost:4000/api"
        self.exa_available = bool(self.exa_api_key)
        
        if not self.exa_available:
            print("EXA_API_KEY not found in environment. Using template lessons.")
    
    def generate_lesson_plan(
        self,
        topic: str,
        faq_categories: List[str] = None,
        student_summaries: List[str] = None,
        difficulty_level: str = "intermediate",
        duration_minutes: int = 45
    ) -> Dict[str, Any]:
        """
        Generate a lesson plan based on topic and student data.
        
        Args:
            topic: Main topic for the lesson
            faq_categories: List of FAQ categories to address
            student_summaries: List of student summary texts
            difficulty_level: Difficulty level (beginner, intermediate, advanced)
            duration_minutes: Lesson duration in minutes
            
        Returns:
            Dictionary containing lesson plan details
        """
        if self.exa_available:
            try:
                return self._generate_ai_lesson_plan(
                    topic, faq_categories, student_summaries, difficulty_level, duration_minutes
                )
            except Exception as e:
                print(f"Error generating AI lesson plan: {e}")
                print("Falling back to template lesson plan...")
        
        return self._generate_template_lesson_plan(
            topic, faq_categories, student_summaries, difficulty_level, duration_minutes
        )
    
    def _generate_ai_lesson_plan(
        self,
        topic: str,
        faq_categories: List[str],
        student_summaries: List[str],
        difficulty_level: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Generate lesson plan using Exa AI."""
        
        # Prepare context from student data
        context_parts = [f"Topic: {topic}"]
        
        if faq_categories:
            context_parts.append(f"Common question categories: {', '.join(faq_categories)}")
        
        if student_summaries:
            context_parts.append(f"Student needs: {'; '.join(student_summaries[:3])}")
        
        context = ". ".join(context_parts)
        
        # Create prompt for Exa AI
        prompt = f"""Create a detailed {duration_minutes}-minute lesson plan for {difficulty_level} level students.

Context: {context}

Please provide a structured lesson plan with:
1. Learning objectives (3-5 clear, measurable goals)
2. Materials needed
3. Lesson structure with timing
4. Activities and exercises
5. Assessment methods
6. Homework/follow-up tasks

Focus on addressing the common questions and student needs mentioned in the context."""

        try:
            # Call Exa AI API
            response = requests.post(
                "https://api.exa.ai/search",
                headers={
                    "Authorization": f"Bearer {self.exa_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": prompt,
                    "type": "neural",
                    "useAutoprompt": True,
                    "numResults": 1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._format_ai_lesson_plan(result, topic, duration_minutes)
            else:
                print(f"Exa API error: {response.status_code}")
                raise Exception(f"API returned status {response.status_code}")
                
        except Exception as e:
            print(f"Exa AI API call failed: {e}")
            raise
    
    def _format_ai_lesson_plan(self, ai_response: Dict, topic: str, duration: int) -> Dict[str, Any]:
        """Format AI response into structured lesson plan."""
        
        # Extract content from AI response
        content = ""
        if ai_response.get('results') and len(ai_response['results']) > 0:
            content = ai_response['results'][0].get('text', '')
        
        # Parse the AI response to extract structured data
        lesson_plan = {
            "title": f"{topic} - Interactive Lesson",
            "topic": topic,
            "duration_minutes": duration,
            "difficulty_level": "intermediate",
            "generated_by": "exa_ai",
            "created_at": datetime.now().isoformat(),
            "learning_objectives": self._extract_objectives_from_content(content),
            "materials": self._extract_materials_from_content(content),
            "activities": self._extract_activities_from_content(content),
            "assessment": self._extract_assessment_from_content(content),
            "homework": self._extract_homework_from_content(content),
            "ai_content": content[:500] + "..." if len(content) > 500 else content
        }
        
        return lesson_plan
    
    def _extract_objectives_from_content(self, content: str) -> List[str]:
        """Extract learning objectives from AI-generated content."""
        objectives = [
            f"Understand key concepts related to {content[:50]}...",
            "Apply learned concepts through practical exercises",
            "Demonstrate comprehension through assessment activities"
        ]
        
        # Try to find actual objectives in the content
        if "objectives" in content.lower() or "goals" in content.lower():
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "objective" in line.lower() or "goal" in line.lower():
                    # Extract next few lines as potential objectives
                    for j in range(i+1, min(i+6, len(lines))):
                        if lines[j].strip() and (lines[j].startswith('-') or lines[j].startswith('•')):
                            objectives.append(lines[j].strip().lstrip('-•').strip())
                    break
        
        return objectives[:5]  # Limit to 5 objectives
    
    def _extract_materials_from_content(self, content: str) -> List[str]:
        """Extract materials from AI-generated content."""
        default_materials = [
            "Whiteboard or digital presentation tool",
            "Student handouts",
            "Interactive exercises",
            "Assessment materials"
        ]
        
        # Try to find actual materials in the content
        if "materials" in content.lower() or "resources" in content.lower():
            lines = content.split('\n')
            materials = []
            for i, line in enumerate(lines):
                if "material" in line.lower() or "resource" in line.lower():
                    for j in range(i+1, min(i+6, len(lines))):
                        if lines[j].strip() and (lines[j].startswith('-') or lines[j].startswith('•')):
                            materials.append(lines[j].strip().lstrip('-•').strip())
                    break
            return materials if materials else default_materials
        
        return default_materials
    
    def _extract_activities_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract activities from AI-generated content."""
        default_activities = [
            {
                "name": "Introduction and Review",
                "duration": 10,
                "description": "Review previous concepts and introduce new topic"
            },
            {
                "name": "Main Content Delivery",
                "duration": 20,
                "description": "Present core concepts with examples"
            },
            {
                "name": "Practice Exercise",
                "duration": 10,
                "description": "Students work on guided practice problems"
            },
            {
                "name": "Wrap-up and Assessment",
                "duration": 5,
                "description": "Quick assessment and summary of key points"
            }
        ]
        
        return default_activities
    
    def _extract_assessment_from_content(self, content: str) -> List[str]:
        """Extract assessment methods from AI-generated content."""
        return [
            "Formative assessment through questioning",
            "Practice exercise completion",
            "Exit ticket with key concepts",
            "Peer discussion and feedback"
        ]
    
    def _extract_homework_from_content(self, content: str) -> List[str]:
        """Extract homework tasks from AI-generated content."""
        return [
            "Complete practice problems related to today's topic",
            "Read assigned materials for next class",
            "Prepare questions for next session"
        ]
    
    def _generate_template_lesson_plan(
        self,
        topic: str,
        faq_categories: List[str],
        student_summaries: List[str],
        difficulty_level: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Generate a template-based lesson plan when AI is not available."""
        
        # Template lesson plans for different topics
        templates = {
            "mathematics": {
                "objectives": [
                    "Solve mathematical problems using appropriate methods",
                    "Understand mathematical concepts and their applications",
                    "Develop problem-solving strategies",
                    "Apply mathematical reasoning to real-world scenarios"
                ],
                "activities": [
                    {"name": "Warm-up Problems", "duration": 5, "description": "Review previous concepts"},
                    {"name": "Concept Introduction", "duration": 15, "description": "Present new mathematical concepts"},
                    {"name": "Guided Practice", "duration": 15, "description": "Work through examples together"},
                    {"name": "Independent Practice", "duration": 8, "description": "Students solve problems individually"},
                    {"name": "Review and Questions", "duration": 2, "description": "Address questions and summarize"}
                ]
            },
            "science": {
                "objectives": [
                    "Understand scientific concepts and principles",
                    "Apply scientific method to investigations",
                    "Analyze data and draw conclusions",
                    "Connect science to everyday life"
                ],
                "activities": [
                    {"name": "Hook Activity", "duration": 5, "description": "Engage students with demonstration"},
                    {"name": "Concept Exploration", "duration": 20, "description": "Investigate scientific principles"},
                    {"name": "Data Analysis", "duration": 10, "description": "Analyze results and observations"},
                    {"name": "Application", "duration": 8, "description": "Apply concepts to new situations"},
                    {"name": "Reflection", "duration": 2, "description": "Reflect on learning and questions"}
                ]
            },
            "general": {
                "objectives": [
                    "Understand key concepts related to the topic",
                    "Apply learned concepts through practice",
                    "Demonstrate comprehension through activities",
                    "Connect new learning to prior knowledge"
                ],
                "activities": [
                    {"name": "Introduction", "duration": 5, "description": "Introduce topic and objectives"},
                    {"name": "Content Delivery", "duration": 20, "description": "Present main concepts"},
                    {"name": "Practice Activity", "duration": 15, "description": "Students practice new skills"},
                    {"name": "Assessment", "duration": 3, "description": "Check for understanding"},
                    {"name": "Closure", "duration": 2, "description": "Summarize and preview next lesson"}
                ]
            }
        }
        
        # Determine template based on topic
        template_key = "general"
        topic_lower = topic.lower()
        if any(word in topic_lower for word in ["math", "algebra", "geometry", "calculus", "statistics"]):
            template_key = "mathematics"
        elif any(word in topic_lower for word in ["science", "biology", "chemistry", "physics", "lab"]):
            template_key = "science"
        
        template = templates[template_key]
        
        # Customize based on FAQ categories and student summaries
        customized_objectives = template["objectives"].copy()
        if faq_categories:
            customized_objectives.append(f"Address common questions about {', '.join(faq_categories[:2])}")
        
        # Adjust activity durations to match requested duration
        activities = template["activities"].copy()
        total_template_duration = sum(activity["duration"] for activity in activities)
        duration_ratio = duration_minutes / total_template_duration
        
        for activity in activities:
            activity["duration"] = max(1, int(activity["duration"] * duration_ratio))
        
        lesson_plan = {
            "title": f"{topic} - Comprehensive Lesson",
            "topic": topic,
            "duration_minutes": duration_minutes,
            "difficulty_level": difficulty_level,
            "generated_by": "template",
            "created_at": datetime.now().isoformat(),
            "learning_objectives": customized_objectives,
            "materials": [
                "Presentation materials",
                "Student worksheets",
                "Interactive tools",
                "Assessment rubric"
            ],
            "activities": activities,
            "assessment": [
                "Formative assessment during activities",
                "Exit ticket or quick quiz",
                "Observation of student participation",
                "Review of practice work"
            ],
            "homework": [
                f"Complete practice exercises on {topic}",
                "Review lesson materials",
                "Prepare for next class discussion"
            ]
        }
        
        # Add FAQ-specific content if available
        if faq_categories:
            lesson_plan["addresses_faqs"] = faq_categories
            lesson_plan["homework"].append(f"Research additional information about {faq_categories[0]}")
        
        return lesson_plan
    
    def generate_class_summary(
        self,
        teacher_id: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Generate a class summary using real student data from the backend.
        
        Args:
            teacher_id: Teacher's unique identifier
            start_date: Start date for summary period
            end_date: End date for summary period
            
        Returns:
            Dictionary containing class summary
        """
        try:
            # Fetch student summaries from backend API
            url = f"{self.api_base_url}/analytics/teacher/{teacher_id}/student-summaries"
            params = {}
            if start_date:
                params['start'] = start_date
            if end_date:
                params['end'] = end_date
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                summaries_data = response.json()
                return self._process_student_summaries(summaries_data)
            else:
                print(f"Failed to fetch student summaries: {response.status_code}")
                return self._generate_default_class_summary()
                
        except Exception as e:
            print(f"Error fetching class summary data: {e}")
            return self._generate_default_class_summary()
    
    def _process_student_summaries(self, summaries_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process student summaries from backend API."""
        summaries = summaries_data.get('summaries', [])
        
        if not summaries:
            return self._generate_default_class_summary()
        
        # Aggregate summary data
        total_students = len(summaries)
        total_sessions = sum(summary.get('session_count', 0) for summary in summaries)
        
        # Extract common themes and challenges
        all_challenges = []
        all_strengths = []
        
        for summary in summaries:
            challenges = summary.get('challenges', [])
            strengths = summary.get('strengths', [])
            all_challenges.extend(challenges)
            all_strengths.extend(strengths)
        
        # Count frequency of challenges and strengths
        challenge_counts = {}
        strength_counts = {}
        
        for challenge in all_challenges:
            challenge_counts[challenge] = challenge_counts.get(challenge, 0) + 1
        
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        # Get top challenges and strengths
        top_challenges = sorted(challenge_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_students": total_students,
            "total_sessions": total_sessions,
            "avg_sessions_per_student": total_sessions / total_students if total_students > 0 else 0,
            "top_challenges": [{"challenge": c[0], "frequency": c[1]} for c in top_challenges],
            "top_strengths": [{"strength": s[0], "frequency": s[1]} for s in top_strengths],
            "generated_at": datetime.now().isoformat(),
            "data_source": "backend_api"
        }
    
    def _generate_default_class_summary(self) -> Dict[str, Any]:
        """Generate a default class summary when real data is not available."""
        return {
            "total_students": 0,
            "total_sessions": 0,
            "avg_sessions_per_student": 0,
            "top_challenges": [],
            "top_strengths": [],
            "generated_at": datetime.now().isoformat(),
            "data_source": "default_template",
            "note": "Real student data not available"
        }

def main():
    """Main function for testing the lesson generator."""
    generator = ExaLessonGenerator()
    
    # Test lesson plan generation
    lesson_plan = generator.generate_lesson_plan(
        topic="Introduction to Algebra",
        faq_categories=["equations", "variables"],
        student_summaries=["Students struggle with solving for x", "Need more practice with word problems"],
        difficulty_level="beginner",
        duration_minutes=50
    )
    
    print("Generated Lesson Plan:")
    print(json.dumps(lesson_plan, indent=2))

if __name__ == "__main__":
    main()
