#!/usr/bin/env python3
"""
Teacher Overview Report Generator

This module generates comprehensive teacher overview reports using real backend data
from the analytics API endpoints. It creates detailed markdown reports with insights,
recommendations, and lesson plans.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from analytical_agent import AnalyticalAgent
import json

class TeacherOverviewBuilder:
    """Builds comprehensive teacher overview reports using backend analytics data."""
    
    def __init__(self, api_base_url: str = "http://localhost:4000/api"):
        """
        Initialize the teacher overview builder.
        
        Args:
            api_base_url: Base URL for the analytics API
        """
        self.agent = AnalyticalAgent(api_base_url)
        self.api_base_url = api_base_url
    
    def generate_overview_report(
        self, 
        teacher_id: str, 
        start_date: str = None, 
        end_date: str = None,
        output_file: str = None
    ) -> str:
        """
        Generate a comprehensive teacher overview report.
        
        Args:
            teacher_id: The teacher's unique identifier
            start_date: Start date in ISO format (YYYY-MM-DD), defaults to last 30 days
            end_date: End date in ISO format (YYYY-MM-DD), defaults to today
            output_file: Optional file path to save the report
            
        Returns:
            Generated markdown report as string
        """
        # Set default date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self.agent.get_date_range_last_month()
        
        print(f"Generating focused analytics report for {teacher_id}")
        print(f"Date range: {start_date} to {end_date}")
        
        # Fetch analytics data
        faqs_data = self.agent.fetch_faqs(teacher_id, start_date, end_date)
        topics_data = self.agent.fetch_topic_performance(teacher_id, start_date, end_date)
        summary_data = self.agent.fetch_analytics_summary(teacher_id, start_date, end_date)
        
        if not faqs_data:
            return self._generate_error_report(teacher_id, "Failed to fetch analytics data")
        
        # Generate focused report
        report = self._build_focused_report(
            teacher_id, start_date, end_date, faqs_data, topics_data, summary_data
        )
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"Report saved to {output_file}")
            except Exception as e:
                print(f"Error saving report to file: {e}")
        
        return report
    
    def _build_focused_report(
        self,
        teacher_id: str,
        start_date: str,
        end_date: str,
        faqs_data: Dict[str, Any],
        topics_data: Dict[str, Any],
        summary_data: Dict[str, Any]
    ) -> str:
        """
        Build a focused markdown report with only the 3 core metrics.
        """
        report_lines = [
            "# Teacher Analytics Report",
            "",
            f"**Teacher ID:** {teacher_id}",
            f"**Report Period:** {start_date} to {end_date}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]
        
        # 1. Most Frequently Asked Questions
        if faqs_data and faqs_data.get('topFaqs'):
            report_lines.extend([
                "## ❓ Most Frequently Asked Questions",
                ""
            ])
            
            for i, faq in enumerate(faqs_data['topFaqs'][:10], 1):
                question = faq.get('question', 'Unknown question')
                category = faq.get('category', 'General')
                frequency = faq.get('frequency', 0)
                success_rate = faq.get('successRate', 0)
                
                report_lines.extend([
                    f"### {i}. {question}",
                    f"- **Category:** {category}",
                    f"- **Asked {frequency} times**",
                    f"- **Success Rate:** {success_rate}%",
                    ""
                ])
        else:
            report_lines.extend([
                "## ❓ Most Frequently Asked Questions",
                "",
                "No FAQ data available for this period.",
                ""
            ])
        
        # 2. Topics Students Are Most Successful At
        if topics_data and topics_data.get('successfulTopics'):
            report_lines.extend([
                "## ✅ Topics Students Excel At",
                "",
                "| Topic | Success Rate | Students | Average Score |",
                "|-------|-------------|----------|---------------|"
            ])
            
            for topic in topics_data['successfulTopics'][:10]:
                topic_name = topic.get('topic', 'Unknown')
                success_rate = topic.get('successRate', 0)
                student_count = topic.get('studentCount', 0)
                avg_score = topic.get('averageScore', 0)
                
                report_lines.append(f"| {topic_name} | {success_rate:.1f}% | {student_count} | {avg_score}% |")
            
            report_lines.append("")
        else:
            report_lines.extend([
                "## ✅ Topics Students Excel At",
                "",
                "No successful topic data available for this period.",
                ""
            ])
        
        # 3. Topics Students Struggle With
        if topics_data and topics_data.get('strugglingTopics'):
            report_lines.extend([
                "## ⚠️ Topics Students Struggle With",
                "",
                "| Topic | Students Affected | Common Issues |",
                "|-------|------------------|---------------|"
            ])
            
            for topic in topics_data['strugglingTopics'][:10]:
                topic_name = topic.get('topic', 'Unknown')
                student_count = topic.get('studentCount', 0)
                issues = topic.get('commonIssues', [])
                issues_text = ', '.join(issues[:3]) if issues else 'General difficulty'
                
                report_lines.append(f"| {topic_name} | {student_count} | {issues_text} |")
            
            report_lines.append("")
        else:
            report_lines.extend([
                "## ⚠️ Topics Students Struggle With",
                "",
                "No struggling topic data available for this period.",
                ""
            ])
        
        # 4. Analytics Summary
        if summary_data and summary_data.get('summary'):
            report_lines.extend([
                "## 📊 Analytics Summary",
                "",
                summary_data['summary'],
                ""
            ])
            
            # Key Insights
            if summary_data.get('keyInsights'):
                report_lines.extend([
                    "### 🔍 Key Insights",
                    ""
                ])
                for insight in summary_data['keyInsights']:
                    report_lines.append(f"- {insight}")
                report_lines.append("")
            
            # Recommendations
            if summary_data.get('recommendations'):
                report_lines.extend([
                    "### 💡 Recommendations",
                    ""
                ])
                for recommendation in summary_data['recommendations']:
                    report_lines.append(f"- {recommendation}")
                report_lines.append("")
        else:
            report_lines.extend([
                "## 📊 Analytics Summary",
                "",
                "No analytics summary available for this period.",
                ""
            ])
        
        # Footer
        report_lines.extend([
            "---",
            "",
            f"*Report generated by Teacher Analytics System on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*"
        ])
        
        return '\n'.join(report_lines)
    
    def _generate_lesson_plans_from_faqs(self, faqs: list) -> list:
        """Generate lesson plans based on FAQ data."""
        lesson_plans = []
        
        for faq in faqs:
            try:
                # Extract FAQ information
                question_text = faq.get('questionText', '')
                category = faq.get('category', 'General')
                frequency = faq.get('frequencyCount', 0)
                
                # Generate lesson plan for this FAQ
                lesson_plan = self.lesson_generator.generate_lesson_plan(
                    topic=category,
                    faq_categories=[category],
                    student_summaries=[f"Students frequently ask: {question_text}"],
                    difficulty_level="intermediate"
                )
                
                if lesson_plan:
                    lesson_plan['source_faq'] = question_text
                    lesson_plan['frequency'] = frequency
                    lesson_plans.append(lesson_plan)
                    
            except Exception as e:
                print(f"Error generating lesson plan for FAQ: {e}")
                continue
        
        return lesson_plans
    
    def _build_markdown_report(
        self,
        teacher_id: str,
        start_date: str,
        end_date: str,
        overview_data: Dict[str, Any],
        faqs_data: Dict[str, Any],
        hourly_data: Dict[str, Any],
        engagement_insights: Dict[str, str],
        lesson_plans: list
    ) -> str:
        """Build the complete markdown report."""
        
        report_lines = []
        
        # Header
        report_lines.extend([
            f"# Teacher Overview Report",
            f"",
            f"**Teacher ID:** {teacher_id}  ",
            f"**Report Period:** {start_date} to {end_date}  ",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"",
            "---",
            ""
        ])
        
        # Executive Summary
        if overview_data and overview_data.get('summary'):
            summary = overview_data['summary']
            report_lines.extend([
                "## 📊 Executive Summary",
                "",
                f"- **Total Students:** {summary.get('totalStudents', 0)}",
                f"- **Active Students:** {summary.get('activeStudents', 0)}",
                f"- **Total Sessions:** {summary.get('totalSessions', 0)}",
                f"- **Completion Rate:** {summary.get('completionRate', 0):.1f}%",
                f"- **Average Session Duration:** {summary.get('avgSessionDuration', 0):.1f} minutes",
                ""
            ])
        
        # Engagement Metrics
        if overview_data and overview_data.get('engagement'):
            engagement = overview_data['engagement']
            report_lines.extend([
                "## 💬 Engagement Metrics",
                "",
                f"- **Total Messages:** {engagement.get('totalMessages', 0):,}",
                f"- **Average Messages per Student:** {engagement.get('avgMessagesPerStudent', 0):.1f}",
                f"- **Peak Activity Hour:** {engagement.get('peakHour', 'N/A')}",
                f"- **Peak Hour Messages:** {engagement.get('peakMessages', 0)}",
                ""
            ])
        
        # Student Activity
        if overview_data and overview_data.get('studentActivity'):
            report_lines.extend([
                "## 👥 Most Active Students",
                ""
            ])
            
            for i, student in enumerate(overview_data['studentActivity'][:5], 1):
                name = student.get('name', 'Unknown')
                sessions = student.get('sessions', 0)
                report_lines.append(f"{i}. **{name}** - {sessions} sessions")
            
            report_lines.append("")
        
        # Engagement Insights
        if engagement_insights:
            report_lines.extend([
                "## 🔍 Engagement Analysis",
                ""
            ])
            
            for insight_type, insight_text in engagement_insights.items():
                if insight_type != 'error':
                    formatted_type = insight_type.replace('_', ' ').title()
                    report_lines.append(f"**{formatted_type}:** {insight_text}")
            
            report_lines.append("")
        
        # Top Challenges
        if overview_data and overview_data.get('topChallenges'):
            report_lines.extend([
                "## 🎯 Top Learning Challenges",
                ""
            ])
            
            for i, challenge in enumerate(overview_data['topChallenges'][:5], 1):
                concept = challenge.get('concept', 'Unknown')
                frequency = challenge.get('frequency', 0)
                report_lines.append(f"{i}. **{concept}** - {frequency} occurrences")
            
            report_lines.append("")
        
        # Frequently Asked Questions
        if faqs_data and faqs_data.get('faqs'):
            report_lines.extend([
                "## ❓ Frequently Asked Questions",
                ""
            ])
            
            for i, faq in enumerate(faqs_data['faqs'][:10], 1):
                question = faq.get('questionText', 'Unknown question')
                category = faq.get('category', 'General')
                frequency = faq.get('frequencyCount', 0)
                success_rate = faq.get('successRate', 0)
                
                report_lines.extend([
                    f"### {i}. {question}",
                    f"- **Category:** {category}",
                    f"- **Asked {frequency} times**",
                    f"- **Success Rate:** {success_rate:.1f}%",
                    ""
                ])
        
        # Hourly Activity Distribution
        if hourly_data and hourly_data.get('hourlyDistribution'):
            report_lines.extend([
                "## ⏰ Hourly Activity Distribution",
                "",
                "| Hour | Messages | Percentage |",
                "|------|----------|------------|"
            ])
            
            distribution = hourly_data['hourlyDistribution']
            # Convert list to dict for easier access
            dist_dict = {str(item['hour']): item['messageCount'] for item in distribution} if distribution else {}
            total_messages = sum(dist_dict.values()) if dist_dict else 1
            
            for hour in range(24):
                messages = dist_dict.get(str(hour), 0)
                percentage = (messages / total_messages * 100) if total_messages > 0 else 0
                report_lines.append(f"| {hour:02d}:00 | {messages} | {percentage:.1f}% |")
            
            report_lines.append("")
        
        # Lesson Plans
        if lesson_plans:
            report_lines.extend([
                "## 📚 Recommended Lesson Plans",
                "",
                "*Based on frequently asked questions and student needs*",
                ""
            ])
            
            for i, lesson in enumerate(lesson_plans, 1):
                title = lesson.get('title', f'Lesson Plan {i}')
                objectives = lesson.get('learning_objectives', [])
                activities = lesson.get('activities', [])
                source_faq = lesson.get('source_faq', '')
                
                report_lines.extend([
                    f"### {i}. {title}",
                    ""
                ])
                
                if source_faq:
                    report_lines.extend([
                        f"**Addresses FAQ:** {source_faq}",
                        ""
                    ])
                
                if objectives:
                    report_lines.extend([
                        "**Learning Objectives:**"
                    ])
                    for obj in objectives[:3]:
                        report_lines.append(f"- {obj}")
                    report_lines.append("")
                
                if activities:
                    report_lines.extend([
                        "**Key Activities:**"
                    ])
                    for activity in activities[:3]:
                        activity_name = activity.get('name', activity) if isinstance(activity, dict) else activity
                        report_lines.append(f"- {activity_name}")
                    report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "## 💡 Recommendations",
            ""
        ])
        
        # Generate recommendations based on data
        recommendations = self._generate_recommendations(overview_data, faqs_data, engagement_insights)
        for rec in recommendations:
            report_lines.append(f"- {rec}")
        
        report_lines.extend([
            "",
            "---",
            "",
            f"*Report generated by Teacher Analytics System on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*"
        ])
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(
        self, 
        overview_data: Dict[str, Any], 
        faqs_data: Dict[str, Any],
        engagement_insights: Dict[str, str]
    ) -> list:
        """Generate actionable recommendations based on analytics data."""
        recommendations = []
        
        if not overview_data:
            return ["Unable to generate recommendations due to missing data."]
        
        # Analyze completion rate
        completion_rate = overview_data.get('summary', {}).get('completionRate', 0)
        if completion_rate < 60:
            recommendations.append(
                "**Improve Session Completion:** Consider shorter, more focused sessions or "
                "additional support for struggling students."
            )
        
        # Analyze engagement
        avg_messages = overview_data.get('engagement', {}).get('avgMessagesPerStudent', 0)
        if avg_messages < 10:
            recommendations.append(
                "**Increase Student Engagement:** Implement interactive elements or "
                "discussion prompts to encourage more participation."
            )
        
        # Analyze FAQ patterns
        if faqs_data and faqs_data.get('faqs'):
            top_categories = {}
            for faq in faqs_data['faqs']:
                category = faq.get('category', 'General')
                top_categories[category] = top_categories.get(category, 0) + 1
            
            if top_categories:
                most_common = max(top_categories.items(), key=lambda x: x[1])
                recommendations.append(
                    f"**Focus on {most_common[0]}:** This topic generates the most questions. "
                    "Consider creating additional resources or lesson plans."
                )
        
        # Analyze session duration
        avg_duration = overview_data.get('summary', {}).get('avgSessionDuration', 0)
        if avg_duration > 45:
            recommendations.append(
                "**Optimize Session Length:** Sessions are running long. Consider breaking "
                "content into smaller, digestible chunks."
            )
        elif avg_duration < 10:
            recommendations.append(
                "**Extend Session Depth:** Sessions are quite short. Students might benefit "
                "from more comprehensive coverage of topics."
            )
        
        # Default recommendations if no specific issues found
        if not recommendations:
            recommendations.extend([
                "**Maintain Current Approach:** Your teaching methods are showing good results.",
                "**Continue Monitoring:** Keep tracking student engagement and adjust as needed.",
                "**Expand Successful Strategies:** Consider applying your effective techniques to new topics."
            ])
        
        return recommendations
    
    def _generate_error_report(self, teacher_id: str, error_message: str) -> str:
        """Generate an error report when data cannot be fetched."""
        return f"""# Teacher Overview Report - Error

**Teacher ID:** {teacher_id}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## ⚠️ Error

{error_message}

Please check:
- Backend API is running on the correct port
- Database connection is established
- Teacher ID exists in the system

---

*Report generated by Teacher Analytics System*
"""

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Generate teacher overview reports')
    parser.add_argument('--teacher-id', required=True, help='Teacher ID to generate report for')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--api-url', default='http://localhost:4000/api', help='API base URL')
    
    args = parser.parse_args()
    
    # Create overview builder
    builder = TeacherOverviewBuilder(api_base_url=args.api_url)
    
    # Generate report
    try:
        report = builder.generate_overview_report(
            teacher_id=args.teacher_id,
            start_date=args.start_date,
            end_date=args.end_date,
            output_file=args.output
        )
        
        if not args.output:
            print("\n" + "="*80)
            print(report)
            print("="*80)
            
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
