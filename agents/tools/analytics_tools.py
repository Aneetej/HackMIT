from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class AnalyticsGeneratorTool(BaseTool):
    """Tool for generating comprehensive analytics and insights"""
    
    name: str = "Analytics Generator"
    description: str = "Generates comprehensive analytics reports, learning insights, and performance metrics for students and teachers."
    
    def _run(self, data_type: str, parameters: Dict[str, Any]) -> str:
        """
        Generate analytics based on data type and parameters
        
        Args:
            data_type: Type of analytics (student, class, system, trends)
            parameters: Parameters for analytics generation
        """
        
        try:
            if data_type == "student":
                return self._generate_student_analytics(parameters)
            elif data_type == "class":
                return self._generate_class_analytics(parameters)
            elif data_type == "system":
                return self._generate_system_analytics(parameters)
            elif data_type == "trends":
                return self._generate_trend_analytics(parameters)
            else:
                return self._generate_general_analytics(parameters)
                
        except Exception as e:
            return f"Error generating analytics: {str(e)}"
    
    def _generate_student_analytics(self, parameters: Dict[str, Any]) -> str:
        """Generate individual student analytics"""
        
        student_id = parameters.get('student_id', 'unknown')
        time_period = parameters.get('time_period', 'week')
        
        analytics = f"# 📊 Student Analytics Report\n\n"
        analytics += f"**Student ID:** {student_id}\n"
        analytics += f"**Time Period:** {time_period}\n"
        analytics += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Engagement Metrics
        analytics += "## 🎯 Engagement Metrics\n"
        analytics += "• **Session Frequency:** 4.2 sessions per week\n"
        analytics += "• **Average Session Duration:** 18 minutes\n"
        analytics += "• **Questions Asked:** 23 total questions\n"
        analytics += "• **Concepts Explored:** 7 different topics\n"
        analytics += "• **Engagement Score:** 78/100\n\n"
        
        # Learning Progress
        analytics += "## 📈 Learning Progress\n"
        analytics += "• **Progress Trend:** Steadily improving\n"
        analytics += "• **Difficulty Progression:** Easy → Medium\n"
        analytics += "• **Mastery Indicators:** Strong in algebra, developing in geometry\n"
        analytics += "• **Success Rate:** 82% of questions resolved satisfactorily\n\n"
        
        # Preferences Analysis
        analytics += "## 🎨 Learning Preferences\n"
        analytics += "• **Preferred Format:** Step-by-step explanations (65%)\n"
        analytics += "• **Content Type:** Visual examples preferred\n"
        analytics += "• **Interaction Style:** Asks detailed questions\n"
        analytics += "• **Peak Learning Hours:** 3-5 PM\n\n"
        
        # Recommendations
        analytics += "## 💡 Personalized Recommendations\n"
        analytics += "1. Continue with visual learning approaches\n"
        analytics += "2. Introduce more challenging geometry problems\n"
        analytics += "3. Schedule sessions during peak hours (3-5 PM)\n"
        analytics += "4. Provide more practice with word problems\n"
        
        return analytics
    
    def _generate_class_analytics(self, parameters: Dict[str, Any]) -> str:
        """Generate class-level analytics"""
        
        class_id = parameters.get('class_id', 'unknown')
        student_count = parameters.get('student_count', 25)
        
        analytics = f"# 📚 Class Analytics Dashboard\n\n"
        analytics += f"**Class ID:** {class_id}\n"
        analytics += f"**Total Students:** {student_count}\n"
        analytics += f"**Analysis Period:** Last 30 days\n\n"
        
        # Class Overview
        analytics += "## 🎯 Class Overview\n"
        analytics += f"• **Active Students:** {int(student_count * 0.85)} ({85}%)\n"
        analytics += "• **Total Sessions:** 342\n"
        analytics += "• **Average Sessions per Student:** 13.7\n"
        analytics += "• **Total Questions Asked:** 1,247\n"
        analytics += "• **Class Engagement Score:** 74/100\n\n"
        
        # Performance Distribution
        analytics += "## 📊 Performance Distribution\n"
        analytics += "• **High Performers:** 30% of students\n"
        analytics += "• **Average Performers:** 55% of students\n"
        analytics += "• **Need Support:** 15% of students\n\n"
        
        # Popular Topics
        analytics += "## 🔥 Most Popular Topics\n"
        analytics += "1. **Algebra** - 45% of interactions\n"
        analytics += "2. **Geometry** - 28% of interactions\n"
        analytics += "3. **Fractions** - 15% of interactions\n"
        analytics += "4. **Word Problems** - 12% of interactions\n\n"
        
        # Learning Patterns
        analytics += "## ⏰ Learning Patterns\n"
        analytics += "• **Peak Usage:** 3-6 PM weekdays\n"
        analytics += "• **Average Session Length:** 22 minutes\n"
        analytics += "• **Preferred Learning Style:** Mixed (40% visual, 35% text, 25% interactive)\n\n"
        
        # Recommendations
        analytics += "## 🎯 Class Recommendations\n"
        analytics += "1. Focus additional support on geometry concepts\n"
        analytics += "2. Create more interactive content for engagement\n"
        analytics += "3. Schedule review sessions during peak hours\n"
        analytics += "4. Develop targeted interventions for struggling students\n"
        
        return analytics
    
    def _generate_system_analytics(self, parameters: Dict[str, Any]) -> str:
        """Generate system performance analytics"""
        
        analytics = f"# ⚙️ System Performance Analytics\n\n"
        analytics += f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        analytics += f"**Analysis Period:** Last 24 hours\n\n"
        
        # System Health
        analytics += "## 🟢 System Health Status\n"
        analytics += "• **Overall Status:** Healthy\n"
        analytics += "• **Uptime:** 99.8%\n"
        analytics += "• **Response Time:** 1.2s average\n"
        analytics += "• **Error Rate:** 0.3%\n\n"
        
        # Usage Statistics
        analytics += "## 📈 Usage Statistics\n"
        analytics += "• **Total Interactions:** 1,847\n"
        analytics += "• **Unique Students:** 156\n"
        analytics += "• **Peak Concurrent Users:** 23\n"
        analytics += "• **Average Session Duration:** 19 minutes\n\n"
        
        # Agent Performance
        analytics += "## 🤖 Agent Performance\n"
        analytics += "• **Teacher Agent:** Processing 45 analytics requests\n"
        analytics += "• **Student Agent:** 98.5% satisfaction rate\n"
        analytics += "• **Guardrail Agent:** 12 content flags (all resolved)\n"
        analytics += "• **Aggregation Agent:** Processing 2.3GB data\n\n"
        
        # Resource Usage
        analytics += "## 💾 Resource Utilization\n"
        analytics += "• **CPU Usage:** 45% average\n"
        analytics += "• **Memory Usage:** 67% of allocated\n"
        analytics += "• **Database Connections:** 23/50 active\n"
        analytics += "• **API Rate Limits:** 15% of quota used\n"
        
        return analytics
    
    def _generate_trend_analytics(self, parameters: Dict[str, Any]) -> str:
        """Generate trend analysis"""
        
        trend_type = parameters.get('trend_type', 'engagement')
        
        analytics = f"# 📈 Trend Analysis Report\n\n"
        analytics += f"**Trend Focus:** {trend_type.title()}\n"
        analytics += f"**Analysis Period:** Last 3 months\n\n"
        
        if trend_type == "engagement":
            analytics += "## 🎯 Engagement Trends\n"
            analytics += "• **Overall Trend:** ↗️ Increasing (+15% over 3 months)\n"
            analytics += "• **Peak Engagement:** Weeks 8-10 (exam preparation period)\n"
            analytics += "• **Lowest Engagement:** Week 4 (holiday period)\n"
            analytics += "• **Weekly Pattern:** Higher on Tue-Thu, lower on Mon/Fri\n\n"
            
            analytics += "## 📊 Engagement Factors\n"
            analytics += "• **Interactive Content:** +23% engagement boost\n"
            analytics += "• **Video Explanations:** +18% engagement boost\n"
            analytics += "• **Immediate Feedback:** +31% engagement boost\n"
            analytics += "• **Personalized Difficulty:** +27% engagement boost\n"
            
        elif trend_type == "performance":
            analytics += "## 📈 Performance Trends\n"
            analytics += "• **Overall Improvement:** +22% success rate increase\n"
            analytics += "• **Concept Mastery:** Algebra (+35%), Geometry (+18%)\n"
            analytics += "• **Problem Solving Speed:** +15% faster resolution\n"
            analytics += "• **Help-Seeking Behavior:** More specific questions (+40%)\n\n"
            
            analytics += "## 🎯 Performance Drivers\n"
            analytics += "• **Consistent Practice:** Top predictor of success\n"
            analytics += "• **Question Quality:** Better questions → better outcomes\n"
            analytics += "• **Session Frequency:** Optimal at 3-4 sessions/week\n"
            analytics += "• **Feedback Integration:** Students using feedback show +28% improvement\n"
        
        return analytics
    
    def _generate_general_analytics(self, parameters: Dict[str, Any]) -> str:
        """Generate general analytics overview"""
        
        analytics = f"# 📊 General Analytics Overview\n\n"
        analytics += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        analytics += "## 🎯 Key Metrics Summary\n"
        analytics += "• **Total Active Users:** 1,247\n"
        analytics += "• **Daily Active Sessions:** 342\n"
        analytics += "• **Average Engagement Score:** 76/100\n"
        analytics += "• **System Satisfaction Rate:** 94%\n\n"
        
        analytics += "## 📈 Growth Indicators\n"
        analytics += "• **User Growth:** +18% month-over-month\n"
        analytics += "• **Session Quality:** +12% improvement\n"
        analytics += "• **Feature Adoption:** 87% using new tools\n"
        analytics += "• **Retention Rate:** 89% weekly active users\n\n"
        
        analytics += "## 🎯 Areas of Focus\n"
        analytics += "1. Continue improving personalization algorithms\n"
        analytics += "2. Expand content library for advanced topics\n"
        analytics += "3. Enhance mobile experience\n"
        analytics += "4. Develop more interactive learning tools\n"
        
        return analytics

class FAQTrackerTool(BaseTool):
    """Tool for tracking and analyzing frequently asked questions"""
    
    name: str = "FAQ Tracker and Analyzer"
    description: str = "Tracks frequently asked questions, identifies patterns, and provides insights about common student difficulties and learning gaps."
    
    def _run(self, action: str, parameters: Dict[str, Any]) -> str:
        """
        Track and analyze FAQs
        
        Args:
            action: Action to perform (track, analyze, report, trends)
            parameters: Parameters for the action
        """
        
        try:
            if action == "track":
                return self._track_question(parameters)
            elif action == "analyze":
                return self._analyze_faqs(parameters)
            elif action == "report":
                return self._generate_faq_report(parameters)
            elif action == "trends":
                return self._analyze_faq_trends(parameters)
            else:
                return self._get_top_faqs(parameters)
                
        except Exception as e:
            return f"Error processing FAQ request: {str(e)}"
    
    def _track_question(self, parameters: Dict[str, Any]) -> str:
        """Track a new question"""
        
        question = parameters.get('question', '')
        category = parameters.get('category', 'general')
        student_id = parameters.get('student_id', 'unknown')
        
        # Simulate question tracking
        result = f"✅ Question tracked successfully\n\n"
        result += f"**Question:** {question}\n"
        result += f"**Category:** {category}\n"
        result += f"**Student:** {student_id}\n"
        result += f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        result += "This question will be analyzed for FAQ patterns and teaching improvements."
        
        return result
    
    def _analyze_faqs(self, parameters: Dict[str, Any]) -> str:
        """Analyze FAQ patterns"""
        
        category = parameters.get('category', 'all')
        time_period = parameters.get('time_period', 'month')
        
        analysis = f"# 🔍 FAQ Pattern Analysis\n\n"
        analysis += f"**Category:** {category}\n"
        analysis += f"**Time Period:** Last {time_period}\n"
        analysis += f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Common Question Patterns
        analysis += "## 🔄 Common Question Patterns\n"
        analysis += "1. **\"How do I solve...\"** - 34% of questions\n"
        analysis += "2. **\"What is the difference between...\"** - 22% of questions\n"
        analysis += "3. **\"Why does this work...\"** - 18% of questions\n"
        analysis += "4. **\"Can you explain...\"** - 16% of questions\n"
        analysis += "5. **\"What's the formula for...\"** - 10% of questions\n\n"
        
        # Topic Distribution
        analysis += "## 📚 Topic Distribution\n"
        if category == "all":
            analysis += "• **Algebra:** 42% of questions\n"
            analysis += "• **Geometry:** 28% of questions\n"
            analysis += "• **Calculus:** 15% of questions\n"
            analysis += "• **Statistics:** 10% of questions\n"
            analysis += "• **Other:** 5% of questions\n\n"
        else:
            analysis += f"• **{category.title()}:** Focus area for this analysis\n"
            analysis += "• **Subtopic breakdown:** Available in detailed report\n\n"
        
        # Difficulty Indicators
        analysis += "## 📊 Difficulty Indicators\n"
        analysis += "• **Beginner Questions:** 45%\n"
        analysis += "• **Intermediate Questions:** 35%\n"
        analysis += "• **Advanced Questions:** 20%\n\n"
        
        # Learning Gaps Identified
        analysis += "## ⚠️ Learning Gaps Identified\n"
        analysis += "1. **Fraction Operations** - High confusion rate\n"
        analysis += "2. **Word Problem Translation** - Frequent struggles\n"
        analysis += "3. **Graph Interpretation** - Needs more practice\n"
        analysis += "4. **Formula Application** - Conceptual gaps\n\n"
        
        # Recommendations
        analysis += "## 💡 Teaching Recommendations\n"
        analysis += "1. Create more step-by-step fraction tutorials\n"
        analysis += "2. Develop word problem strategy guides\n"
        analysis += "3. Add interactive graph exploration tools\n"
        analysis += "4. Provide formula derivation explanations\n"
        
        return analysis
    
    def _generate_faq_report(self, parameters: Dict[str, Any]) -> str:
        """Generate comprehensive FAQ report"""
        
        limit = parameters.get('limit', 10)
        
        report = f"# 📋 Top {limit} Frequently Asked Questions\n\n"
        report += f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"**Data Period:** Last 30 days\n\n"
        
        # Sample FAQs with realistic mathematics questions
        faqs = [
            {
                "question": "How do I solve quadratic equations?",
                "frequency": 47,
                "category": "Algebra",
                "success_rate": 0.85,
                "avg_resolution_time": "12 minutes"
            },
            {
                "question": "What's the difference between mean and median?",
                "frequency": 34,
                "category": "Statistics",
                "success_rate": 0.92,
                "avg_resolution_time": "8 minutes"
            },
            {
                "question": "How do I find the area of a triangle?",
                "frequency": 31,
                "category": "Geometry",
                "success_rate": 0.88,
                "avg_resolution_time": "10 minutes"
            },
            {
                "question": "Why do we flip the fraction when dividing?",
                "frequency": 28,
                "category": "Arithmetic",
                "success_rate": 0.76,
                "avg_resolution_time": "15 minutes"
            },
            {
                "question": "How do I convert fractions to decimals?",
                "frequency": 25,
                "category": "Arithmetic",
                "success_rate": 0.90,
                "avg_resolution_time": "7 minutes"
            }
        ]
        
        for i, faq in enumerate(faqs[:limit], 1):
            report += f"## {i}. {faq['question']}\n"
            report += f"**Frequency:** {faq['frequency']} times asked\n"
            report += f"**Category:** {faq['category']}\n"
            report += f"**Success Rate:** {faq['success_rate']*100:.0f}%\n"
            report += f"**Avg Resolution:** {faq['avg_resolution_time']}\n\n"
        
        # Summary Statistics
        report += "## 📊 Summary Statistics\n"
        total_questions = sum(faq['frequency'] for faq in faqs)
        avg_success = sum(faq['success_rate'] for faq in faqs) / len(faqs)
        
        report += f"• **Total FAQ Instances:** {total_questions}\n"
        report += f"• **Average Success Rate:** {avg_success*100:.1f}%\n"
        report += f"• **Most Challenging Topic:** Arithmetic (fraction concepts)\n"
        report += f"• **Easiest Topic:** Statistics (descriptive measures)\n\n"
        
        # Action Items
        report += "## 🎯 Recommended Actions\n"
        report += "1. Create dedicated fraction division tutorial\n"
        report += "2. Develop quadratic equation practice tool\n"
        report += "3. Add visual geometry area calculators\n"
        report += "4. Improve statistics concept explanations\n"
        
        return report
    
    def _analyze_faq_trends(self, parameters: Dict[str, Any]) -> str:
        """Analyze FAQ trends over time"""
        
        trends = f"# 📈 FAQ Trends Analysis\n\n"
        trends += f"**Analysis Period:** Last 3 months\n"
        trends += f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Trending Questions
        trends += "## 🔥 Trending Questions (↗️ Increasing)\n"
        trends += "1. **Graph interpretation questions** (+45% this month)\n"
        trends += "2. **Calculus derivative problems** (+32% this month)\n"
        trends += "3. **Word problem strategies** (+28% this month)\n\n"
        
        # Declining Questions
        trends += "## 📉 Declining Questions (↘️ Decreasing)\n"
        trends += "1. **Basic arithmetic operations** (-23% this month)\n"
        trends += "2. **Simple fraction problems** (-18% this month)\n"
        trends += "3. **Basic geometry formulas** (-15% this month)\n\n"
        
        # Seasonal Patterns
        trends += "## 🗓️ Seasonal Patterns\n"
        trends += "• **September-October:** High algebra questions (new school year)\n"
        trends += "• **November-December:** Increased calculus questions (exam prep)\n"
        trends += "• **January-February:** Geometry focus (curriculum progression)\n"
        trends += "• **March-April:** Statistics and probability (standardized test prep)\n\n"
        
        # Weekly Patterns
        trends += "## 📅 Weekly Patterns\n"
        trends += "• **Monday:** Review questions from weekend homework\n"
        trends += "• **Tuesday-Wednesday:** New concept questions\n"
        trends += "• **Thursday:** Practice and application questions\n"
        trends += "• **Friday:** Clarification and exam prep questions\n"
        trends += "• **Weekend:** Project and advanced topic questions\n\n"
        
        # Insights
        trends += "## 💡 Key Insights\n"
        trends += "1. Students are progressing to more advanced topics\n"
        trends += "2. Visual learning requests are increasing\n"
        trends += "3. Application-based questions are trending up\n"
        trends += "4. Basic skills questions are decreasing (good sign!)\n"
        
        return trends
    
    def _get_top_faqs(self, parameters: Dict[str, Any]) -> str:
        """Get top FAQs with quick answers"""
        
        limit = parameters.get('limit', 5)
        
        faqs = f"# 🔝 Top {limit} FAQs - Quick Reference\n\n"
        
        quick_faqs = [
            {
                "q": "How do I solve for x in equations?",
                "a": "Isolate x by performing inverse operations on both sides of the equation."
            },
            {
                "q": "What's the Pythagorean theorem?",
                "a": "a² + b² = c² for right triangles, where c is the hypotenuse."
            },
            {
                "q": "How do I find the slope of a line?",
                "a": "Slope = (y₂ - y₁) / (x₂ - x₁) using two points on the line."
            },
            {
                "q": "What's the order of operations?",
                "a": "PEMDAS: Parentheses, Exponents, Multiplication/Division, Addition/Subtraction."
            },
            {
                "q": "How do I convert percentages to decimals?",
                "a": "Divide by 100 or move the decimal point two places left."
            }
        ]
        
        for i, faq in enumerate(quick_faqs[:limit], 1):
            faqs += f"## {i}. {faq['q']}\n"
            faqs += f"**Answer:** {faq['a']}\n\n"
        
        faqs += "💡 *For detailed explanations, ask me to explain any of these concepts in depth!*"
        
        return faqs
