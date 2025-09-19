#!/usr/bin/env python3
"""
Standalone Analytics Agent

This module provides a standalone analytics agent that generates comprehensive
teacher reports using real backend data from the analytics API endpoints.
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from analytical_agent import AnalyticalAgent
from build_teacher_overview import TeacherOverviewBuilder
from exa_lesson_generator import ExaLessonGenerator
from nlp_summary_generator import NLPSummaryGenerator

class StandaloneAnalytics:
    """Standalone analytics agent for generating comprehensive teacher reports."""
    
    def __init__(self, api_base_url: str = "http://localhost:4000/api"):
        """
        Initialize the standalone analytics agent.
        
        Args:
            api_base_url: Base URL for the analytics API
        """
        self.api_base_url = api_base_url
        self.analytics_agent = AnalyticalAgent(api_base_url=api_base_url)
        self.overview_builder = TeacherOverviewBuilder(api_base_url=api_base_url)
        self.lesson_generator = ExaLessonGenerator(api_base_url=api_base_url)
        self.nlp_generator = NLPSummaryGenerator(api_base_url=api_base_url)
    
    def generate_comprehensive_report(
        self,
        teacher_id: str,
        start_date: str = None,
        end_date: str = None,
        include_lesson_plans: bool = True,
        include_nlp_analysis: bool = True,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report for a teacher.
        
        Args:
            teacher_id: Teacher's unique identifier
            start_date: Start date for analysis period
            end_date: End date for analysis period
            include_lesson_plans: Whether to include AI-generated lesson plans
            include_nlp_analysis: Whether to include NLP-based analysis
            output_format: Output format ("markdown", "json")
            
        Returns:
            Dictionary containing comprehensive report data
        """
        print(f"Generating comprehensive report for teacher {teacher_id}")
        
        # Set default date range if not provided
        if not start_date or not end_date:
            start_date, end_date = self.analytics_agent.get_date_range_last_month()
        
        print(f"Analysis period: {start_date} to {end_date}")
        
        # Check API health first
        if not self.analytics_agent.check_api_health():
            print("Warning: Analytics API health check failed. Some data may be unavailable.")
        
        # Gather all analytics data
        report_data = {
            "teacher_id": teacher_id,
            "period": {"start": start_date, "end": end_date},
            "generated_at": datetime.now().isoformat(),
            "api_base_url": self.api_base_url
        }
        
        # Fetch core analytics data
        print("Fetching teacher overview data...")
        overview_data = self.analytics_agent.fetch_teacher_overview(teacher_id, start_date, end_date)
        if overview_data:
            report_data["overview"] = overview_data
            report_data["engagement_insights"] = self.analytics_agent.analyze_engagement_trends(overview_data)
        else:
            print("Failed to fetch overview data")
            report_data["overview"] = None
            report_data["engagement_insights"] = {"error": "No overview data available"}
        
        # Fetch FAQs
        print("Fetching FAQ data...")
        faqs_data = self.analytics_agent.fetch_faqs(teacher_id, limit=15)
        if faqs_data:
            report_data["faqs"] = faqs_data
        else:
            print("Failed to fetch FAQ data")
            report_data["faqs"] = {"faqs": []}
        
        # Fetch hourly distribution
        print("Fetching hourly activity distribution...")
        hourly_data = self.analytics_agent.fetch_hourly_distribution(teacher_id, start_date, end_date)
        if hourly_data:
            report_data["hourly_distribution"] = hourly_data
        else:
            print("Failed to fetch hourly distribution data")
            report_data["hourly_distribution"] = {"hourlyDistribution": {}}
        
        # Generate NLP analysis if requested
        if include_nlp_analysis:
            print("Generating NLP-based class summary...")
            try:
                nlp_summary = self.nlp_generator.generate_class_summary(
                    teacher_id=teacher_id,
                    start_date=start_date,
                    end_date=end_date,
                    include_sentiment=True,
                    include_topics=True,
                    include_recommendations=True
                )
                report_data["nlp_analysis"] = nlp_summary
            except Exception as e:
                print(f"NLP analysis failed: {e}")
                report_data["nlp_analysis"] = {"error": str(e)}
        
        # Generate lesson plans if requested
        if include_lesson_plans and faqs_data and faqs_data.get('faqs'):
            print("Generating AI-powered lesson plans...")
            try:
                lesson_plans = self._generate_lesson_plans_from_data(faqs_data['faqs'][:5])
                report_data["lesson_plans"] = lesson_plans
            except Exception as e:
                print(f"Lesson plan generation failed: {e}")
                report_data["lesson_plans"] = {"error": str(e)}
        
        # Generate actionable insights
        report_data["actionable_insights"] = self._generate_actionable_insights(report_data)
        
        # Generate recommendations
        report_data["recommendations"] = self._generate_comprehensive_recommendations(report_data)
        
        return report_data
    
    def _generate_lesson_plans_from_data(self, faqs: list) -> list:
        """Generate lesson plans based on FAQ data."""
        lesson_plans = []
        
        # Group FAQs by category
        faq_categories = {}
        for faq in faqs:
            category = faq.get('category', 'General')
            if category not in faq_categories:
                faq_categories[category] = []
            faq_categories[category].append(faq)
        
        # Generate lesson plan for each category
        for category, category_faqs in faq_categories.items():
            try:
                # Prepare student summaries from FAQ questions
                student_summaries = [f"Students ask: {faq.get('questionText', '')}" for faq in category_faqs]
                
                lesson_plan = self.lesson_generator.generate_lesson_plan(
                    topic=category,
                    faq_categories=[category],
                    student_summaries=student_summaries[:3],
                    difficulty_level="intermediate",
                    duration_minutes=45
                )
                
                if lesson_plan:
                    lesson_plan["addresses_faqs"] = len(category_faqs)
                    lesson_plan["category"] = category
                    lesson_plans.append(lesson_plan)
                    
            except Exception as e:
                print(f"Error generating lesson plan for category {category}: {e}")
                continue
        
        return lesson_plans
    
    def _generate_actionable_insights(self, report_data: Dict[str, Any]) -> list:
        """Generate actionable insights from all collected data."""
        insights = []
        
        # Overview insights
        overview = report_data.get("overview", {})
        if overview and overview.get("summary"):
            summary = overview["summary"]
            completion_rate = summary.get("completionRate", 0)
            total_students = summary.get("totalStudents", 0)
            active_students = summary.get("activeStudents", 0)
            
            if completion_rate < 60:
                insights.append({
                    "type": "completion_rate",
                    "priority": "high",
                    "insight": f"Low completion rate ({completion_rate:.1f}%) indicates students may be struggling or losing interest",
                    "action": "Review session content difficulty and consider breaking into shorter segments"
                })
            
            if total_students > 0 and active_students / total_students < 0.7:
                insights.append({
                    "type": "student_activity",
                    "priority": "medium",
                    "insight": f"Only {active_students}/{total_students} students are actively participating",
                    "action": "Implement engagement strategies to encourage inactive students"
                })
        
        # Engagement insights
        engagement_insights = report_data.get("engagement_insights", {})
        for insight_type, insight_text in engagement_insights.items():
            if insight_type != "error" and "low" in insight_text.lower():
                insights.append({
                    "type": insight_type,
                    "priority": "medium",
                    "insight": insight_text,
                    "action": "Consider implementing more interactive elements"
                })
        
        # FAQ insights
        faqs = report_data.get("faqs", {}).get("faqs", [])
        if faqs:
            # Find most frequent questions
            top_faq = max(faqs, key=lambda x: x.get("frequencyCount", 0))
            if top_faq.get("frequencyCount", 0) > 5:
                insights.append({
                    "type": "frequent_questions",
                    "priority": "high",
                    "insight": f"Question '{top_faq.get('questionText', '')}' asked {top_faq.get('frequencyCount', 0)} times",
                    "action": "Create dedicated content or lesson plan to address this common question"
                })
        
        # NLP insights
        nlp_analysis = report_data.get("nlp_analysis", {})
        if nlp_analysis and not nlp_analysis.get("error"):
            nlp_insights = nlp_analysis.get("insights", [])
            for nlp_insight in nlp_insights:
                insights.append({
                    "type": "nlp_analysis",
                    "priority": "low",
                    "insight": nlp_insight,
                    "action": "Monitor and adjust teaching strategies accordingly"
                })
        
        return insights
    
    def _generate_comprehensive_recommendations(self, report_data: Dict[str, Any]) -> list:
        """Generate comprehensive recommendations based on all data."""
        recommendations = []
        
        # Performance-based recommendations
        overview = report_data.get("overview", {})
        if overview and overview.get("summary"):
            summary = overview["summary"]
            completion_rate = summary.get("completionRate", 0)
            avg_duration = summary.get("avgSessionDuration", 0)
            
            if completion_rate < 70:
                recommendations.append({
                    "category": "session_optimization",
                    "priority": "high",
                    "recommendation": "Optimize session structure to improve completion rates",
                    "specific_actions": [
                        "Break long sessions into smaller chunks",
                        "Add progress indicators",
                        "Include more interactive elements",
                        "Provide clear learning objectives upfront"
                    ]
                })
            
            if avg_duration > 45:
                recommendations.append({
                    "category": "time_management",
                    "priority": "medium",
                    "recommendation": "Sessions are running longer than optimal",
                    "specific_actions": [
                        "Review content density",
                        "Identify areas where students get stuck",
                        "Consider pre-session preparation materials"
                    ]
                })
        
        # Content-based recommendations
        faqs = report_data.get("faqs", {}).get("faqs", [])
        if faqs:
            # Group FAQs by category for targeted recommendations
            category_counts = {}
            for faq in faqs:
                category = faq.get("category", "General")
                category_counts[category] = category_counts.get(category, 0) + faq.get("frequencyCount", 0)
            
            if category_counts:
                top_category = max(category_counts.items(), key=lambda x: x[1])
                recommendations.append({
                    "category": "content_focus",
                    "priority": "high",
                    "recommendation": f"Focus on {top_category[0]} - highest question volume",
                    "specific_actions": [
                        f"Create comprehensive {top_category[0]} resource guide",
                        "Develop interactive exercises for this topic",
                        "Consider dedicated office hours for this subject",
                        "Update lesson plans to address common misconceptions"
                    ]
                })
        
        # Engagement-based recommendations
        engagement = report_data.get("overview", {}).get("engagement", {})
        if engagement:
            avg_messages = engagement.get("avgMessagesPerStudent", 0)
            if avg_messages < 15:
                recommendations.append({
                    "category": "engagement",
                    "priority": "medium",
                    "recommendation": "Increase student interaction and participation",
                    "specific_actions": [
                        "Implement discussion prompts",
                        "Use polls and quick assessments",
                        "Encourage peer-to-peer learning",
                        "Gamify learning activities"
                    ]
                })
        
        # NLP-based recommendations
        nlp_analysis = report_data.get("nlp_analysis", {})
        if nlp_analysis and not nlp_analysis.get("error"):
            nlp_recommendations = nlp_analysis.get("recommendations", [])
            if nlp_recommendations:
                recommendations.append({
                    "category": "data_driven_insights",
                    "priority": "low",
                    "recommendation": "Implement data-driven teaching improvements",
                    "specific_actions": nlp_recommendations
                })
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations.append({
                "category": "general",
                "priority": "low",
                "recommendation": "Continue monitoring and maintain current approach",
                "specific_actions": [
                    "Regular data review sessions",
                    "Student feedback collection",
                    "Continuous improvement mindset"
                ]
            })
        
        return recommendations
    
    def export_report(
        self,
        report_data: Dict[str, Any],
        output_file: str,
        format_type: str = "markdown"
    ) -> bool:
        """
        Export report to file in specified format.
        
        Args:
            report_data: Complete report data
            output_file: Output file path
            format_type: Export format ("markdown", "json")
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if format_type.lower() == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, default=str)
            else:
                # Generate markdown report using overview builder
                markdown_content = self._generate_markdown_report(report_data)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            print(f"Report exported to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False
    
    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Generate markdown report from comprehensive data."""
        lines = []
        
        # Header
        teacher_id = report_data.get("teacher_id", "Unknown")
        period = report_data.get("period", {})
        start_date = period.get("start", "Unknown")
        end_date = period.get("end", "Unknown")
        
        lines.extend([
            f"# Comprehensive Analytics Report",
            f"",
            f"**Teacher ID:** {teacher_id}  ",
            f"**Analysis Period:** {start_date} to {end_date}  ",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"",
            "---",
            ""
        ])
        
        # Executive Summary
        overview = report_data.get("overview", {})
        if overview and overview.get("summary"):
            summary = overview["summary"]
            lines.extend([
                "## 📊 Executive Summary",
                "",
                f"- **Total Students:** {summary.get('totalStudents', 0)}",
                f"- **Active Students:** {summary.get('activeStudents', 0)}",
                f"- **Total Sessions:** {summary.get('totalSessions', 0)}",
                f"- **Completion Rate:** {summary.get('completionRate', 0):.1f}%",
                f"- **Average Session Duration:** {summary.get('avgSessionDuration', 0):.1f} minutes",
                ""
            ])
        
        # Actionable Insights
        insights = report_data.get("actionable_insights", [])
        if insights:
            lines.extend([
                "## 🔍 Key Insights",
                ""
            ])
            
            for insight in insights:
                priority = insight.get("priority", "medium").upper()
                insight_text = insight.get("insight", "")
                action = insight.get("action", "")
                
                lines.extend([
                    f"### {priority} Priority",
                    f"**Insight:** {insight_text}",
                    f"**Action:** {action}",
                    ""
                ])
        
        # Recommendations
        recommendations = report_data.get("recommendations", [])
        if recommendations:
            lines.extend([
                "## 💡 Recommendations",
                ""
            ])
            
            for rec in recommendations:
                category = rec.get("category", "general").title()
                recommendation = rec.get("recommendation", "")
                actions = rec.get("specific_actions", [])
                
                lines.extend([
                    f"### {category}",
                    f"{recommendation}",
                    ""
                ])
                
                if actions:
                    lines.append("**Specific Actions:**")
                    for action in actions:
                        lines.append(f"- {action}")
                    lines.append("")
        
        # Lesson Plans
        lesson_plans = report_data.get("lesson_plans", [])
        if lesson_plans and not isinstance(lesson_plans, dict):
            lines.extend([
                "## 📚 Recommended Lesson Plans",
                ""
            ])
            
            for i, plan in enumerate(lesson_plans, 1):
                title = plan.get("title", f"Lesson Plan {i}")
                category = plan.get("category", "General")
                objectives = plan.get("learning_objectives", [])
                
                lines.extend([
                    f"### {i}. {title}",
                    f"**Category:** {category}",
                    ""
                ])
                
                if objectives:
                    lines.append("**Learning Objectives:**")
                    for obj in objectives[:3]:
                        lines.append(f"- {obj}")
                    lines.append("")
        
        lines.extend([
            "---",
            "",
            f"*Report generated by Standalone Analytics System on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*"
        ])
        
        return "\n".join(lines)

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Generate comprehensive analytics reports')
    parser.add_argument('--teacher-id', required=True, help='Teacher ID to analyze')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='Output format')
    parser.add_argument('--api-url', default='http://localhost:4000/api', help='API base URL')
    parser.add_argument('--no-lesson-plans', action='store_true', help='Skip lesson plan generation')
    parser.add_argument('--no-nlp', action='store_true', help='Skip NLP analysis')
    
    args = parser.parse_args()
    
    # Create analytics agent
    analytics = StandaloneAnalytics(api_base_url=args.api_url)
    
    try:
        # Generate comprehensive report
        report_data = analytics.generate_comprehensive_report(
            teacher_id=args.teacher_id,
            start_date=args.start_date,
            end_date=args.end_date,
            include_lesson_plans=not args.no_lesson_plans,
            include_nlp_analysis=not args.no_nlp,
            output_format=args.format
        )
        
        # Export or display report
        if args.output:
            success = analytics.export_report(report_data, args.output, args.format)
            if not success:
                sys.exit(1)
        else:
            if args.format == 'json':
                print(json.dumps(report_data, indent=2, default=str))
            else:
                markdown_report = analytics._generate_markdown_report(report_data)
                print("\n" + "="*80)
                print(markdown_report)
                print("="*80)
        
        print(f"\nReport generation completed successfully!")
        
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
