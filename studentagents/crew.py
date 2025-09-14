#This file establishes the crew for the system.

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from langchain_anthropic import ChatAnthropic
from typing import List
import os

@CrewBase
class Studentagents():
    """Studentagents crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, student_context=None):
        super().__init__()
        # Store student context for agent personalization
        self.student_context = student_context or self._create_default_context()
        
        # Initialize Claude LLM for student conversations
        self.student_llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7, 
            max_tokens=1000,
        )
        
        # Initialize Claude LLM for analytics
        self.analyst_llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            #Low temperature allows for more focused and accurate analysis
            temperature=0.3, 
            max_tokens=1000,
 
        )

        # Initialize Claude LLM for guideline checking
        self.guideline_llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            #Low temperature allows for more focused and accurate analysis
            temperature=0.3,  
        )

        cerebras_llm = LLM(
            model="cerebras/llama-4-scout-17b-16e-instruct", 
            api_key=os.environ.get("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            temperature=0.5,
        )

        self.relevance_llm = cerebras_llm
        self.crew_llm = self.student_llm

    def _create_default_context(self):
        """Create default student context when none provided"""
        return {
            'learning_style': 'visual',
            'student_name': 'Student',
            'grade': '10',
            'subject_focus': 'algebra',
            'preferred_content': 'interactive',
            'concepts_mastered': 'basic arithmetic',
            'improvement_areas': 'word problems',
            'total_sessions': 1,
            'total_messages': 0,
            'total_time_spent': 0,
            'average_engagement': 75,
            'teacher_name': 'Teacher',
            'class_name': 'Demo Class',
            'teaching_style': 'interactive'
        }

    def _format_agent_config(self, agent_config):
        """Format agent configuration with student context variables"""
        if not isinstance(agent_config, dict):
            return agent_config
        
        formatted_config = {}
        for key, value in agent_config.items():
            if isinstance(value, str):
                try:
                    formatted_config[key] = value.format(**self.student_context)
                except KeyError as e:
                    # If template variable not found, use original value
                    formatted_config[key] = value
            else:
                formatted_config[key] = value
        
        return formatted_config

    #Pull from yaml config file with student context
    @agent
    def studentAgent(self) -> Agent:
        config = self._format_agent_config(self.agents_config['studentAgent'])
        return Agent(
            config=config,
            #Errors will show up if there are any
            verbose=True,
            memory=True,
            llm=self.student_llm
        )

    #Pull from yaml config file with student context
    @agent
    def studentAnalyst(self) -> Agent:
        config = self._format_agent_config(self.agents_config['studentAnalyst'])
        return Agent(
            config=config,
            verbose=True,
            llm=self.analyst_llm
        )

    #Pull from yaml config file with student context
    @agent
    def relevanceAgent(self) -> Agent:
        config = self._format_agent_config(self.agents_config['relevanceAgent'])
        return Agent(
            config=config,
            verbose=True,
            llm=self.relevance_llm
        )

    #Pull from yaml config file with student context
    @agent
    def guidelineAgent(self) -> Agent:
        config = self._format_agent_config(self.agents_config['guidelineAgent'])
        return Agent(
            config=config,
            verbose=True,
            llm=self.guideline_llm
        )

    #Pull from yaml config file
    @task
    def studentTask(self) -> Task:
        return Task(
            config=self.tasks_config['studentTask']
        )

    #Pull from yaml config file
    @task
    def analystTask(self) -> Task:
        return Task(
            config=self.tasks_config['analystTask'],
            output_file='report.md'
        )

    #Pull from yaml config file
    @task
    def relevanceTask(self) -> Task:
        return Task(
            config=self.tasks_config['relevanceTask'],
        )

    @task
    def guidelineTask(self) -> Task:
        return Task(
            config=self.tasks_config['guidelineTask'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Studentagents crew"""
        
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            manager_llm=self.crew_llm 
        )
