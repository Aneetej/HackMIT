from crewai import Agent
from typing import Dict, List, Any, Optional
import re
import json
from datetime import datetime

class GuardrailAgent:
    """
    Guardrail Agent - Content safety and quality assurance
    
    Responsibilities:
    - Ensure content safety and appropriateness
    - Verify mathematical accuracy
    - Filter inappropriate content
    - Maintain educational standards
    - Protect student privacy
    """
    
    def __init__(self):
        self.inappropriate_patterns = self._load_inappropriate_patterns()
        self.math_validation_rules = self._load_math_validation_rules()
        self.safety_flags = []
        
        # Initialize the crewAI agent
        self.agent = Agent(
            role="Content Safety and Quality Assurance Specialist",
            goal="""Ensure all educational content is safe, appropriate, mathematically 
                   accurate, and maintains high educational standards while protecting 
                   student privacy and well-being.""",
            backstory="""You are a dedicated educational content moderator with expertise 
                        in mathematics education, child safety, and academic integrity. 
                        You have extensive experience in identifying inappropriate content, 
                        verifying mathematical accuracy, and ensuring educational 
                        interactions meet the highest standards.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
    
    def get_crewai_agent(self) -> Agent:
        """Return the crewAI agent instance"""
        return self.agent
    
    async def check_content(self, content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive content safety and quality check
        
        Args:
            content: The content to check (student message or agent response)
            context: Optional context information
            
        Returns:
            Dict containing safety assessment and recommendations
        """
        
        safety_result = {
            'safe': True,
            'confidence': 1.0,
            'flags': [],
            'message': '',
            'recommendations': []
        }
        
        # Check for inappropriate content
        inappropriate_check = await self._check_inappropriate_content(content)
        if not inappropriate_check['safe']:
            safety_result.update(inappropriate_check)
            return safety_result
        
        # Check for privacy violations
        privacy_check = await self._check_privacy_violations(content)
        if not privacy_check['safe']:
            safety_result.update(privacy_check)
            return safety_result
        
        # Check mathematical accuracy (for agent responses)
        if context and context.get('type') == 'agent_response':
            math_check = await self._check_mathematical_accuracy(content)
            if not math_check['safe']:
                safety_result.update(math_check)
                return safety_result
        
        # Check educational appropriateness
        educational_check = await self._check_educational_appropriateness(content)
        if not educational_check['safe']:
            safety_result.update(educational_check)
            return safety_result
        
        # All checks passed
        safety_result['message'] = 'Content approved for educational use'
        return safety_result
    
    async def validate_math_response(self, response: str, original_question: str) -> Dict[str, Any]:
        """
        Validate mathematical accuracy of agent responses
        
        Args:
            response: The mathematical response to validate
            original_question: The original student question
            
        Returns:
            Dict containing validation results
        """
        
        validation_result = {
            'accurate': True,
            'confidence': 0.8,
            'issues': [],
            'suggestions': []
        }
        
        # Check for common mathematical errors
        math_errors = await self._detect_math_errors(response)
        if math_errors:
            validation_result['accurate'] = False
            validation_result['issues'].extend(math_errors)
        
        # Check for completeness
        completeness_check = await self._check_response_completeness(response, original_question)
        if not completeness_check['complete']:
            validation_result['suggestions'].extend(completeness_check['suggestions'])
        
        # Check for clarity
        clarity_check = await self._check_response_clarity(response)
        if not clarity_check['clear']:
            validation_result['suggestions'].extend(clarity_check['suggestions'])
        
        return validation_result
    
    async def monitor_interaction_safety(
        self, 
        student_message: str, 
        agent_response: str, 
        student_id: str
    ) -> Dict[str, Any]:
        """
        Monitor entire interaction for safety and appropriateness
        
        Args:
            student_message: The student's message
            agent_response: The agent's response
            student_id: Student identifier (for tracking patterns)
            
        Returns:
            Dict containing interaction safety assessment
        """
        
        interaction_safety = {
            'safe': True,
            'student_message_safe': True,
            'agent_response_safe': True,
            'interaction_appropriate': True,
            'flags': [],
            'recommendations': []
        }
        
        # Check student message
        student_check = await self.check_content(student_message)
        if not student_check['safe']:
            interaction_safety['student_message_safe'] = False
            interaction_safety['safe'] = False
            interaction_safety['flags'].extend(student_check['flags'])
        
        # Check agent response
        agent_check = await self.check_content(
            agent_response, 
            context={'type': 'agent_response'}
        )
        if not agent_check['safe']:
            interaction_safety['agent_response_safe'] = False
            interaction_safety['safe'] = False
            interaction_safety['flags'].extend(agent_check['flags'])
        
        # Check interaction appropriateness
        interaction_check = await self._check_interaction_appropriateness(
            student_message, agent_response, student_id
        )
        if not interaction_check['appropriate']:
            interaction_safety['interaction_appropriate'] = False
            interaction_safety['safe'] = False
            interaction_safety['flags'].extend(interaction_check['flags'])
        
        return interaction_safety
    
    async def _check_inappropriate_content(self, content: str) -> Dict[str, Any]:
        """Check for inappropriate content using pattern matching"""
        
        content_lower = content.lower()
        
        for pattern_category, patterns in self.inappropriate_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return {
                        'safe': False,
                        'confidence': 0.9,
                        'flags': [f'inappropriate_content_{pattern_category}'],
                        'message': 'Content contains inappropriate material and cannot be processed.',
                        'recommendations': ['Please rephrase your message using appropriate language']
                    }
        
        return {'safe': True}
    
    async def _check_privacy_violations(self, content: str) -> Dict[str, Any]:
        """Check for potential privacy violations"""
        
        privacy_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
            r'\b\d{1,5}\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr)\b',  # Address pattern
        ]
        
        for pattern in privacy_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    'safe': False,
                    'confidence': 0.95,
                    'flags': ['privacy_violation'],
                    'message': 'Please avoid sharing personal information like addresses, phone numbers, or email addresses.',
                    'recommendations': ['Remove personal information from your message']
                }
        
        return {'safe': True}
    
    async def _check_mathematical_accuracy(self, content: str) -> Dict[str, Any]:
        """Check mathematical accuracy in responses"""
        
        # Check for common mathematical notation errors
        math_error_patterns = [
            r'1/0',  # Division by zero
            r'√-\d+',  # Square root of negative (without complex context)
            r'log\(0\)',  # Log of zero
            r'log\(-\d+\)',  # Log of negative number
        ]
        
        for pattern in math_error_patterns:
            if re.search(pattern, content):
                return {
                    'safe': False,
                    'confidence': 0.8,
                    'flags': ['mathematical_error'],
                    'message': 'Mathematical content contains potential errors.',
                    'recommendations': ['Review mathematical expressions for accuracy']
                }
        
        # Check for contradictory statements
        if self._contains_contradictions(content):
            return {
                'safe': False,
                'confidence': 0.7,
                'flags': ['mathematical_contradiction'],
                'message': 'Content contains contradictory mathematical statements.',
                'recommendations': ['Review content for consistency']
            }
        
        return {'safe': True}
    
    async def _check_educational_appropriateness(self, content: str) -> Dict[str, Any]:
        """Check if content is educationally appropriate"""
        
        # Check for overly complex content without proper scaffolding
        complexity_indicators = [
            'advanced calculus', 'differential equations', 'complex analysis',
            'abstract algebra', 'topology', 'real analysis'
        ]
        
        basic_indicators = [
            'addition', 'subtraction', 'multiplication', 'division',
            'fractions', 'decimals', 'basic algebra'
        ]
        
        content_lower = content.lower()
        
        # If advanced topics are mentioned without basic context
        has_advanced = any(indicator in content_lower for indicator in complexity_indicators)
        has_basic_context = any(indicator in content_lower for indicator in basic_indicators)
        
        if has_advanced and not has_basic_context and len(content) < 200:
            return {
                'safe': False,
                'confidence': 0.6,
                'flags': ['educational_complexity_mismatch'],
                'message': 'Content may be too advanced without proper context.',
                'recommendations': ['Provide more scaffolding for advanced topics']
            }
        
        return {'safe': True}
    
    async def _check_interaction_appropriateness(
        self, 
        student_message: str, 
        agent_response: str, 
        student_id: str
    ) -> Dict[str, Any]:
        """Check if the interaction is appropriate and educational"""
        
        # Check if agent response addresses the student's question
        if not self._response_addresses_question(student_message, agent_response):
            return {
                'appropriate': False,
                'flags': ['response_mismatch'],
                'recommendations': ['Ensure response directly addresses student question']
            }
        
        # Check for appropriate tone and language level
        if not self._appropriate_tone(agent_response):
            return {
                'appropriate': False,
                'flags': ['inappropriate_tone'],
                'recommendations': ['Adjust tone to be more supportive and encouraging']
            }
        
        return {'appropriate': True}
    
    async def _detect_math_errors(self, response: str) -> List[str]:
        """Detect common mathematical errors in responses"""
        
        errors = []
        
        # Check for calculation errors (simple patterns)
        calculation_patterns = [
            (r'2\s*\+\s*2\s*=\s*5', 'Basic arithmetic error detected'),
            (r'0\s*/\s*0\s*=\s*1', 'Division by zero error'),
            (r'x\s*\+\s*x\s*=\s*x²', 'Incorrect algebraic simplification'),
        ]
        
        for pattern, error_msg in calculation_patterns:
            if re.search(pattern, response):
                errors.append(error_msg)
        
        return errors
    
    async def _check_response_completeness(self, response: str, question: str) -> Dict[str, Any]:
        """Check if response completely addresses the question"""
        
        question_lower = question.lower()
        response_lower = response.lower()
        
        # Check for question words that should be addressed
        question_indicators = {
            'how': ['step', 'method', 'process', 'way'],
            'what': ['definition', 'meaning', 'is', 'are'],
            'why': ['because', 'reason', 'explanation'],
            'when': ['time', 'condition', 'situation'],
            'where': ['location', 'position', 'place']
        }
        
        missing_elements = []
        
        for question_word, expected_elements in question_indicators.items():
            if question_word in question_lower:
                if not any(element in response_lower for element in expected_elements):
                    missing_elements.append(f"Response should address '{question_word}' with {'/'.join(expected_elements)}")
        
        return {
            'complete': len(missing_elements) == 0,
            'suggestions': missing_elements
        }
    
    async def _check_response_clarity(self, response: str) -> Dict[str, Any]:
        """Check if response is clear and well-structured"""
        
        clarity_issues = []
        
        # Check for overly long sentences
        sentences = response.split('.')
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            clarity_issues.append("Consider breaking down long sentences for better clarity")
        
        # Check for mathematical notation without explanation
        math_symbols = ['∫', '∑', '∂', '∇', '∞', '≤', '≥', '≠']
        unexplained_symbols = []
        for symbol in math_symbols:
            if symbol in response and f"where {symbol}" not in response and f"{symbol} means" not in response:
                unexplained_symbols.append(symbol)
        
        if unexplained_symbols:
            clarity_issues.append(f"Consider explaining mathematical symbols: {', '.join(unexplained_symbols)}")
        
        return {
            'clear': len(clarity_issues) == 0,
            'suggestions': clarity_issues
        }
    
    def _contains_contradictions(self, content: str) -> bool:
        """Check for contradictory mathematical statements"""
        
        # Simple contradiction patterns
        contradiction_patterns = [
            (r'always true.*never true', True),
            (r'equal.*not equal', True),
            (r'positive.*negative.*same', True),
        ]
        
        content_lower = content.lower()
        for pattern, _ in contradiction_patterns:
            if re.search(pattern, content_lower):
                return True
        
        return False
    
    def _response_addresses_question(self, question: str, response: str) -> bool:
        """Check if response addresses the original question"""
        
        question_lower = question.lower()
        response_lower = response.lower()
        
        # Extract key terms from question
        question_words = set(question_lower.split())
        response_words = set(response_lower.split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'}
        
        question_keywords = question_words - stop_words
        response_keywords = response_words - stop_words
        
        # Check for overlap in keywords
        overlap = len(question_keywords & response_keywords)
        overlap_ratio = overlap / len(question_keywords) if question_keywords else 0
        
        return overlap_ratio >= 0.3  # At least 30% keyword overlap
    
    def _appropriate_tone(self, response: str) -> bool:
        """Check if response has appropriate educational tone"""
        
        response_lower = response.lower()
        
        # Positive indicators
        positive_indicators = [
            'let\'s', 'great', 'excellent', 'good', 'well done',
            'keep going', 'you can', 'try', 'practice'
        ]
        
        # Negative indicators
        negative_indicators = [
            'wrong', 'incorrect', 'bad', 'terrible', 'stupid',
            'obviously', 'clearly you don\'t', 'you should know'
        ]
        
        has_positive = any(indicator in response_lower for indicator in positive_indicators)
        has_negative = any(indicator in response_lower for indicator in negative_indicators)
        
        # Appropriate tone has positive elements and no negative elements
        return has_positive or not has_negative
    
    def _load_inappropriate_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for inappropriate content detection"""
        
        return {
            'profanity': [
                r'\b(damn|hell|crap)\b',  # Mild profanity patterns
                # Add more patterns as needed
            ],
            'harassment': [
                r'\b(stupid|idiot|dumb|loser)\b',
                r'you (are|re) (so|really) (bad|terrible)',
            ],
            'violence': [
                r'\b(kill|murder|hurt|harm|violence)\b',
            ],
            'discrimination': [
                r'\b(hate|racist|sexist)\b',
            ]
        }
    
    def _load_math_validation_rules(self) -> Dict[str, Any]:
        """Load mathematical validation rules"""
        
        return {
            'division_by_zero': r'(?:^|[^a-zA-Z])(?:\d+|[a-zA-Z]+)\s*/\s*0(?:[^a-zA-Z]|$)',
            'undefined_operations': [
                r'log\(0\)',
                r'log\(-\d+\)',
                r'√-\d+(?![i])',  # Negative square root without imaginary unit
            ],
            'notation_errors': [
                r'[a-zA-Z]\s*[a-zA-Z](?![a-zA-Z])',  # Variables without multiplication sign
                r'\)\s*\(',  # Missing multiplication between parentheses
            ]
        }
