#!/usr/bin/env python3
"""
Exa AI Lesson Plan Generator
Generates personalized lesson plans based on student misconceptions using Exa API.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from exa_py import Exa
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ExaLessonGenerator:
    """Generate lesson plans using Exa AI based on student misconceptions"""
    
    def __init__(self):
        """Initialize the Exa lesson generator with API credentials"""
        self.api_key = os.getenv('EXA_API_KEY')
        
        if self.api_key:
            try:
                # Initialize proper Exa client
                self.client = Exa(api_key=self.api_key)
                print("Exa client initialized successfully")
            except Exception as e:
                print(f"Error initializing Exa client: {e}")
                self.client = None
        else:
            print("No EXA_API_KEY found - using template fallbacks")
            self.client = None
    
    def generate_lesson_plan_query(self, faqs: List[Dict], student_summaries: str) -> str:
        """Generate a search query for technical lesson plans based on FAQ data"""
        if not faqs:
            return "mathematics teaching strategies lesson plan techniques"
        
        top_faq = faqs[0]
        category = top_faq.get('category', 'mathematics')
        frequency = top_faq.get('frequencyCount', 0)
        
        return f"advanced {category} teaching techniques lesson plan strategies student difficulties {category} pedagogy mathematics education methods"
    
    def search_lesson_plans(self, faqs: List[Dict[str, Any]], student_summaries: str) -> str:
        """
        Search for lesson plans using Exa AI based on FAQ data and summaries
        
        Args:
            faqs: List of frequently asked questions with categories and success rates
            student_summaries: Aggregated summary of student learning patterns
            
        Returns:
            Generated lesson plan content
        """
        if not self.client:
            return self._fallback_lesson_plan(faqs)
        
        top_faq = faqs[0] if faqs else {'category': 'mathematics', 'frequencyCount': 0, 'successRate': 0.7}
        query = self.generate_lesson_plan_query(faqs, student_summaries)
        
        try:
            # Use Exa search to find technical lesson plan content
            results = self.client.search_and_contents(
                query,
                num_results=5
            )
            
            lesson_content = self._format_exa_lesson_plan(
                results,
                top_faq.get('category', 'mathematics'),
                top_faq.get('frequencyCount', 0),
                top_faq.get('successRate', 0.7),
                student_summaries
            )
            return lesson_content
            
        except Exception as e:
            print(f"Error calling Exa API: {e}")
            if faqs and len(faqs) > 0:
                return self._fallback_5_point_lesson_plan(faqs[0].get('category', 'mathematics'), faqs[0].get('frequencyCount', 0), faqs[0].get('successRate', 0.7))
            else:
                return self._fallback_5_point_lesson_plan('mathematics', 0, 0.7)
    
    def generate_class_summary(self, individual_summaries: List[str], use_nlp: bool = True) -> str:
        """
        Generate an aggregated class summary from individual student summaries
        
        Args:
            individual_summaries: List of individual student summary strings from database
            use_nlp: Whether to use advanced NLP techniques (default: True)
            
        Returns:
            Comprehensive class summary based solely on individual summaries
        """
        if not individual_summaries:
            return "No individual student summaries available for analysis."
        
        if use_nlp:
            try:
                # Use advanced NLP-based summary generation
                from nlp_summary_generator import generate_nlp_based_summary
                return generate_nlp_based_summary(individual_summaries)
            except Exception as e:
                print(f"NLP summary generation failed: {e}")
                print("Falling back to keyword-based approach...")
        
        # Fallback to original keyword-based approach
        strengths = self._extract_strengths(individual_summaries)
        challenges = self._extract_challenges(individual_summaries)
        subject_patterns = self._extract_subject_patterns(individual_summaries)
        
        # Generate comprehensive class summary
        summary = self._format_aggregated_summary(
            individual_summaries, strengths, challenges, subject_patterns
        )
        return summary
    
    def _extract_strengths(self, summaries: List[str]) -> List[str]:
        """Extract common strengths from individual summaries"""
        strengths = []
        strength_keywords = ["strong", "excellent", "good grasp", "solid", "excels", "understanding", "progress"]
        
        for summary in summaries:
            summary_lower = summary.lower()
            for keyword in strength_keywords:
                if keyword in summary_lower:
                    # Extract the strength context
                    words = summary.split()
                    for i, word in enumerate(words):
                        if keyword in word.lower():
                            # Get surrounding context
                            start = max(0, i-2)
                            end = min(len(words), i+5)
                            strength_phrase = " ".join(words[start:end])
                            if strength_phrase not in strengths:
                                strengths.append(strength_phrase)
                            break
        
        return strengths[:5]  # Top 5 strengths
    
    def _extract_challenges(self, summaries: List[str]) -> List[str]:
        """Extract common challenges from individual summaries"""
        challenges = []
        challenge_keywords = ["struggles", "difficulty", "challenges", "needs work", "needs support", "problems"]
        
        for summary in summaries:
            summary_lower = summary.lower()
            for keyword in challenge_keywords:
                if keyword in summary_lower:
                    # Extract the challenge context
                    words = summary.split()
                    for i, word in enumerate(words):
                        if keyword in word.lower():
                            # Get surrounding context
                            start = max(0, i-2)
                            end = min(len(words), i+5)
                            challenge_phrase = " ".join(words[start:end])
                            if challenge_phrase not in challenges:
                                challenges.append(challenge_phrase)
                            break
        
        return challenges[:5]  # Top 5 challenges
    
    def _extract_subject_patterns(self, summaries: List[str]) -> dict:
        """Extract subject-specific patterns from summaries"""
        subjects = ["algebra", "geometry", "calculus", "statistics", "trigonometry"]
        patterns = {}
        
        for subject in subjects:
            subject_mentions = []
            for summary in summaries:
                if subject in summary.lower():
                    subject_mentions.append(summary)
            
            if subject_mentions:
                patterns[subject] = len(subject_mentions)
        
        return patterns
    
    def _format_aggregated_summary(self, summaries: List[str], strengths: List[str], challenges: List[str], subject_patterns: dict) -> str:
        """
        Format comprehensive class summary from extracted patterns using paragraph format
        
        Method for determining overall summary:
        1. Text analysis: Extract strength/challenge keywords and surrounding context
        2. Subject pattern analysis: Count subject mentions across all summaries
        3. Frequency analysis: Identify most common themes and issues
        4. Synthesis: Combine patterns into coherent narrative paragraphs
        """
        
        # Count students
        total_students = len(summaries)
        
        # Identify most common subjects
        top_subjects = sorted(subject_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create paragraph-style summary
        strengths_text = self._create_strengths_paragraph(strengths[:3])
        challenges_text = self._create_challenges_paragraph(challenges[:3])
        subjects_text = self._create_subjects_paragraph(top_subjects)
        
        summary = f"""**Class Learning Summary** ({total_students} students analyzed):

{strengths_text}

{challenges_text}

{subjects_text}

**Individual Student Summaries**: {' '.join([f"Student {i+1}: {summary}." for i, summary in enumerate(summaries)])}

**Overall Assessment**: This class demonstrates diverse mathematical learning patterns with varying strengths and challenges across computational and conceptual domains. The analysis reveals both individual differences and common themes that can inform targeted instructional approaches."""
        
        return summary
    
    def _create_strengths_paragraph(self, strengths: List[str]) -> str:
        """Create paragraph describing common strengths"""
        if not strengths:
            return "**Common Strengths**: No clear strength patterns identified across student summaries."
        
        # Clean up strength phrases and create coherent text
        cleaned_strengths = []
        for strength in strengths:
            # Extract key concepts from strength phrases
            if "strong" in strength.lower():
                cleaned_strengths.append("demonstrate strong foundational skills")
            elif "excellent" in strength.lower():
                cleaned_strengths.append("show excellent understanding")
            elif "good grasp" in strength.lower():
                cleaned_strengths.append("have good conceptual grasp")
        
        if cleaned_strengths:
            return f"**Common Strengths**: Students in this class {', '.join(cleaned_strengths[:2])} in various mathematical areas. These strengths provide a solid foundation for building more advanced concepts."
        else:
            return f"**Common Strengths**: Analysis of individual summaries reveals positive learning patterns including {', '.join(strengths[:2])}."
    
    def _create_challenges_paragraph(self, challenges: List[str]) -> str:
        """Create paragraph describing common challenges"""
        if not challenges:
            return "**Common Challenges**: No significant challenge patterns identified across student summaries."
        
        # Extract key challenge themes
        challenge_themes = []
        for challenge in challenges:
            if "word problems" in challenge.lower():
                challenge_themes.append("word problem interpretation")
            elif "difficulty" in challenge.lower():
                challenge_themes.append("conceptual difficulties")
            elif "struggles" in challenge.lower():
                challenge_themes.append("procedural struggles")
        
        if challenge_themes:
            return f"**Common Challenges**: The most prevalent learning challenges include {', '.join(challenge_themes[:2])}. These areas require focused attention and alternative instructional strategies to support student success."
        else:
            return f"**Common Challenges**: Students face similar difficulties in areas such as {', '.join(challenges[:2])}. Addressing these common challenges will benefit the entire class."
    
    def _create_subjects_paragraph(self, top_subjects: List[tuple]) -> str:
        """Create paragraph describing subject area patterns"""
        if not top_subjects:
            return "**Subject Focus Areas**: No clear subject patterns identified in the summaries."
        
        subject_list = [f"{subject} ({count} students)" for subject, count in top_subjects]
        return f"**Subject Focus Areas**: The analysis reveals that students are primarily engaged with {', '.join(subject_list)}. This distribution indicates the current mathematical focus areas and can guide curriculum planning and resource allocation."
    
    def _fallback_class_summary(self, summaries: List[str]) -> str:
        """Fallback summary when other methods fail"""
        if not summaries:
            return "No individual student summaries available for analysis."
        
        return f"""**Class Learning Summary**:
Students demonstrate varied mathematical abilities across different domains.

**Individual Student Summaries**:
{chr(10).join([f"{i+1}. {summary}" for i, summary in enumerate(summaries)])}

**Key Areas for Focus**: Based on individual patterns, focus on addressing common learning challenges."""

    def generate_targeted_lesson(self, category: str, frequency: int, success_rate: float, student_summaries: str) -> str:
        """
        Generate targeted lesson plans based on student struggles and teaching opportunities
        
        Args:
            category: FAQ category (e.g., 'calculus', 'algebra')
            frequency: How many times students asked about this topic
            success_rate: Success rate for this topic (0.0 to 1.0)
            student_summaries: Aggregated summary of student learning patterns
            
        Returns:
            Generated lesson plan content focused on student needs
        """
        return self._generate_targeted_lesson_plan(category, frequency, success_rate, student_summaries)
    
    def _generate_targeted_lesson_plan(self, category: str, frequency: int, success_rate: float, student_summaries: str) -> str:
        """Generate a targeted lesson plan based on student struggles and data"""
        topic = category.replace('_', ' ').title()
        
        # Analyze student struggles from summaries
        struggles = self._extract_common_struggles(student_summaries, category)
        
        # Get technical content for the specific math topic
        technical_content = self._get_technical_math_content(category)
        
        lesson_plan = f"""# {topic} - Advanced Mathematical Lesson Plan

## Student Context Analysis
- **Topic Focus**: {topic}
- **Student Questions**: {frequency} students have asked about this topic
- **Current Success Rate**: {success_rate:.1%}
- **Key Student Struggles**: {', '.join(struggles) if struggles else 'General comprehension difficulties'}

## Teaching Strategy (Based on Student Data)
"""
        
        # Add targeted strategies based on success rate
        if success_rate < 0.7:
            lesson_plan += f"""
### Phase 1: Mathematical Foundation Building (20 minutes)
- **Diagnostic Assessment**: Quick problem set to identify specific gaps
- **Prerequisite Review**: Focus on the mathematical concepts students are missing
- **Common Error Analysis**: Address the top {frequency} misconceptions with worked examples
- **Conceptual Connections**: Use multiple representations (algebraic, graphical, numerical)

### Phase 2: Guided Mathematical Practice (25 minutes)
- **Structured Problem Solving**: Step-by-step approach using mathematical reasoning
- **Think-Aloud Protocol**: Students verbalize their mathematical thinking process
- **Error Correction**: Immediate feedback on mathematical procedures and logic
- **Scaffolded Examples**: Progress from simple to complex applications

### Phase 3: Independent Mathematical Application (10 minutes)
- **Targeted Problem Sets**: Focus on the specific mathematical skills identified as weaknesses
- **Mathematical Justification**: Require students to explain their reasoning
- **Peer Mathematical Discourse**: Students explain solutions to each other using proper terminology
"""
        else:
            lesson_plan += f"""
### Phase 1: Mathematical Review & Extension (10 minutes)
- **Quick Diagnostic**: Verify mastery of core concepts
- **Advanced Connections**: Link to higher-level mathematical concepts

### Phase 2: Advanced Mathematical Applications (30 minutes)
- **Complex Problem Solving**: Multi-step problems requiring mathematical reasoning
- **Real-World Mathematical Modeling**: Apply {topic.lower()} to authentic scenarios
- **Mathematical Investigation**: Open-ended exploration of mathematical relationships
- **Proof and Reasoning**: Construct mathematical arguments and justifications

### Phase 3: Mathematical Assessment & Challenge (15 minutes)
- **Comprehensive Assessment**: Problems testing deep understanding
- **Mathematical Extensions**: Advanced topics for accelerated learners
- **Cross-Curricular Connections**: Link mathematics to other disciplines
"""
        
        lesson_plan += f"""
## Mathematical Differentiation Strategies
- **For struggling students**: 
  - Provide mathematical scaffolds and step-by-step solution templates
  - Use concrete mathematical examples before abstract concepts
  - Break complex problems into smaller mathematical sub-problems
- **For advanced students**: 
  - Extend to higher-level mathematical applications and proofs
  - Introduce related advanced mathematical topics
  - Challenge with open-ended mathematical investigations
- **Mathematical Learning Styles**:
  - **Visual**: Mathematical graphs, diagrams, and geometric representations
  - **Analytical**: Algebraic manipulations and symbolic reasoning
  - **Applied**: Real-world mathematical modeling and applications

## Sample Technical Problems
{self._generate_sample_problems(category, success_rate)}

*This advanced mathematical lesson plan integrates rigorous content with data-driven instruction to maximize student learning outcomes in {topic.lower()}.*"""
        
        return lesson_plan
    
    def _extract_common_struggles(self, student_summaries: str, category: str) -> List[str]:
        """Extract common struggle areas from student summaries"""
        if not student_summaries:
            return ["Basic concept understanding", "Problem-solving approach"]
        
        struggles = []
        summary_lower = student_summaries.lower()
        
        # Look for common struggle indicators
        struggle_keywords = {
            'algebra': ['equations', 'variables', 'solving', 'factoring'],
            'calculus': ['derivatives', 'integrals', 'limits', 'chain rule'],
            'geometry': ['proofs', 'angles', 'area', 'volume'],
            'statistics': ['probability', 'distributions', 'hypothesis testing']
        }
        
        category_keywords = struggle_keywords.get(category.lower(), ['problem solving', 'concepts'])
        
        for keyword in category_keywords:
            if keyword in summary_lower:
                struggles.append(keyword.title())
        
        # Look for general struggle indicators
        if 'difficult' in summary_lower or 'struggle' in summary_lower:
            struggles.append("Conceptual understanding")
        if 'confused' in summary_lower or 'unclear' in summary_lower:
            struggles.append("Clarity of explanations")
        
        return struggles[:3]  # Return top 3 struggles
    
    def _format_exa_lesson_plan(self, results: List[Dict], category: str, frequency: int, success_rate: float, student_summaries: str) -> str:
        """Format Exa search results into a concise 5-bullet point lesson plan"""
        topic = category.replace('_', ' ').title()
        
        # Extract key teaching strategies from Exa results
        teaching_strategies = self._extract_teaching_strategies(results)
        
        lesson_plan = f"""# {topic} - Technical Lesson Plan

## Student Context
- **Topic**: {topic} ({frequency} student questions, {success_rate:.1%} success rate)
- **Key Challenges**: {self._extract_student_challenges(student_summaries, category)}

## 5-Point Teaching Strategy (Based on Educational Research)

{teaching_strategies}

---
*Generated using Exa AI educational research and student analytics data*
"""
        return lesson_plan
    
    def _extract_teaching_strategies(self, results) -> str:
        """Extract 5 key teaching strategies from Exa search results"""
        strategies = []
        
        # Handle Exa SearchResponse object properly
        try:
            if hasattr(results, 'results'):
                search_results = results.results
            else:
                search_results = results
                
            # Process Exa search results to extract teaching advice
            for i, result in enumerate(search_results[:5], 1):
                if hasattr(result, 'text') and result.text:
                    # Extract key teaching points from the content
                    content = result.text[:500]  # First 500 chars for relevance
                    strategy = self._extract_strategy_from_content(content, i)
                    strategies.append(f"**{i}.** {strategy}")
        except Exception as e:
            print(f"Error processing Exa results: {e}")
        
        # Fill in with generic strategies if not enough results
        while len(strategies) < 5:
            num = len(strategies) + 1
            strategies.append(f"**{num}.** Use multiple representations and check for understanding frequently")
        
        return '\n\n'.join(strategies)
    
    def _extract_strategy_from_content(self, content: str, number: int) -> str:
        """Extract a teaching strategy from Exa content"""
        content_lower = content.lower()
        
        # Look for key teaching strategy keywords
        if 'visual' in content_lower or 'diagram' in content_lower or 'graph' in content_lower:
            return "Use visual representations and diagrams to help students understand abstract concepts"
        elif 'practice' in content_lower or 'exercise' in content_lower:
            return "Provide structured practice with immediate feedback and error correction"
        elif 'misconception' in content_lower or 'error' in content_lower or 'mistake' in content_lower:
            return "Address common misconceptions explicitly with targeted examples and explanations"
        elif 'step' in content_lower or 'process' in content_lower or 'method' in content_lower:
            return "Break down complex problems into manageable steps with clear procedures"
        elif 'connect' in content_lower or 'relate' in content_lower or 'application' in content_lower:
            return "Connect new concepts to prior knowledge and real-world applications"
        elif 'group' in content_lower or 'collaborative' in content_lower or 'peer' in content_lower:
            return "Use collaborative learning and peer explanations to deepen understanding"
        elif 'assess' in content_lower or 'check' in content_lower or 'evaluate' in content_lower:
            return "Implement frequent formative assessment to monitor student progress"
        else:
            # Default strategies based on position
            defaults = [
                "Start with concrete examples before introducing abstract concepts",
                "Use scaffolded questioning to guide student discovery",
                "Encourage mathematical discourse and explanation of reasoning",
                "Provide multiple pathways to solution and celebrate different approaches",
                "End with synthesis and connection to upcoming topics"
            ]
            return defaults[(number - 1) % len(defaults)]
    
    def _extract_student_challenges(self, student_summaries: str, category: str) -> str:
        """Extract main student challenges from summaries"""
        if not student_summaries:
            return "General conceptual understanding"
        
        challenges = []
        summary_lower = student_summaries.lower()
        
        # Look for specific challenge indicators
        if 'difficult' in summary_lower or 'struggle' in summary_lower:
            challenges.append("conceptual understanding")
        if 'confused' in summary_lower or 'unclear' in summary_lower:
            challenges.append("clarity of explanations")
        if 'problem' in summary_lower or 'solving' in summary_lower:
            challenges.append("problem-solving approach")
        if 'step' in summary_lower or 'process' in summary_lower:
            challenges.append("procedural fluency")
        
        return ', '.join(challenges[:3]) if challenges else "General mathematical reasoning"
    
    def _get_technical_math_content(self, category: str) -> dict:
        """Generate technical mathematical content for specific topics"""
        category_lower = category.lower()
        
        if 'algebra' in category_lower or 'equation' in category_lower:
            return {
                'prerequisites': """- Linear equations in one variable: ax + b = c
- Properties of equality: addition, subtraction, multiplication, division
- Order of operations (PEMDAS/BODMAS)
- Basic algebraic manipulation and simplification""",
                
                'core_concepts': """**Linear Equations**: ax + b = c where a ≠ 0
- **Standard Form**: Ax + By = C
- **Slope-Intercept Form**: y = mx + b where m = slope, b = y-intercept
- **Point-Slope Form**: y - y₁ = m(x - x₁)

**Quadratic Equations**: ax² + bx + c = 0 where a ≠ 0
- **Quadratic Formula**: x = (-b ± √(b² - 4ac)) / (2a)
- **Discriminant**: Δ = b² - 4ac determines nature of roots
- **Factoring Methods**: (x - r₁)(x - r₂) = 0 where r₁, r₂ are roots""",
                
                'objectives': """1. Solve linear equations using algebraic manipulation: ax + b = c → x = (c - b)/a
2. Apply the quadratic formula to find roots of ax² + bx + c = 0
3. Analyze discriminant values: Δ > 0 (two real roots), Δ = 0 (one root), Δ < 0 (complex roots)
4. Factor quadratic expressions using techniques like grouping and completing the square
5. Graph linear and quadratic functions and interpret their key features""",
                
                'formulation': """**Linear System Solving**:
Given: {ax + by = c₁, dx + ey = c₂}
Matrix form: [a b][x] = [c₁]
             [d e][y]   [c₂]

Solution using Cramer's Rule:
x = |c₁ b|/|a b|, y = |a c₁|/|a b|
    |c₂ e| |d e|      |d c₂| |d e|

**Quadratic Analysis**:
For f(x) = ax² + bx + c:
- Vertex: (-b/2a, f(-b/2a))
- Axis of symmetry: x = -b/2a
- Roots: x = (-b ± √Δ)/2a where Δ = b² - 4ac"""
            }
            
        elif 'calculus' in category_lower or 'derivative' in category_lower or 'integral' in category_lower:
            return {
                'prerequisites': "",
                'core_concepts': "",
                'objectives': "",
                'formulation': ""
            }
            
        elif 'geometry' in category_lower or 'proof' in category_lower:
            return {
                'prerequisites': "",
                'core_concepts': "",
                'objectives': "",
                'formulation': ""
            }
            
        elif 'statistics' in category_lower or 'probability' in category_lower:
            return {
                'prerequisites': "",
                'core_concepts': "",
                'objectives': "",
                'formulation': ""
            }
            
        else:
            # Default mathematical content - simplified
            return {
                'prerequisites': "",
                'core_concepts': "",
                'objectives': "",
                'formulation': ""
            }
    
    def _generate_sample_problems(self, category: str, success_rate: float) -> str:
        """Generate technical sample problems for the specific mathematical topic"""
        category_lower = category.lower()
        difficulty = "Advanced" if success_rate > 0.8 else "Intermediate" if success_rate > 0.6 else "Foundational"
        
        if 'algebra' in category_lower or 'equation' in category_lower:
            if success_rate < 0.6:
                return f"""**{difficulty} Level Problems:**

1. **Linear Equation Solving**: 
   Solve: 3(2x - 4) + 5 = 2(x + 3) - 1
   Show all algebraic steps and verify your solution.

2. **System of Linear Equations**:
   Solve using substitution method:
   {{2x + 3y = 7
   {{x - y = 1
   
3. **Quadratic Factoring**:
   Factor completely: x² - 5x - 14
   Then solve x² - 5x - 14 = 0"""
            else:
                return f"""**{difficulty} Level Problems:**

1. **Complex Quadratic Analysis**:
   For f(x) = 2x² - 8x + 3:
   a) Find vertex using completing the square
   b) Determine axis of symmetry and y-intercept
   c) Solve f(x) = 0 using quadratic formula
   d) Sketch the graph showing all key features

2. **System with Parameters**:
   For what values of k does the system have:
   {{kx + 2y = 4
   {{3x + ky = 6
   a) Exactly one solution  b) No solution  c) Infinitely many solutions

3. **Rational Equation Application**:
   A boat travels 60 km upstream in the same time it takes to travel 100 km downstream.
   If the current speed is 5 km/h, find the boat's speed in still water."""
                
        elif 'calculus' in category_lower:
            if success_rate < 0.6:
                return f"""**{difficulty} Level Problems:**

1. **Basic Derivative Computation**:
   Find f'(x) for: f(x) = 3x⁴ - 2x³ + 5x - 7
   Show each step using power rule.

2. **Chain Rule Application**:
   Find dy/dx: y = (2x³ - 1)⁵
   
3. **Simple Integration**:
   Evaluate: ∫(4x³ - 6x² + 2x) dx"""
            else:
                return f"""**{difficulty} Level Problems:**

1. **Optimization Problem**:
   A rectangular box with square base has surface area 150 cm².
   Find dimensions that maximize volume. Use calculus to:
   a) Set up the constraint equation
   b) Express volume as function of one variable
   c) Find critical points and verify maximum

2. **Related Rates**:
   A spherical balloon is inflated at 20 cm³/min.
   How fast is the radius changing when r = 5 cm?
   (V = (4/3)πr³)

3. **Definite Integration**:
   Evaluate: ∫₀² (x² + 1)√(x³ + 3x + 2) dx
   Use substitution method."""
                
        elif 'geometry' in category_lower:
            if success_rate < 0.6:
                return f"""**{difficulty} Level Problems:**

1. **Triangle Congruence Proof**:
   Given: AB ≅ CD, ∠A ≅ ∠C, ∠B ≅ ∠D
   Prove: △ABC ≅ △CDA
   Write formal two-column proof.

2. **Area Calculation**:
   Find the area of triangle with vertices A(1,2), B(5,4), C(3,7)
   Use coordinate geometry methods.

3. **Circle Properties**:
   In circle O, chord AB = 8 cm and is 3 cm from center.
   Find the radius of the circle."""
            else:
                return f"""**{difficulty} Level Problems:**

1. **Advanced Proof (Similarity)**:
   Prove: If two triangles have two pairs of sides proportional and 
   included angles equal, then the triangles are similar.
   Provide complete formal proof.

2. **3D Geometry**:
   A right circular cone has base radius 6 cm and height 8 cm.
   A plane parallel to the base cuts the cone 3 cm from the apex.
   Find: a) Radius of circular cross-section
        b) Volume of smaller cone
        c) Volume of frustum

3. **Coordinate Geometry Proof**:
   Prove that the diagonals of a rhombus are perpendicular bisectors
   of each other using coordinate geometry."""
                
        elif 'statistics' in category_lower:
            if success_rate < 0.6:
                return f"""**{difficulty} Level Problems:**

1. **Basic Probability**:
   A bag contains 5 red, 3 blue, and 2 green marbles.
   Find P(red or blue) when drawing one marble.

2. **Normal Distribution**:
   Heights are normally distributed with μ = 170 cm, σ = 8 cm.
   Find P(162 < X < 178).

3. **Sample Statistics**:
   Data: 12, 15, 18, 20, 22, 25, 28
   Calculate: mean, median, standard deviation."""
            else:
                return f"""**{difficulty} Level Problems:**

1. **Hypothesis Testing**:
   A company claims their light bulbs last 1000 hours on average.
   Sample of 36 bulbs: x̄ = 980 hours, s = 120 hours.
   Test at α = 0.05 level. State hypotheses, calculate test statistic,
   find p-value, and make conclusion.

2. **Confidence Interval**:
   Construct 95% confidence interval for population proportion
   if 180 out of 400 surveyed support a proposal.
   Interpret the result.

3. **Regression Analysis**:
   Given correlation r = 0.85 between study hours (x) and test scores (y).
   If x̄ = 6, sx = 2, ȳ = 78, sy = 12:
   a) Find regression equation ŷ = a + bx
   b) Predict score for student who studies 8 hours
   c) Calculate coefficient of determination R²"""
                
        else:
            return f"""**{difficulty} Level Mathematical Problems:**

1. **Problem-Solving Application**:
   Use mathematical reasoning to solve a multi-step problem
   involving the concepts from {category}.

2. **Mathematical Modeling**:
   Create a mathematical model for a real-world scenario
   related to {category} concepts.

3. **Proof and Reasoning**:
   Construct a logical argument demonstrating a key property
   or theorem related to {category}."""
    
    
    def _fallback_5_point_lesson_plan(self, category: str, frequency: int, success_rate: float) -> str:
        """Generate a 5-point lesson plan when Exa API is unavailable"""
        topic = category.replace('_', ' ').title()
        
        return f"""# {topic} - Technical Lesson Plan

## Student Context
- **Topic**: {topic} ({frequency} student questions, {success_rate:.1%} success rate)
- **Key Challenges**: Common conceptual understanding difficulties

## 5-Point Teaching Strategy (Template)

**1.** Start with diagnostic assessment to identify specific knowledge gaps and misconceptions

**2.** Use visual representations and concrete examples to build conceptual understanding

**3.** Provide structured, step-by-step problem-solving practice with immediate feedback

**4.** Implement collaborative learning where students explain their reasoning to peers

**5.** End with formative assessment and connection to real-world applications

---
*Template lesson plan. Configure EXA_API_KEY for research-based content.*
"""
    
    def _fallback_lesson_plan(self, category: str) -> str:
        """Generate a basic lesson plan when Exa API is unavailable"""
        topic = category.replace('_', ' ').title()
        
        return f"""# Template Lesson Plan: {topic}

## Overview
This is a template lesson plan generated when Exa AI is unavailable.

## Objective
Help students understand {topic.lower()} concepts and address common questions.

## Materials
- Whiteboard or projector
- Practice worksheets
- Calculator (if needed)

## Lesson Structure
1. **Review** (10 minutes): Quick review of prerequisite concepts
2. **Introduction** (15 minutes): Introduce new {topic.lower()} concepts
3. **Guided Practice** (15 minutes): Work through examples together
4. **Independent Practice** (10 minutes): Students work on problems individually
5. **Wrap-up** (5 minutes): Address questions and preview next lesson

## Assessment
- Exit ticket with 2-3 practice problems
- Observe student work during independent practice

*Note: This is a template lesson plan. For AI-generated content, please configure your EXA_API_KEY.*
"""
    
    def _fallback_single_lesson(self, faq_category: str, frequency: int, success_rate: float) -> str:
        """Fallback for single lesson generation"""
        return f"""# Targeted Lesson: {faq_category.replace('_', ' ').title()}
        
**Question Frequency:** Asked {frequency} times by students
**Current Success Rate:** {success_rate}%

**Lesson Structure:**
1. **Diagnostic Check** (5 min): Quick assessment of current understanding
2. **Concept Review** (15 min): Address frequently asked questions directly
3. **Guided Practice** (20 min): Step-by-step problem solving
4. **Independent Work** (5 min): Students practice with support

**Key Teaching Points:**
- Address the most common questions explicitly
- Use multiple representations (visual, verbal, symbolic)
- Provide immediate feedback and correction
- Focus on improving success rate

*Configure Exa API key for more detailed, research-based lesson plans.*
"""

# Example usage and testing
if __name__ == "__main__":
    # Test the lesson generator
    generator = ExaLessonGenerator()
    
    # Mock misconceptions data
    test_misconceptions = [
        {
            "category": "algebraic_equations",
            "frequency": 9,
            "commonMisconceptions": [
                "Students confuse solving for x with substituting values",
                "Difficulty with multi-step equations and order of operations"
            ]
        },
        {
            "category": "geometric_proofs", 
            "frequency": 7,
            "commonMisconceptions": [
                "Students struggle with logical reasoning and proof structure"
            ]
        }
    ]
    
    test_summaries = "Students are struggling with word problem interpretation and showing work clearly. Many students have difficulty with algebraic equations and geometric proofs."
    
    print("=== Testing Exa Lesson Generator ===")
    print("\n1. Generated Query:")
    query = generator.generate_lesson_plan_query(test_misconceptions, test_summaries)
    print(query)
    
    print("\n2. Generated Lesson Plan:")
    lesson_plan = generator.search_lesson_plans(test_misconceptions, test_summaries)
    print(lesson_plan)
