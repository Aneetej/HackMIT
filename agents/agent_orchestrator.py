from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime

from .teacher_agent import TeacherAgent
from .student_agent import StudentAgent
from .guardrail_agent import GuardrailAgent
from .aggregation_agent import AggregationAgent
from .takeaway_agent import TakeawayAgent
from .tools.math_tools import MathSolverTool, ConceptExplainerTool, VideoSearchTool
from .tools.analytics_tools import AnalyticsGeneratorTool, FAQTrackerTool
from database.models import ChatSession, ChatMessage, StudentPreference

class AgentOrchestrator:
    """
    Orchestrates the hierarchical agent network for mathematics learning engagement.
    Manages communication between Teacher, Student, Guardrail, Aggregation, and Takeaway agents.
    """
    
    def __init__(self):
        self.agents = {}
        self.crews = {}
        self.active_sessions = {}
        self.tools = {}
        
    async def initialize(self):
        """Initialize all agents and tools"""
        # Initialize tools
        await self._initialize_tools()
        
        # Initialize agents
        await self._initialize_agents()
        
        # Create specialized crews for different workflows
        await self._create_crews()
        
    async def _initialize_tools(self):
        """Initialize all tools used by agents"""
        self.tools = {
            'math_solver': MathSolverTool(),
            'concept_explainer': ConceptExplainerTool(),
            'video_search': VideoSearchTool(),
            'analytics_generator': AnalyticsGeneratorTool(),
            'faq_tracker': FAQTrackerTool()
        }
        
    async def _initialize_agents(self):
        """Initialize all agents in the hierarchy"""
        # Teacher Agent (Top Level)
        self.agents['teacher'] = TeacherAgent(
            tools=[
                self.tools['analytics_generator'],
                self.tools['faq_tracker']
            ]
        )
        
        # Student Agent
        self.agents['student'] = StudentAgent(
            tools=[
                self.tools['math_solver'],
                self.tools['concept_explainer'],
                self.tools['video_search']
            ]
        )
        
        # Guardrail Agent
        self.agents['guardrail'] = GuardrailAgent()
        
        # Aggregation Agent
        self.agents['aggregation'] = AggregationAgent()
        
        # Takeaway Agent
        self.agents['takeaway'] = TakeawayAgent()
        
    async def _create_crews(self):
        """Create specialized crews for different workflows"""
        
        # Student Learning Crew
        self.crews['student_learning'] = Crew(
            agents=[
                self.agents['student'].get_crewai_agent(),
                self.agents['guardrail'].get_crewai_agent()
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Teacher Analytics Crew
        self.crews['teacher_analytics'] = Crew(
            agents=[
                self.agents['teacher'].get_crewai_agent(),
                self.agents['aggregation'].get_crewai_agent()
            ],
            process=Process.sequential,
            verbose=True
        )
        
        # Session Analysis Crew
        self.crews['session_analysis'] = Crew(
            agents=[
                self.agents['takeaway'].get_crewai_agent(),
                self.agents['aggregation'].get_crewai_agent()
            ],
            process=Process.sequential,
            verbose=True
        )
    
    async def process_student_message(
        self, 
        student_id: str, 
        message: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a student message through the agent hierarchy
        
        Args:
            student_id: Unique identifier for the student
            message: The student's message/question
            session_id: Optional existing session ID
            
        Returns:
            Dict containing the response and metadata
        """
        
        # Step 1: Guardrail check
        guardrail_result = await self.agents['guardrail'].check_content(message)
        if not guardrail_result['safe']:
            return {
                'response': guardrail_result['message'],
                'session_id': session_id,
                'flagged': True
            }
        
        # Step 2: Get student preferences
        preferences = await self._get_student_preferences(student_id)
        
        # Step 3: Process with Student Agent
        student_response = await self.agents['student'].process_message(
            message=message,
            student_id=student_id,
            preferences=preferences,
            session_id=session_id
        )
        
        # Step 4: Log interaction for aggregation
        await self.agents['aggregation'].log_interaction(
            student_id=student_id,
            message=message,
            response=student_response,
            session_id=student_response['session_id']
        )
        
        # Step 5: Update preferences based on interaction
        await self._update_student_preferences(
            student_id, 
            student_response.get('preference_indicators', {})
        )
        
        # Step 6: Notify Teacher Agent of interaction
        await self.agents['teacher'].notify_interaction(
            student_id=student_id,
            session_id=student_response['session_id'],
            summary=student_response.get('summary', '')
        )
        
        return student_response
    
    async def generate_teacher_analytics(
        self, 
        teacher_id: str, 
        request_type: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate analytics for teacher dashboard
        
        Args:
            teacher_id: Unique identifier for the teacher
            request_type: Type of analytics requested
            parameters: Additional parameters for the request
            
        Returns:
            Dict containing analytics data
        """
        
        # Create analytics task
        analytics_task = Task(
            description=f"""
            Generate {request_type} analytics for teacher {teacher_id}.
            Parameters: {json.dumps(parameters)}
            
            Analyze student interactions, learning patterns, and frequently asked questions.
            Provide actionable insights and recommendations.
            """,
            agent=self.agents['teacher'].get_crewai_agent(),
            expected_output="Comprehensive analytics report with insights and recommendations"
        )
        
        # Execute analytics crew
        result = await self.crews['teacher_analytics'].kickoff_async(
            tasks=[analytics_task]
        )
        
        return {
            'analytics': result,
            'generated_at': datetime.utcnow().isoformat(),
            'request_type': request_type
        }
    
    async def analyze_session_completion(self, session_id: str) -> Dict[str, Any]:
        """
        Analyze a completed learning session for takeaways
        
        Args:
            session_id: The completed session ID
            
        Returns:
            Dict containing session analysis and takeaways
        """
        
        # Create takeaway analysis task
        takeaway_task = Task(
            description=f"""
            Analyze the completed learning session {session_id}.
            
            Extract key takeaways including:
            - Successful learning patterns
            - Effective teaching methods used
            - Student engagement indicators
            - Concepts that were well understood
            - Areas for improvement
            
            Generate insights that can be used to improve future tutoring sessions.
            """,
            agent=self.agents['takeaway'].get_crewai_agent(),
            expected_output="Detailed session analysis with actionable takeaways"
        )
        
        # Execute session analysis crew
        result = await self.crews['session_analysis'].kickoff_async(
            tasks=[takeaway_task]
        )
        
        return {
            'takeaways': result,
            'session_id': session_id,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    async def get_frequently_asked_questions(
        self, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get frequently asked questions, optionally filtered by category"""
        
        return await self.agents['teacher'].get_faqs(
            category=category,
            limit=limit
        )
    
    async def _get_student_preferences(self, student_id: str) -> Dict[str, Any]:
        """Retrieve student learning preferences from database"""
        # This would typically query the database
        # For now, return default preferences
        return {
            'content_format': 'mixed',
            'explanation_style': 'step_by_step',
            'difficulty_pace': 'adaptive',
            'preferred_examples': 'visual'
        }
    
    async def _update_student_preferences(
        self, 
        student_id: str, 
        indicators: Dict[str, Any]
    ):
        """Update student preferences based on interaction indicators"""
        # This would update the database with new preference indicators
        # Implementation would depend on the specific indicators detected
        pass
    
    async def cleanup(self):
        """Cleanup resources when shutting down"""
        # Close any open connections, save state, etc.
        for agent in self.agents.values():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()
        
        self.active_sessions.clear()
        print("🧹 Agent orchestrator cleanup completed")
