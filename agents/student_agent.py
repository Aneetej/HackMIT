from crewai import Agent
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import uuid

class StudentAgent:
    """
    Student Agent - Personalized mathematics tutor
    
    Responsibilities:
    - Provide personalized tutoring based on student preferences
    - Adapt teaching style to individual learning patterns
    - Generate appropriate content (videos, text, interactive examples)
    - Track learning progress and adjust difficulty
    - Detect and respond to learning preferences
    """
    
    def __init__(self, tools: List = None):
        self.tools = tools or []
        self.student_contexts = {}
        
        # Initialize the crewAI agent
        self.agent = Agent(
            role="Personalized Mathematics Tutor",
            goal="""Provide highly personalized mathematics tutoring that adapts to each 
                   student's learning style, preferences, and pace. Create engaging and 
                   effective learning experiences tailored to individual needs.""",
            backstory="""You are an expert mathematics tutor with deep understanding of 
                        different learning styles and pedagogical approaches. You excel at 
                        identifying how each student learns best and adapting your teaching 
                        methods accordingly. You can provide explanations through various 
                        formats including step-by-step text, visual examples, videos, and 
                        interactive demonstrations.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
    
    def get_crewai_agent(self) -> Agent:
        """Return the crewAI agent instance"""
        return self.agent
    
    async def process_message(
        self,
        message: str,
        student_id: str,
        preferences: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a student message and generate personalized response
        
        Args:
            message: The student's question or message
            student_id: Unique identifier for the student
            preferences: Student's learning preferences
            session_id: Optional existing session ID
            
        Returns:
            Dict containing response and metadata
        """
        
        # Create or continue session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize student context if new
        if student_id not in self.student_contexts:
            self.student_contexts[student_id] = {
                'learning_history': [],
                'preferred_formats': [],
                'difficulty_level': 'medium',
                'recent_topics': [],
                'success_patterns': {}
            }
        
        context = self.student_contexts[student_id]
        
        # Analyze the message to understand the request
        message_analysis = await self._analyze_message(message)
        
        # Generate personalized response based on preferences
        response = await self._generate_personalized_response(
            message=message,
            analysis=message_analysis,
            preferences=preferences,
            context=context
        )
        
        # Detect learning preference indicators from interaction
        preference_indicators = await self._detect_preference_indicators(
            message, response, context
        )
        
        # Update student context
        await self._update_student_context(
            student_id, message_analysis, response, preference_indicators
        )
        
        return {
            'response': response['content'],
            'session_id': session_id,
            'response_type': response['type'],
            'concepts_covered': message_analysis.get('concepts', []),
            'difficulty_level': response.get('difficulty', 'medium'),
            'preference_indicators': preference_indicators,
            'summary': f"Discussed {', '.join(message_analysis.get('concepts', ['mathematics']))}",
            'metadata': {
                'response_format': response.get('format', 'text'),
                'engagement_level': response.get('engagement_level', 'medium'),
                'followup_suggestions': response.get('followup_suggestions', [])
            }
        }
    
    async def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze student message to understand intent and content"""
        
        message_lower = message.lower()
        
        # Detect question type
        question_types = []
        if any(word in message_lower for word in ['how', 'what', 'why', 'when', 'where']):
            question_types.append('conceptual')
        if any(word in message_lower for word in ['solve', 'calculate', 'find', 'compute']):
            question_types.append('procedural')
        if any(word in message_lower for word in ['example', 'show me', 'demonstrate']):
            question_types.append('example_request')
        
        # Detect mathematical concepts
        concepts = self._extract_math_concepts(message)
        
        # Detect difficulty indicators
        difficulty_indicators = []
        if any(word in message_lower for word in ['basic', 'simple', 'easy', 'beginner']):
            difficulty_indicators.append('easy')
        if any(word in message_lower for word in ['advanced', 'complex', 'difficult', 'hard']):
            difficulty_indicators.append('hard')
        
        # Detect format preferences in the question
        format_preferences = []
        if any(word in message_lower for word in ['video', 'watch', 'visual', 'see']):
            format_preferences.append('video')
        if any(word in message_lower for word in ['step', 'steps', 'explain', 'breakdown']):
            format_preferences.append('step_by_step')
        if any(word in message_lower for word in ['example', 'practice', 'try']):
            format_preferences.append('interactive')
        
        return {
            'question_types': question_types,
            'concepts': concepts,
            'difficulty_indicators': difficulty_indicators,
            'format_preferences': format_preferences,
            'urgency': self._detect_urgency(message),
            'confidence_level': self._detect_student_confidence(message)
        }
    
    def _extract_math_concepts(self, message: str) -> List[str]:
        """Extract mathematical concepts from the message"""
        message_lower = message.lower()
        
        concept_keywords = {
            'algebra': ['variable', 'equation', 'solve', 'linear', 'quadratic', 'polynomial'],
            'geometry': ['triangle', 'circle', 'area', 'perimeter', 'angle', 'shape', 'volume'],
            'calculus': ['derivative', 'integral', 'limit', 'function', 'rate', 'slope'],
            'statistics': ['mean', 'median', 'probability', 'data', 'graph', 'distribution'],
            'arithmetic': ['add', 'subtract', 'multiply', 'divide', 'fraction', 'decimal'],
            'trigonometry': ['sin', 'cos', 'tan', 'sine', 'cosine', 'tangent', 'triangle']
        }
        
        detected_concepts = []
        for concept, keywords in concept_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_concepts.append(concept)
        
        return detected_concepts if detected_concepts else ['general_math']
    
    def _detect_urgency(self, message: str) -> str:
        """Detect urgency level from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['urgent', 'asap', 'quickly', 'fast', 'hurry']):
            return 'high'
        elif any(word in message_lower for word in ['soon', 'today', 'now']):
            return 'medium'
        else:
            return 'low'
    
    def _detect_student_confidence(self, message: str) -> str:
        """Detect student's confidence level"""
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ['i don\'t understand', 'confused', 'lost', 'help']):
            return 'low'
        elif any(phrase in message_lower for phrase in ['i think', 'maybe', 'not sure']):
            return 'medium'
        else:
            return 'high'
    
    async def _generate_personalized_response(
        self,
        message: str,
        analysis: Dict[str, Any],
        preferences: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized response based on student preferences and context"""
        
        # Determine response format based on preferences and request
        response_format = self._determine_response_format(analysis, preferences)
        
        # Adjust difficulty based on context and analysis
        difficulty_level = self._determine_difficulty_level(analysis, context)
        
        # Generate content based on format and difficulty
        if response_format == 'video':
            content = await self._generate_video_response(message, analysis, difficulty_level)
        elif response_format == 'step_by_step':
            content = await self._generate_step_by_step_response(message, analysis, difficulty_level)
        elif response_format == 'interactive':
            content = await self._generate_interactive_response(message, analysis, difficulty_level)
        else:
            content = await self._generate_text_response(message, analysis, difficulty_level)
        
        # Add engagement elements
        engagement_elements = self._add_engagement_elements(analysis, preferences)
        
        return {
            'content': content,
            'type': analysis.get('question_types', ['general'])[0] if analysis.get('question_types') else 'general',
            'format': response_format,
            'difficulty': difficulty_level,
            'engagement_level': self._calculate_engagement_level(analysis, preferences),
            'followup_suggestions': self._generate_followup_suggestions(analysis),
            'engagement_elements': engagement_elements
        }
    
    def _determine_response_format(self, analysis: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """Determine the best response format for this student and question"""
        
        # Check explicit format preferences in the question
        if analysis.get('format_preferences'):
            return analysis['format_preferences'][0]
        
        # Use student's general preferences
        preferred_content = preferences.get('preferred_content', 'mixed')
        
        if preferred_content == 'videos':
            return 'video'
        elif preferred_content == 'text':
            return 'step_by_step'
        elif preferred_content == 'interactive':
            return 'interactive'
        else:
            # For mixed preference, choose based on question type
            question_types = analysis.get('question_types', [])
            if 'example_request' in question_types:
                return 'interactive'
            elif 'procedural' in question_types:
                return 'step_by_step'
            else:
                return 'text'
    
    def _determine_difficulty_level(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Determine appropriate difficulty level"""
        
        # Check explicit difficulty indicators
        if analysis.get('difficulty_indicators'):
            return analysis['difficulty_indicators'][0]
        
        # Use student's confidence level
        confidence = analysis.get('confidence_level', 'medium')
        if confidence == 'low':
            return 'easy'
        elif confidence == 'high':
            return 'medium'  # Don't assume they want hard content
        
        # Use historical context
        return context.get('difficulty_level', 'medium')
    
    async def _generate_video_response(self, message: str, analysis: Dict[str, Any], difficulty: str) -> str:
        """Generate response with video recommendations"""
        
        concepts = analysis.get('concepts', ['general_math'])
        main_concept = concepts[0] if concepts else 'general_math'
        
        # Use video search tool if available
        if hasattr(self, 'tools') and any('video' in str(tool).lower() for tool in self.tools):
            # This would use the VideoSearchTool
            video_results = f"Here are some excellent video explanations for {main_concept}:\n\n"
            video_results += f"🎥 **Recommended Videos:**\n"
            video_results += f"1. 'Understanding {main_concept.title()}' - Khan Academy (5 min)\n"
            video_results += f"2. '{main_concept.title()} Explained Simply' - Professor Leonard (12 min)\n"
            video_results += f"3. 'Practice Problems: {main_concept.title()}' - PatrickJMT (8 min)\n\n"
        else:
            video_results = f"I'd recommend looking for videos on {main_concept} to help visualize the concepts.\n\n"
        
        # Add text explanation as backup
        text_explanation = await self._generate_text_response(message, analysis, difficulty)
        
        return video_results + "**Quick Text Explanation:**\n" + text_explanation
    
    async def _generate_step_by_step_response(self, message: str, analysis: Dict[str, Any], difficulty: str) -> str:
        """Generate detailed step-by-step response"""
        
        concepts = analysis.get('concepts', ['general_math'])
        
        response = "Let me break this down step by step:\n\n"
        
        # Generate steps based on the mathematical concept
        if 'algebra' in concepts:
            response += self._generate_algebra_steps(message, difficulty)
        elif 'geometry' in concepts:
            response += self._generate_geometry_steps(message, difficulty)
        elif 'calculus' in concepts:
            response += self._generate_calculus_steps(message, difficulty)
        else:
            response += self._generate_general_math_steps(message, difficulty)
        
        response += "\n\n**Key Points to Remember:**\n"
        response += "• Take your time with each step\n"
        response += "• Check your work as you go\n"
        response += "• Don't hesitate to ask if any step is unclear\n"
        
        return response
    
    async def _generate_interactive_response(self, message: str, analysis: Dict[str, Any], difficulty: str) -> str:
        """Generate interactive response with practice problems"""
        
        concepts = analysis.get('concepts', ['general_math'])
        main_concept = concepts[0] if concepts else 'general_math'
        
        response = f"Let's practice {main_concept} together! Here's an interactive approach:\n\n"
        
        # Generate practice problem
        response += "**Practice Problem:**\n"
        response += self._generate_practice_problem(main_concept, difficulty)
        response += "\n\n**Try solving this step by step:**\n"
        response += "1. Identify what you're looking for\n"
        response += "2. Write down what you know\n"
        response += "3. Choose the right formula or method\n"
        response += "4. Solve step by step\n"
        response += "5. Check your answer\n\n"
        response += "Share your work and I'll help guide you through it! 🤝"
        
        return response
    
    async def _generate_text_response(self, message: str, analysis: Dict[str, Any], difficulty: str) -> str:
        """Generate comprehensive text response"""
        
        concepts = analysis.get('concepts', ['general_math'])
        question_types = analysis.get('question_types', ['conceptual'])
        
        if 'conceptual' in question_types:
            return self._generate_conceptual_explanation(concepts, difficulty)
        elif 'procedural' in question_types:
            return self._generate_procedural_explanation(concepts, difficulty)
        else:
            return self._generate_general_explanation(concepts, difficulty)
    
    def _generate_algebra_steps(self, message: str, difficulty: str) -> str:
        """Generate algebra-specific steps"""
        steps = "**Step 1:** Identify the type of equation (linear, quadratic, etc.)\n"
        steps += "**Step 2:** Isolate variables on one side\n"
        steps += "**Step 3:** Perform inverse operations\n"
        steps += "**Step 4:** Simplify your answer\n"
        steps += "**Step 5:** Check by substituting back\n"
        return steps
    
    def _generate_geometry_steps(self, message: str, difficulty: str) -> str:
        """Generate geometry-specific steps"""
        steps = "**Step 1:** Draw and label a diagram\n"
        steps += "**Step 2:** Identify given information\n"
        steps += "**Step 3:** Choose the appropriate formula\n"
        steps += "**Step 4:** Substitute known values\n"
        steps += "**Step 5:** Calculate and include units\n"
        return steps
    
    def _generate_calculus_steps(self, message: str, difficulty: str) -> str:
        """Generate calculus-specific steps"""
        steps = "**Step 1:** Identify the type of problem (derivative, integral, limit)\n"
        steps += "**Step 2:** Apply the appropriate rule or theorem\n"
        steps += "**Step 3:** Simplify the expression\n"
        steps += "**Step 4:** Check for domain restrictions\n"
        steps += "**Step 5:** Verify your result\n"
        return steps
    
    def _generate_general_math_steps(self, message: str, difficulty: str) -> str:
        """Generate general math problem-solving steps"""
        steps = "**Step 1:** Read the problem carefully\n"
        steps += "**Step 2:** Identify what you need to find\n"
        steps += "**Step 3:** Organize the given information\n"
        steps += "**Step 4:** Choose your strategy\n"
        steps += "**Step 5:** Solve and check your answer\n"
        return steps
    
    def _generate_practice_problem(self, concept: str, difficulty: str) -> str:
        """Generate a practice problem based on concept and difficulty"""
        
        problems = {
            'algebra': {
                'easy': "Solve for x: 2x + 5 = 13",
                'medium': "Solve for x: 3x² - 12x + 9 = 0",
                'hard': "Solve the system: 2x + 3y = 7, 4x - y = 1"
            },
            'geometry': {
                'easy': "Find the area of a rectangle with length 8 and width 5",
                'medium': "Find the area of a triangle with base 10 and height 6",
                'hard': "Find the volume of a cylinder with radius 4 and height 10"
            }
        }
        
        return problems.get(concept, {}).get(difficulty, "Practice with the concept we just discussed!")
    
    def _generate_conceptual_explanation(self, concepts: List[str], difficulty: str) -> str:
        """Generate conceptual explanation"""
        main_concept = concepts[0] if concepts else 'mathematics'
        
        explanation = f"**Understanding {main_concept.title()}:**\n\n"
        explanation += f"{main_concept.title()} is a fundamental area of mathematics that helps us "
        explanation += "solve real-world problems and understand patterns.\n\n"
        explanation += "**Key Ideas:**\n"
        explanation += f"• {main_concept.title()} deals with relationships and patterns\n"
        explanation += "• It provides tools for problem-solving\n"
        explanation += "• Practice helps build intuition and fluency\n"
        
        return explanation
    
    def _generate_procedural_explanation(self, concepts: List[str], difficulty: str) -> str:
        """Generate procedural explanation"""
        main_concept = concepts[0] if concepts else 'mathematics'
        
        explanation = f"**How to Approach {main_concept.title()} Problems:**\n\n"
        explanation += "Follow these general steps:\n"
        explanation += "1. **Understand** what the problem is asking\n"
        explanation += "2. **Plan** your approach\n"
        explanation += "3. **Execute** your plan step by step\n"
        explanation += "4. **Check** your work\n\n"
        explanation += "Remember: practice makes perfect! 💪"
        
        return explanation
    
    def _generate_general_explanation(self, concepts: List[str], difficulty: str) -> str:
        """Generate general explanation"""
        return "I'm here to help you understand mathematics better! Feel free to ask specific questions about any topic you're working on."
    
    def _add_engagement_elements(self, analysis: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Add elements to increase engagement"""
        
        elements = {
            'encouragement': True,
            'emojis': preferences.get('explanation_style') != 'formal',
            'real_world_connections': True,
            'progress_tracking': True
        }
        
        return elements
    
    def _calculate_engagement_level(self, analysis: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """Calculate expected engagement level for this interaction"""
        
        confidence = analysis.get('confidence_level', 'medium')
        urgency = analysis.get('urgency', 'low')
        
        if confidence == 'low' and urgency == 'high':
            return 'high'  # Student needs immediate help
        elif confidence == 'high':
            return 'medium'  # Student is confident, moderate engagement needed
        else:
            return 'medium'
    
    def _generate_followup_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions for follow-up questions or practice"""
        
        concepts = analysis.get('concepts', ['general_math'])
        suggestions = []
        
        for concept in concepts[:2]:  # Limit to 2 concepts
            suggestions.append(f"Would you like to practice more {concept} problems?")
            suggestions.append(f"Do you want to explore advanced {concept} topics?")
        
        suggestions.append("Is there anything specific about this topic you'd like me to clarify?")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def _detect_preference_indicators(
        self, 
        message: str, 
        response: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect learning preference indicators from the interaction"""
        
        indicators = {}
        
        # Detect format preferences from message
        message_lower = message.lower()
        if any(word in message_lower for word in ['video', 'watch', 'see']):
            indicators['prefers_visual'] = 0.8
        if any(word in message_lower for word in ['explain', 'steps', 'how']):
            indicators['prefers_detailed_explanation'] = 0.7
        if any(word in message_lower for word in ['example', 'practice', 'try']):
            indicators['prefers_interactive'] = 0.6
        
        # Detect difficulty preferences
        if any(word in message_lower for word in ['simple', 'basic', 'easy']):
            indicators['prefers_easier_content'] = 0.7
        elif any(word in message_lower for word in ['challenge', 'advanced', 'harder']):
            indicators['prefers_challenging_content'] = 0.7
        
        return indicators
    
    async def _update_student_context(
        self,
        student_id: str,
        message_analysis: Dict[str, Any],
        response: Dict[str, Any],
        preference_indicators: Dict[str, Any]
    ):
        """Update student context with new interaction data"""
        
        context = self.student_contexts[student_id]
        
        # Update learning history
        context['learning_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'concepts': message_analysis.get('concepts', []),
            'difficulty': response.get('difficulty', 'medium'),
            'format': response.get('format', 'text'),
            'engagement': response.get('engagement_level', 'medium')
        })
        
        # Keep only recent history (last 20 interactions)
        context['learning_history'] = context['learning_history'][-20:]
        
        # Update preferred formats based on usage
        format_used = response.get('format', 'text')
        if format_used not in context['preferred_formats']:
            context['preferred_formats'].append(format_used)
        
        # Update recent topics
        new_concepts = message_analysis.get('concepts', [])
        for concept in new_concepts:
            if concept not in context['recent_topics']:
                context['recent_topics'].append(concept)
        
        # Keep only recent topics (last 10)
        context['recent_topics'] = context['recent_topics'][-10:]
        
        # Update success patterns based on preference indicators
        for indicator, confidence in preference_indicators.items():
            if indicator not in context['success_patterns']:
                context['success_patterns'][indicator] = []
            context['success_patterns'][indicator].append(confidence)
            
            # Keep only recent patterns (last 5)
            context['success_patterns'][indicator] = context['success_patterns'][indicator][-5:]
