#!/usr/bin/env python3
"""
Standalone Analytics Agent for Educational Data Analysis
Generates comprehensive teacher overview reports with actionable insights.
"""

import argparse
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from mock_data_generator import MockDataGenerator
from analytical_agent import AnalyticalAgent

# Load environment variables from .env file
load_dotenv()

class StandaloneAnalytics:
    """Terminal-based analytics that works without external dependencies"""
    
    def __init__(self, use_mock_data: bool = True):
        self.use_mock_data = use_mock_data
        self.mock_generator = MockDataGenerator()
        self.agent = AnalyticalAgent() if not use_mock_data else None
    
    def get_teacher_overview(self, teacher_id: str, start_date: str, end_date: str) -> dict:
        """Get teacher overview data"""
        if self.use_mock_data:
            return self.mock_generator.generate_complete_overview(teacher_id, start_date, end_date)
        else:
            # This would call the real API when available
            return self.agent.fetch_teacher_overview(teacher_id, start_date, end_date)
    
    def get_hourly_distribution(self, teacher_id: str, start_date: str, end_date: str) -> dict:
        """Get hourly message distribution"""
        if self.use_mock_data:
            return self.mock_generator.generate_hourly_data(teacher_id, start_date, end_date)
        else:
            return self.agent.fetch_hourly_distribution(teacher_id, start_date, end_date)
    
    def get_faqs_data(self, teacher_id: str, start_date: str, end_date: str, limit: int = 10) -> dict:
        """Get FAQs data from schema"""
        if self.use_mock_data:
            return self.mock_generator.generate_faqs_data(teacher_id, start_date, end_date, limit)
        else:
            return self.agent.fetch_faqs_data(teacher_id, start_date, end_date, limit)
    
    def get_sessions_per_student(self, teacher_id: str, start_date: str, end_date: str) -> list:
        """Get sessions per student data"""
        if self.use_mock_data:
            return self.mock_generator.generate_sessions_per_student(teacher_id, start_date, end_date)
        else:
            return self.agent.fetch_sessions_per_student(teacher_id, start_date, end_date)
    
    def generate_insights(self, overview_data: dict) -> dict:
        """Generate insights from overview data"""
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
    
    def generate_markdown_report(self, teacher_id: str, start_date: str, end_date: str) -> str:
        """Generate complete markdown report"""
        
        # Fetch all data
        overview_data = self.get_teacher_overview(teacher_id, start_date, end_date)
        hourly_data = self.get_hourly_distribution(teacher_id, start_date, end_date)
        faqs_data = self.get_faqs_data(teacher_id, start_date, end_date)
        insights = self.generate_insights(overview_data)
        
        # Extract data for report
        cohort_info = overview_data.get('cohortInfo', {})
        engagement = overview_data.get('engagementMetrics', {})
        session_metrics = overview_data.get('sessionMetrics', {})
        student_activity = overview_data.get('studentActivity', [])
        faqs = faqs_data.get('topFaqs', [])
        
        total_students = cohort_info.get('totalStudents', 0)
        active_students = len([s for s in student_activity if s.get('sessionCount', 0) > 0])
        
        # Find peak activity hour
        peak_hour = "N/A"
        if hourly_data and 'summary' in hourly_data:
            peak_info = hourly_data['summary'].get('peakHour', {})
            if peak_info:
                peak_hour = f"{peak_info.get('hour', 'N/A')}:00"
        
        # Top FAQs
        top_faqs = faqs_data.get('topFaqs', [])[:5]
        
        report = f"""# Teacher Overview Report
**Teacher ID:** {teacher_id}  
**Period:** {start_date} to {end_date}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Executive Summary

- **Total Students:** {total_students}
- **Active Students:** {active_students} ({(active_students/total_students*100) if total_students > 0 else 0:.1f}%)
- **Total Sessions:** {session_metrics.get('totalSessions', 0)}
- **Completion Rate:** {session_metrics.get('completionRate', 0):.1f}%
- **Avg Session Duration:** {session_metrics.get('avgDurationMinutes', 0):.1f} minutes

---

## 🎯 Engagement Analysis

### Message Activity
- **Avg Messages per Student:** {engagement.get('avgMessagesPerStudent', 0):.1f}
- **Avg Messages per Class:** {engagement.get('avgMessagesPerClass', 0):.1f}
- **Daily Session Average:** {engagement.get('avgSessionsPerDay', 0):.1f}

### Peak Activity
- **Most Active Hour:** {peak_hour}
- **Total Messages:** {hourly_data.get('summary', {}).get('totalMessages', 0) if hourly_data else 0}

---

## 📈 Key Insights

"""

        # Add insights
        for insight_type, insight_text in insights.items():
            report += f"### {insight_type.replace('_', ' ').title()}\n{insight_text}\n\n"

        report += """---

## 👥 Student Activity Overview

"""

        # Generate most active students section
        sessions_data = self.get_sessions_per_student(teacher_id, start_date, end_date)
        report += "### Most Active Students\n"
        for i, student_data in enumerate(sessions_data[:5], 1):
            student_id = student_data['studentId']
            session_count = student_data['sessionCount']
            report += f"{i}. **{student_id}** - {session_count} sessions\n"
        if faqs:
            report += "### Top Learning Challenges\n"
            for faq in faqs[:3]:
                category = faq.get('category', 'Unknown')
                frequency = faq.get('frequencyCount', 0)
                report += f"- **{category}** ({frequency} questions)\n"
            report += "\n"

        # Add FAQs
        if top_faqs:
            report += "---\n\n## ❓ Frequently Asked Questions\n\n"
            for i, faq in enumerate(top_faqs, 1):
                question = faq.get('questionText', 'Unknown question')
                category = faq.get('category', 'General')
                frequency = faq.get('frequencyCount', 0)
                success_rate = faq.get('successRate')
                
                report += f"{i}. **{question}**\n"
                report += f"   - Category: {category}\n"
                report += f"   - Asked {frequency} times\n"
                if success_rate is not None:
                    report += f"   - Success Rate: {success_rate}%\n"
                report += "\n"

        # Add student summaries section
        from mock_data_generator import MockDataGenerator
        mock_gen = MockDataGenerator()
        student_summaries = mock_gen.generate_student_summaries(teacher_id)
        
        report += """---

## 📝 Student Learning Summary

"""
        report += f"{student_summaries}\n\n"
        
        # Add data-driven recommendations
        report += """---

## 💡 Recommendations

"""

        # Generate smart recommendations based on actual data
        recommendations = []
        
        completion_rate = session_metrics.get('completionRate', 0)
        if completion_rate < 70:
            recommendations.append("**Improve Session Completion:** Consider shorter, more focused sessions or check for technical issues causing dropouts.")
        elif completion_rate > 90:
            recommendations.append("**Excellent Completion Rate:** Maintain current session structure and engagement strategies.")
        
        avg_messages = engagement.get('avgMessagesPerStudent', 0)
        if avg_messages < 15:
            recommendations.append("**Increase Engagement:** Encourage more student questions and interactive elements in tutoring sessions.")
        elif avg_messages > 40:
            recommendations.append("**High Engagement:** Consider if students need more guided practice vs. Q&A time.")
        
        if active_students < total_students * 0.7:
            recommendations.append("**Boost Participation:** Reach out to inactive students and provide additional support or motivation.")
        
        # Smart FAQ-based recommendations
        if faqs:
            top_faq = faqs[0]
            category = top_faq.get('category', '').replace('_', ' ')
            frequency = top_faq.get('frequencyCount', 0)
            success_rate = top_faq.get('successRate')
            
            if frequency > 15:
                recommendations.append(f"**Address High-Frequency Questions:** {frequency} questions about {category} suggest this needs focused attention.")
            
            if success_rate and success_rate < 70:
                recommendations.append(f"**Improve Success Rate:** {category} has {success_rate}% success rate - consider alternative teaching approaches.")
        
        if not recommendations:
            recommendations.append("**Maintain Excellence:** Current metrics show good student engagement and learning progress.")
        
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"

        # Generate detailed lesson plans for top FAQ categories
        report += """
----

## 📚 Suggested Lesson Plans

Based on your students' most frequently asked questions, here are detailed lesson plans to address key learning areas:

"""

        # Try to generate AI lesson plans using Exa directly
        from exa_lesson_generator import ExaLessonGenerator
        exa_generator = ExaLessonGenerator()
        
        if exa_generator.client and faqs:
            # Use Exa AI to generate lesson plans
            report += f"""
## 🤖 AI-Generated Lesson Plans

*The following lesson plans were generated using Exa AI based on your students' frequently asked questions and learning patterns:*

"""
            for i, faq in enumerate(faqs[:2], 1):
                category = faq.get('category', '')
                frequency = faq.get('frequency', 0)
                
                # Get student summaries for context
                from mock_data_generator import MockDataGenerator
                mock_gen = MockDataGenerator()
                student_summaries = mock_gen.generate_student_summaries(teacher_id)
                
                try:
                    lesson_plan = exa_generator.generate_targeted_lesson(
                        category, frequency, 0.75, student_summaries
                    )
                    report += f"""### Lesson Plan {i}: {category.replace('_', ' ').title()}

**Target:** Address {frequency} student questions in this area

{lesson_plan}

---

"""
                except Exception as e:
                    print(f"Error generating lesson plan for {category}: {e}")
                    # Fallback to template lesson
                    from mock_data_generator import MockDataGenerator
                    mock_gen = MockDataGenerator()
                    
                    for i, faq in enumerate(faqs[:2], 1):
                        category = faq.get('category', '')
                        frequency = faq.get('frequency', 0)
                        
                        template_plans = mock_gen.generate_lesson_plans(teacher_id, start_date, end_date)
                        matching_plan = next((p for p in template_plans if p.get('targetMisconception') == category), template_plans[0] if template_plans else {})
                        
                        report += f"""### Lesson Plan {i}: {category.replace('_', ' ').title()}

**Target:** Address {frequency} student questions in this area

**Objective:** {matching_plan.get('objective', f'Help students master {category.replace("_", " ")} concepts')}

**Duration:** {matching_plan.get('duration', '45-50 minutes')}

**Materials:** {', '.join(matching_plan.get('materials', ['Whiteboard', 'Practice worksheets', 'Calculator']))}

**Activities:**
{chr(10).join([f"- {activity}" for activity in matching_plan.get('activities', [f'Review {category.replace("_", " ")} fundamentals', 'Guided practice problems', 'Independent work time'])])}

**Assessment:** {matching_plan.get('assessment', 'Exit ticket with 2-3 practice problems')}

---

"""
        else:
            # Fallback to template lesson plans when no AI available
            from mock_data_generator import MockDataGenerator
            mock_gen = MockDataGenerator()
            
            for i, faq in enumerate(faqs[:2], 1):
                category = faq.get('category', '')
                frequency = faq.get('frequency', 0)
                
                template_plans = mock_gen.generate_lesson_plans(teacher_id, start_date, end_date)
                matching_plan = next((p for p in template_plans if p.get('targetMisconception') == category), template_plans[0] if template_plans else {})
                
                report += f"""### Lesson Plan {i}: {category.replace('_', ' ').title()}

**Target:** Address {frequency} student questions in this area

**Objective:** {matching_plan.get('objective', f'Help students master {category.replace("_", " ")} concepts')}

**Duration:** {matching_plan.get('duration', '45-50 minutes')}

**Materials:** {', '.join(matching_plan.get('materials', ['Whiteboard', 'Practice worksheets', 'Calculator']))}

**Activities:**
{chr(10).join([f"- {activity}" for activity in matching_plan.get('activities', [f'Review {category.replace("_", " ")} fundamentals', 'Guided practice problems', 'Independent work time'])])}

**Assessment:** {matching_plan.get('assessment', 'Exit ticket with 2-3 practice problems')}

---

"""

        # Implementation Timeline section
        report += """
## 📋 Implementation Timeline

"""
        
        # Generate implementation timeline
        if faqs:
            report += f"""**Week 1:** Focus on {faqs[0].get('category', 'top FAQ category').replace('_', ' ')} 
- Implement the lesson plan above
- Monitor student progress through targeted questions
- Adjust pacing based on student responses

**Week 2:** Address {faqs[1].get('category', 'second FAQ category').replace('_', ' ') if len(faqs) > 1 else 'reinforcement'}
- Build on previous week's concepts
- Provide additional practice opportunities
- Assess improvement through formative evaluation

**Ongoing:** 
- Continue monitoring FAQ patterns for emerging learning challenges
- Adapt lesson plans based on real-time student feedback
- Schedule individual check-ins with students showing persistent difficulties

"""
        else:
            report += """**Week 1:** Focus on key concepts 
- Implement targeted lesson plans
- Monitor student progress through targeted questions
- Adjust pacing based on student responses

**Week 2:** Address reinforcement activities
- Build on previous week's concepts
- Provide additional practice opportunities
- Assess improvement through formative evaluation

**Ongoing:** 
- Continue monitoring FAQ patterns for emerging learning challenges
- Adapt lesson plans based on real-time student feedback
- Schedule individual check-ins with students showing persistent difficulties

"""

        report += """---

*Report generated by Standalone Analytics Agent*
"""

        return report

def main():
    parser = argparse.ArgumentParser(description='Generate teacher analytics reports')
    parser.add_argument('--teacher-id', required=True, help='Teacher ID to analyze')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD), defaults to 7 days ago')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--output', help='Output file path (optional)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='Output format')
    parser.add_argument('--real-data', action='store_true', help='Use real API data instead of mock data')
    
    args = parser.parse_args()
    
    # Set default dates
    if not args.start_date or not args.end_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        args.start_date = args.start_date or start_date.strftime('%Y-%m-%d')
        args.end_date = args.end_date or end_date.strftime('%Y-%m-%d')
    
    # Create analytics instance
    analytics = StandaloneAnalytics(use_mock_data=not args.real_data)
    
    if args.format == 'markdown':
        # Generate markdown report
        report = analytics.generate_markdown_report(args.teacher_id, args.start_date, args.end_date)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)
    
    elif args.format == 'json':
        # Generate JSON data
        overview_data = analytics.get_teacher_overview(args.teacher_id, args.start_date, args.end_date)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(overview_data, f, indent=2)
            print(f"Data saved to {args.output}")
        else:
            print(json.dumps(overview_data, indent=2))

if __name__ == "__main__":
    main()
