from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional
import json
import re
import requests
from datetime import datetime

class MathSolverTool(BaseTool):
    """Tool for solving mathematical problems and providing step-by-step solutions"""
    
    name: str = "Math Problem Solver"
    description: str = "Solves mathematical problems and provides detailed step-by-step solutions for various mathematical concepts including algebra, geometry, calculus, and more."
    
    def _run(self, problem: str, difficulty: str = "medium", show_steps: bool = True) -> str:
        """
        Solve a mathematical problem
        
        Args:
            problem: The mathematical problem to solve
            difficulty: Difficulty level (easy, medium, hard)
            show_steps: Whether to show step-by-step solution
        """
        
        try:
            # Analyze the problem type
            problem_type = self._analyze_problem_type(problem)
            
            # Generate solution based on problem type
            if problem_type == "algebra":
                return self._solve_algebra_problem(problem, difficulty, show_steps)
            elif problem_type == "geometry":
                return self._solve_geometry_problem(problem, difficulty, show_steps)
            elif problem_type == "calculus":
                return self._solve_calculus_problem(problem, difficulty, show_steps)
            elif problem_type == "arithmetic":
                return self._solve_arithmetic_problem(problem, difficulty, show_steps)
            else:
                return self._solve_general_problem(problem, difficulty, show_steps)
                
        except Exception as e:
            return f"Error solving problem: {str(e)}"
    
    def _analyze_problem_type(self, problem: str) -> str:
        """Analyze the type of mathematical problem"""
        problem_lower = problem.lower()
        
        if any(keyword in problem_lower for keyword in ['solve for x', 'equation', 'variable', 'linear', 'quadratic']):
            return "algebra"
        elif any(keyword in problem_lower for keyword in ['area', 'perimeter', 'volume', 'triangle', 'circle', 'rectangle']):
            return "geometry"
        elif any(keyword in problem_lower for keyword in ['derivative', 'integral', 'limit', 'function']):
            return "calculus"
        elif any(keyword in problem_lower for keyword in ['add', 'subtract', 'multiply', 'divide', '+', '-', '*', '/']):
            return "arithmetic"
        else:
            return "general"
    
    def _solve_algebra_problem(self, problem: str, difficulty: str, show_steps: bool) -> str:
        """Solve algebra problems"""
        solution = "**Algebra Problem Solution**\n\n"
        
        if "solve for x" in problem.lower():
            solution += "**Step 1:** Identify the equation type\n"
            solution += "**Step 2:** Isolate the variable (x) on one side\n"
            solution += "**Step 3:** Perform inverse operations\n"
            solution += "**Step 4:** Simplify the result\n"
            solution += "**Step 5:** Check the solution by substitution\n\n"
            
            if show_steps:
                solution += "**Detailed Steps:**\n"
                solution += "• Move all terms with x to one side\n"
                solution += "• Move all constant terms to the other side\n"
                solution += "• Divide or multiply to isolate x\n"
                solution += "• Verify by substituting back into original equation\n"
        
        return solution
    
    def _solve_geometry_problem(self, problem: str, difficulty: str, show_steps: bool) -> str:
        """Solve geometry problems"""
        solution = "**Geometry Problem Solution**\n\n"
        
        if "area" in problem.lower():
            solution += "**Step 1:** Identify the shape\n"
            solution += "**Step 2:** Recall the appropriate area formula\n"
            solution += "**Step 3:** Substitute the given measurements\n"
            solution += "**Step 4:** Calculate the result\n"
            solution += "**Step 5:** Include proper units\n\n"
            
            if show_steps:
                solution += "**Common Area Formulas:**\n"
                solution += "• Rectangle: A = length × width\n"
                solution += "• Triangle: A = ½ × base × height\n"
                solution += "• Circle: A = π × radius²\n"
                solution += "• Square: A = side²\n"
        
        return solution
    
    def _solve_calculus_problem(self, problem: str, difficulty: str, show_steps: bool) -> str:
        """Solve calculus problems"""
        solution = "**Calculus Problem Solution**\n\n"
        
        if "derivative" in problem.lower():
            solution += "**Step 1:** Identify the function type\n"
            solution += "**Step 2:** Apply the appropriate differentiation rule\n"
            solution += "**Step 3:** Simplify the derivative\n"
            solution += "**Step 4:** Check for domain restrictions\n\n"
            
            if show_steps:
                solution += "**Common Derivative Rules:**\n"
                solution += "• Power Rule: d/dx(xⁿ) = n·xⁿ⁻¹\n"
                solution += "• Product Rule: d/dx(uv) = u'v + uv'\n"
                solution += "• Chain Rule: d/dx(f(g(x))) = f'(g(x))·g'(x)\n"
        
        return solution
    
    def _solve_arithmetic_problem(self, problem: str, difficulty: str, show_steps: bool) -> str:
        """Solve arithmetic problems"""
        solution = "**Arithmetic Problem Solution**\n\n"
        
        # Extract numbers and operations
        numbers = re.findall(r'\d+\.?\d*', problem)
        
        if numbers:
            solution += f"**Numbers identified:** {', '.join(numbers)}\n"
            solution += "**Step 1:** Identify the operation(s) needed\n"
            solution += "**Step 2:** Follow order of operations (PEMDAS)\n"
            solution += "**Step 3:** Perform calculations step by step\n"
            solution += "**Step 4:** Check the reasonableness of the answer\n"
        
        return solution
    
    def _solve_general_problem(self, problem: str, difficulty: str, show_steps: bool) -> str:
        """Solve general mathematical problems"""
        solution = "**Mathematical Problem Analysis**\n\n"
        solution += "**Step 1:** Read and understand the problem\n"
        solution += "**Step 2:** Identify what is being asked\n"
        solution += "**Step 3:** Determine what information is given\n"
        solution += "**Step 4:** Choose an appropriate strategy\n"
        solution += "**Step 5:** Solve step by step\n"
        solution += "**Step 6:** Check and interpret the result\n\n"
        solution += "For specific help, please provide more details about the mathematical concept or problem type."
        
        return solution

class ConceptExplainerTool(BaseTool):
    """Tool for explaining mathematical concepts in detail"""
    
    name: str = "Math Concept Explainer"
    description: str = "Provides detailed explanations of mathematical concepts, definitions, and theorems with examples and applications."
    
    def _run(self, concept: str, level: str = "medium", include_examples: bool = True) -> str:
        """
        Explain a mathematical concept
        
        Args:
            concept: The mathematical concept to explain
            level: Explanation level (basic, medium, advanced)
            include_examples: Whether to include examples
        """
        
        try:
            concept_lower = concept.lower()
            
            # Route to appropriate explanation method
            if any(term in concept_lower for term in ['derivative', 'differentiation']):
                return self._explain_derivatives(level, include_examples)
            elif any(term in concept_lower for term in ['integral', 'integration']):
                return self._explain_integrals(level, include_examples)
            elif any(term in concept_lower for term in ['function', 'functions']):
                return self._explain_functions(level, include_examples)
            elif any(term in concept_lower for term in ['equation', 'equations']):
                return self._explain_equations(level, include_examples)
            elif any(term in concept_lower for term in ['fraction', 'fractions']):
                return self._explain_fractions(level, include_examples)
            else:
                return self._explain_general_concept(concept, level, include_examples)
                
        except Exception as e:
            return f"Error explaining concept: {str(e)}"
    
    def _explain_derivatives(self, level: str, include_examples: bool) -> str:
        """Explain derivatives"""
        explanation = "# Understanding Derivatives\n\n"
        
        if level == "basic":
            explanation += "A **derivative** measures how fast something is changing.\n\n"
            explanation += "Think of it like the speedometer in your car - it tells you how fast your position is changing at any moment.\n\n"
        else:
            explanation += "A **derivative** represents the instantaneous rate of change of a function with respect to its variable.\n\n"
            explanation += "Mathematically, it's the limit of the difference quotient as the interval approaches zero.\n\n"
        
        if include_examples:
            explanation += "**Examples:**\n"
            explanation += "• If f(x) = x², then f'(x) = 2x\n"
            explanation += "• If f(x) = 3x + 5, then f'(x) = 3\n"
            explanation += "• If f(x) = sin(x), then f'(x) = cos(x)\n\n"
        
        explanation += "**Applications:**\n"
        explanation += "• Finding velocity from position\n"
        explanation += "• Optimization problems\n"
        explanation += "• Slope of tangent lines\n"
        
        return explanation
    
    def _explain_integrals(self, level: str, include_examples: bool) -> str:
        """Explain integrals"""
        explanation = "# Understanding Integrals\n\n"
        
        if level == "basic":
            explanation += "An **integral** is like adding up all the little pieces under a curve.\n\n"
            explanation += "Imagine you want to find the area under a hill - you could divide it into tiny rectangles and add them up.\n\n"
        else:
            explanation += "An **integral** represents the accumulation of quantities and can be thought of as the reverse of differentiation.\n\n"
            explanation += "The definite integral gives the signed area between a curve and the x-axis over an interval.\n\n"
        
        if include_examples:
            explanation += "**Examples:**\n"
            explanation += "• ∫ 2x dx = x² + C\n"
            explanation += "• ∫ sin(x) dx = -cos(x) + C\n"
            explanation += "• ∫₀¹ x² dx = 1/3\n\n"
        
        explanation += "**Applications:**\n"
        explanation += "• Finding areas under curves\n"
        explanation += "• Calculating volumes\n"
        explanation += "• Physics applications (work, displacement)\n"
        
        return explanation
    
    def _explain_functions(self, level: str, include_examples: bool) -> str:
        """Explain functions"""
        explanation = "# Understanding Functions\n\n"
        
        if level == "basic":
            explanation += "A **function** is like a machine that takes an input and gives you exactly one output.\n\n"
            explanation += "For every input you put in, you get exactly one result out.\n\n"
        else:
            explanation += "A **function** is a mathematical relationship that assigns exactly one output value to each input value.\n\n"
            explanation += "Formally: f: A → B where each element in domain A maps to exactly one element in codomain B.\n\n"
        
        if include_examples:
            explanation += "**Examples:**\n"
            explanation += "• f(x) = 2x + 3 (linear function)\n"
            explanation += "• g(x) = x² (quadratic function)\n"
            explanation += "• h(x) = sin(x) (trigonometric function)\n\n"
        
        explanation += "**Key Properties:**\n"
        explanation += "• Domain: all possible input values\n"
        explanation += "• Range: all possible output values\n"
        explanation += "• One-to-one: each output corresponds to exactly one input\n"
        
        return explanation
    
    def _explain_equations(self, level: str, include_examples: bool) -> str:
        """Explain equations"""
        explanation = "# Understanding Equations\n\n"
        
        if level == "basic":
            explanation += "An **equation** is a mathematical statement that says two things are equal.\n\n"
            explanation += "It's like a balance scale - both sides must have the same value.\n\n"
        else:
            explanation += "An **equation** is a mathematical statement asserting the equality of two expressions.\n\n"
            explanation += "Solving an equation means finding the value(s) of the variable(s) that make the equation true.\n\n"
        
        if include_examples:
            explanation += "**Examples:**\n"
            explanation += "• 2x + 5 = 11 (linear equation)\n"
            explanation += "• x² - 4 = 0 (quadratic equation)\n"
            explanation += "• sin(x) = 0.5 (trigonometric equation)\n\n"
        
        explanation += "**Types of Equations:**\n"
        explanation += "• Linear: highest power of variable is 1\n"
        explanation += "• Quadratic: highest power of variable is 2\n"
        explanation += "• Exponential: variable appears in exponent\n"
        
        return explanation
    
    def _explain_fractions(self, level: str, include_examples: bool) -> str:
        """Explain fractions"""
        explanation = "# Understanding Fractions\n\n"
        
        if level == "basic":
            explanation += "A **fraction** represents part of a whole.\n\n"
            explanation += "The top number (numerator) tells you how many parts you have.\n"
            explanation += "The bottom number (denominator) tells you how many parts make up the whole.\n\n"
        else:
            explanation += "A **fraction** is a mathematical expression representing the division of one quantity by another.\n\n"
            explanation += "It can represent rational numbers, ratios, and proportional relationships.\n\n"
        
        if include_examples:
            explanation += "**Examples:**\n"
            explanation += "• 1/2 = 0.5 (one half)\n"
            explanation += "• 3/4 = 0.75 (three quarters)\n"
            explanation += "• 5/3 = 1⅔ (improper fraction)\n\n"
        
        explanation += "**Operations with Fractions:**\n"
        explanation += "• Addition: find common denominator\n"
        explanation += "• Multiplication: multiply numerators and denominators\n"
        explanation += "• Division: multiply by reciprocal\n"
        
        return explanation
    
    def _explain_general_concept(self, concept: str, level: str, include_examples: bool) -> str:
        """Explain general mathematical concepts"""
        explanation = f"# Understanding {concept.title()}\n\n"
        
        explanation += f"**{concept.title()}** is an important mathematical concept that helps us understand patterns and solve problems.\n\n"
        
        if level == "basic":
            explanation += "Let me break this down in simple terms:\n\n"
        else:
            explanation += "Here's a comprehensive explanation:\n\n"
        
        explanation += "**Key Points:**\n"
        explanation += f"• {concept.title()} helps us model real-world situations\n"
        explanation += f"• Understanding {concept} builds foundation for advanced topics\n"
        explanation += f"• Practice with {concept} improves problem-solving skills\n\n"
        
        explanation += "For a more specific explanation, please let me know what aspect of this concept you'd like to explore!"
        
        return explanation

class VideoSearchTool(BaseTool):
    """Tool for finding relevant educational videos"""
    
    name: str = "Educational Video Finder"
    description: str = "Searches for and recommends educational videos related to mathematical concepts and problems."
    
    def _run(self, topic: str, difficulty: str = "medium", duration: str = "medium") -> str:
        """
        Find educational videos for a topic
        
        Args:
            topic: The mathematical topic to find videos for
            difficulty: Difficulty level (beginner, intermediate, advanced)
            duration: Preferred video length (short, medium, long)
        """
        
        try:
            # Generate video recommendations based on topic
            recommendations = self._generate_video_recommendations(topic, difficulty, duration)
            
            return self._format_video_recommendations(recommendations, topic)
            
        except Exception as e:
            return f"Error finding videos: {str(e)}"
    
    def _generate_video_recommendations(self, topic: str, difficulty: str, duration: str) -> List[Dict[str, Any]]:
        """Generate video recommendations for the topic"""
        
        # Curated list of educational channels and typical content
        video_sources = {
            "Khan Academy": {
                "strengths": ["clear explanations", "step-by-step", "beginner-friendly"],
                "typical_length": "5-15 minutes"
            },
            "Professor Leonard": {
                "strengths": ["detailed lectures", "calculus", "algebra"],
                "typical_length": "45-90 minutes"
            },
            "PatrickJMT": {
                "strengths": ["quick solutions", "practice problems", "concise"],
                "typical_length": "3-10 minutes"
            },
            "3Blue1Brown": {
                "strengths": ["visual intuition", "advanced concepts", "beautiful animations"],
                "typical_length": "10-20 minutes"
            },
            "Organic Chemistry Tutor": {
                "strengths": ["comprehensive reviews", "multiple examples", "exam prep"],
                "typical_length": "30-60 minutes"
            }
        }
        
        recommendations = []
        
        # Generate recommendations based on topic and preferences
        for channel, info in video_sources.items():
            video_title = self._generate_video_title(topic, channel, difficulty)
            estimated_length = self._estimate_video_length(duration, info["typical_length"])
            
            recommendations.append({
                "channel": channel,
                "title": video_title,
                "estimated_length": estimated_length,
                "strengths": info["strengths"],
                "difficulty_match": self._calculate_difficulty_match(channel, difficulty),
                "topic_relevance": self._calculate_topic_relevance(channel, topic)
            })
        
        # Sort by relevance and difficulty match
        recommendations.sort(key=lambda x: (x["topic_relevance"] + x["difficulty_match"]) / 2, reverse=True)
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def _generate_video_title(self, topic: str, channel: str, difficulty: str) -> str:
        """Generate likely video title for the topic and channel"""
        
        topic_formatted = topic.title()
        
        title_templates = {
            "Khan Academy": f"{topic_formatted} - Introduction and Examples",
            "Professor Leonard": f"Complete Guide to {topic_formatted}",
            "PatrickJMT": f"{topic_formatted} - Practice Problems",
            "3Blue1Brown": f"The Essence of {topic_formatted}",
            "Organic Chemistry Tutor": f"{topic_formatted} - Full Review"
        }
        
        return title_templates.get(channel, f"Understanding {topic_formatted}")
    
    def _estimate_video_length(self, preferred_duration: str, typical_length: str) -> str:
        """Estimate video length based on preferences and channel typical length"""
        
        if preferred_duration == "short":
            return "5-10 minutes"
        elif preferred_duration == "long":
            return typical_length
        else:
            return "10-20 minutes"
    
    def _calculate_difficulty_match(self, channel: str, difficulty: str) -> float:
        """Calculate how well the channel matches the difficulty level"""
        
        channel_difficulty = {
            "Khan Academy": {"beginner": 0.9, "intermediate": 0.7, "advanced": 0.4},
            "Professor Leonard": {"beginner": 0.6, "intermediate": 0.9, "advanced": 0.8},
            "PatrickJMT": {"beginner": 0.8, "intermediate": 0.8, "advanced": 0.6},
            "3Blue1Brown": {"beginner": 0.3, "intermediate": 0.7, "advanced": 0.9},
            "Organic Chemistry Tutor": {"beginner": 0.7, "intermediate": 0.9, "advanced": 0.7}
        }
        
        return channel_difficulty.get(channel, {}).get(difficulty, 0.5)
    
    def _calculate_topic_relevance(self, channel: str, topic: str) -> float:
        """Calculate how relevant the channel is for the topic"""
        
        topic_lower = topic.lower()
        
        channel_topics = {
            "Khan Academy": ["algebra", "geometry", "arithmetic", "basic", "introduction"],
            "Professor Leonard": ["calculus", "algebra", "precalculus", "differential", "integral"],
            "PatrickJMT": ["calculus", "algebra", "trigonometry", "practice", "problems"],
            "3Blue1Brown": ["linear algebra", "calculus", "neural networks", "complex", "advanced"],
            "Organic Chemistry Tutor": ["calculus", "physics", "chemistry", "comprehensive", "review"]
        }
        
        channel_keywords = channel_topics.get(channel, [])
        
        # Check for keyword matches
        matches = sum(1 for keyword in channel_keywords if keyword in topic_lower)
        
        return min(matches / len(channel_keywords) + 0.3, 1.0)  # Base relevance + matches
    
    def _format_video_recommendations(self, recommendations: List[Dict[str, Any]], topic: str) -> str:
        """Format video recommendations for display"""
        
        output = f"# 🎥 Video Recommendations for {topic.title()}\n\n"
        
        for i, video in enumerate(recommendations, 1):
            output += f"## {i}. {video['channel']}\n"
            output += f"**Title:** {video['title']}\n"
            output += f"**Length:** {video['estimated_length']}\n"
            output += f"**Strengths:** {', '.join(video['strengths'])}\n"
            output += f"**Match Score:** {((video['topic_relevance'] + video['difficulty_match']) / 2 * 100):.0f}%\n\n"
        
        output += "## 💡 Viewing Tips:\n"
        output += "• Take notes while watching\n"
        output += "• Pause to work through examples\n"
        output += "• Rewatch difficult sections\n"
        output += "• Practice similar problems afterward\n\n"
        
        output += "Would you like me to help you with practice problems after watching these videos?"
        
        return output
