import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

class MockDataGenerator:
    """Generate realistic mock data for testing analytics functions"""
    
    def __init__(self):
        self.subjects = ["algebra", "geometry", "calculus", "statistics", "trigonometry"]
        self.misconception_categories = [
            "algebraic_equations", "geometric_proofs", "derivative_rules", 
            "integration_techniques", "probability_concepts"
        ]
        # Generate realistic student IDs (matching Prisma cuid format)
        self.student_ids = [
            "clm1a2b3c4d5e6f7g8h9", "clm2b3c4d5e6f7g8h9i0", 
            "clm3c4d5e6f7g8h9i0j1", "clm4d5e6f7g8h9i0j1k2",
            "clm5e6f7g8h9i0j1k2l3", "clm6f7g8h9i0j1k2l3m4",
            "clm7g8h9i0j1k2l3m4n5", "clm8h9i0j1k2l3m4n5o6"
        ]
        
        # Student names (available in schema)
        self.student_names = [
            "Alice Johnson", "Bob Chen", "Carol Davis", "David Rodriguez", 
            "Emma Wilson", "Frank Kim", "Grace Taylor", "Henry Brown"
        ]
        
        # Detailed lesson plan templates for common misconceptions
        self.lesson_plans = {
            "algebraic_equations": {
                "common_issues": [
                    "Students confuse solving for x with substituting values",
                    "Difficulty with multi-step equations and order of operations",
                    "Trouble isolating variables when coefficients are fractions"
                ],
                "lesson_plan": {
                    "title": "Mastering Algebraic Equations: Step-by-Step Problem Solving",
                    "duration": "45 minutes",
                    "objectives": [
                        "Identify the correct sequence of operations to isolate variables",
                        "Apply inverse operations systematically",
                        "Check solutions by substitution"
                    ],
                    "activities": [
                        "Warm-up: Review order of operations with numerical examples (10 min)",
                        "Guided practice: Work through 3x + 7 = 22 step-by-step (15 min)",
                        "Interactive exercise: Students solve equations with peer checking (15 min)",
                        "Wrap-up: Common mistake analysis and prevention strategies (5 min)"
                    ],
                    "materials": ["Algebra tiles (optional)", "Whiteboard", "Practice worksheets"],
                    "assessment": "Exit ticket with 2 equations to solve independently"
                }
            },
            "geometric_proofs": {
                "common_issues": [
                    "Students struggle with logical reasoning and proof structure",
                    "Difficulty identifying which theorems to apply",
                    "Confusion between given information and what needs to be proven"
                ],
                "lesson_plan": {
                    "title": "Building Geometric Proofs: From Statements to Conclusions",
                    "duration": "50 minutes",
                    "objectives": [
                        "Distinguish between given information and conclusions",
                        "Apply triangle congruence theorems correctly",
                        "Write clear, logical proof statements"
                    ],
                    "activities": [
                        "Review: Identify given vs. prove in sample problems (10 min)",
                        "Demonstration: Complete proof with class input (15 min)",
                        "Guided practice: Fill-in-the-blank proofs (15 min)",
                        "Independent work: Students attempt simplified proofs (10 min)"
                    ],
                    "materials": ["Geometry software/tools", "Proof templates", "Triangle diagrams"],
                    "assessment": "Students complete one two-column proof with teacher feedback"
                }
            },
            "derivative_rules": {
                "common_issues": [
                    "Mixing up power rule, product rule, and chain rule applications",
                    "Forgetting to apply chain rule for composite functions",
                    "Arithmetic errors when combining rules"
                ],
                "lesson_plan": {
                    "title": "Derivative Rules Mastery: When and How to Apply Each Rule",
                    "duration": "45 minutes",
                    "objectives": [
                        "Identify which derivative rule applies to different function types",
                        "Apply chain rule correctly for composite functions",
                        "Combine multiple rules in complex expressions"
                    ],
                    "activities": [
                        "Quick review: Basic derivative rules with examples (8 min)",
                        "Decision tree: When to use each rule (12 min)",
                        "Worked examples: Complex functions requiring multiple rules (15 min)",
                        "Practice: Students solve and explain their rule choices (10 min)"
                    ],
                    "materials": ["Function cards", "Rule reference sheet", "Graphing calculator"],
                    "assessment": "Quiz on identifying and applying correct derivative rules"
                }
            },
            "integration_techniques": {
                "common_issues": [
                    "Difficulty choosing between substitution and integration by parts",
                    "Forgetting to add constant of integration",
                    "Errors in u-substitution setup and back-substitution"
                ],
                "lesson_plan": {
                    "title": "Integration Strategies: Choosing the Right Technique",
                    "duration": "50 minutes",
                    "objectives": [
                        "Recognize patterns that suggest specific integration techniques",
                        "Execute u-substitution correctly with proper back-substitution",
                        "Apply integration by parts using the LIATE rule"
                    ],
                    "activities": [
                        "Pattern recognition: Sort integrals by technique needed (10 min)",
                        "U-substitution walkthrough with common mistakes (15 min)",
                        "Integration by parts demonstration using LIATE (15 min)",
                        "Mixed practice with technique selection justification (10 min)"
                    ],
                    "materials": ["Integration technique flowchart", "Practice integral sets"],
                    "assessment": "Students solve 3 integrals using different techniques"
                }
            },
            "probability_concepts": {
                "common_issues": [
                    "Confusing independent vs. dependent events",
                    "Misapplying addition vs. multiplication rules",
                    "Difficulty with conditional probability calculations"
                ],
                "lesson_plan": {
                    "title": "Probability Fundamentals: Events, Rules, and Real Applications",
                    "duration": "45 minutes",
                    "objectives": [
                        "Distinguish between independent and dependent events",
                        "Apply appropriate probability rules for different scenarios",
                        "Calculate conditional probabilities using proper notation"
                    ],
                    "activities": [
                        "Real-world scenarios: Classify events as independent/dependent (10 min)",
                        "Interactive demo: Card draws and probability calculations (15 min)",
                        "Conditional probability with tree diagrams (15 min)",
                        "Application problems with peer discussion (5 min)"
                    ],
                    "materials": ["Playing cards", "Probability trees", "Real-world scenario cards"],
                    "assessment": "Problem set covering all three probability rule types"
                }
            }
        }
        
    def generate_teacher_cohort(self, teacher_id: str) -> Dict[str, Any]:
        """Generate mock teacher cohort data using realistic student IDs"""
        num_students = random.randint(6, 12)
        # Use realistic student IDs that match Prisma cuid format
        student_ids = self.student_ids[:num_students]
        
        return {
            "teacherId": teacher_id,
            "studentIds": student_ids,
            "totalStudents": num_students,
            "activeStudents": num_students,  # Assume all are active for mock data
            "dateRange": {
                "start": "2025-09-06",
                "end": "2025-09-13"
            }
        }
    
    def generate_sessions_per_student(self, teacher_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Generate mock sessions per student data"""
        cohort = self.generate_teacher_cohort(teacher_id)
        sessions_data = []
        
        for i, student_id in enumerate(cohort["studentIds"]):
            session_count = random.randint(2, 15)  # Realistic range
            sessions_data.append({
                "studentId": student_id,
                "sessionCount": session_count
            })
        
        return sorted(sessions_data, key=lambda x: x["sessionCount"], reverse=True)
    
    def generate_engagement_metrics(self) -> Dict[str, float]:
        """Generate mock engagement metrics"""
        return {
            "avgMessagesPerStudent": round(random.uniform(15, 45), 2),
            "avgMessagesPerClass": round(random.uniform(20, 50), 2),
            "avgSessionsPerDay": round(random.uniform(2, 8), 2)
        }
    
    def generate_session_metrics(self) -> Dict[str, Any]:
        """Generate mock session completion metrics"""
        total_sessions = random.randint(50, 150)
        completed_sessions = int(total_sessions * random.uniform(0.6, 0.9))
        
        return {
            "totalSessions": total_sessions,
            "completedSessions": completed_sessions,
            "completionRate": round((completed_sessions / total_sessions) * 100, 1),
            "avgDurationMinutes": round(random.uniform(12, 35), 1)
        }
    
    def generate_hourly_distribution(self) -> List[Dict[str, int]]:
        """Generate mock hourly message distribution"""
        hourly_data = []
        
        for hour in range(24):
            # Simulate realistic patterns - more activity during school hours
            if 8 <= hour <= 16:  # School hours
                message_count = random.randint(20, 80)
            elif 17 <= hour <= 21:  # After school
                message_count = random.randint(10, 40)
            else:  # Night/early morning
                message_count = random.randint(0, 5)
                
            hourly_data.append({
                "hour": hour,
                "messageCount": message_count
            })
        
        return hourly_data
    
    def generate_faqs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate mock FAQ data"""
        questions = [
            "How do I solve quadratic equations?",
            "What's the difference between sine and cosine?",
            "How do I find the derivative of x²?",
            "Can you explain the Pythagorean theorem?",
            "What is the chain rule in calculus?",
            "How do I factor polynomials?",
            "What's the area of a circle formula?",
            "How do I solve systems of equations?",
            "What is the quadratic formula?",
            "How do I graph linear functions?"
        ]
        
        faqs = []
        for i in range(min(limit, len(questions))):
            faqs.append({
                "questionText": questions[i],
                "category": random.choice(self.subjects),
                "frequencyCount": random.randint(5, 25),
                "successRate": random.randint(60, 95) if random.random() > 0.2 else None
            })
        
        return sorted(faqs, key=lambda x: x["frequencyCount"], reverse=True)
    
    def generate_misconceptions(self) -> List[Dict[str, Any]]:
        """Generate mock misconception data with lesson plan information"""
        misconceptions = []
        
        for category in self.misconception_categories:
            # Use detailed common issues from lesson plans if available
            if category in self.lesson_plans:
                common_issues = self.lesson_plans[category]["common_issues"]
            else:
                common_issues = [
                    f"Confusion about {category.replace('_', ' ')} basics",
                    f"Incorrect application of {category.replace('_', ' ')} rules",
                    f"Misunderstanding {category.replace('_', ' ')} concepts"
                ]
            
            misconceptions.append({
                "category": category,
                "frequency": random.randint(3, 15),
                "commonMisconceptions": random.sample(common_issues, random.randint(1, 3)),
                "lesson_plan": self.lesson_plans.get(category, {}).get("lesson_plan", {})
            })
        
        return sorted(misconceptions, key=lambda x: x["frequency"], reverse=True)
    
    def generate_ai_lesson_plans(self) -> List[Dict[str, Any]]:
        """Generate AI-powered lesson plans using Exa API"""
        try:
            from exa_lesson_generator import ExaLessonGenerator
            exa_generator = ExaLessonGenerator()
            
            # Get misconceptions data for AI generation
            misconceptions_data = self.generate_misconceptions()
            
            lesson_plans = []
            
            # Try to generate AI-powered lesson plans
            if exa_generator.client:
                # Generate general lesson plan for multiple misconceptions
                ai_lesson_content = exa_generator.search_lesson_plans(misconceptions_data)
                
                lesson_plans.append({
                    "title": "AI-Generated Lesson: Addressing Student Misconceptions",
                    "duration": "45-50 minutes",
                    "targetMisconception": "multiple_areas",
                    "aiGenerated": True,
                    "content": ai_lesson_content,
                    "source": "Exa AI API",
                    "basedOn": [m.get('category', '') for m in misconceptions_data[:3]],
                    "studentsAffected": sum(m.get('frequency', 0) for m in misconceptions_data[:3])
                })
                
                # Generate targeted lesson for top misconception
                if misconceptions_data:
                    top_misconception = misconceptions_data[0]
                    targeted_lesson_content = exa_generator.generate_targeted_lesson(
                        top_misconception.get('category', ''),
                        top_misconception.get('frequency', 0),
                        top_misconception.get('commonMisconceptions', [])
                    )
                    
                    lesson_plans.append({
                        "title": f"Targeted Lesson: {top_misconception.get('category', '').replace('_', ' ').title()}",
                        "duration": "45 minutes",
                        "targetMisconception": top_misconception.get('category', ''),
                        "aiGenerated": True,
                        "content": targeted_lesson_content,
                        "source": "Exa AI API - Targeted",
                        "studentsAffected": top_misconception.get('frequency', 0),
                        "commonIssues": top_misconception.get('commonMisconceptions', [])
                    })
                
                return lesson_plans
            else:
                print("Exa API not configured, falling back to template lessons")
                
        except ImportError:
            print("Exa lesson generator not available, using template lessons")
        except Exception as e:
            print(f"Error generating AI lessons: {e}, falling back to templates")
        
        # Fallback to template lesson plans with AI indicator
        return self.generate_template_lesson_plans()
    
    def generate_template_lesson_plans(self) -> List[Dict[str, Any]]:
        """Generate template lesson plans as fallback"""
        lesson_plans = []
        
        for category, plan_data in self.lesson_plans.items():
            lesson_plan = plan_data.get("lesson_plan", {}).copy()
            lesson_plan.update({
                "targetMisconception": category,
                "aiGenerated": False,
                "source": "Template",
                "note": "Template lesson - configure Exa API for AI-generated content",
                "commonIssues": plan_data.get("common_issues", [])
            })
            lesson_plans.append(lesson_plan)
        
        return lesson_plans
    
    def generate_student_summaries(self, teacher_id: str) -> str:
        """Generate aggregated student summaries using Exa AI from database summaries"""
        # Mock individual summaries from database (in real implementation, query Summary table)
        individual_summaries = [
            "Student shows strong progress in algebraic manipulation but struggles with word problems",
            "Excellent understanding of geometric concepts, needs work on proof writing", 
            "Good grasp of basic calculus, difficulty with integration techniques",
            "Strong in statistics, needs support with probability concepts",
            "Solid foundation in trigonometry, challenges with complex applications",
            "Demonstrates understanding of linear equations but needs practice with systems",
            "Excels at computational tasks, struggles with conceptual explanations"
        ]
        
        # Generate class summary from individual summaries only
        try:
            from exa_lesson_generator import ExaLessonGenerator
            exa_generator = ExaLessonGenerator()
            
            return exa_generator.generate_class_summary(individual_summaries)
                
        except Exception as e:
            # Generate class summary using NLP-powered summary generator
            try:
                from exa_lesson_generator import ExaLessonGenerator
                generator = ExaLessonGenerator()
                # Use NLP-based summary generation
                class_summary = generator.generate_class_summary(individual_summaries, use_nlp=True)
            except Exception as e:
                print(f"Error generating NLP summary: {e}")
                # Fallback to template summary
                class_summary = f"""Class Summary for {teacher_id}: Students demonstrate varied strengths across mathematical domains. 
        Common patterns include strong computational skills but challenges in application and proof-writing. 
        Word problem interpretation and multi-step reasoning appear as consistent areas for improvement. 
        Individual summaries: {'; '.join(individual_summaries[:4])}"""
            return class_summary
    
    def generate_complete_overview(self, teacher_id: str, start_date: str, end_date: str) -> dict:
        """Generate complete mock overview data"""
        cohort = self.generate_teacher_cohort(teacher_id)
        sessions_data = self.generate_sessions_per_student(teacher_id, start_date, end_date)
        
        return {
            "teacherId": teacher_id,
            "dateRange": {
                "start": start_date,
                "end": end_date
            },
            "cohort": cohort,
            "sessions": sessions_data,
            "engagement": self.generate_engagement_metrics(),
            "sessionMetrics": self.generate_session_metrics(),
            "hourlyDistribution": self.generate_hourly_data(teacher_id, start_date, end_date),
            "faqs": self.generate_faqs_data(teacher_id, start_date, end_date),
            "summaries": self.generate_student_summaries(teacher_id)
        }
    
    def generate_overall_summary(self, student_summaries: List[Dict[str, Any]]) -> str:
        """Generate an overall summary of all student summaries"""
        total_students = len(student_summaries)
        
        # Analyze trends
        improving_students = len([s for s in student_summaries if s["recentPerformance"]["improvementTrend"] == "improving"])
        high_engagement = len([s for s in student_summaries if s["recentPerformance"]["engagementLevel"] == "high"])
        avg_score = sum(s["recentPerformance"]["averageScore"] for s in student_summaries) / total_students
        
        # Collect common challenges
        all_challenges = []
        for summary in student_summaries:
            all_challenges.extend(summary["challenges"])
        
        challenge_counts = {}
        for challenge in all_challenges:
            challenge_counts[challenge] = challenge_counts.get(challenge, 0) + 1
        
        top_challenges = sorted(challenge_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Collect common strengths
        all_strengths = []
        for summary in student_summaries:
            all_strengths.extend(summary["strengths"])
        
        strength_counts = {}
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate comprehensive summary
        summary = f"""## Class Overview Summary

**Total Students:** {total_students}
**Class Average Score:** {avg_score:.1f}%
**Students Showing Improvement:** {improving_students}/{total_students} ({(improving_students/total_students)*100:.1f}%)
**High Engagement Students:** {high_engagement}/{total_students} ({(high_engagement/total_students)*100:.1f}%)

### Class Strengths
The class demonstrates strong capabilities in:
"""
        
        for i, (strength, count) in enumerate(top_strengths, 1):
            percentage = (count / total_students) * 100
            summary += f"{i}. **{strength.title()}** - {count} students ({percentage:.1f}%)\n"
        
        summary += f"""
### Common Challenges
Areas where multiple students need support:
"""
        
        for i, (challenge, count) in enumerate(top_challenges, 1):
            percentage = (count / total_students) * 100
            summary += f"{i}. **{challenge.title()}** - {count} students ({percentage:.1f}%)\n"
        
        summary += f"""
### Key Insights
- **Performance Trend:** {improving_students} students are showing improvement, indicating effective teaching strategies
- **Engagement Level:** {high_engagement} students show high engagement, suggesting good classroom dynamics
- **Priority Focus:** The most common challenge is "{top_challenges[0][0]}" affecting {top_challenges[0][1]} students
- **Building on Strengths:** Leverage the class's strength in "{top_strengths[0][0]}" to address weaker areas

### Recommended Class-Wide Strategies
1. **Targeted Intervention:** Create small groups to address "{top_challenges[0][0]}" challenges
2. **Peer Learning:** Pair students strong in "{top_strengths[0][0]}" with those needing support
3. **Differentiated Instruction:** Provide varied approaches for the {total_students - high_engagement} students with lower engagement
4. **Progress Monitoring:** Continue tracking the {improving_students} students showing positive trends

*Summary generated from individual student progress reports*
"""
        
        return summary
    
    def get_lesson_plan_for_category(self, category: str) -> Dict[str, Any]:
        """Get detailed lesson plan for a specific misconception category"""
        return self.lesson_plans.get(category, {})
    
    def generate_complete_overview(self, teacher_id: str, start_date: str, end_date: str) -> dict:
        """Generate complete mock overview data"""
        cohort = self.generate_teacher_cohort(teacher_id)
        sessions_data = self.generate_sessions_per_student(teacher_id, start_date, end_date)
        
        return {
            "teacherId": teacher_id,
            "dateRange": {
                "start": start_date,
                "end": end_date
            },
            "cohortInfo": {
                "totalStudents": cohort["totalStudents"],
                "studentIds": cohort["studentIds"]
            },
            "engagementMetrics": self.generate_engagement_metrics(),
            "sessionMetrics": self.generate_session_metrics(),
            "studentActivity": sessions_data,
            "topMisconceptions": self.generate_misconceptions()[:5]
        }
    
    def generate_hourly_data(self, teacher_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate complete hourly distribution data"""
        hourly_distribution = self.generate_hourly_distribution()
        total_messages = sum(h["messageCount"] for h in hourly_distribution)
        peak_hour = max(hourly_distribution, key=lambda x: x["messageCount"])
        
        return {
            "teacherId": teacher_id,
            "dateRange": {
                "start": start_date,
                "end": end_date
            },
            "hourlyDistribution": hourly_distribution,
            "summary": {
                "totalMessages": total_messages,
                "peakHour": peak_hour,
                "activeHours": len([h for h in hourly_distribution if h["messageCount"] > 0])
            }
        }
    
    def generate_faqs_data(self, teacher_id: str, start_date: str, end_date: str, limit: int = 10) -> Dict[str, Any]:
        """Generate complete FAQs and misconceptions data"""
        faqs = self.generate_faqs(limit)
        misconceptions = self.generate_misconceptions()
        
        # Group FAQs by category
        faqs_by_category = {}
        for faq in faqs:
            category = faq["category"]
            if category not in faqs_by_category:
                faqs_by_category[category] = []
            faqs_by_category[category].append({
                "question": faq["questionText"],
                "frequency": faq["frequencyCount"],
                "successRate": faq["successRate"]
            })
        
        return {
            "teacherId": teacher_id,
            "dateRange": {
                "start": start_date,
                "end": end_date
            },
            "topFaqs": faqs,
            "faqsByCategory": faqs_by_category,
            "misconceptions": misconceptions,
            "summary": {
                "totalFaqs": len(faqs),
                "categoriesCount": len(faqs_by_category),
                "avgSuccessRate": round(sum(f["successRate"] for f in faqs if f["successRate"]) / 
                                       len([f for f in faqs if f["successRate"]]), 1) if faqs else None
            }
        }
