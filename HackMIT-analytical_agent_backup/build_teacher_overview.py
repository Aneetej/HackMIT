from analytical_agent import create_analytical_agent
from datetime import datetime, timedelta
import json

def execute_teacher_overview_analysis(
    teacher_id: str,
    start_date: str = None,
    end_date: str = None,
    use_mock_data: bool = True
) -> str:
    """
    Execute the teacher overview analysis and return markdown report.
    
    Args:
        teacher_id: The teacher's unique identifier
        start_date: Start date in ISO format (defaults to 7 days ago)
        end_date: End date in ISO format (defaults to today)
        use_mock_data: Whether to use mock data (True) or real API data (False)
        
    Returns:
        Markdown-formatted teacher overview report
    """
    
    # Use the standalone analytics instead of API calls
    from standalone_analytics import StandaloneAnalytics
    
    analytics = StandaloneAnalytics(use_mock_data=use_mock_data)
    
    # Set default dates if not provided
    if not start_date or not end_date:
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=7)
        start_date = start_date or start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date or end_date_obj.strftime('%Y-%m-%d')
    
    return analytics.generate_markdown_report(teacher_id, start_date, end_date)

def generate_markdown_report(
    teacher_id: str,
    start_date: str,
    end_date: str,
    overview_data: dict,
    hourly_data: dict,
    faqs_data: dict,
    insights: dict
) -> str:
    """
    Generate a markdown-formatted teacher overview report.
    
    Returns:
        Markdown-formatted report string
    """
    
    cohort_info = overview_data.get('cohortInfo', {})
    engagement = overview_data.get('engagementMetrics', {})
    session_metrics = overview_data.get('sessionMetrics', {})
    student_activity = overview_data.get('studentActivity', [])
    misconceptions = overview_data.get('topMisconceptions', [])
    
    # Calculate additional metrics
    total_students = cohort_info.get('totalStudents', 0)
    active_students = len([s for s in student_activity if s.get('sessionCount', 0) > 0])
    
    # Find peak activity hour
    peak_hour = "N/A"
    if hourly_data and 'summary' in hourly_data:
        peak_info = hourly_data['summary'].get('peakHour', {})
        if peak_info:
            peak_hour = f"{peak_info.get('hour', 'N/A')}:00"
    
    # Top FAQs
    top_faqs = []
    if faqs_data and 'topFaqs' in faqs_data:
        top_faqs = faqs_data['topFaqs'][:5]
    
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

    # Add top active students
    if student_activity:
        report += "### Most Active Students\n"
        for i, student in enumerate(student_activity[:5], 1):
            report += f"{i}. **{student.get('studentName', 'Unknown')}** - {student.get('sessionCount', 0)} sessions\n"
        report += "\n"

    # Add misconceptions
    if misconceptions:
        report += "### Top Learning Challenges\n"
        for misconception in misconceptions[:3]:
            category = misconception.get('category', 'Unknown')
            frequency = misconception.get('frequency', 0)
            report += f"- **{category}** ({frequency} occurrences)\n"
        report += "\n"

    # Add FAQs
    if top_faqs:
        report += "---\n\n## ❓ Frequently Asked Questions\n\n"
        for i, faq in enumerate(top_faqs, 1):
            question = faq.get('question', 'Unknown question')
            category = faq.get('category', 'General')
            frequency = faq.get('frequency', 0)
            success_rate = faq.get('successRate')
            
            report += f"{i}. **{question}**\n"
            report += f"   - Category: {category}\n"
            report += f"   - Asked {frequency} times\n"
            if success_rate is not None:
                report += f"   - Success Rate: {success_rate}%\n"
            report += "\n"

    # Add recommendations
    report += """---

## 💡 Recommendations

"""

    # Generate recommendations based on data
    recommendations = []
    
    completion_rate = session_metrics.get('completionRate', 0)
    if completion_rate < 60:
        recommendations.append("**Improve Session Completion:** Consider shorter, more focused sessions or check for technical issues causing dropouts.")
    
    avg_messages = engagement.get('avgMessagesPerStudent', 0)
    if avg_messages < 10:
        recommendations.append("**Increase Engagement:** Encourage more student questions and interactive elements in tutoring sessions.")
    
    if active_students < total_students * 0.7:
        recommendations.append("**Boost Participation:** Reach out to inactive students and provide additional support or motivation.")
    
    if misconceptions:
        top_misconception = misconceptions[0].get('category', '')
        recommendations.append(f"**Address Common Misconceptions:** Focus on {top_misconception} concepts in upcoming lessons.")
    
    if not recommendations:
        recommendations.append("**Maintain Excellence:** Current metrics show good student engagement and learning progress.")
    
    for i, rec in enumerate(recommendations, 1):
        report += f"{i}. {rec}\n"

    report += f"""
---

## 📋 Next Steps

1. Review individual student progress for those with low activity
2. Analyze peak activity hours to optimize tutoring availability  
3. Prepare targeted content for common misconception areas
4. Monitor completion rates and adjust session structure if needed

---

*Report generated by CrewAI Analytics Agent*
"""

    return report

def run_teacher_overview_analysis(
    teacher_id: str,
    start_date: str = None,
    end_date: str = None,
    use_mock_data: bool = True
) -> str:
    """
    Run teacher overview analysis using standalone analytics.
    
    Args:
        teacher_id: The teacher's unique identifier
        start_date: Start date in ISO format (defaults to 7 days ago)
        end_date: End date in ISO format (defaults to today)
        use_mock_data: Whether to use mock data (True) or real API data (False)
        
    Returns:
        Markdown-formatted teacher overview report
    """
    
    # Use the standalone analytics instead of API calls
    from standalone_analytics import StandaloneAnalytics
    
    analytics = StandaloneAnalytics(use_mock_data=use_mock_data)
    
    # Set default dates if not provided
    if not start_date or not end_date:
        from datetime import datetime, timedelta
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=7)
        start_date = start_date or start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date or end_date_obj.strftime('%Y-%m-%d')
    
    return analytics.generate_markdown_report(teacher_id, start_date, end_date)

# Example usage
if __name__ == "__main__":
    # Example: Generate overview for teacher with ID "teacher_123"
    teacher_id = "teacher_123"
    
    # Generate report for last week
    report = run_teacher_overview_analysis(teacher_id)
    
    print(report)
    
    # Save to file
    with open(f"teacher_overview_{teacher_id}_{datetime.now().strftime('%Y%m%d')}.md", "w") as f:
        f.write(report)
